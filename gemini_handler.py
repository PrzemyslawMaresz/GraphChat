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


def _call_gemini_api(api_key: str, pil_image, detailed_prompt: str) -> str:
    model = get_gemini_model(api_key)
    if not model:
        return "Gemini model not available. Please check your API key and configuration in the sidebar."

    try:
        # The expert persona prompt is always included
        base_prompt = (
            "You are an expert in reading charts and graphs. "
            "Look at the given graph and answer the following question accurately. "
            "Provide the numeric value or observation directly based on the graph content. "
            "Do not include any additional explanatory text in your response, only the extracted data."
        )
        content_parts = [base_prompt, detailed_prompt, pil_image]
        response = model.generate_content(content_parts)

        if response.parts:
            return response.text
        elif response.prompt_feedback and response.prompt_feedback.block_reason:
            return (
                f"Response blocked by Gemini due to: "
                f"{response.prompt_feedback.block_reason.name}. "
            )
        else:
            return "Gemini did not return any content for this query. "
    except Exception as e:
        st.error(f"An unexpected error occurred while communicating with Gemini: {str(e)}")
        return f"An error occurred while trying to get a response from Gemini: {str(e)}. "


def generate_chat_response(api_key: str, pil_image, user_prompt: str) -> str:
    return _call_gemini_api(api_key, pil_image, user_prompt)


def get_response_for_line_chart(api_key: str, pil_image, num_points: int) -> str:
    prompt = (
        f"This is a line chart. Read the (x, y) coordinates for {num_points} points from it. "
        f"The points should be evenly distributed along the X-axis, from minimum to maximum. "
        f"If there is more than one line, extract points for all lines. "
        f"Return the results in the format: '[line name or color]: list of (x, y) pairs'."
    )
    return _call_gemini_api(api_key, pil_image, prompt)


def get_response_for_bar_chart(api_key: str, pil_image) -> str:
    prompt = (
        "This is a bar chart. For each bar, identify its label on the category axis (X-axis) and "
        "read its corresponding numerical value from the value axis (Y-axis). "
        "Return the results as a clean list of 'Bar Label: Value' pairs. "
        "If it is a grouped or stacked bar chart, identify the series for each bar (by color or legend)."
    )
    return _call_gemini_api(api_key, pil_image, prompt)


def get_response_for_scatter_plot(api_key: str, pil_image, num_points: int) -> str:
    prompt = (
        f"This is a scatter plot. Extract the (x, y) coordinates for {num_points} points for it."
        f"The points should be evenly distributed along the X-axis, from minimum to maximum."
        "If there are multiple groups of points (differentiated by color or shape), "
        "identify which group each point belongs to. "
        "Return the results as a list of (x, y) coordinates, grouped by series name if applicable."
    )
    return _call_gemini_api(api_key, pil_image, prompt)