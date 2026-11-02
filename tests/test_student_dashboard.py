# tests/test_student_dashboard.py
import pytest
from app.database.db_manager import DBManager
from app.database.seed_data import seed_demo_data
from app.analytics.performance_analytics import get_student_performance_summary

@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_student_dash.db"
    db = DBManager(db_file)
    db.init_db()
    seed_demo_data(db)
    return db

def test_student_performance_summary(test_db):
    # Student 1 (Aarav) has seeded marks
    summary = test_db.get_student_attendance_summary(1)
    assert summary["total_sessions"] >= 1
    assert summary["attended_sessions"] >= 1
    assert summary["percentage"] > 0

    perf = get_student_performance_summary(test_db, 1)
    assert perf["total_obtained"] > 0
    assert perf["total_max"] > 0
    assert perf["percentage"] > 0
    assert perf["grade"] in ["A+", "A", "B", "C", "D", "F"]

def test_empty_student_performance(test_db):
    # Student 4 (Sneha) has no initial marks
    perf = get_student_performance_summary(test_db, 4)
    assert perf["total_obtained"] == 0.0
    assert perf["grade"] == "N/A"
