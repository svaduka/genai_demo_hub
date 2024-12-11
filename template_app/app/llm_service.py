from openai import OpenAI
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Retrieve API key from the .env file
OPEN_API_KEY = os.getenv("OPEN_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=OPEN_API_KEY)

def get_response(
    system_content="Summarize the input.",
    user_content="Explain recursion in programming.",
    model="gpt-4"
):
    """
    Get a response from OpenAI's Chat Completion API.

    Args:
        system_content (str): Instruction for the AI (default: "Summarize the input.").
        user_content (str): The user's input or query.
        model (str): The model to use (default: "gpt-4").
    
    Returns:
        str: The AI's response or error message.
    """
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage
if __name__ == "__main__":
    system_instruction = input("Enter system content (default: Summarize the input): ") or "Summarize the input."
    user_input = input("Enter user content: ")
    model_choice = input("Enter model (default: gpt-4): ") or "gpt-4"

    response = get_response(
        system_content=system_instruction,
        user_content=user_input,
        model=model_choice
    )
    print("\nAI Response:")
    print(response)