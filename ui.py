import streamlit as st
import io
import uuid
from PIL import Image
from app_config import (
    SESS_API_KEY,
    SESS_UPLOADED_IMAGES,
    GEMINI_MODEL_NAME,
    SUPPORTED_IMAGE_TYPES
)
from gemini_handler import generate_chat_response


def render_sidebar():

    with st.sidebar:
        st.header("Configuration")

        current_api_key = st.session_state.get(SESS_API_KEY, "") or ""
        new_api_key = st.text_input(
            "Enter your Gemini API Key:",
            type="password",
            value=current_api_key,
            key="api_key_input_field_sidebar_main"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Key", key="save_api_key_button_sidebar_main"):
                if new_api_key:
                    st.session_state[SESS_API_KEY] = new_api_key
                    st.success("API Key saved!", icon="✅")
                    st.rerun()
                else:
                    st.warning("Please enter an API Key to save.", icon="⚠️")
        with col2:
            if st.button("Clear Key", key="clear_api_key_button_sidebar_main"):
                st.session_state[SESS_API_KEY] = None
                st.info("API Key cleared.")
                st.rerun()

        if st.session_state.get(SESS_API_KEY):
            st.success("Gemini API Key is set and active.", icon="🔑")
        else:
            st.warning("Gemini API Key is not set. Please provide one to use the chat features.")

        st.markdown("---")
        st.caption("Upload chart images and ask questions about them.")
        st.markdown(f"Using model: **{GEMINI_MODEL_NAME}**")

def render_image_uploader():
    st.subheader("Upload Your Charts")
    uploaded_files = st.file_uploader(
        "Choose image files (PNG, JPG, JPEG, WEBP):",
        type=SUPPORTED_IMAGE_TYPES,
        accept_multiple_files=True,
        key=f"file_uploader_widget_main_app_{st.session_state['file_uploader_key']}"
    )

    if uploaded_files:
        new_files_processed = False
        for uploaded_file in uploaded_files:
            is_duplicate = any(
                img_data['name'] == uploaded_file.name and
                len(img_data['bytes_data']) == uploaded_file.size
                for img_data in st.session_state[SESS_UPLOADED_IMAGES].values()
            )

            if not is_duplicate:
                img_id = str(uuid.uuid4())
                bytes_data = uploaded_file.getvalue()
                try:
                    pil_image = Image.open(io.BytesIO(bytes_data))
                    pil_image.verify()
                    pil_image = Image.open(io.BytesIO(bytes_data))

                    st.session_state[SESS_UPLOADED_IMAGES][img_id] = {
                        "id": img_id,
                        "name": uploaded_file.name,
                        "bytes_data": bytes_data,
                        "pil_image": pil_image,
                        "chat_log": []
                    }
                    new_files_processed = True
                except Exception as e:
                    st.error(
                        f"Error processing file '{uploaded_file.name}': {e}. It might not be a valid image format.")

        if new_files_processed:
            st.session_state['file_uploader_key'] += 1
            st.rerun()

def render_analysis_sections():
    if not st.session_state[SESS_UPLOADED_IMAGES]:
        st.info("No images uploaded yet. Use the uploader above to add some charts to analyze.")
        return

    st.subheader("Your Uploaded Charts & Analysis")

    for img_id, img_data in list(st.session_state[SESS_UPLOADED_IMAGES].items()):
        with st.expander(f"Analyze Chart: {img_data['name']}", expanded=True):
            col1, col2 = st.columns([0.4, 0.6])

            with col1:
                st.image(img_data['bytes_data'], caption=img_data['name'], use_container_width=True)
                if st.button(f"Remove Image", key=f"delete_button_img_{img_id}"):
                    del st.session_state[SESS_UPLOADED_IMAGES][img_id]
                    st.rerun()

            with col2:
                st.write(f"**Chat with Gemini about: __{img_data['name']}__**")

                for message in img_data['chat_log']:
                    avatar_icon = "❔" if message["role"] == "user" else "👾"
                    with st.chat_message(message["role"], avatar=avatar_icon):
                        st.markdown(message["parts"][0])


                user_prompt = st.chat_input(
                    f"Ask a question about {img_data['name']}...",
                    key=f"chat_input_img_{img_id}"
                )

                if user_prompt:
                    current_api_key = st.session_state.get(SESS_API_KEY)
                    if not current_api_key:
                        st.warning(
                            "Please set your Gemini API Key in the sidebar to enable chat functionality.", icon="🔑")
                    else:
                        img_data['chat_log'].append({"role": "user", "parts": [user_prompt]})

                        with st.spinner("Gemini is thinking..."):
                            response_text = generate_chat_response(
                                api_key=current_api_key,
                                pil_image=img_data['pil_image'],
                                user_prompt=user_prompt
                            )

                        img_data['chat_log'].append({"role": "model", "parts": [response_text]})
                        st.rerun()