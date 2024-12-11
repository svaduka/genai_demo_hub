import streamlit as st

def load_summarize_job_description():
    st.title("Summarize Job Description")
    st.write("Upload a job description file to summarize its key points.")
    uploaded_file = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt"])
    if uploaded_file:
        st.write(f"File uploaded: {uploaded_file.name}")
        # Add your summarization logic here
        st.write("**Summary:**")
        st.write("Key points extracted from the job description will appear here.")