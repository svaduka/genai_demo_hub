import os
from openai import OpenAI
from dotenv import load_dotenv

class OpenAIChatClient:
    def __init__(self):
        """
        Initializes the OpenAIChatClient class by loading environment variables
        and setting up the OpenAI client.
        """
        # Load the .env file
        load_dotenv()
        
        # Retrieve API key from the .env file
        self.api_key = os.getenv("OPEN_API_KEY")
        if not self.api_key:
            raise ValueError("OPEN_API_KEY not found in the environment variables.")
        
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.api_key)

    def get_response(self, messages, model="gpt-4",temperature=0.1,):
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
            response = self.client.chat.completions.create(
                    model=model,
                    temperature=temperature,
                    messages=messages)

            return response.choices[0].message.content
        except Exception as e:
            return f"An error occurred: {str(e)}"