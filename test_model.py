import json, cv2
from pathlib import Path

MODELS_DIR = Path('app/data/models')
model_path = MODELS_DIR / "lbph_model.yml"
labels_path = MODELS_DIR / "labels.json"

if not (model_path.exists() and labels_path.exists()):
    print("Model files not found.")
else:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(model_path))
    with open(labels_path, "r", encoding="utf-8") as f:
        label_map = json.load(f)
    print("Model loaded successfully.")
    print("Labels:", label_map)
