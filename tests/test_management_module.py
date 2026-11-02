# tests/test_management_module.py
import pytest
from app.database.db_manager import DBManager
from app.database.seed_data import seed_demo_data
from app.utils.helpers import hash_password

@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_mgmt.db"
    db = DBManager(db_file)
    db.init_db()
    seed_demo_data(db)
    return db

def test_add_and_update_student(test_db):
    pw = hash_password("pass123")
    uid = test_db.create_user("student_new", pw, "student")
    sid = test_db.create_student(uid, "Kunal Shah", "CS99", 1, "kunal@college.edu")
    assert sid > 0

    s = test_db.get_student_by_id(sid)
    assert s["name"] == "Kunal Shah"
    assert s["roll_number"] == "CS99"

    test_db.update_student(sid, "Kunal R. Shah", "CS99", 1, "kunal.shah@college.edu")
    s_updated = test_db.get_student_by_id(sid)
    assert s_updated["name"] == "Kunal R. Shah"
    assert s_updated["email"] == "kunal.shah@college.edu"

def test_deactivate_and_reactivate_student(test_db):
    s = test_db.get_student_by_id(1)
    assert s["is_active"] == 1

    test_db.set_student_active(1, 0)
    s_off = test_db.get_student_by_id(1)
    assert s_off["is_active"] == 0

    test_db.set_student_active(1, 1)
    s_on = test_db.get_student_by_id(1)
    assert s_on["is_active"] == 1

def test_add_and_deactivate_teacher(test_db):
    pw = hash_password("pass123")
    uid = test_db.create_user("prof_sunil", pw, "teacher")
    tid = test_db.create_teacher(uid, "Prof. Sunil Mehta", "Electronics", "sunil@college.edu")
    assert tid > 0

    t = test_db.get_teacher_by_id(tid)
    assert t["name"] == "Prof. Sunil Mehta"
    assert t["is_active"] == 1

    test_db.set_teacher_active(tid, 0)
    t_off = test_db.get_teacher_by_id(tid)
    assert t_off["is_active"] == 0
