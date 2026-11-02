# app/dashboards/student_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import cv2
from app.database.db_manager import DBManager
from app.auth.session import get_user_details
from app.components.cards import metric_card, grade_badge
from app.components.charts import create_attendance_gauge, create_marks_bar_chart, create_exam_comparison_chart
from app.analytics.performance_analytics import get_student_performance_summary
from app.analytics.attendance_analytics import get_student_attendance_dataframe
from app.face_attendance.attendance_marker import AttendanceMarker
from app.face_attendance.webcam import capture_single_frame

def render_student_dashboard(db: DBManager):
    student = get_user_details()
    student_id = student.get("student_id")

    st.title("🎓 Student Portal")
    st.markdown(f"**Welcome, {student.get('name', 'Student')}** | Roll No: `{student.get('roll_number', 'N/A')}` | Class: `{student.get('class_name', '')} - {student.get('division', '')}`")

    # Fetch performance and attendance metrics
    perf = get_student_performance_summary(db, student_id)
    att_summary = db.get_student_attendance_summary(student_id)
    active_session = db.get_active_session_for_student(student_id)

    tab_names = ["👤 My Profile", "📊 Academic Performance", "📅 Attendance History"]
    if active_session:
        tab_names.append("📸 Take Attendance (Active)")
    else:
        tab_names.append("📸 Take Attendance")

    tabs = st.tabs(tab_names)

    # ---------------- TAB 1: PROFILE ----------------
    with tabs[0]:
        st.subheader("Student Academic Profile")
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            metric_card("Attendance", f"{att_summary['percentage']:.1f}%", f"{att_summary['attended_sessions']} / {att_summary['total_sessions']} Sessions", "#10B981")
        with col_p2:
            metric_card("Overall Score", f"{perf['percentage']:.1f}%", f"{perf['total_obtained']} / {perf['total_max']} Marks", "#3B82F6")
        with col_p3:
            metric_card("Current Grade", perf["grade"], perf["grade_desc"], "#6366F1")
        with col_p4:
            status_text = "Enrolled & Active" if student.get("is_active", 1) == 1 else "Deactivated"
            metric_card("Enrollment", status_text, f"Academic Year {student.get('academic_year', '2025-26')}", "#F59E0B")

        st.markdown("#### Personal & Academic Details")
        st.write(f"- **Full Name:** {student.get('name')}")
        st.write(f"- **Roll Number:** {student.get('roll_number')}")
        st.write(f"- **Class & Division:** {student.get('class_name')} - Div {student.get('division')}")
        st.write(f"- **Registered Email:** {student.get('email')}")
        st.write(f"- **Login Username:** {student.get('username')}")

    # ---------------- TAB 2: MARKS & PERFORMANCE ----------------
    with tabs[1]:
        st.subheader("Academic Performance & Exam Results")
        marks_df = perf["marks_df"]

        if marks_df.empty:
            st.info("No exam marks have been uploaded by your instructors yet.")
        else:
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                sub_agg = marks_df.groupby("subject_name").agg({
                    "marks": "sum",
                    "max_marks": "sum"
                }).reset_index()
                sub_agg["percentage"] = (sub_agg["marks"] / sub_agg["max_marks"] * 100.0).round(1)
                fig_bar = create_marks_bar_chart(sub_agg)
                if fig_bar:
                    st.plotly_chart(fig_bar, use_container_width=True)

            with col_chart2:
                fig_comp = create_exam_comparison_chart(marks_df)
                if fig_comp:
                    st.plotly_chart(fig_comp, use_container_width=True)

            st.markdown("#### Detailed Marks Breakdown")
            display_df = marks_df[["subject_code", "subject_name", "exam_type", "marks", "max_marks", "percentage", "exam_date"]].copy()
            display_df.columns = ["Code", "Subject Name", "Exam", "Obtained", "Max Marks", "Score (%)", "Date"]
            st.dataframe(display_df, use_container_width=True)

    # ---------------- TAB 3: ATTENDANCE HISTORY ----------------
    with tabs[2]:
        st.subheader("Attendance History & Percentage")
        col_g1, col_g2 = st.columns([1, 2])
        with col_g1:
            fig_gauge = create_attendance_gauge(att_summary["percentage"])
            st.plotly_chart(fig_gauge, use_container_width=True)
            if att_summary["percentage"] < 75.0:
                st.error("⚠️ Warning: Your overall attendance is below the mandatory 75% threshold.")
            else:
                st.success("✅ Good Standing: Attendance satisfies university guidelines.")

        with col_g2:
            st.markdown("#### Verification Log")
            att_history = get_student_attendance_dataframe(db, student_id)
            if att_history.empty:
                st.info("No attendance records found.")
            else:
                hist_disp = att_history[["session_date", "subject_name", "teacher_name", "verified_at", "method", "status"]].copy()
                hist_disp.columns = ["Date", "Subject", "Instructor", "Time Verified", "Method", "Status"]
                st.dataframe(hist_disp, use_container_width=True)

    # ---------------- TAB 4: TAKE ATTENDANCE ----------------
    with tabs[3]:
        st.subheader("📸 Webcam Identity Verification & Attendance")

        if not active_session:
            st.info("🔒 No attendance session is currently open for your class.\n\nYour instructor must click **Allow Attendance** from the Teacher Dashboard before you can verify your attendance.")
        else:
            session_id = active_session["session_id"]
            already_marked = db.has_student_attended(session_id, student_id)

            st.success(f"🟢 **Active Session Found!**\n- **Subject:** {active_session['subject_name']} ({active_session['subject_code']})\n- **Faculty:** {active_session['teacher_name']}\n- **Opened At:** {active_session['opened_at']}")

            if already_marked:
                st.info("✅ You have already marked attendance for this session. Duplicate verification is prevented.")
            else:
                st.markdown("""
                    > 💡 **Notice:** You can verify your identity using either the **Direct OpenCV Camera** button (recommended) or the **In-Browser Camera** below.
                """)

                # Option A: Direct Hardware OpenCV Capture
                with st.container(border=True):
                    st.markdown("#### ⚡ Option 1: Direct OpenCV Camera (Instant Hardware Access)")
                    st.caption("Directly accesses your laptop webcam without requiring browser permission prompts.")
                    if st.button("📸 Capture & Verify via OpenCV Camera", type="primary", use_container_width=True):
                        with st.spinner("Opening camera hardware and detecting face..."):
                            frame = capture_single_frame()
                            if frame is None:
                                st.error("❌ Could not connect to laptop webcam. Please ensure your camera is not being used by another application.")
                            else:
                                marker = AttendanceMarker(db)
                                success, message, confidence, annotated = marker.verify_and_mark(session_id, student_id, frame)
                                if success:
                                    st.balloons()
                                    st.success(f"🎉 {message} (Face Match Confidence: {confidence:.1f})")
                                    if annotated is not None:
                                        st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), caption="Verified Identity Frame", width=360)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Verification Failed: {message}")
                                    if annotated is not None:
                                        st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), caption="Verification Attempt", width=360)

                # Option B: In-Browser Camera Input
                with st.container(border=True):
                    st.markdown("#### 🌐 Option 2: In-Browser Camera")
                    st.caption("If the 'Take Photo' button is greyed out, please click **Allow** on Chrome's camera permission prompt (top-left address bar).")

                    camera_photo = st.camera_input("Browser Camera Feed", key=f"cam_att_{session_id}")
                    if camera_photo:
                        file_bytes = np.asarray(bytearray(camera_photo.read()), dtype=np.uint8)
                        frame = cv2.imdecode(file_bytes, 1)

                        marker = AttendanceMarker(db)
                        success, message, confidence, annotated = marker.verify_and_mark(session_id, student_id, frame)

                        if success:
                            st.balloons()
                            st.success(f"🎉 {message} (Face Match Confidence: {confidence:.1f})")
                            if annotated is not None:
                                st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), caption="Verified Identity Frame", width=360)
                            st.rerun()
                        else:
                            st.error(f"❌ Verification Failed: {message}")
                            if annotated is not None:
                                st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), caption="Verification Attempt", width=360)

                # Option C: Image File Upload Fallback
                with st.expander("📁 Option 3: Upload Photo Verification (Fallback)"):
                    uploaded_file = st.file_uploader("Upload clear frontal face photo", type=["jpg", "jpeg", "png"], key=f"upload_att_{session_id}")
                    if uploaded_file and st.button("Verify Uploaded Photo"):
                        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                        frame = cv2.imdecode(file_bytes, 1)

                        marker = AttendanceMarker(db)
                        success, message, confidence, annotated = marker.verify_and_mark(session_id, student_id, frame)

                        if success:
                            st.balloons()
                            st.success(f"🎉 {message} (Face Match Confidence: {confidence:.1f})")
                            if annotated is not None:
                                st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), caption="Verified Identity Frame", width=360)
                            st.rerun()
                        else:
                            st.error(f"❌ Verification Failed: {message}")
                            if annotated is not None:
                                st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), caption="Verification Attempt", width=360)
