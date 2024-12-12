import mimetypes
from typing import Union
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
import json


def get_file_type(file: BytesIO, file_name: str) -> str:
    """
    Determine the type of an uploaded file based on its MIME type or extension.

    Args:
        file (BytesIO): The uploaded file object.
        file_name (str): The name of the uploaded file.

    Returns:
        str: The file type ("pdf", "docx", "text", or "unknown").
    """
    mime_type, _ = mimetypes.guess_type(file_name)
    file_extension = file_name.split(".")[-1].lower()

    if file_extension == "pdf":
        return "pdf"
    elif file_extension in ["docx", "doc"]:
        return "docx"
    elif file_extension in ["txt"]:
        return "text"
    elif mime_type and "text" in mime_type:
        return "text"
    else:
        return "unknown"


def extract_content_from_file(file: BytesIO, file_name: str) -> Union[str, None]:
    """
    Extract content from an uploaded file based on its type.

    Args:
        file (BytesIO): The uploaded file object.
        file_name (str): The name of the uploaded file.

    Returns:
        str: The extracted content from the file.
    """
    file_type = get_file_type(file, file_name)

    try:
        if file_type == "pdf":
            return extract_content_from_pdf(file)
        elif file_type == "docx":
            return extract_content_from_docx(file)
        elif file_type == "text":
            return extract_content_from_text(file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        raise ValueError(f"Error reading file '{file_name}': {str(e)}")


def extract_content_from_pdf(file: BytesIO) -> str:
    """
    Extract content from an uploaded PDF file.

    Args:
        file (BytesIO): The uploaded PDF file object.

    Returns:
        str: The extracted content from the PDF.
    """
    try:
        reader = PdfReader(file)
        content = ""
        for page in reader.pages:
            content += page.extract_text()
        return content.strip()
    except Exception as e:
        raise ValueError(f"Error extracting content from PDF: {str(e)}")


def extract_content_from_docx(file: BytesIO) -> str:
    """
    Extract content from an uploaded DOCX file.

    Args:
        file (BytesIO): The uploaded DOCX file object.

    Returns:
        str: The extracted content from the DOCX file.
    """
    try:
        document = Document(file)
        content = "\n".join([paragraph.text for paragraph in document.paragraphs])
        return content.strip()
    except Exception as e:
        raise ValueError(f"Error extracting content from DOCX: {str(e)}")


def extract_content_from_text(file: BytesIO) -> str:
    """
    Extract content from an uploaded text file.

    Args:
        file (BytesIO): The uploaded text file object.

    Returns:
        str: The extracted content from the text file.
    """
    try:
        return file.read().decode("utf-8").strip()
    except Exception as e:
        raise ValueError(f"Error extracting content from text file: {str(e)}")

def parse_json(input_data: Union[str, dict]) -> dict:
    """
    Parse the input to ensure it's a JSON object.

    Args:
        input_data (str or dict): The input data, either as a JSON string or dictionary.
    
    Returns:
        dict: The parsed JSON object.
    """
    if isinstance(input_data, str):
        return json.loads(input_data)
    elif isinstance(input_data, dict):
        return input_data
    else:
        raise ValueError("Input must be a JSON string or dictionary.")
        

def convert_to_html_table(json_data: dict) -> str:
    """
    Convert a JSON object into an HTML table.

    Args:
        json_data (dict): The JSON object to be converted.
    
    Returns:
        str: HTML string representing the table.
    """
    table_html = "<table border='1' style='border-collapse: collapse; width: 50%; text-align: left;'>"
    table_html += "<tr><th>Key</th><th>Value</th></tr>"

    for key, value in json_data.items():
        table_html += f"<tr><td>{key}</td><td>{value}</td></tr>"

    table_html += "</table>"
    return table_html
def parse_nested_json_to_html_table(json_data):
    """
    Parse the given JSON into an HTML table.

    Args:
        json_data (dict): The JSON data to parse.

    Returns:
        str: An HTML string representing the table.
    """
    try:
        # Start the HTML table
        html = """
        <table border="1" style="border-collapse: collapse; width: 100%; text-align: left;">
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Job Description</th>
                    <th>Candidate</th>
                </tr>
            </thead>
            <tbody>
        """

        # Iterate through the JSON data and build table rows
        for key, value in json_data.items():
            if isinstance(value, dict):  # Handle nested dictionaries
                html += f"<tr><td>{key}</td>"  # Add the main key as a row
                # Ensure two cells for nested dictionaries
                sub_values = list(value.values())
                if len(sub_values) == 2:  # Expected two keys: 'Required' and 'Candidate'
                    html += f"<td>{sub_values[0]}</td><td>{sub_values[1]}</td></tr>"
                else:
                    raise ValueError(f"Nested dictionary for '{key}' must have exactly two keys.")
            else:  # Handle simple key-value pairs
                html += f"""
                <tr>
                    <td>{key}</td>
                    <td colspan="2">{value}</td>
                </tr>
                """

        # Close the HTML table
        html += """
            </tbody>
        </table>
        """
        return html
    except Exception as e:
        raise ValueError(f"Error generating HTML table: {str(e)}")