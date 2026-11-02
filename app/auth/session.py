# app/auth/session.py
import streamlit as st

def init_session():
    defaults = {
        "logged_in": False,
        "user_id": None,
        "username": None,
        "role": None,
        "user_details": {}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def set_user_session(user: dict, details: dict = None):
    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user["user_id"]
    st.session_state["username"] = user["username"]
    st.session_state["role"] = user["role"]
    st.session_state["user_details"] = details or {}

def clear_session():
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.session_state["role"] = None
    st.session_state["user_details"] = {}

def is_authenticated() -> bool:
    return st.session_state.get("logged_in", False)

def get_current_role() -> str:
    return st.session_state.get("role", "")

def get_current_user_id() -> int:
    return st.session_state.get("user_id")

def get_user_details() -> dict:
    return st.session_state.get("user_details", {})
