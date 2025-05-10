import streamlit as st

def load_summarize_resume():
    st.title("Summarize Resume")
    st.write("Upload a resume to summarize its key points.")
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
    if uploaded_file:
        st.write(f"File uploaded: {uploaded_file.name}")
        # Add your summarization logic here
        st.write("**Summary:**")
        st.write("Key skills and experiences from the resume will appear here.")