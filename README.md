
# AttendAI – Smart Face Recognition Attendance System 🎓🤖

AttendAI is a smart, AI-powered biometric attendance system that uses **Real-Time Facial Recognition** to automate and securely log attendance data.  
Built for schools, workplaces, and labs where automation and accuracy matter.

## 🚀 Features

- 📸 **Live Face Detection & Recognition**
- 🧠 **Trained ML Model (LBPH / Haar Cascade)**
- 🔁 **Automatic Realtime Attendance Logging**
- 🔐 **Unique Identity Per User**
- 🗂 **SQLite Database Storage**
- 📁 **Dataset Creation + Model Training Support**
- 📤 **Export Attendance as CSV/Excel**
- 🖥 **Supports Camera Input (Laptop/Webcam)**

## 🛠 Tech Stack

| Type | Technology |
|------|------------|
| Language | Python |
| AI / Vision | OpenCV, LBPH Face Recognizer |
| Database | SQLite |
| Frontend (optional) | Next.js |
| Used Models | Haar Cascade Classifier |


## 📂 Project Structure
```

AttendAI/
├── app/
│   ├── main.py
│   ├── register_faces.py
│   ├── train_model.py
│   ├── recognize_and_mark.py
│   ├── export_csv.py
│   └── config.py
├── requirements.txt
└── README.md
```

> **Note:** Dataset images & trained model are NOT included due to file size and privacy — see download section below.


## 📦 Installation

### 1️⃣ Clone Repository

```sh
git clone https://github.com/pranayr710/AttendAI-Smart-Face-Recognition-Attendance-System.git
cd AttendAI-Smart-Face-Recognition-Attendance-System
````

### 2️⃣ Create & Activate Virtual Environment

```sh
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
```

### 3️⃣ Install Dependencies

```sh
pip install -r requirements.txt
```

## 🔧 Usage Guide

### 📍 Step 1 — Register a User & Generate Dataset

```sh
python app/register_faces.py
```

User images will be captured and stored.


### 📍 Step 2 — Train the face recognition model

```sh
python app/train_model.py
```

This generates a `.yml` trained ML model.


### 📍 Step 3 — Start Attendance System

```sh
python app/recognize_and_mark.py
```

The camera will open and start realtime recognition.


### 📍 Step 4 — Export Attendance

```sh
python app/export_csv.py
```


## 📁 Dataset & Model Download

> *(Add links when uploaded — GitHub Releases recommended)*

* 📦 Dataset: `Coming soon`
* 🤖 Trained Model: `Coming soon`



## 🧩 Roadmap

* [ ] Mobile App Integration
* [ ] Admin Dashboard
* [ ] Multi-Camera Support
* [ ] Cloud Sync
* [ ] Attendance Analytics & Graphs


## 🤝 Contributing

PRs and feature improvements are welcome!

1. Fork the repo
2. Create a branch: `feature-name`
3. Commit changes
4. Create a Pull Request 🚀



## 🛡 License

This project is licensed under the **MIT License**.
