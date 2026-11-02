# tests/test_attendance_permission.py
import pytest
from app.database.db_manager import DBManager
from app.database.seed_data import seed_demo_data

@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_attendance.db"
    db = DBManager(db_file)
    db.init_db()
    seed_demo_data(db)
    return db

def test_teacher_open_and_close_session(test_db):
    # Teacher 1 opens session for Class 1 (BE-CSE A), Subject 1 (CS801)
    sess_id = test_db.create_attendance_session(class_id=1, subject_id=1, teacher_id=1)
    assert sess_id > 0

    active_sess = test_db.get_active_session_for_class_subject(1, 1)
    assert active_sess is not None
    assert active_sess["session_id"] == sess_id
    assert active_sess["status"] == "active"

    # Close session
    closed = test_db.close_attendance_session(sess_id, teacher_id=1)
    assert closed is True

    # Check active session is gone
    active_now = test_db.get_active_session_for_class_subject(1, 1)
    assert active_now is None

def test_student_attendance_marking_and_duplicate_prevention(test_db):
    # Open session
    sess_id = test_db.create_attendance_session(class_id=1, subject_id=1, teacher_id=1)

    # Student 1 marks attendance
    success, msg = test_db.mark_attendance(sess_id, student_id=1, method='face_verification')
    assert success is True
    assert "successfully" in msg.lower()

    # Student 1 attempts to mark again -> duplicate blocked
    success_dup, msg_dup = test_db.mark_attendance(sess_id, student_id=1, method='face_verification')
    assert success_dup is False
    assert "duplicate" in msg_dup.lower()

    # Close session
    test_db.close_attendance_session(sess_id, teacher_id=1)

    # Student 2 attempts to mark after session closed -> rejected
    success_closed, msg_closed = test_db.mark_attendance(sess_id, student_id=2, method='face_verification')
    assert success_closed is False
    assert "closed" in msg_closed.lower()

def test_deactivated_student_cannot_mark_attendance(test_db):
    sess_id = test_db.create_attendance_session(class_id=1, subject_id=1, teacher_id=1)
    # Deactivate student 3
    test_db.set_student_active(3, 0)

    success, msg = test_db.mark_attendance(sess_id, student_id=3)
    assert success is False
    assert "not active" in msg.lower()
