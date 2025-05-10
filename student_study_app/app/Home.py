import streamlit as st
import logging
from logger import log_msg,configure_logging  # Assuming logger is implemented in logger.py
from ReadMePage import load_readme_page
from SummarizeJobDescription import load_summarize_job_description
from SummarizeResume import load_summarize_resume
from JobDescriptionToResume import load_job_description_to_resume

css_file = "./static/style.css"

configure_logging()

def load_css(file_name):
    """
    Load the CSS file to style the Streamlit app.
    """
    try:
        with open(file_name, "r") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
        log_msg(f"CSS file '{file_name}' loaded successfully.", level=logging.INFO)
    except FileNotFoundError:
        log_msg(f"CSS file '{file_name}' not found.", level=logging.ERROR)
    except Exception as e:
        log_msg(f"Error loading CSS file '{file_name}': {str(e)}", level=logging.ERROR)

# Load external CSS file
load_css(css_file)

# Create the sidebar menu
menu_options = [
    "Home",
    "Summarize Job Description",
    "Summarize Resume",
    "Job Description to Resume"
]
log_msg(f"Sidebar menu created with options: {menu_options}", level=logging.INFO)

selected_option = st.sidebar.radio("Navigation", menu_options)
log_msg(f"User selected sidebar option: {selected_option}", level=logging.INFO)

# Define the content for each section
if selected_option == "Home":
    log_msg("Navigating to Home page.", level=logging.INFO)
    load_readme_page()
elif selected_option == "Summarize Job Description":
    log_msg("Navigating to Summarize Job Description page.", level=logging.INFO)
    load_summarize_job_description()
elif selected_option == "Summarize Resume":
    log_msg("Navigating to Summarize Resume page.", level=logging.INFO)
    load_summarize_resume()
elif selected_option == "Job Description to Resume":
    log_msg("Navigating to Job Description to Resume page.", level=logging.INFO)
    load_job_description_to_resume()