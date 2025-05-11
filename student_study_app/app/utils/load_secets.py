import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# App settings
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DATA_DIRECTORY = os.getenv("DATA_DIRECTORY", "data/")
OUTPUT_DIRECTORY = os.getenv("OUTPUT_DIRECTORY", "output/")

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ParentSquare credentials
PARENTSQUARE_USERNAME = os.getenv("PARENTSQUARE_USERNAME")
PARENTSQUARE_PASSWORD = os.getenv("PARENTSQUARE_PASSWORD")
# URLs
PARENTSQUARE_LOGIN_URL = os.getenv("PARENTSQUARE_LOGIN_URL")
PARENTSQUARE_FEEDS_URL = os.getenv("PARENTSQUARE_FEEDS_URL")
TEACHERS_LIST = os.getenv("TEACHERS_LIST","").split(",")

# Proxy settings
HTTP_PROXY = os.getenv("HTTP_PROXY")
HTTPS_PROXY = os.getenv("HTTPS_PROXY")

# Database connection
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Streamlit config
STREAMLIT_SERVER_PORT = os.getenv("STREAMLIT_SERVER_PORT")

# For testing/debug
if __name__ == "__main__":
    print(f"APP_ENV = {APP_ENV}")
    print(f"OPENAI_API_KEY = {'*****' if OPENAI_API_KEY else None}")
    print(f"PARENTSQUARE_USERNAME = {PARENTSQUARE_USERNAME}")