import streamlit as st
from ReadMePage import load_readme_page
from SummarizeJobDescription import load_summarize_job_description
from SummarizeResume import load_summarize_resume
from JobDescriptionToResume import load_job_description_to_resume

css_file = "./static/style.css"

def load_css(file_name):
    with open(file_name, "r") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Load external CSS file
load_css(css_file)

# Create the sidebar menu
menu_options = [
    "Home",
    "Summarize Job Description",
    "Summarize Resume",
    "Job Description to Resume"
]
selected_option = st.sidebar.radio("Navigation", menu_options)

# Define the content for each section
if selected_option == "Home":
    load_readme_page()
elif selected_option == "Summarize Job Description":
    load_summarize_job_description()
elif selected_option == "Summarize Resume":
    load_summarize_resume()
elif selected_option == "Job Description to Resume":
    load_job_description_to_resume()