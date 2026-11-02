# app/database/db_manager.py
import sqlite3
from typing import Optional, Dict, Any, List
from config.settings import DB_PATH
from app.database.schema import ALL_TABLES
from app.utils.helpers import today_str, now_iso

class DBManager:
    def __init__(self, db_path=None):
        self.db_path = str(db_path or DB_PATH)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for stmt in ALL_TABLES:
                cursor.execute(stmt)
            conn.commit()

    # ---------------- USER & AUTH ----------------
    def get_user_by_username(self, username: str) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            return cursor.fetchone()

    def get_user_by_id(self, user_id: int) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone()

    def create_user(self, username: str, password_hash: str, role: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, is_active) VALUES (?, ?, ?, 1)",
                (username, password_hash, role)
            )
            conn.commit()
            return cursor.lastrowid

    def set_user_active(self, user_id: int, is_active: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_active = ? WHERE user_id = ?", (is_active, user_id))
            conn.commit()

    # ---------------- TEACHERS ----------------
    def get_teacher_by_user_id(self, user_id: int) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teachers WHERE user_id = ?", (user_id,))
            return cursor.fetchone()

    def get_teacher_by_id(self, teacher_id: int) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teachers WHERE teacher_id = ?", (teacher_id,))
            return cursor.fetchone()

    def get_all_teachers(self, include_inactive: bool = True) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if include_inactive:
                cursor.execute("SELECT t.*, u.username FROM teachers t JOIN users u ON t.user_id = u.user_id ORDER BY t.name")
            else:
                cursor.execute("SELECT t.*, u.username FROM teachers t JOIN users u ON t.user_id = u.user_id WHERE t.is_active = 1 AND u.is_active = 1 ORDER BY t.name")
            return cursor.fetchall()

    def create_teacher(self, user_id: int, name: str, department: str, email: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO teachers (user_id, name, department, email, is_active) VALUES (?, ?, ?, ?, 1)",
                (user_id, name, department, email)
            )
            conn.commit()
            return cursor.lastrowid

    def update_teacher(self, teacher_id: int, name: str, department: str, email: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE teachers SET name = ?, department = ?, email = ? WHERE teacher_id = ?",
                (name, department, email, teacher_id)
            )
            conn.commit()

    def set_teacher_active(self, teacher_id: int, is_active: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM teachers WHERE teacher_id = ?", (teacher_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE teachers SET is_active = ? WHERE teacher_id = ?", (is_active, teacher_id))
                cursor.execute("UPDATE users SET is_active = ? WHERE user_id = ?", (is_active, row["user_id"]))
                conn.commit()

    # ---------------- STUDENTS ----------------
    def get_student_by_user_id(self, user_id: int) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, c.class_name, c.division, c.academic_year, u.username
                FROM students s
                JOIN classes c ON s.class_id = c.class_id
                JOIN users u ON s.user_id = u.user_id
                WHERE s.user_id = ?
            """, (user_id,))
            return cursor.fetchone()

    def get_student_by_id(self, student_id: int) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, c.class_name, c.division, c.academic_year, u.username
                FROM students s
                JOIN classes c ON s.class_id = c.class_id
                JOIN users u ON s.user_id = u.user_id
                WHERE s.student_id = ?
            """, (student_id,))
            return cursor.fetchone()

    def get_student_by_roll_number(self, roll_number: str) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE roll_number = ?", (roll_number,))
            return cursor.fetchone()

    def get_all_students(self, include_inactive: bool = True) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT s.*, c.class_name, c.division, c.academic_year, u.username
                FROM students s
                JOIN classes c ON s.class_id = c.class_id
                JOIN users u ON s.user_id = u.user_id
            """
            if not include_inactive:
                query += " WHERE s.is_active = 1 AND u.is_active = 1"
            query += " ORDER BY c.class_name, s.roll_number"
            cursor.execute(query)
            return cursor.fetchall()

    def get_students_by_class(self, class_id: int, include_inactive: bool = False) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT s.*, c.class_name, c.division, u.username
                FROM students s
                JOIN classes c ON s.class_id = c.class_id
                JOIN users u ON s.user_id = u.user_id
                WHERE s.class_id = ?
            """
            if not include_inactive:
                query += " AND s.is_active = 1 AND u.is_active = 1"
            query += " ORDER BY s.roll_number"
            cursor.execute(query, (class_id,))
            return cursor.fetchall()

    def create_student(self, user_id: int, name: str, roll_number: str, class_id: int, email: str, photo_path: str = "") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO students (user_id, name, roll_number, class_id, email, photo_path, is_active) VALUES (?, ?, ?, ?, ?, ?, 1)",
                (user_id, name, roll_number, class_id, email, photo_path)
            )
            conn.commit()
            return cursor.lastrowid

    def update_student(self, student_id: int, name: str, roll_number: str, class_id: int, email: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE students SET name = ?, roll_number = ?, class_id = ?, email = ? WHERE student_id = ?",
                (name, roll_number, class_id, email, student_id)
            )
            conn.commit()

    def set_student_active(self, student_id: int, is_active: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM students WHERE student_id = ?", (student_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE students SET is_active = ? WHERE student_id = ?", (is_active, student_id))
                cursor.execute("UPDATE users SET is_active = ? WHERE user_id = ?", (is_active, row["user_id"]))
                conn.commit()

    def search_students(self, keyword: str) -> List[sqlite3.Row]:
        pattern = f"%{keyword.strip()}%"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, c.class_name, c.division, c.academic_year, u.username
                FROM students s
                JOIN classes c ON s.class_id = c.class_id
                JOIN users u ON s.user_id = u.user_id
                WHERE s.name LIKE ? OR s.roll_number LIKE ? OR s.email LIKE ? OR u.username LIKE ?
                ORDER BY s.roll_number
            """, (pattern, pattern, pattern, pattern))
            return cursor.fetchall()

    # ---------------- CLASSES & SUBJECTS ----------------
    def get_all_classes(self) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classes ORDER BY class_name, division")
            return cursor.fetchall()

    def get_class_by_id(self, class_id: int) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classes WHERE class_id = ?", (class_id,))
            return cursor.fetchone()

    def get_all_subjects(self) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, c.class_name, c.division, t.name as teacher_name
                FROM subjects s
                JOIN classes c ON s.class_id = c.class_id
                JOIN teachers t ON s.teacher_id = t.teacher_id
                ORDER BY s.subject_code
            """)
            return cursor.fetchall()

    def get_subjects_by_class(self, class_id: int) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, t.name as teacher_name
                FROM subjects s
                JOIN teachers t ON s.teacher_id = t.teacher_id
                WHERE s.class_id = ?
                ORDER BY s.subject_code
            """, (class_id,))
            return cursor.fetchall()

    def get_subjects_by_teacher(self, teacher_id: int) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, c.class_name, c.division
                FROM subjects s
                JOIN classes c ON s.class_id = c.class_id
                WHERE s.teacher_id = ?
                ORDER BY c.class_name, s.subject_name
            """, (teacher_id,))
            return cursor.fetchall()

    def get_subject_by_id(self, subject_id: int) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM subjects WHERE subject_id = ?", (subject_id,))
            return cursor.fetchone()

    def get_subject_by_code(self, subject_code: str) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM subjects WHERE subject_code = ?", (subject_code.strip().upper(),))
            return cursor.fetchone()

    def create_subject(self, subject_code: str, subject_name: str, class_id: int, teacher_id: int, total_marks: int = 100) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO subjects (subject_code, subject_name, class_id, teacher_id, total_marks)
                VALUES (?, ?, ?, ?, ?)
            """, (subject_code.strip().upper(), subject_name.strip(), class_id, teacher_id, total_marks))
            conn.commit()
            return cursor.lastrowid

    def assign_subject_to_teacher(self, subject_id: int, teacher_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE subjects SET teacher_id = ? WHERE subject_id = ?", (teacher_id, subject_id))
            conn.commit()

    # ---------------- ATTENDANCE SESSIONS ----------------
    def create_attendance_session(self, class_id: int, subject_id: int, teacher_id: int) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO attendance_sessions (class_id, subject_id, teacher_id, session_date, status, opened_at)
                VALUES (?, ?, ?, ?, 'active', ?)
            """, (class_id, subject_id, teacher_id, today_str(), now_iso()))
            conn.commit()
            return cursor.lastrowid

    def close_attendance_session(self, session_id: int, teacher_id: Optional[int] = None) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if teacher_id:
                cursor.execute("""
                    UPDATE attendance_sessions
                    SET status = 'closed', closed_at = ?
                    WHERE session_id = ? AND teacher_id = ? AND status = 'active'
                """, (now_iso(), session_id, teacher_id))
            else:
                cursor.execute("""
                    UPDATE attendance_sessions
                    SET status = 'closed', closed_at = ?
                    WHERE session_id = ? AND status = 'active'
                """, (now_iso(), session_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_active_session_for_class_subject(self, class_id: int, subject_id: int) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM attendance_sessions
                WHERE class_id = ? AND subject_id = ? AND status = 'active'
                ORDER BY session_id DESC LIMIT 1
            """, (class_id, subject_id))
            return cursor.fetchone()

    def get_active_session_for_student(self, student_id: int) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sess.*, subj.subject_name, subj.subject_code, t.name as teacher_name
                FROM attendance_sessions sess
                JOIN students stud ON sess.class_id = stud.class_id
                JOIN subjects subj ON sess.subject_id = subj.subject_id
                JOIN teachers t ON sess.teacher_id = t.teacher_id
                WHERE stud.student_id = ? AND sess.status = 'active' AND stud.is_active = 1
                ORDER BY sess.session_id DESC LIMIT 1
            """, (student_id,))
            return cursor.fetchone()

    def get_session_by_id(self, session_id: int) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sess.*, c.class_name, c.division, s.subject_name, s.subject_code, t.name as teacher_name
                FROM attendance_sessions sess
                JOIN classes c ON sess.class_id = c.class_id
                JOIN subjects s ON sess.subject_id = s.subject_id
                JOIN teachers t ON sess.teacher_id = t.teacher_id
                WHERE sess.session_id = ?
            """, (session_id,))
            return cursor.fetchone()

    def get_sessions_by_teacher(self, teacher_id: int, limit: int = 20) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sess.*, c.class_name, c.division, s.subject_name,
                       COUNT(r.record_id) as total_present
                FROM attendance_sessions sess
                JOIN classes c ON sess.class_id = c.class_id
                JOIN subjects s ON sess.subject_id = s.subject_id
                LEFT JOIN attendance_records r ON sess.session_id = r.session_id
                WHERE sess.teacher_id = ?
                GROUP BY sess.session_id
                ORDER BY sess.session_id DESC
                LIMIT ?
            """, (teacher_id, limit))
            return cursor.fetchall()

    # ---------------- ATTENDANCE RECORDS ----------------
    def has_student_attended(self, session_id: int, student_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT record_id FROM attendance_records
                WHERE session_id = ? AND student_id = ?
            """, (session_id, student_id))
            return cursor.fetchone() is not None

    def mark_attendance(self, session_id: int, student_id: int, method: str = 'face_verification') -> tuple[bool, str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 1. Check if session is active
            cursor.execute("SELECT status, class_id FROM attendance_sessions WHERE session_id = ?", (session_id,))
            sess = cursor.fetchone()
            if not sess:
                return False, "Attendance session does not exist."
            if sess["status"] != "active":
                return False, "Attendance session is closed. Attendance cannot be recorded."

            # 2. Check student active and matching class
            cursor.execute("SELECT is_active, class_id FROM students WHERE student_id = ?", (student_id,))
            stud = cursor.fetchone()
            if not stud or stud["is_active"] == 0:
                return False, "Student account is not active."
            if stud["class_id"] != sess["class_id"]:
                return False, "Student is not enrolled in this class."

            # 3. Check duplicate
            cursor.execute("SELECT record_id FROM attendance_records WHERE session_id = ? AND student_id = ?", (session_id, student_id))
            if cursor.fetchone():
                return False, "Duplicate attendance: You have already marked attendance for this session."

            # 4. Insert
            cursor.execute("""
                INSERT INTO attendance_records (session_id, student_id, status, method, verified_at)
                VALUES (?, ?, 'present', ?, ?)
            """, (session_id, student_id, method, now_iso()))
            conn.commit()
            return True, "Attendance marked successfully!"

    def get_records_by_session(self, session_id: int) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.*, s.name, s.roll_number, s.email
                FROM attendance_records r
                JOIN students s ON r.student_id = s.student_id
                WHERE r.session_id = ?
                ORDER BY s.roll_number
            """, (session_id,))
            return cursor.fetchall()

    def get_student_attendance_summary(self, student_id: int) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT class_id FROM students WHERE student_id = ?", (student_id,))
            stud = cursor.fetchone()
            if not stud:
                return {"total_sessions": 0, "attended_sessions": 0, "percentage": 0.0}

            class_id = stud["class_id"]
            cursor.execute("SELECT COUNT(*) as cnt FROM attendance_sessions WHERE class_id = ?", (class_id,))
            total_sessions = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) as cnt FROM attendance_records WHERE student_id = ?", (student_id,))
            attended = cursor.fetchone()["cnt"]

            pct = (attended / total_sessions * 100.0) if total_sessions > 0 else 0.0
            return {
                "total_sessions": total_sessions,
                "attended_sessions": attended,
                "percentage": round(pct, 2)
            }

    def get_student_attendance_history(self, student_id: int) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.record_id, r.verified_at, r.method, r.status,
                       sess.session_date, subj.subject_name, subj.subject_code,
                       t.name as teacher_name
                FROM attendance_records r
                JOIN attendance_sessions sess ON r.session_id = sess.session_id
                JOIN subjects subj ON sess.subject_id = subj.subject_id
                JOIN teachers t ON sess.teacher_id = t.teacher_id
                WHERE r.student_id = ?
                ORDER BY r.verified_at DESC
            """, (student_id,))
            return cursor.fetchall()

    # ---------------- MARKS ----------------
    def enter_or_update_marks(self, student_id: int, subject_id: int, exam_type: str,
                              marks: float, max_marks: float = 100.0, exam_date: Optional[str] = None) -> tuple[bool, str]:
        if max_marks <= 0:
            return False, "Maximum marks must be greater than zero."
        if marks < 0 or marks > max_marks:
            return False, f"Marks ({marks}) must be between 0 and maximum marks ({max_marks})."

        exam_date = exam_date or today_str()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check student active
            cursor.execute("SELECT is_active FROM students WHERE student_id = ?", (student_id,))
            st = cursor.fetchone()
            if not st or st["is_active"] == 0:
                return False, "Student account is deactivated."

            cursor.execute("""
                INSERT INTO marks (student_id, subject_id, exam_type, marks, max_marks, exam_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id, subject_id, exam_type)
                DO UPDATE SET marks = excluded.marks, max_marks = excluded.max_marks,
                              exam_date = excluded.exam_date, created_at = excluded.created_at
            """, (student_id, subject_id, exam_type, marks, max_marks, exam_date, now_iso()))
            conn.commit()
            return True, "Marks saved successfully."

    def get_student_marks(self, student_id: int) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.*, s.subject_name, s.subject_code,
                       ROUND((m.marks / m.max_marks) * 100.0, 2) as percentage
                FROM marks m
                JOIN subjects s ON m.subject_id = s.subject_id
                WHERE m.student_id = ?
                ORDER BY s.subject_name, m.exam_type
            """, (student_id,))
            return cursor.fetchall()

    def get_marks_by_class_subject_exam(self, class_id: int, subject_id: int, exam_type: str) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.student_id, s.roll_number, s.name, s.email,
                       m.mark_id, m.marks, m.max_marks, m.exam_date
                FROM students s
                LEFT JOIN marks m ON s.student_id = m.student_id AND m.subject_id = ? AND m.exam_type = ?
                WHERE s.class_id = ? AND s.is_active = 1
                ORDER BY s.roll_number
            """, (subject_id, exam_type, class_id))
            return cursor.fetchall()

    # ---------------- FACE RECOGNITION METADATA ----------------
    def register_face_label(self, student_id: int, numeric_label: int, image_path: str = ""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO face_encodings (student_id, numeric_label, image_path, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(student_id)
                DO UPDATE SET numeric_label = excluded.numeric_label,
                              image_path = excluded.image_path,
                              created_at = excluded.created_at
            """, (student_id, numeric_label, image_path, now_iso()))
            conn.commit()

    def get_student_by_numeric_label(self, numeric_label: int) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, f.numeric_label
                FROM face_encodings f
                JOIN students s ON f.student_id = s.student_id
                WHERE f.numeric_label = ? AND s.is_active = 1
            """, (numeric_label,))
            return cursor.fetchone()

    def get_face_label_by_student_id(self, student_id: int) -> Optional[int]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT numeric_label FROM face_encodings WHERE student_id = ?", (student_id,))
            row = cursor.fetchone()
            return row["numeric_label"] if row else None

    def get_all_face_mappings(self) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.numeric_label, s.student_id, s.roll_number, s.name, s.is_active
                FROM face_encodings f
                JOIN students s ON f.student_id = s.student_id
            """)
            return cursor.fetchall()
