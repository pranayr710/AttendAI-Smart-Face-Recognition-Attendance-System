import argparse, json, cv2
from pathlib import Path
from .config import MODELS_DIR
from .attendance_db import init_db, mark_attendance
from .auto_export import export_all

CASCADE_PATH = str(Path(__file__).resolve().parent.parent / "haarcascade_frontalface_default.xml")

def main():
    p = argparse.ArgumentParser(description="Recognize and mark attendance")
    p.add_argument("--camera-index", type=int, default=0)
    p.add_argument("--threshold", type=float, default=70.0)
    p.add_argument("--subject-id", required=True, help="Subject ID to mark attendance for")
    args = p.parse_args()

    init_db()

    model_path = MODELS_DIR / "lbph_model.yml"
    labels_path = MODELS_DIR / "labels.json"
    if not (model_path.exists() and labels_path.exists()):
        raise RuntimeError("Model missing. Run train_model.py first.")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(model_path))
    with open(labels_path, "r", encoding="utf-8") as f:
        label_map = json.load(f)

    detector = cv2.CascadeClassifier(CASCADE_PATH)
    cap = cv2.VideoCapture(args.camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {args.camera_index}")

    print("[INFO] Q=quit")
    while True:
        ok, frame = cap.read()
        if not ok: continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.1, 5, minSize=(100,100))
        for (x,y,w,h) in faces:
            face = gray[y:y+h, x:x+w]
            label_id, conf = recognizer.predict(face)
            meta = label_map.get(str(label_id)) or label_map.get(label_id)
            if meta and conf <= args.threshold:
                person_id, name = meta["person_id"], meta["name"]
                created, msg = mark_attendance(person_id, args.subject_id)
                color = (0,255,0) if created else (255,255,0)
                cv2.putText(frame, f"{name} ({person_id})", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                cv2.putText(frame, f"{args.subject_id}  conf={conf:.1f}", (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.rectangle(frame, (x,y), (x+w,y+h), color, 2)
                # Auto export on each successful mark (idempotent due to UNIQUE constraint)
                export_all()
            else:
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,255), 2)
                cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
        cv2.imshow("Attendance", frame)
        if (cv2.waitKey(1) & 0xFF) in (ord('q'), ord('Q')): break
    cap.release(); cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
