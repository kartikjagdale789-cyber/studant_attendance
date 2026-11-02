# app/components/charts.py
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_attendance_gauge(percentage: float):
    color = "#10B981" if percentage >= 75 else ("#F59E0B" if percentage >= 60 else "#EF4444")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        number={'suffix': "%"},
        title={'text': "Overall Attendance", 'font': {'size': 18}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 60], 'color': "#FEE2E2"},
                {'range': [60, 75], 'color': "#FEF3C7"},
                {'range': [75, 100], 'color': "#D1FAE5"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def create_marks_bar_chart(df: pd.DataFrame):
    if df.empty:
        return None
    fig = px.bar(
        df,
        x="subject_name",
        y="percentage",
        color="percentage",
        color_continuous_scale="Blues",
        labels={"subject_name": "Subject", "percentage": "Score (%)"},
        title="Subject-wise Performance Percentage",
        text="percentage"
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(yaxis=dict(range=[0, 110]), height=320, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def create_exam_comparison_chart(df: pd.DataFrame):
    if df.empty or "exam_type" not in df.columns:
        return None
    fig = px.bar(
        df,
        x="subject_name",
        y="percentage",
        color="exam_type",
        barmode="group",
        title="Performance Comparison by Exam",
        labels={"percentage": "Score (%)", "subject_name": "Subject", "exam_type": "Exam"}
    )
    fig.update_layout(yaxis=dict(range=[0, 110]), height=340, margin=dict(l=20, r=20, t=40, b=20))
    return fig
