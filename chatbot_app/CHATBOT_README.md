# Chatbot Application Using Streamlit and OpenAI (ChatGPT)

## Overview
This project is a chatbot application built using **Streamlit** and integrated with **OpenAI's ChatGPT**. The chatbot functions as an intelligent knowledge base assistant, allowing users to upload documents containing questions and descriptions. Based on the uploaded content, the chatbot generates relevant responses in **JSON format**.

---

## Features
- **Document Upload**: Accepts documents containing questions and related descriptions.
- **Knowledge Base Integration**: Uses the uploaded document as a knowledge base for generating responses.
- **Interactive Chatbot**: Provides conversational responses to user queries based on the knowledge base.
- **JSON Output**: Outputs chatbot responses in a structured JSON format.
- **Streamlit Interface**: User-friendly and interactive web interface for seamless interaction.

---

## Installation

### Prerequisites
- Python 3.7 or above
- Streamlit
- OpenAI API key

### Steps to Install
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/svaduka/genai_demo_hub.git
   cd genai_demo_hub/chatbot-app
   ``` 

### Install Dependencies:
   ```
   pip install -r requirements.txt
   ```

### Set Environment Variables:
1. **Create a .env file in the project directory with the following:**:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```
    Replace your_openai_api_key with your actual OpenAI API key.

### Run the Application:
   ```
   streamlit run app.py
   ```

## How It Works

1. **Upload Document**:
   - Users upload a document (e.g., `.txt`, `.docx`, or `.pdf`) containing questions and descriptions.
   - The document is parsed to extract the knowledge base.

2. **Query Processing**:
   - Users type their questions into the chatbot interface.
   - The chatbot uses OpenAI’s ChatGPT to generate responses by referencing the uploaded knowledge base.

3. **JSON Output**:
   - Responses are displayed in both conversational text and JSON format.

