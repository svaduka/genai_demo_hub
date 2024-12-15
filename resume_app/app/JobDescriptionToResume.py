import streamlit as st
import traceback
import logging
from logger import log_msg  # Assuming logger class with log_msg is already implemented
import file_utils as fu
import app_prompt as prmpt
from llm_service import OpenAIChatClient


def compare_job_description_to_resume(job_description_text, resume_content):
    """
    Compare a job description with a candidate's resume using LLM and return an HTML summary.

    Args:
        job_description_text (str): Text of the job description.
        resume_content (str): Content of the candidate's resume.

    Returns:
        str: HTML table summarizing the comparison.
    """
    try:
        log_msg("Starting job description and resume comparison.", level=logging.INFO)

        # Prepare prompt arguments for LLM
        log_msg("Preparing summarization request.", level=logging.INFO)
        llm_args = prmpt.get_job_description_to_resume_comparision(
            job_description_content=job_description_text,
            resume_content=resume_content
        )
        log_msg(f"Input prompt: {llm_args}", level=logging.DEBUG)

        # Initialize LLM client and send request
        llm = OpenAIChatClient()
        log_msg("Sending request to OpenAIChatClient.", level=logging.INFO)
        response = llm.get_response(**llm_args)
        log_msg("Received response from OpenAIChatClient.", level=logging.INFO)
        return response

    except Exception as e:
        # Log the exception with traceback
        log_msg(f"Error during job description and resume comparison: {str(e)}\n{traceback.format_exc()}", level=logging.ERROR)
        raise


def load_job_description_to_resume():
    """
    Streamlit app for uploading and comparing job descriptions with resumes.
    """
    try:
        st.title("Job Description to Resume")
        log_msg("Job Description to Resume app loaded successfully.", level=logging.INFO)

        # Create two horizontal sections
        col1, col2 = st.columns([2, 1])  # Adjust column widths

        # Section 1: Inputs
        with col1:
            st.subheader("Input Section")
            log_msg("Input section loaded.", level=logging.INFO)

            # Job Description: Upload or Text Area
            job_description_text = st.text_area("Or enter Job Description manually", height=200)
            if job_description_text:
                log_msg("Job description entered manually.", level=logging.INFO)

            job_description_file = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt"])
            if job_description_file:
                job_description_file_name = job_description_file.name
                log_msg(f"Job description file uploaded: {job_description_file_name}", level=logging.INFO)
                job_description_text = fu.extract_content_from_file(job_description_file, job_description_file_name)

            # Resume Upload
            resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
            resume_text = None
            if resume_file:
                resume_file_name = resume_file.name
                log_msg(f"Resume file uploaded: {resume_file_name}", level=logging.INFO)
                resume_text = fu.extract_content_from_file(resume_file, resume_file_name)

            # Compare Button
            if st.button("Compare"):
                log_msg("Compare button clicked.", level=logging.INFO)
                try:
                    if job_description_text and resume_text:
                        json_response_str = compare_job_description_to_resume(job_description_text, resume_text)
                        # Parse response and convert to HTML table
                        log_msg("Parsing response JSON.", level=logging.INFO)
                        json_response = fu.parse_json(json_response_str)

                        log_msg("Converting JSON response to HTML table.", level=logging.INFO)
                        output_html = fu.parse_nested_json_to_html_table(json_response)

                        log_msg("Successfully generated HTML table for comparison.", level=logging.INFO)
                        st.session_state["json_response_str"] = json_response_str
                        st.session_state["output"] = output_html
                        st.session_state["jd_uploaded"] = (
                            job_description_file.name if job_description_file else "Manually Entered"
                        )
                        st.session_state["resume_uploaded"] = resume_file.name
                        log_msg("Comparison executed successfully.", level=logging.INFO)
                    else:
                        log_msg("Comparison failed: Missing inputs.", level=logging.WARNING)
                        st.warning("Please upload both a job description and a resume.")
                except Exception as e:
                    log_msg(f"Error during comparison: {str(e)}\n{traceback.format_exc()}", level=logging.ERROR)
                    st.error("An error occurred during the comparison. Check logs for details.")

        # Section 2: Output
        with col2:
            st.subheader("Output Section")
            log_msg("Output section loaded.", level=logging.INFO)

            try:
                # Display the comparison results as an HTML table
                output_html = st.session_state.get("output", None)
                json_response_str = st.session_state.get("json_response_str", None)
                if output_html:
                    st.markdown(
                        f"""
                        <div class="output-container">
                            <div class="output-title">Compatibility Assessment:</div>
                            {output_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    log_msg("Comparison results displayed successfully.", level=logging.INFO)
                    # Generate downloadable files
                    pdf_buffer = fu.json_to_pdf(json_response_str)
                    docx_buffer = fu.json_to_docx(json_response_str)
                    # Add download buttons
                    st.download_button(
                        label="Download as PDF",
                        data=pdf_buffer,
                        file_name="compatibility_assessment.pdf",
                        mime="application/pdf",
                    )
                    st.download_button(
                        label="Download as DOCX",
                        data=docx_buffer,
                        file_name="compatibility_assessment.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                else:
                    st.markdown(
                        """
                        <div class="output-container">
                            <div class="output-title">Compatibility Assessment:</div>
                            <p>Output will be displayed here after comparison.</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Display filenames if uploaded
                if "jd_uploaded" in st.session_state and "resume_uploaded" in st.session_state:
                    st.write(f"**Job Description:** {st.session_state['jd_uploaded']}")
                    st.write(f"**Resume:** {st.session_state['resume_uploaded']}")
                    log_msg("Uploaded filenames displayed successfully.", level=logging.INFO)

            except Exception as e:
                log_msg(f"Error displaying output: {str(e)}\n{traceback.format_exc()}", level=logging.ERROR)
                st.error("An error occurred while displaying the output. Check logs for details.")

    except Exception as e:
        log_msg(f"Error initializing app: {str(e)}\n{traceback.format_exc()}", level=logging.ERROR)
        st.error("An error occurred while loading the app. Check logs for details.")