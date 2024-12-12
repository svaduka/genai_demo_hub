import mimetypes
from typing import Union
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document


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