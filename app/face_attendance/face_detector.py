# app/face_attendance/face_detector.py
import cv2
import os
from config.settings import CASCADE_PATH

class FaceDetector:
    def __init__(self, cascade_path=None):
        path = cascade_path or CASCADE_PATH
        if not os.path.exists(path):
            # Fallback to OpenCV built-in
            path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.cascade_path = str(path)
        self.classifier = cv2.CascadeClassifier(self.cascade_path)
        if self.classifier.empty():
            raise RuntimeError(f"Failed to load Haar Cascade from {self.cascade_path}")

    def detect_faces(self, frame, scale_factor=1.2, min_neighbors=5, min_size=(100, 100)):
        """Detect faces in BGR image, returns (gray_frame, list_of_faces)."""
        if frame is None:
            return None, []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.classifier.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_size
        )
        return gray, faces
