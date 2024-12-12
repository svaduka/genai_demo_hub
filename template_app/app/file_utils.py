import os
import mimetypes
from typing import Union
from PyPDF2 import PdfReader
from docx import Document

def get_file_type(file_path: str) -> str:
    """
    Determine the type of a file based on its extension or MIME type.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The file type ("pdf", "docx", "text", or "unknown").
    """
    file_name, file_extension = os.path.splitext(file_path.lower())
    mime_type, _ = mimetypes.guess_type(file_path)

    if file_extension == ".pdf":
        return "pdf"
    elif file_extension in [".docx", ".doc"]:
        return "docx"
    elif file_extension in [".txt"]:
        return "text"
    elif mime_type and "text" in mime_type:
        return "text"
    else:
        return "unknown"

def extract_content_from_file(file_path: str) -> Union[str, None]:
    """
    Extract content from a file based on its type.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The extracted content from the file.
    """
    file_type = get_file_type(file_path)

    try:
        if file_type == "pdf":
            return extract_content_from_pdf(file_path)
        elif file_type == "docx":
            return extract_content_from_docx(file_path)
        elif file_type == "text":
            return extract_content_from_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        raise ValueError(f"Error reading file '{file_path}': {str(e)}")

def extract_content_from_pdf(file_path: str) -> str:
    """
    Extract content from a PDF file.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The extracted content from the PDF.
    """
    try:
        reader = PdfReader(file_path)
        content = ""
        for page in reader.pages:
            content += page.extract_text()
        return content.strip()
    except Exception as e:
        raise ValueError(f"Error extracting content from PDF: {str(e)}")

def extract_content_from_docx(file_path: str) -> str:
    """
    Extract content from a DOCX file.

    Args:
        file_path (str): The path to the DOCX file.

    Returns:
        str: The extracted content from the DOCX file.
    """
    try:
        document = Document(file_path)
        content = "\n".join([paragraph.text for paragraph in document.paragraphs])
        return content.strip()
    except Exception as e:
        raise ValueError(f"Error extracting content from DOCX: {str(e)}")

def extract_content_from_text(file_path: str) -> str:
    """
    Extract content from a text file.

    Args:
        file_path (str): The path to the text file.

    Returns:
        str: The extracted content from the text file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        raise ValueError(f"Error extracting content from text file: {str(e)}")