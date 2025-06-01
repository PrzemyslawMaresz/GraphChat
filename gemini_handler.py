# gemini_handler.py
import streamlit as st
import google.generativeai as genai
from app_config import GEMINI_MODEL_NAME


def configure_gemini_api(api_key: str) -> bool:
    if api_key:
        try:
            genai.configure(api_key=api_key)
            return True
        except Exception as e:
            st.error(f"Failed to configure Gemini: {e}")
            return False
    return False


def get_gemini_model(api_key: str):
    if configure_gemini_api(api_key):
        try:
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            return model
        except Exception as e:
            st.error(f"Error creating Gemini model '{GEMINI_MODEL_NAME}': {e}")
    return None


def generate_chat_response(api_key: str, pil_image, user_prompt: str) -> str:
    model = get_gemini_model(api_key)
    if not model:
        return "Gemini model not available. Please check your API key and configuration in the sidebar."

    try:
        prompt = (
            "You are an expert in reading charts and graphs. "
            "Look at the given graph and answer the following question accurately. "
            "Provide the numeric value or observation directly based on the graph content."
        )
        content_parts = [prompt, user_prompt, pil_image]
        response = model.generate_content(content_parts)

        if response.parts:
            response_text = response.text
        elif response.prompt_feedback and response.prompt_feedback.block_reason:
            response_text = (
                f"Response blocked by Gemini due to: "
                f"{response.prompt_feedback.block_reason.name}. "
            )
        else:
            response_text = "Gemini did not return any content for this query. "
        return response_text
    except Exception as e:
        st.error(f"An unexpected error occurred while communicating with Gemini: {str(e)}")
        return f"An error occurred while trying to get a response from Gemini: {str(e)}. "