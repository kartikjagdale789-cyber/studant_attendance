# app/components/cards.py
import streamlit as st

def metric_card(title: str, value: str, subtitle: str = "", border_color: str = "#2563EB"):
    st.markdown(f"""
        <div style="
            background: #FFFFFF;
            padding: 16px 20px;
            border-radius: 10px;
            border-left: 5px solid {border_color};
            box-shadow: 0 2px 4px rgba(0,0,0,0.06);
            margin-bottom: 12px;
        ">
            <div style="font-size: 0.85rem; color: #64748B; font-weight: 600; text-transform: uppercase;">{title}</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #1E293B; margin: 4px 0;">{value}</div>
            <div style="font-size: 0.8rem; color: #94A3B8;">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)

def grade_badge(grade: str) -> str:
    color_map = {
        "A+": "#10B981",
        "A": "#3B82F6",
        "B": "#6366F1",
        "C": "#F59E0B",
        "D": "#EC4899",
        "F": "#EF4444"
    }
    bg = color_map.get(grade, "#6B7280")
    return f'<span style="background-color: {bg}; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold;">{grade}</span>'
