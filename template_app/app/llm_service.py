import os
import traceback
from openai import OpenAI
from dotenv import load_dotenv
from logger import log_msg  # Assuming logger and log_msg are already defined
import logging

class OpenAIChatClient:
    def __init__(self):
        """
        Initializes the OpenAIChatClient class by loading environment variables
        and setting up the OpenAI client.
        """
        try:
            # Load the .env file
            load_dotenv()

            # Retrieve API key from the .env file
            self.api_key = os.getenv("OPEN_API_KEY")
            if not self.api_key:
                log_msg("OPEN_API_KEY not found in the environment variables.", level=logging.ERROR)
                raise ValueError("OPEN_API_KEY not found in the environment variables.")

            # Initialize the OpenAI client
            self.client = OpenAI(api_key=self.api_key)
            log_msg("OpenAIChatClient initialized successfully.", level=logging.INFO)

        except Exception as e:
            log_msg(f"Error initializing OpenAIChatClient: {str(e)}\n{traceback.format_exc()}", level=logging.ERROR)
            raise

    def get_response(self, messages, model="gpt-4", temperature=0.1):
        """
        Get a response from OpenAI's Chat Completion API.

        Args:
            messages (list): List of message dictionaries (role and content).
            model (str): The model to use (default: "gpt-4").
            temperature (float): Sampling temperature to control randomness.

        Returns:
            str: The AI's response or error message.
        """
        try:
            log_msg(f"Sending request to OpenAI model '{model}' with messages: {messages}", level=logging.INFO)
            response = self.client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=messages
            )

            # Log the response content
            response_content = response.choices[0].message.content
            log_msg(f"Received response: {response_content}", level=logging.INFO)
            return response_content

        except Exception as e:
            log_msg(f"Error during API call: {str(e)}\n{traceback.format_exc()}", level=logging.ERROR)
            return f"An error occurred: {str(e)}"
