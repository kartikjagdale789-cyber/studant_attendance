# app/analytics/attendance_analytics.py
import pandas as pd
from app.database.db_manager import DBManager

def get_student_attendance_dataframe(db: DBManager, student_id: int) -> pd.DataFrame:
    rows = db.get_student_attendance_history(student_id)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(r) for r in rows])

def get_session_attendance_dataframe(db: DBManager, session_id: int) -> pd.DataFrame:
    rows = db.get_records_by_session(session_id)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(r) for r in rows])
