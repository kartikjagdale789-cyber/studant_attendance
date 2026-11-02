# app/analytics/performance_analytics.py
import pandas as pd
from app.database.db_manager import DBManager
from app.utils.helpers import calculate_percentage, get_grade

def get_student_performance_summary(db: DBManager, student_id: int) -> dict:
    rows = db.get_student_marks(student_id)
    if not rows:
        return {
            "total_obtained": 0.0,
            "total_max": 0.0,
            "percentage": 0.0,
            "grade": "N/A",
            "grade_desc": "No marks entered yet",
            "marks_df": pd.DataFrame()
        }

    records = [dict(r) for r in rows]
    df = pd.DataFrame(records)

    total_obtained = df["marks"].sum()
    total_max = df["max_marks"].sum()
    pct = calculate_percentage(total_obtained, total_max)
    grade, desc = get_grade(pct)

    return {
        "total_obtained": round(total_obtained, 1),
        "total_max": round(total_max, 1),
        "percentage": pct,
        "grade": grade,
        "grade_desc": desc,
        "marks_df": df
    }
