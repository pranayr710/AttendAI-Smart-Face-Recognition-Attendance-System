import argparse, cv2
from pathlib import Path
from .config import DATASET_DIR
from .attendance_db import init_db, upsert_student

CASCADE_PATH = str(Path(__file__).resolve().parent.parent / "haarcascade_frontalface_default.xml")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--person-id", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--max-samples", type=int, default=50)
    p.add_argument("--camera-index", type=int, default=0)
    args = p.parse_args()

    init_db()
    upsert_student(args.person_id, args.name)

    person_dir = DATASET_DIR / f"{args.person_id}_{args.name.replace(' ', '_')}"
    person_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(args.camera_index)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open camera index {args.camera_index}")
        return
    detector = cv2.CascadeClassifier(CASCADE_PATH)

    print("[INFO] SPACE=capture  Q=quit")
    count = 0
    while True:
        ok, frame = cap.read()
        if not ok: continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.1, 5, minSize=(100,100))
        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (255,255,255), 2)
        cv2.imshow("Register", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            if len(faces)==0:
                print("[INFO] No face, try again."); continue
            (x,y,w,h) = sorted(faces, key=lambda b:b[2]*b[3], reverse=True)[0]
            face = gray[y:y+h, x:x+w]
            outp = person_dir / f"img_{count:03d}.png"
            cv2.imwrite(str(outp), face)
            print(f"[SAVED] {outp}"); count += 1
            if count >= args.max_samples:
                print("[DONE] Collected max samples."); break
        elif key in (ord('q'), ord('Q')):
            break
    cap.release(); cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
