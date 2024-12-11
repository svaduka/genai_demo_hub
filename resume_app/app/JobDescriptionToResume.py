import streamlit as st

def load_job_description_to_resume():
    st.title("Job Description to Resume")
    st.write("Upload a job description and a resume to assess their compatibility.")
    job_description_file = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt"])
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
    if job_description_file and resume_file:
        st.write(f"Job Description uploaded: {job_description_file.name}")
        st.write(f"Resume uploaded: {resume_file.name}")
        # Add your analysis logic here
        st.write("**Compatibility Assessment:**")
        st.write("Compatibility results will appear here.")