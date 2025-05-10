import openai
from app.utils.logger import logger

class OpenAIProcessor:
    def __init__(self, api_key):
        openai.api_key = api_key

    def extract_topics(self, content):
        logger.info("Calling OpenAI to extract topics...")
        prompt = f"""
        From the following text, extract a structured list of subjects (like Math, Science, Reading), 
        and under each subject list topics taught for 3rd-grade students. Return in JSON.

        Text:
        {content}
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content']