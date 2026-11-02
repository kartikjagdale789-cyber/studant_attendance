# app/auth/login.py
import streamlit as st
from app.database.db_manager import DBManager
from app.auth.session import set_user_session
from app.utils.helpers import verify_password
from config.constants import ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT

def render_login(db: DBManager):
    st.markdown("""
        <div style="text-align: center; padding: 25px 0;">
            <h1 style="color: #1E3A8A; margin-bottom: 5px;">🎓 Student Performance, Attendance & Face Verification System</h1>
            <p style="color: #64748B; font-size: 1.1rem;">Academic Analytics & OpenCV Face-Verified Attendance Portal</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.subheader("🔐 Sign In")
            username = st.text_input("Username", placeholder="e.g. admin, teacher1, S001")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            if st.button("Log In", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("Please enter both username and password.")
                    return

                user = db.get_user_by_username(username.strip())
                if not user:
                    st.error("Invalid username or password.")
                    return

                if user["is_active"] == 0:
                    st.error("Your account has been deactivated. Please contact the administrator.")
                    return

                if not verify_password(password, user["password_hash"]):
                    st.error("Invalid username or password.")
                    return

                # Load role specific details
                details = {}
                role = user["role"]
                if role == ROLE_TEACHER:
                    t = db.get_teacher_by_user_id(user["user_id"])
                    if not t or t["is_active"] == 0:
                        st.error("Teacher account is inactive or not found.")
                        return
                    details = dict(t)
                elif role == ROLE_STUDENT:
                    s = db.get_student_by_user_id(user["user_id"])
                    if not s or s["is_active"] == 0:
                        st.error("Student account is inactive or not found.")
                        return
                    details = dict(s)
                elif role == ROLE_ADMIN:
                    details = {"name": "System Administrator", "email": "admin@college.edu"}

                set_user_session(dict(user), details)
                st.success(f"Welcome back, {details.get('name', username)}!")
                st.rerun()

        with st.expander("ℹ️ Demo Credentials"):
            st.markdown("""
            - **Administrator**: `admin` / `admin@123`
            - **Teacher**: `teacher1` or `teacher2` / `teach@123`
            - **Student**: `S001` or `S002` / `student@123`
            """)
