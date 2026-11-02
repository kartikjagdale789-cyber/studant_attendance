# tests/test_marks_module.py
import pytest
from app.database.db_manager import DBManager
from app.database.seed_data import seed_demo_data
from app.utils.validators import validate_marks

@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_marks.db"
    db = DBManager(db_file)
    db.init_db()
    seed_demo_data(db)
    return db

def test_marks_validation():
    # Valid
    ok, msg = validate_marks(85.5, 100)
    assert ok is True

    # Zero marks is valid
    ok, msg = validate_marks(0, 100)
    assert ok is True

    # Max marks
    ok, msg = validate_marks(100, 100)
    assert ok is True

    # Negative marks invalid
    ok, msg = validate_marks(-5, 100)
    assert ok is False
    assert "negative" in msg.lower()

    # Marks > max invalid
    ok, msg = validate_marks(105, 100)
    assert ok is False
    assert "cannot exceed" in msg.lower()

    # Max <= 0 invalid
    ok, msg = validate_marks(50, 0)
    assert ok is False
    assert "greater than zero" in msg.lower()

def test_enter_and_update_marks_db(test_db):
    # Enter marks for Student 1
    ok, msg = test_db.enter_or_update_marks(student_id=1, subject_id=1, exam_type="Quiz 1", marks=18.0, max_marks=20.0)
    assert ok is True

    marks = test_db.get_student_marks(1)
    quiz_mark = [m for m in marks if m["exam_type"] == "Quiz 1" and m["subject_id"] == 1]
    assert len(quiz_mark) == 1
    assert quiz_mark[0]["marks"] == 18.0

    # Update marks
    ok_up, msg_up = test_db.enter_or_update_marks(student_id=1, subject_id=1, exam_type="Quiz 1", marks=19.5, max_marks=20.0)
    assert ok_up is True

    marks_updated = test_db.get_student_marks(1)
    quiz_updated = [m for m in marks_updated if m["exam_type"] == "Quiz 1" and m["subject_id"] == 1]
    assert len(quiz_updated) == 1
    assert quiz_updated[0]["marks"] == 19.5
