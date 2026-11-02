# app/face_attendance/face_recognizer.py
import cv2
import os
import numpy as np
from PIL import Image
from config.settings import TRAINED_MODEL_PATH, CONFIDENCE_THRESHOLD, TRAINING_IMAGES_DIR

class FaceRecognizerLBPH:
    def __init__(self, model_path=None):
        self.model_path = str(model_path or TRAINED_MODEL_PATH)
        if not hasattr(cv2, 'face') or not hasattr(cv2.face, 'LBPHFaceRecognizer_create'):
            raise RuntimeError("OpenCV contrib is required for LBPHFaceRecognizer.")
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.is_loaded = False
        if os.path.exists(self.model_path):
            self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            self.recognizer.read(self.model_path)
            self.is_loaded = True
            return True
        return False

    def train_model(self, images_dir=None):
        """Train LBPH recognizer from images in training folder."""
        dir_path = str(images_dir or TRAINING_IMAGES_DIR)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            return False, "Training directory is empty."

        image_paths = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not image_paths:
            return False, "No face samples found in training directory."

        face_samples = []
        ids = []

        for path in image_paths:
            try:
                # Expected format: Student.<label>.<sample>.jpg or <label>_<sample>.jpg
                filename = os.path.basename(path)
                parts = filename.split(".")
                if len(parts) >= 3 and parts[0] == "Student":
                    label = int(parts[1])
                elif "_" in filename:
                    label = int(filename.split("_")[0])
                else:
                    continue

                pil_img = Image.open(path).convert('L')
                img_np = np.array(pil_img, 'uint8')
                face_samples.append(img_np)
                ids.append(label)
            except Exception:
                continue

        if not face_samples:
            return False, "No valid face samples could be parsed."

        self.recognizer.train(face_samples, np.array(ids))
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.recognizer.write(self.model_path)
        self.is_loaded = True
        return True, f"Trained successfully with {len(face_samples)} samples across {len(set(ids))} students."

    def predict(self, face_gray_crop, threshold=CONFIDENCE_THRESHOLD):
        """
        Predict identity.
        Returns: (label, confidence, is_recognized)
        In LBPH, confidence represents distance (0 = identical, lower = more confident).
        """
        if not self.is_loaded:
            if not self.load_model():
                return None, 999.0, False

        label, confidence = self.recognizer.predict(face_gray_crop)
        is_recognized = (confidence < threshold)
        return label, confidence, is_recognized
