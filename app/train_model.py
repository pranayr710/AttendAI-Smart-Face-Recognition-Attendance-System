import json, cv2, numpy as np
from pathlib import Path
from .config import DATASET_DIR, MODELS_DIR

CASCADE_PATH = str(Path(__file__).resolve().parent.parent / "haarcascade_frontalface_default.xml")

def main():
    image_paths, labels = [], []
    label_map, idx = {}, 0
    for person_folder in sorted(DATASET_DIR.glob("*")):
        if not person_folder.is_dir(): continue
        parts = person_folder.name.split("_",1)
        if len(parts)!=2: 
            print(f"[SKIP] {person_folder.name}"); 
            continue
        person_id, name = parts[0], parts[1].replace("_"," ")
        label_map[idx] = {"person_id": person_id, "name": name}
        for img in sorted(person_folder.glob("*.png")):
            image_paths.append(img); labels.append(idx)
        idx += 1

    if not image_paths:
        raise RuntimeError("No images found. Run register_faces.py first.")

    detector = cv2.CascadeClassifier(CASCADE_PATH)
    faces, y = [], []
    for img_path, lbl in zip(image_paths, labels):
        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        if img is None: continue
        det = detector.detectMultiScale(img, 1.1, 5, minSize=(80,80))
        if len(det)>0:
            (x,y1,w,h) = sorted(det, key=lambda b:b[2]*b[3], reverse=True)[0]
            face = img[y1:y1+h, x:x+w]
        else:
            face = img
        faces.append(face); y.append(lbl)

    if not faces: raise RuntimeError("No faces detected for training.")

    recognizer = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
    recognizer.train(faces, np.array(y))
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    recognizer.save(str(MODELS_DIR / "lbph_model.yml"))
    with open(MODELS_DIR / "labels.json", "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    print("[OK] Model saved.")

if __name__ == "__main__":
    main()
