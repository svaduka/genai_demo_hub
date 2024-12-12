import streamlit as st

def summarize_content(input_text):
    """
    Simulates summarization of the input text.
    Replace this logic with actual summarization implementation.
    """
    return "Hello, World!"

def load_summarize_job_description():
    st.title("Summarize Job Description")
    
    # Layout with columns: Inputs on the left, Output on the right
    col1, col2 = st.columns([2, 1])  # Adjust column widths

    # Section 1: Input (Vertical Layout)
    with col1:
        st.subheader("Input Section")

        # Text Area for manual input
        job_description = st.text_area("Enter Job Description Manually")

        # File uploader for uploading job descriptions
        uploaded_file = st.file_uploader("Or Upload a File", type=["pdf", "docx", "txt"])

        # Combine inputs for processing
        input_text = ""
        if job_description:
            input_text = job_description
        elif uploaded_file:
            input_text = f"Uploaded file: {uploaded_file.name}"  # Placeholder for file content processing

        # Summarize Button
        if st.button("Summarize"):
            if input_text:
                st.session_state["summary"] = summarize_content(input_text)
            else:
                st.warning("Please enter a job description or upload a file.")

    # Section 2: Output
    with col2:
        st.subheader("Summarization Report")
        # Add a border around the output section using existing CSS classes
        st.markdown(
            f"""
            <div class="output-container">
                <div class="output-title">Output:</div>
                {st.session_state.get("summary", "Output will be displayed here after summarization.")}
            </div>
            """,
            unsafe_allow_html=True,
        )