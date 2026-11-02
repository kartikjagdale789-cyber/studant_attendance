# tests/test_db_auth.py
import pytest
import sqlite3
from app.database.db_manager import DBManager
from app.database.seed_data import seed_demo_data
from app.utils.helpers import hash_password, verify_password

@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_auth.db"
    db = DBManager(db_file)
    db.init_db()
    seed_demo_data(db)
    return db

def test_user_authentication(test_db):
    admin = test_db.get_user_by_username("admin")
    assert admin is not None
    assert admin["role"] == "admin"
    assert verify_password("admin@123", admin["password_hash"])
    assert not verify_password("wrong_password", admin["password_hash"])

def test_teacher_authentication(test_db):
    teacher = test_db.get_user_by_username("teacher1")
    assert teacher is not None
    assert teacher["role"] == "teacher"
    assert verify_password("teach@123", teacher["password_hash"])

def test_student_authentication(test_db):
    student = test_db.get_user_by_username("S001")
    assert student is not None
    assert student["role"] == "student"
    assert verify_password("student@123", student["password_hash"])

def test_create_user_and_deactivate(test_db):
    pw = hash_password("secret123")
    uid = test_db.create_user("temp_user", pw, "student")
    assert uid > 0
    u = test_db.get_user_by_username("temp_user")
    assert u["is_active"] == 1
    test_db.set_user_active(uid, 0)
    u_deactivated = test_db.get_user_by_username("temp_user")
    assert u_deactivated["is_active"] == 0
