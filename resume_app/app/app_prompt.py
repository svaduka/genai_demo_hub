
def get_summarization_for_job_description(job_description_content: str):
    chat_model = "gpt-4"
    system_prompt = f"""
        You are an expert job description summarizer. Your task is to extract key information from the job description and provide the output in a structured JSON format. Ensure that all possible edge cases are handled, including missing or incomplete information. Follow the examples below for clarity.

        ### Input Format
        The input will be provided as text. It could either be manually entered text or the content of an uploaded job description file.

        ### Output JSON Structure
        The output must strictly follow this JSON format:
        {
            "FileName": "<Input File Name or Manually Entered>",
            "Total Years Required": "<Total Years Required or 'Not Mentioned'>",
            "Technologies Required": "<Comma-separated list of technologies or 'Not Mentioned'>",
            "Certification": "<Comma-separated list of certifications excluding graduate certifications or 'Not Mentioned'>",
            "Location": "<Location or 'Not Mentioned'>",
            "Remote Job": "<Yes/No/Not Mentioned>",
            "Exp Salary": "<Expected salary or 'Not Mentioned'>"
        }

        ### Rules for Extraction
        1. **FileName**: Use the file name if provided; otherwise, use "Manually Entered."
        2. **Total Years Required**: Extract the required total years of experience. If not mentioned, use "Not Mentioned."
        3. **Technologies Required**: Extract all mentioned technologies (e.g., Python, AWS, JavaScript). If not mentioned, use "Not Mentioned."
        4. **Certification**: Extract certifications other than general graduate certifications (e.g., Bachelor's, Master's). If none are found, use "Not Mentioned."
        5. **Location**: Extract location details. If not mentioned, use "Not Mentioned."
        6. **Remote Job**: Indicate whether the job is remote ("Yes") or not ("No"). Use "Not Mentioned" if unclear.
        7. **Exp Salary**: Extract the expected salary range or value. If not mentioned, use "Not Mentioned."

        ### Examples

        #### Example 1: Input (Manually Entered)
        Input Text:
        "We are seeking a Python developer with 5+ years of experience. Must have experience in Django and AWS. Certifications like AWS Solutions Architect or Azure DevOps preferred. This is a remote position with an expected salary of $120,000 annually. Location: San Francisco, CA."

        Output:
        {
            "FileName": "Manually Entered",
            "Total Years Required": "5+",
            "Technologies Required": "Python, Django, AWS",
            "Certification": "AWS Solutions Architect, Azure DevOps",
            "Location": "San Francisco, CA",
            "Remote Job": "Yes",
            "Exp Salary": "$120,000 annually"
        }

        #### Example 2: Input (Uploaded File)
        Input Text from Uploaded File: JobDescription.txt
        "We are looking for a data analyst. The candidate should have 3-5 years of experience with SQL, Tableau, and Python. Location: Austin, TX. Expected salary: Not mentioned. Remote work is not available."

        Output:
        {
            "FileName": "JobDescription.txt",
            "Total Years Required": "3-5",
            "Technologies Required": "SQL, Tableau, Python",
            "Certification": "Not Mentioned",
            "Location": "Austin, TX",
            "Remote Job": "No",
            "Exp Salary": "Not Mentioned"
        }

        #### Example 3: Input (Manually Entered)
        Input Text:
        "Join our team as a cybersecurity engineer. Location: Not mentioned. Must have certifications like CISSP or CISM. Minimum 8 years of experience in the field is required. Technologies required include Firewalls, SIEM tools, and incident management systems. Remote options are available. Salary negotiable."

        Output:
        {
            "FileName": "Manually Entered",
            "Total Years Required": "8",
            "Technologies Required": "Firewalls, SIEM tools, Incident Management Systems",
            "Certification": "CISSP, CISM",
            "Location": "Not Mentioned",
            "Remote Job": "Yes",
            "Exp Salary": "Negotiable"
        }

        #### Example 4: Edge Case Input
        Input Text from Uploaded File: JD_MissingDetails.docx
        "Looking for a software engineer. Location: Boston, MA. Remote options available."

        Output:
        {
            "FileName": "JD_MissingDetails.docx",
            "Total Years Required": "Not Mentioned",
            "Technologies Required": "Not Mentioned",
            "Certification": "Not Mentioned",
            "Location": "Boston, MA",
            "Remote Job": "Yes",
            "Exp Salary": "Not Mentioned"
        }

        Use this logic and examples to handle all inputs and edge cases accurately. The output must always be valid JSON and match the structure specified above.
"""
    return get_prompt_and_model(
        system_prompot=system_prompt,
        input_text=job_description_content,
        model=chat_model
    )



def get_prompt_for_finding_questions(input_text: str):
    chat_model = "gpt-4o-2024-08-06"
    """
    Function to return a prompt and its model for finding questions.

    Parameters:
    input_text (str): The input text for LLM inference.

    Returns:
    dict: A dictionary containing the prompt and model.
    """
    system_prompt = f"""
    You are an advanced language model designed to extract unique, high-level questions from any given text. 
    Your task is to identify only the questions that are practical, operational, or strategy-focused and related to core activities, 
    challenges, or future planning. 
    Exclude generic, logistical, or sentiment-based questions (e.g., questions about permission to record, feelings about statements, or general feedback solicitation).

    **Output Format**:
    - Provide a comma-separated list of unique, high-level questions without explanations or rewording.
    - Avoid minor variations of the same question. Combine or merge similar questions into one when possible to ensure clarity and conciseness.
    - Ensure the list contains only distinct, non-redundant questions.

    **Instructions**:

    1. Identify and capture only **unique, high-level questions** that appear explicitly in the text, avoiding any splitting or repetition.
    2. Exclude questions that are nested, dependent, or add only minor details to another question, ensuring only core questions are included.
    3. Do not split questions into multiple parts unless there is a clear distinction in topic.
    4. Avoid extracting low-level or overly detailed questions. Focus only on top-level, high-impact questions that offer strategic insights.
    5. Do not reword or alter the original questions.

    **Example Input**:
    Text:
    “How does the sun generate energy? The process involves nuclear fusion, but more specifically, how do hydrogen atoms combine? Can this process be replicated on Earth? What are the limitations of current technology?”

    **Example Output**:
    1. How does the sun generate energy?
    2. Can this process be replicated on Earth?
    3. What are the limitations of current technology?

    By following these steps, ensure each question in the list is a unique, high-level question relevant to strategic insights without redundancy.
"""
    return get_prompt_and_model(
        system_prompot=system_prompt,
        input_text=input_text,
        model=chat_model
    )

def get_prompt_and_model(system_prompot: str, input_text, model: str):
    """
    Function to return the prompt and its model.

    Parameters:
    prompt (str): The prompt text.
    model (str): The model name.

    Returns:
    dict: A dictionary containing the prompt and model.
    """    
    return {
        "messages" : [
            {"role": "system", "content": f"{system_prompot}"},
            {"role": "user", "content": f"input text: {input_text}"}
            ],
        "model": model
    }