# app/face_attendance/webcam.py
import cv2
from config.settings import CAMERA_INDEX

class WebcamStream:
    def __init__(self, camera_index=CAMERA_INDEX):
        self.camera_index = camera_index
        self.cap = None

    def __enter__(self):
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_index)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def read_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

def capture_single_frame(camera_index=CAMERA_INDEX):
    """Safely capture a single frame from the webcam."""
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        return None
    try:
        # warm up camera
        for _ in range(3):
            cap.read()
        ret, frame = cap.read()
        return frame if ret else None
    finally:
        cap.release()
