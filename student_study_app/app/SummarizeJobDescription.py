# Standard Library Imports
import json
import traceback
from typing import Union
import logging

# Third-Party Imports
import streamlit as st

# Application-Specific Imports
from llm_service import OpenAIChatClient
import app_prompt as prmpt
from logger import log_msg  # Assuming a logger class exists
import file_utils as fu

def summarize_content(input_text: str) -> str:
    """
    Summarize the job description content using OpenAIChatClient.

    Args:
        input_text (str): The job description content.

    Returns:
        str: HTML table of the summarized content.
    """
    try:
        log_msg("Preparing summarization request.", level=logging.INFO)
        llm_args = prmpt.get_summarization_for_job_description(job_description_content=input_text)
        log_msg(f"Input prompt : {llm_args}")
        llm = OpenAIChatClient()
        response = llm.get_response(**llm_args)
        log_msg("Received response from OpenAIChatClient.", level=logging.INFO)
        
        json_response = fu.parse_json(response)
        output_html = fu.convert_to_html_table(json_response)
        log_msg("Successfully generated HTML table for summarization.", level=logging.INFO)
        return output_html
    except Exception as e:
        log_msg(f"Error during summarization: {str(e)}\n{traceback.format_exc()}", level=logging.ERROR)
        return "<p>An error occurred while generating the summary. Please try again.</p>"

def load_summarize_job_description():
    """
    Load the Streamlit UI for summarizing job descriptions.
    """
    st.title("Summarize Job Description")
    
    # Layout with columns: Inputs on the left, Output on the right
    col1, col2 = st.columns([2, 1])  # Adjust column widths

    # Section 1: Input
    with col1:
        st.subheader("Input Section")
        log_msg("Loading input section.", level=logging.INFO)

        # Text Area for manual input
        job_description = st.text_area("Enter Job Description Manually")

        # File uploader for uploading job descriptions
        uploaded_file = st.file_uploader("Or Upload a File", type=["pdf", "docx", "txt"])

        # Combine inputs for processing
        input_text = ""
        if job_description:
            input_text = job_description
        elif uploaded_file:
            input_file_name = uploaded_file.name  # Placeholder for file content processing
            log_msg(f"Input file name: {input_file_name}")
            input_text = fu.extract_content_from_file(uploaded_file, input_file_name)
        
        log_msg(f"Input text: {input_text}")

        # Summarize Button
        if st.button("Summarize"):
            if input_text:
                log_msg("Summarize button clicked.", level=logging.INFO)
                st.session_state["summary"] = summarize_content(input_text)
            else:
                log_msg("No input provided for summarization.", level=logging.WARNING)
                st.warning("Please enter a job description or upload a file.")

    # Section 2: Output
    with col2:
        st.subheader("Summarization Report")
        log_msg("Loading output section.", level=logging.INFO)
        # Display the output HTML table
        st.markdown(
            f"""
            <div class="output-container">
                <div class="output-title">Output:</div>
                {st.session_state.get("summary", "Output will be displayed here after summarization.")}
            </div>
            """,
            unsafe_allow_html=True,
        )