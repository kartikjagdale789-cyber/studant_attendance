# app/face_attendance/face_registration.py
import cv2
import os
import numpy as np
from PIL import Image
from config.settings import TRAINING_IMAGES_DIR, MIN_FACE_SAMPLES
from app.face_attendance.face_detector import FaceDetector
from app.face_attendance.face_recognizer import FaceRecognizerLBPH
from app.database.db_manager import DBManager

class FaceRegistrationService:
    def __init__(self, db: DBManager):
        self.db = db
        self.detector = FaceDetector()
        self.recognizer = FaceRecognizerLBPH()

    def register_face_from_frames(self, student_id: int, frames: list, label: int = None) -> tuple[bool, str, int]:
        """Process a batch of captured frames for a student, save samples, and retrain."""
        if not frames:
            return False, "No frames provided for registration.", 0

        if label is None:
            existing_label = self.db.get_face_label_by_student_id(student_id)
            label = existing_label if existing_label is not None else student_id

        os.makedirs(TRAINING_IMAGES_DIR, exist_ok=True)
        saved_count = 0

        for idx, frame in enumerate(frames):
            gray, faces = self.detector.detect_faces(frame)
            if len(faces) == 1:
                x, y, w, h = faces[0]
                face_crop = gray[y:y+h, x:x+w]
                face_crop = cv2.resize(face_crop, (200, 200))
                filename = f"Student.{label}.{saved_count + 1}.jpg"
                save_path = os.path.join(TRAINING_IMAGES_DIR, filename)
                cv2.imwrite(save_path, face_crop)
                saved_count += 1
                if saved_count >= 50:
                    break

        if saved_count < MIN_FACE_SAMPLES:
            return False, f"Only {saved_count} valid face samples captured (minimum {MIN_FACE_SAMPLES} required). Please try again under better lighting.", saved_count

        # Save metadata to DB
        self.db.register_face_label(student_id, label, str(TRAINING_IMAGES_DIR))

        # Train model
        success, msg = self.recognizer.train_model(TRAINING_IMAGES_DIR)
        if not success:
            return False, f"Samples saved ({saved_count}), but training failed: {msg}", saved_count

        return True, f"Face registration successful! {saved_count} samples trained for student.", saved_count
