# main.py
import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database.db_manager import DBManager
from app.database.seed_data import seed_demo_data
from app.auth.session import init_session, is_authenticated, get_current_role, clear_session, get_user_details
from app.auth.login import render_login
from app.dashboards.admin_dashboard import render_admin_dashboard
from app.dashboards.teacher_dashboard import render_teacher_dashboard
from app.dashboards.student_dashboard import render_student_dashboard
from config.constants import ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT

st.set_page_config(
    page_title="Student Performance & Face Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database & Seed
db = DBManager()
db.init_db()
seed_demo_data(db)

# Initialize Session
init_session()

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #1E3A8A; margin-bottom: 0;">🎓 EduFace Analytics</h2>
            <small style="color: #64748B;">AI-Powered Attendance & Academic Tracking</small>
        </div>
    """, unsafe_allow_html=True)

    if is_authenticated():
        user_info = get_user_details()
        role = get_current_role()
        role_badges = {
            ROLE_ADMIN: "🛡️ Administrator",
            ROLE_TEACHER: "🏫 Faculty Teacher",
            ROLE_STUDENT: "🎓 Student"
        }
        st.markdown(f"""
            <div style="background: #F1F5F9; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                <div style="font-size: 0.8rem; color: #64748B;">SIGNED IN AS</div>
                <div style="font-weight: 700; color: #1E293B;">{user_info.get('name', st.session_state.get('username'))}</div>
                <div style="font-size: 0.85rem; color: #2563EB; font-weight: 600;">{role_badges.get(role, role)}</div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Sign Out", use_container_width=True):
            clear_session()
            st.rerun()

        st.markdown("---")
        st.markdown("""
            **System Status:**  
            🟢 OpenCV LBPH Active  
            🟢 SQLite DB Connected  
            🟢 Session Security On
        """)
    else:
        st.info("Please log in with your university credentials.")

# Route Page based on Authentication & Role
if not is_authenticated():
    render_login(db)
else:
    role = get_current_role()
    if role == ROLE_ADMIN:
        render_admin_dashboard(db)
    elif role == ROLE_TEACHER:
        render_teacher_dashboard(db)
    elif role == ROLE_STUDENT:
        render_student_dashboard(db)
    else:
        st.error(f"Unknown role '{role}'. Please re-login.")
        clear_session()
        st.rerun()
