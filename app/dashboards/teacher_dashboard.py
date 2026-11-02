# app/dashboards/teacher_dashboard.py
import streamlit as st
import pandas as pd
from app.database.db_manager import DBManager
from app.auth.session import get_user_details
from app.components.cards import metric_card
from app.face_attendance.face_registration import FaceRegistrationService
from app.face_attendance.face_recognizer import FaceRecognizerLBPH
from config.constants import EXAM_TYPES
from app.utils.validators import validate_email, validate_marks

def render_teacher_dashboard(db: DBManager):
    teacher = get_user_details()
    teacher_id = teacher.get("teacher_id")

    st.title("🏫 Faculty & Teacher Dashboard")
    st.markdown(f"**Welcome, {teacher.get('name', 'Professor')}** | Department of {teacher.get('department', 'Engineering')}")

    assigned_subjects = db.get_subjects_by_teacher(teacher_id)
    if not assigned_subjects:
        st.warning("You currently have no classes or subjects assigned. Please contact the administrator.")
        return

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Attendance Control",
        "📝 Enter Marks",
        "👥 Student Directory",
        "📸 Face Registration & Training"
    ])

    # ---------------- TAB 1: ATTENDANCE CONTROL ----------------
    with tab1:
        st.subheader("Class Attendance Session Permission")
        subj_options = {
            f"{s['subject_name']} ({s['subject_code']}) - {s['class_name']} Div {s['division']}": s
            for s in assigned_subjects
        }
        selected_subj_key = st.selectbox("Select Assigned Subject & Class", list(subj_options.keys()), key="att_subj_sel")
        selected_subj = subj_options[selected_subj_key]
        class_id = selected_subj["class_id"]
        subject_id = selected_subj["subject_id"]

        active_session = db.get_active_session_for_class_subject(class_id, subject_id)

        col_ctrl1, col_ctrl2 = st.columns([1, 1])
        with col_ctrl1:
            if not active_session:
                st.info("No active attendance session for this class.")
                if st.button("🟢 Allow Attendance (Open Session)", type="primary", use_container_width=True):
                    sess_id = db.create_attendance_session(class_id, subject_id, teacher_id)
                    st.success(f"Attendance session #{sess_id} opened! Students can now mark attendance using webcam verification.")
                    st.rerun()
            else:
                st.success(f"🟢 Attendance Session #{active_session['session_id']} is ACTIVE!")
                st.write(f"Opened at: `{active_session['opened_at']}`")
                if st.button("🔴 Close Attendance Session", type="primary", use_container_width=True):
                    db.close_attendance_session(active_session["session_id"], teacher_id)
                    st.warning("Attendance session closed. No further attendance can be marked.")
                    st.rerun()

        with col_ctrl2:
            if active_session:
                records = db.get_records_by_session(active_session["session_id"])
                metric_card("Students Verified", str(len(records)), "Marked present via webcam", "#10B981")
            else:
                metric_card("Session Status", "Closed", "Press 'Allow Attendance' to open", "#64748B")

        # Real-time list for active session
        if active_session:
            st.markdown("#### Real-Time Attendance Roll")
            records = db.get_records_by_session(active_session["session_id"])
            if records:
                rec_df = pd.DataFrame([{
                    "Roll No": r["roll_number"],
                    "Student Name": r["name"],
                    "Status": r["status"].capitalize(),
                    "Method": r["method"],
                    "Timestamp": r["verified_at"]
                } for r in records])
                st.dataframe(rec_df, use_container_width=True)
            else:
                st.info("Waiting for students to verify attendance...")

        # Past sessions table
        with st.expander("🕒 Past Attendance Sessions History"):
            past_sessions = db.get_sessions_by_teacher(teacher_id)
            if past_sessions:
                st.dataframe(pd.DataFrame([{
                    "Session ID": ps["session_id"],
                    "Class": f"{ps['class_name']} - {ps['division']}",
                    "Subject": ps["subject_name"],
                    "Date": ps["session_date"],
                    "Status": ps["status"].upper(),
                    "Total Present": ps["total_present"]
                } for ps in past_sessions]), use_container_width=True)

    # ---------------- TAB 2: ENTER MARKS ----------------
    with tab2:
        st.subheader("Student Academic Performance & Marks Entry")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            m_subj_key = st.selectbox("Subject & Class", list(subj_options.keys()), key="marks_subj_sel")
            m_subj = subj_options[m_subj_key]
        with col_m2:
            m_exam = st.selectbox("Exam Type", EXAM_TYPES, key="marks_exam_sel")
        with col_m3:
            m_max = st.number_input("Maximum Marks", min_value=10.0, max_value=500.0, value=100.0, step=5.0)

        students_in_class = db.get_marks_by_class_subject_exam(m_subj["class_id"], m_subj["subject_id"], m_exam)

        if not students_in_class:
            st.info("No active students found in this class.")
        else:
            st.write(f"Entering marks for: **{m_subj['subject_name']}** | Exam: **{m_exam}** (Max: {m_max})")
            with st.form("batch_marks_form"):
                new_marks = {}
                for stud in students_in_class:
                    c1, c2, c3 = st.columns([1, 2, 2])
                    with c1:
                        st.markdown(f"**{stud['roll_number']}**")
                    with c2:
                        st.markdown(f"{stud['name']}")
                    with c3:
                        existing_val = float(stud["marks"]) if stud["marks"] is not None else 0.0
                        new_marks[stud["student_id"]] = st.number_input(
                            f"Score",
                            min_value=0.0,
                            max_value=float(m_max),
                            value=existing_val,
                            step=1.0,
                            key=f"mark_in_{stud['student_id']}",
                            label_visibility="collapsed"
                        )

                save_marks_btn = st.form_submit_button("💾 Save All Marks", type="primary")
                if save_marks_btn:
                    success_count = 0
                    errors = []
                    for sid, score in new_marks.items():
                        is_valid, msg = validate_marks(score, m_max)
                        if not is_valid:
                            errors.append(f"Student ID {sid}: {msg}")
                            continue
                        ok, db_msg = db.enter_or_update_marks(sid, m_subj["subject_id"], m_exam, score, m_max)
                        if ok:
                            success_count += 1
                        else:
                            errors.append(f"Student ID {sid}: {db_msg}")

                    if success_count > 0:
                        st.success(f"Successfully saved marks for {success_count} student(s)!")
                    if errors:
                        for err in errors:
                            st.error(err)
                    st.rerun()

    # ---------------- TAB 3: STUDENT DIRECTORY ----------------
    with tab3:
        st.subheader("Students in Your Assigned Classes")
        class_ids = list({s["class_id"] for s in assigned_subjects})
        all_class_students = []
        for cid in class_ids:
            all_class_students.extend(db.get_students_by_class(cid, include_inactive=True))

        if all_class_students:
            st.dataframe(pd.DataFrame([{
                "Student ID": s["student_id"],
                "Roll No": s["roll_number"],
                "Name": s["name"],
                "Class": f"{s['class_name']} - {s['division']}",
                "Username": s["username"],
                "Status": "Active" if s["is_active"] == 1 else "Deactivated"
            } for s in all_class_students]), use_container_width=True)

    # ---------------- TAB 4: FACE REGISTRATION ----------------
    with tab4:
        st.subheader("OpenCV Face Registration & LBPH Model Training")
        st.write("Register face data for students to enable webcam-verified attendance marking.")

        reg_service = FaceRegistrationService(db)
        students_active = [s for s in all_class_students if s["is_active"] == 1]

        if not students_active:
            st.info("No active students available for face registration.")
        else:
            s_map = {f"{s['roll_number']} - {s['name']} (ID: {s['student_id']})": s for s in students_active}
            sel_student_name = st.selectbox("Select Student to Register Face Data", list(s_map.keys()))
            target_student = s_map[sel_student_name]

            st.markdown("#### Option 1: Live Webcam Snapshot Capture")
            cam_pic = st.camera_input("Capture Student Face Sample")
            if cam_pic:
                import numpy as np
                import cv2
                file_bytes = np.asarray(bytearray(cam_pic.read()), dtype=np.uint8)
                frame = cv2.imdecode(file_bytes, 1)

                # Simulate multiple sample augmentations from clean frame
                frames_batch = [frame]
                for scale in [0.95, 1.05]:
                    h, w = frame.shape[:2]
                    M = cv2.getRotationMatrix2D((w/2, h/2), 0, scale)
                    scaled = cv2.warpAffine(frame, M, (w, h))
                    frames_batch.append(scaled)
                # repeat to generate sufficient samples for training
                full_batch = frames_batch * 10

                success, msg, count = reg_service.register_face_from_frames(
                    target_student["student_id"],
                    full_batch,
                    label=target_student["student_id"]
                )
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

            st.markdown("---")
            st.markdown("#### Option 2: Retrain LBPH Face Recognizer")
            if st.button("⚙️ Retrain LBPH Recognizer on Existing Samples"):
                recognizer = FaceRecognizerLBPH()
                ok, retrain_msg = recognizer.train_model()
                if ok:
                    st.success(retrain_msg)
                else:
                    st.error(retrain_msg)
