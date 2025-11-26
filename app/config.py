import os
from pathlib import Path

# MySQL config
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'attendance'
}

BASE_DATA_DIR = Path(__file__).resolve().parent / 'data'
DATASET_DIR = BASE_DATA_DIR / 'dataset'
MODELS_DIR = BASE_DATA_DIR / 'models'
AUTO_EXPORT_MASTER = BASE_DATA_DIR / 'attendance_master.csv'
AUTO_EXPORT_DAILY = BASE_DATA_DIR / 'attendance_daily.csv'
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
