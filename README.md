# 🎓 Student Performance, Attendance & Face Verification Analytics System

A comprehensive full-stack Python and OpenCV academic analytics platform featuring role-based dashboards (Admin, Teacher, Student), teacher-controlled attendance permissions, Haar Cascade face detection, LBPH facial recognition for identity verification, batch marks entry, and interactive Plotly analytics.

---

## 🌟 Key Features

1. **Role-Based Access Control (RBAC):**
   - **Administrator:** Full management of faculty/teachers and students, account deactivation/reactivation, and system diagnostics.
   - **Faculty / Teacher:** Attendance session permission control (`Allow Attendance` / `Close Attendance`), batch marks entry with boundary validations, student roster management, and OpenCV face dataset registration.
   - **Student:** Profile details, attendance gauge and percentage tracking, subject-wise and exam-wise performance charts, and webcam-verified attendance marking during open sessions.

2. **Teacher-Controlled Face Attendance Workflow:**
   - Teacher opens an attendance session for an assigned class and subject.
   - Student logs in and accesses the **Take Attendance** tab (only enabled during an active session).
   - OpenCV captures the webcam frame, detects the student's face via Haar Cascade, crops and processes grayscale images.
   - The LBPH Face Recognizer matches the face against the student's registered biometric identity.
   - If verified and confirmed to be the logged-in student, attendance is permanently recorded in SQLite.
   - Strict prevention of duplicate attendance within the same session.
   - Once closed by the teacher, subsequent attendance attempts are rejected.

3. **Academic Performance & Marks Entry:**
   - Multi-student batch entry form for Midterm, Final, Quizzes, and Assignments.
   - Strict server-side validation ($0 \le \text{marks} \le \text{max\_marks}$).
   - Overall grade calculation, percentage, and interactive Plotly visualization.

4. **Biometric Face Registration & Training:**
   - Multi-sample face capture using Haar Cascade face detection.
   - Fast local training using OpenCV's LBPH (Local Binary Patterns Histograms) algorithm without external paid APIs.

---

## 🛠️ Technology Stack

- **Frontend & Web Framework:** [Streamlit](https://streamlit.io/)
- **Computer Vision & Face Recognition:** OpenCV (`opencv-contrib-python`), Haar Cascade Classifiers, LBPH Face Recognizer
- **Database:** SQLite (parameterized SQL queries, ACID compliance, soft-deletes)
- **Data Analytics & Visualization:** Pandas, NumPy, Plotly Express & Graph Objects
- **Authentication & Security:** bcrypt password hashing, session state gating

---

## 🚀 Setup & Execution Instructions (Windows)

### 1. Prerequisites
Ensure Python 3.10+ is installed on your computer.

### 2. Install Dependencies
Open PowerShell or Command Prompt in the project folder and run:
```powershell
pip install -r requirements.txt
```

> **Note on OpenCV:** Make sure `opencv-contrib-python` is installed (included in `requirements.txt`) as it provides the `cv2.face` module required for LBPH recognition.

### 3. Run the Application
Launch the Streamlit web dashboard:
```powershell
streamlit run main.py
```
The application will open automatically in your default web browser at `http://localhost:8501`.

---

## 🔑 Default Credentials (Pre-seeded Demo Accounts)

| Role | Username | Password | Notes |
|---|---|---|---|
| **Administrator** | `admin` | `admin@123` | Master control & faculty management |
| **Faculty / Teacher** | `teacher1` | `teach@123` | Computer Science department |
| **Faculty / Teacher** | `teacher2` | `teach@123` | Information Technology department |
| **Student** | `S001` | `student@123` | Aarav Patel (BE-CSE Div A) |
| **Student** | `S002` | `student@123` | Diya Joshi (BE-CSE Div A) |
| **Student** | `S003` | `student@123` | Rohan Verma (BE-CSE Div A) |
| **Student** | `S004` | `student@123` | Sneha Kulkarni (BE-IT Div B) |

---

## 🧪 Running Automated Tests

Run the test suite to verify database integrity, authentication, attendance permissions, marks validation, and face detection:
```powershell
pytest -v
```

---

## 📁 Project Structure

```
├── main.py                           # Application entry point and router
├── requirements.txt                  # Python package dependencies
├── README.md                         # Documentation & user guide
├── config/
│   ├── settings.py                   # Paths, thresholds, directory creation
│   └── constants.py                  # Roles, status codes, grade boundaries
├── app/
│   ├── auth/
│   │   ├── login.py                  # Login form & authentication
│   │   └── session.py                # Role-gated session management
│   ├── dashboards/
│   │   ├── admin_dashboard.py        # Faculty & student management
│   │   ├── teacher_dashboard.py      # Attendance control & marks entry
│   │   └── student_dashboard.py      # Student profile & attendance marking
│   ├── face_attendance/
│   │   ├── webcam.py                 # Safe webcam capture & release
│   │   ├── face_detector.py          # Haar Cascade face detection
│   │   ├── face_recognizer.py        # LBPH recognition & training
│   │   ├── face_registration.py      # Dataset collection pipeline
│   │   └── attendance_marker.py      # Verification & marking pipeline
│   ├── analytics/
│   │   ├── performance_analytics.py  # GPA, grades, marks aggregation
│   │   └── attendance_analytics.py   # Attendance percentages & logs
│   ├── database/
│   │   ├── schema.py                 # SQLite table definitions
│   │   ├── db_manager.py             # CRUD & transaction helper methods
│   │   └── seed_data.py              # Demo dataset generator
│   ├── components/
│   │   ├── cards.py                  # KPI summary cards
│   │   └── charts.py                 # Interactive Plotly visual charts
│   └── utils/
│       ├── helpers.py                # Password hashing & math utilities
│       └── validators.py             # Form & data validation
├── assets/
│   └── haarcascade_frontalface_default.xml # Face detection model
└── tests/
    ├── test_db_auth.py
    ├── test_attendance_permission.py
    ├── test_management_module.py
    ├── test_marks_module.py
    └── test_face_attendance_step5.py
```
