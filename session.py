import streamlit as st
import json
import os
from PIL import Image
import io
from app_config import SESS_API_KEY, SESS_UPLOADED_IMAGES, SESSION_DATA_DIR, SESSION_DATA_FILE

def _get_session_data_path():
    project_dir = os.path.dirname(__file__)
    data_dir_path = os.path.join(project_dir, SESSION_DATA_DIR)
    os.makedirs(data_dir_path, exist_ok=True)
    return os.path.join(data_dir_path, SESSION_DATA_FILE)

def load_session_data():
    data_path = _get_session_data_path()
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if SESS_UPLOADED_IMAGES in data:
                    for img_id, img_info in data[SESS_UPLOADED_IMAGES].items():
                        if 'bytes_data' in img_info and img_info['bytes_data']:
                            if isinstance(img_info['bytes_data'], list):
                                img_info['bytes_data'] = bytes(img_info['bytes_data'])

                            img_info['pil_image'] = Image.open(io.BytesIO(img_info['bytes_data']))
                        else:
                            if 'pil_image' in img_info:
                                del img_info['pil_image']
                return data
            except json.JSONDecodeError as e:
                st.warning(f"Error reading session data from JSON file: {e}. A new session will be created.")
                return {}
            except Exception as e:
                st.error(f"An unexpected error occurred while loading session data: {e}")
                return {}
    return {}

def save_session_data(data_to_save):
    data_path = _get_session_data_path()
    serializable_data = data_to_save.copy()

    if SESS_UPLOADED_IMAGES in serializable_data:
        for img_id, img_info in serializable_data[SESS_UPLOADED_IMAGES].items():
            if 'bytes_data' in img_info:
                if isinstance(img_info['bytes_data'], bytes):
                    img_info['bytes_data'] = list(img_info['bytes_data'])
            if 'pil_image' in img_info:
                del img_info['pil_image']

    try:
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving session data to file: {e}")

def initialize_session_state():
    if "session_initialized" not in st.session_state:
        persisted_data = load_session_data()
        st.session_state[SESS_API_KEY] = persisted_data.get(SESS_API_KEY)
        st.session_state[SESS_UPLOADED_IMAGES] = persisted_data.get(SESS_UPLOADED_IMAGES, {})
        st.session_state['file_uploader_key'] = 0
        st.session_state["session_initialized"] = True
    else:
        if SESS_API_KEY not in st.session_state:
            st.session_state[SESS_API_KEY] = None
        if SESS_UPLOADED_IMAGES not in st.session_state:
            st.session_state[SESS_UPLOADED_IMAGES] = {}
        if 'file_uploader_key' not in st.session_state:
            st.session_state['file_uploader_key'] = 0