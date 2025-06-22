import streamlit as st
from app_config import APP_TITLE, APP_ICON, SESS_API_KEY, SESS_UPLOADED_IMAGES
from session import initialize_session_state, save_session_data
from ui import render_sidebar, render_image_uploader, render_analysis_sections

def run_application():
    initialize_session_state()

    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    render_sidebar()
    st.title(f'📈{APP_TITLE}')

    st.markdown(
        "Upload images of charts, then interact with the LLM to ask questions "
        "about the content of each chart."
    )
    st.markdown("---")
    render_image_uploader()
    st.markdown("---")
    render_analysis_sections()

    data_to_save = {
        SESS_API_KEY: st.session_state.get(SESS_API_KEY),
        SESS_UPLOADED_IMAGES: st.session_state.get(SESS_UPLOADED_IMAGES)
    }
    save_session_data(data_to_save)


if __name__ == "__main__":
    run_application()