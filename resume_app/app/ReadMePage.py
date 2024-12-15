import streamlit as st
def load_readme_page():
    """
    Loads the Home page with an introduction and Quick Links to key app functionalities.
    """
    st.title("Welcome to the Streamlit App!")
    st.write("""
    ## About This App
    This application provides the following functionalities:
    1. **Summarize Job Description** - Extracts key points from job descriptions.
    2. **Summarize Resume** - Summarizes resumes to highlight key skills and experiences.
    3. **Job Description to Resume** - Maps job descriptions to resumes to assess fit.
    """)