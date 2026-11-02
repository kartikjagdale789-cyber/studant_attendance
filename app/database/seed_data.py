# app/database/seed_data.py
from app.database.db_manager import DBManager
from app.utils.helpers import hash_password, today_str, now_iso

def seed_demo_data(db: DBManager):
    """Seed clean initial demo data for testing."""
    db.init_db()

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM users")
        if cursor.fetchone()["cnt"] > 0:
            return  # Already seeded

        # 1. Admin
        admin_pass = hash_password("admin@123")
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES ('admin', ?, 'admin')", (admin_pass,))

        # 2. Classes
        classes_data = [
            ("BE-CSE", "A", "2025-2026"),
            ("BE-IT", "B", "2025-2026")
        ]
        cursor.executemany("INSERT INTO classes (class_name, division, academic_year) VALUES (?, ?, ?)", classes_data)
        class_cs_id = 1
        class_it_id = 2

        # 3. Teachers
        teacher_pass = hash_password("teach@123")
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES ('teacher1', ?, 'teacher')", (teacher_pass,))
        t1_uid = cursor.lastrowid
        cursor.execute("INSERT INTO teachers (user_id, name, department, email) VALUES (?, 'Prof. Rajesh Sharma', 'Computer Science', 'rajesh@college.edu')", (t1_uid,))
        t1_id = cursor.lastrowid

        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES ('teacher2', ?, 'teacher')", (teacher_pass,))
        t2_uid = cursor.lastrowid
        cursor.execute("INSERT INTO teachers (user_id, name, department, email) VALUES (?, 'Prof. Anita Desai', 'Information Tech', 'anita@college.edu')", (t2_uid,))
        t2_id = cursor.lastrowid

        # 4. Students
        student_pass = hash_password("student@123")
        students_info = [
            ("S001", "Aarav Patel", "CS01", class_cs_id, "aarav@college.edu", 1),
            ("S002", "Diya Joshi", "CS02", class_cs_id, "diya@college.edu", 2),
            ("S003", "Rohan Verma", "CS03", class_cs_id, "rohan@college.edu", 3),
            ("S004", "Sneha Kulkarni", "IT01", class_it_id, "sneha@college.edu", 4),
        ]

        student_ids = {}
        for uname, name, roll, cid, email, num_label in students_info:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'student')", (uname, student_pass))
            uid = cursor.lastrowid
            cursor.execute("INSERT INTO students (user_id, name, roll_number, class_id, email) VALUES (?, ?, ?, ?, ?)",
                           (uid, name, roll, cid, email))
            sid = cursor.lastrowid
            student_ids[uname] = sid
            # Register face mapping label
            cursor.execute("INSERT INTO face_encodings (student_id, numeric_label) VALUES (?, ?)", (sid, num_label))

        # 5. Subjects
        subjects_data = [
            ("CS801", "Computer Vision", class_cs_id, t1_id, 100),
            ("CS802", "Machine Learning", class_cs_id, t1_id, 100),
            ("IT801", "Cloud Computing", class_it_id, t2_id, 100)
        ]
        cursor.executemany("INSERT INTO subjects (subject_code, subject_name, class_id, teacher_id, total_marks) VALUES (?, ?, ?, ?, ?)", subjects_data)
        sub_cv_id = 1
        sub_ml_id = 2

        # 6. Sample Marks
        marks_data = [
            (student_ids["S001"], sub_cv_id, "Midterm", 85.0, 100.0, today_str(), now_iso()),
            (student_ids["S001"], sub_cv_id, "Final", 90.0, 100.0, today_str(), now_iso()),
            (student_ids["S001"], sub_ml_id, "Midterm", 78.0, 100.0, today_str(), now_iso()),
            (student_ids["S002"], sub_cv_id, "Midterm", 92.0, 100.0, today_str(), now_iso()),
            (student_ids["S002"], sub_ml_id, "Midterm", 88.0, 100.0, today_str(), now_iso()),
            (student_ids["S003"], sub_cv_id, "Midterm", 64.0, 100.0, today_str(), now_iso()),
        ]
        cursor.executemany("INSERT INTO marks (student_id, subject_id, exam_type, marks, max_marks, exam_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", marks_data)

        # 7. Sample Attendance Sessions
        cursor.execute("""
            INSERT INTO attendance_sessions (class_id, subject_id, teacher_id, session_date, status, opened_at, closed_at)
            VALUES (?, ?, ?, ?, 'closed', ?, ?)
        """, (class_cs_id, sub_cv_id, t1_id, today_str(), now_iso(), now_iso()))
        sess1_id = cursor.lastrowid

        # Mark S001 and S002 present in session 1
        cursor.execute("INSERT INTO attendance_records (session_id, student_id, status, method, verified_at) VALUES (?, ?, 'present', 'face_verification', ?)",
                       (sess1_id, student_ids["S001"], now_iso()))
        cursor.execute("INSERT INTO attendance_records (session_id, student_id, status, method, verified_at) VALUES (?, ?, 'present', 'face_verification', ?)",
                       (sess1_id, student_ids["S002"], now_iso()))

        conn.commit()

if __name__ == "__main__":
    db = DBManager()
    seed_demo_data(db)
    print("Database seeded successfully!")
