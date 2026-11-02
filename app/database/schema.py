# app/database/schema.py

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'teacher', 'student')),
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_CLASSES_TABLE = """
CREATE TABLE IF NOT EXISTS classes (
    class_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL,
    division TEXT NOT NULL,
    academic_year TEXT NOT NULL,
    UNIQUE(class_name, division, academic_year)
);
"""

CREATE_TEACHERS_TABLE = """
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE RESTRICT
);
"""

CREATE_STUDENTS_TABLE = """
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    roll_number TEXT UNIQUE NOT NULL,
    class_id INTEGER NOT NULL,
    email TEXT UNIQUE NOT NULL,
    photo_path TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    FOREIGN KEY(class_id) REFERENCES classes(class_id) ON DELETE RESTRICT
);
"""

CREATE_SUBJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_code TEXT UNIQUE NOT NULL,
    subject_name TEXT NOT NULL,
    class_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    total_marks INTEGER DEFAULT 100,
    FOREIGN KEY(class_id) REFERENCES classes(class_id) ON DELETE RESTRICT,
    FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id) ON DELETE RESTRICT
);
"""

CREATE_MARKS_TABLE = """
CREATE TABLE IF NOT EXISTS marks (
    mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    exam_type TEXT NOT NULL,
    marks REAL NOT NULL,
    max_marks REAL NOT NULL DEFAULT 100.0,
    exam_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE RESTRICT,
    FOREIGN KEY(subject_id) REFERENCES subjects(subject_id) ON DELETE RESTRICT,
    UNIQUE(student_id, subject_id, exam_type)
);
"""

CREATE_ATTENDANCE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS attendance_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    session_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('active', 'closed')),
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    FOREIGN KEY(class_id) REFERENCES classes(class_id) ON DELETE RESTRICT,
    FOREIGN KEY(subject_id) REFERENCES subjects(subject_id) ON DELETE RESTRICT,
    FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id) ON DELETE RESTRICT
);
"""

CREATE_ATTENDANCE_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS attendance_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('present', 'absent')),
    method TEXT NOT NULL CHECK(method IN ('face_verification', 'manual')),
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES attendance_sessions(session_id) ON DELETE RESTRICT,
    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE RESTRICT,
    UNIQUE(session_id, student_id)
);
"""

CREATE_FACE_ENCODINGS_TABLE = """
CREATE TABLE IF NOT EXISTS face_encodings (
    encoding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER UNIQUE NOT NULL,
    numeric_label INTEGER UNIQUE NOT NULL,
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE RESTRICT
);
"""

ALL_TABLES = [
    CREATE_USERS_TABLE,
    CREATE_CLASSES_TABLE,
    CREATE_TEACHERS_TABLE,
    CREATE_STUDENTS_TABLE,
    CREATE_SUBJECTS_TABLE,
    CREATE_MARKS_TABLE,
    CREATE_ATTENDANCE_SESSIONS_TABLE,
    CREATE_ATTENDANCE_RECORDS_TABLE,
    CREATE_FACE_ENCODINGS_TABLE
]
