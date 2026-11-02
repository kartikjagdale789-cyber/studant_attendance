# config/constants.py

# Roles
ROLE_ADMIN = "admin"
ROLE_TEACHER = "teacher"
ROLE_STUDENT = "student"
ALL_ROLES = [ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT]

# Session status
SESSION_ACTIVE = "active"
SESSION_CLOSED = "closed"

# Attendance methods
METHOD_FACE = "face_verification"
METHOD_MANUAL = "manual"

# Attendance status
ATTENDANCE_PRESENT = "present"
ATTENDANCE_ABSENT = "absent"

# Exam types
EXAM_TYPES = ["Midterm", "Final", "Quiz 1", "Quiz 2", "Assignment 1", "Assignment 2", "Project"]

# Grading scale
GRADE_BOUNDARIES = [
    (90, "A+", "Outstanding"),
    (80, "A", "Excellent"),
    (70, "B", "Very Good"),
    (60, "C", "Good"),
    (50, "D", "Pass"),
    (0, "F", "Fail")
]
