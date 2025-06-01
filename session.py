import streamlit as st
from app_config import SESS_API_KEY, SESS_UPLOADED_IMAGES


def initialize_session_state():
    if SESS_API_KEY not in st.session_state:
        st.session_state[SESS_API_KEY] = None

    if SESS_UPLOADED_IMAGES not in st.session_state:
        st.session_state[SESS_UPLOADED_IMAGES] = {}