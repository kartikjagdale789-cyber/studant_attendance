# app/face_attendance/attendance_marker.py
import cv2
import numpy as np
from app.face_attendance.face_detector import FaceDetector
from app.face_attendance.face_recognizer import FaceRecognizerLBPH
from app.database.db_manager import DBManager

class AttendanceMarker:
    def __init__(self, db: DBManager):
        self.db = db
        self.detector = FaceDetector()
        self.recognizer = FaceRecognizerLBPH()

    def verify_and_mark(self, session_id: int, expected_student_id: int, frame: np.ndarray) -> tuple[bool, str, float, np.ndarray]:
        """
        Verify face in frame against expected student identity and mark attendance.
        Returns: (success, message, confidence, annotated_frame)
        """
        if frame is None:
            return False, "Failed to capture image from camera.", 999.0, None

        annotated = frame.copy()
        gray, faces = self.detector.detect_faces(frame)

        if len(faces) == 0:
            return False, "No face detected. Please face the camera directly in good lighting.", 999.0, annotated

        if len(faces) > 1:
            for (x, y, w, h) in faces:
                cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 2)
            return False, "Multiple faces detected. Only one student must be in frame.", 999.0, annotated

        x, y, w, h = faces[0]
        face_crop = gray[y:y+h, x:x+w]
        face_crop = cv2.resize(face_crop, (200, 200))

        # Check registered label
        expected_label = self.db.get_face_label_by_student_id(expected_student_id)
        if expected_label is None:
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(annotated, "Not Registered", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return False, "Your face data has not been registered yet. Please contact your instructor.", 999.0, annotated

        if not self.recognizer.is_loaded and not self.recognizer.load_model():
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 165, 255), 2)
            cv2.putText(annotated, "Model Not Trained", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            return False, "Face recognition model has not been trained yet. Please ask your instructor to register your face samples in Teacher Dashboard > 'Face Registration & Training'.", 999.0, annotated

        predicted_label, confidence, is_recognized = self.recognizer.predict(face_crop)

        if not is_recognized:
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(annotated, f"Unknown ({confidence:.1f})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return False, f"Face verification failed: Identity could not be verified (confidence distance: {confidence:.1f}).", confidence, annotated

        if predicted_label != expected_label:
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(annotated, "Identity Mismatch", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return False, f"Identity mismatch: Detected identity does not match your student account.", confidence, annotated

        # Face matched! Mark attendance in DB
        success, db_msg = self.db.mark_attendance(session_id, expected_student_id, method='face_verification')
        color = (0, 255, 0) if success else (0, 165, 255)
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
        cv2.putText(annotated, f"Verified ({confidence:.1f})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        return success, db_msg, confidence, annotated
