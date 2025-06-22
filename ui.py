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
from gemini_handler import (
    generate_chat_response,
    get_response_for_line_chart,
    get_response_for_bar_chart,
    get_response_for_scatter_plot
)


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
                img_data.get('size') == uploaded_file.size
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
                        "size": uploaded_file.size,
                        "bytes_data": bytes_data,
                        "pil_image": pil_image,
                        "chat_log": []
                    }
                    new_files_processed = True
                except Exception as e:
                    st.error(
                        f"Error processing file '{uploaded_file.name}': {e}. It might not be a valid image format."
                    )

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
                if 'pil_image' not in img_data or img_data['pil_image'] is None:
                    if 'bytes_data' in img_data and img_data['bytes_data']:
                        try:
                            current_bytes_data = img_data['bytes_data']
                            if isinstance(current_bytes_data, list):
                                current_bytes_data = bytes(current_bytes_data)

                            img_data['pil_image'] = Image.open(io.BytesIO(current_bytes_data))
                        except Exception as e:
                            st.error(f"Could not reconstruct image for '{img_data['name']}': {e}")
                            if st.button(f"Remove Corrupted Image", key=f"remove_corrupted_{img_id}"):
                                del st.session_state[SESS_UPLOADED_IMAGES][img_id]
                                st.rerun()
                            continue
                    else:
                        st.warning(f"No valid image data available for '{img_data['name']}'.")
                        continue

                if 'pil_image' in img_data and img_data['pil_image'] is not None:
                    st.image(img_data['pil_image'], caption=img_data['name'], use_container_width=True)
                else:
                    st.warning(f"Image '{img_data['name']}' could not be displayed.")

                if st.button(f"Remove Image", key=f"delete_button_img_{img_id}"):
                    del st.session_state[SESS_UPLOADED_IMAGES][img_id]
                    st.rerun()

            with col2:
                st.write(f"**Chat with Gemini about: __{img_data['name']}__**")
                for message in img_data['chat_log']:
                    avatar_icon = "❔" if message["role"] == "user" else "👾"
                    with st.chat_message(message["role"], avatar=avatar_icon):
                        st.markdown(message["parts"][0])

                st.write("")
                analysis_mode = st.radio(
                    "Choose analysis method:",
                    ("Manual Question", "Line Chart: Point Detection", "Bar Chart: Value Extraction", "Scatter Plot: Point Extraction"),
                    key=f"analysis_mode_radio_{img_id}"
                )

                current_pil_image = img_data.get('pil_image')

                if analysis_mode == "Manual Question":
                    user_prompt = st.chat_input(f"Ask a question about {img_data['name']}...", key=f"chat_input_img_{img_id}")
                    if user_prompt:
                        current_api_key = st.session_state.get(SESS_API_KEY)
                        if not current_api_key:
                            st.warning("Please set your Gemini API Key in the sidebar.", icon="🔑")
                        elif not current_pil_image:
                            st.warning("Image data not available for analysis.")
                        else:
                            img_data['chat_log'].append({"role": "user", "parts": [user_prompt]})
                            with st.spinner("Gemini is thinking..."):
                                response_text = generate_chat_response(
                                    api_key=current_api_key, pil_image=current_pil_image, user_prompt=user_prompt
                                )
                            img_data['chat_log'].append({"role": "model", "parts": [response_text]})
                            st.rerun()

                elif analysis_mode == "Line Chart: Point Detection":
                    with st.form(key=f"line_chart_form_{img_id}"):
                        num_points = st.number_input("Enter the number of points to detect:", min_value=2, step=1, value=10)
                        submitted = st.form_submit_button("Detect Points")
                        if submitted:
                            current_api_key = st.session_state.get(SESS_API_KEY)
                            if not current_api_key:
                                st.warning("Please set your Gemini API Key in the sidebar.", icon="🔑")
                            elif not current_pil_image:
                                st.warning("Image data not available for analysis.")
                            else:
                                user_display_message = f"Request for detection of {num_points} points on a line chart."
                                img_data['chat_log'].append({"role": "user", "parts": [user_display_message]})
                                with st.spinner("Gemini is analyzing the line chart..."):
                                    response_text = get_response_for_line_chart(
                                        api_key=current_api_key, pil_image=current_pil_image, num_points=num_points
                                    )
                                img_data['chat_log'].append({"role": "model", "parts": [response_text]})
                                st.rerun()

                elif analysis_mode == "Bar Chart: Value Extraction":
                    with st.form(key=f"bar_chart_form_{img_id}"):
                        submitted = st.form_submit_button("Extract Bar Values")
                        if submitted:
                            current_api_key = st.session_state.get(SESS_API_KEY)
                            if not current_api_key:
                                st.warning("Please set your Gemini API Key in the sidebar.", icon="🔑")
                            elif not current_pil_image:
                                st.warning("Image data not available for analysis.")
                            else:
                                user_display_message = "Request for bar chart value extraction."
                                img_data['chat_log'].append({"role": "user", "parts": [user_display_message]})
                                with st.spinner("Gemini is analyzing the bar chart..."):
                                    response_text = get_response_for_bar_chart(
                                        api_key=current_api_key, pil_image=current_pil_image
                                    )
                                img_data['chat_log'].append({"role": "model", "parts": [response_text]})
                                st.rerun()

                elif analysis_mode == "Scatter Plot: Point Extraction":
                    with st.form(key=f"scatter_plot_form_{img_id}"):
                        num_points = st.number_input("Enter the number of points to detect:", min_value=2, step=1,value=10)
                        submitted = st.form_submit_button("Extract All Points")
                        if submitted:
                            current_api_key = st.session_state.get(SESS_API_KEY)
                            if not current_api_key:
                                st.warning("Please set your Gemini API Key in the sidebar.", icon="🔑")
                            elif not current_pil_image:
                                st.warning("Image data not available for analysis.")
                            else:
                                user_display_message = f"Request for detection of {num_points} points on a scatter plot."
                                img_data['chat_log'].append({"role": "user", "parts": [user_display_message]})
                                with st.spinner("Gemini is analyzing the scatter plot..."):
                                    response_text = get_response_for_scatter_plot(
                                        api_key=current_api_key,
                                        pil_image=current_pil_image,
                                        num_points=num_points
                                    )
                                img_data['chat_log'].append({"role": "model", "parts": [response_text]})
                                st.rerun()