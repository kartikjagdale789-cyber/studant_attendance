# tests/test_face_attendance_step5.py
import pytest
import numpy as np
import cv2
import os
from app.face_attendance.face_detector import FaceDetector
from app.face_attendance.face_recognizer import FaceRecognizerLBPH

def test_face_detector_initialization():
    detector = FaceDetector()
    assert detector.classifier is not None
    assert not detector.classifier.empty()

def test_face_detector_on_frame():
    detector = FaceDetector()
    # Dummy black frame
    frame = np.zeros((300, 300, 3), dtype=np.uint8)
    gray, faces = detector.detect_faces(frame)
    assert gray is not None
    assert len(faces) == 0

def test_lbph_recognizer_train_and_predict(tmp_path):
    model_path = tmp_path / "test_model.yml"
    images_dir = tmp_path / "training"
    images_dir.mkdir()

    # Create synthetic face images for 2 students
    for sample_id in range(1, 5):
        img = np.full((100, 100), fill_value=sample_id * 30, dtype=np.uint8)
        cv2.imwrite(str(images_dir / f"Student.1.{sample_id}.jpg"), img)
        cv2.imwrite(str(images_dir / f"Student.2.{sample_id}.jpg"), 255 - img)

    recognizer = FaceRecognizerLBPH(model_path=model_path)
    ok, msg = recognizer.train_model(images_dir)
    assert ok is True
    assert os.path.exists(model_path)

    # Predict
    test_img = np.full((100, 100), fill_value=30, dtype=np.uint8)
    label, conf, is_match = recognizer.predict(test_img)
    assert label == 1
