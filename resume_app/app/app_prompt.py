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