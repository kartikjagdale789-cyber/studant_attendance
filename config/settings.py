# config/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "dashboard.db"

# Assets and models
ASSETS_DIR = BASE_DIR / "assets"
CASCADE_PATH = ASSETS_DIR / "haarcascade_frontalface_default.xml"

# Face Data storage
TRAINING_IMAGES_DIR = DATA_DIR / "TrainingImage"
TRAINED_MODEL_DIR = DATA_DIR / "TrainingImageLabel"
TRAINED_MODEL_PATH = TRAINED_MODEL_DIR / "Trainner.yml"
STUDENT_DETAILS_CSV = DATA_DIR / "StudentDetails" / "StudentDetails.csv"

# Camera & Recognition configuration
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 70.0  # LBPH distance threshold: lower = stricter match
MIN_FACE_SAMPLES = 20
MAX_FACE_SAMPLES = 50

# Ensure essential directories exist
for p in [DATA_DIR, ASSETS_DIR, TRAINING_IMAGES_DIR, TRAINED_MODEL_DIR, DATA_DIR / "StudentDetails"]:
    p.mkdir(parents=True, exist_ok=True)
