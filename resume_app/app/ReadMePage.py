import streamlit as st

def load_readme_page():
    st.title("Welcome to the Streamlit App!")
    st.write("""
    ## About This App
    This application provides the following functionalities:
    1. **Summarize Job Description** - Extracts key points from job descriptions.
    2. **Summarize Resume** - Summarizes resumes to highlight key skills and experiences.
    3. **Job Description to Resume** - Maps job descriptions to resumes to assess fit.

    ## Quick Links
    - [Documentation](https://example.com/documentation)
    - [GitHub Repository](https://github.com/your-repo)
    - [Support](mailto:support@example.com)
    """)