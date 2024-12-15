from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from io import BytesIO
import json


def parse_nested_json_to_pdf_table(input_json):
    """
    Parse the given JSON into a PDF table and return it as BytesIO.

    Args:
        input_json (str): The JSON data to parse as a string.

    Returns:
        BytesIO: A BytesIO object containing the generated PDF.
    """
    try:
        # Parse the input JSON
        json_data = json.loads(input_json)

        # Prepare table data
        table_data = [["Component", "Job Description", "Candidate"]]  # Header row
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]

        for key, value in json_data.items():
            if isinstance(value, dict):  # Handle nested dictionaries
                sub_values = list(value.values())
                if len(sub_values) == 2:  # Expected two keys: 'Required' and 'Candidate'
                    table_data.append([
                        Paragraph(key, normal_style),
                        Paragraph(sub_values[0], normal_style),
                        Paragraph(sub_values[1], normal_style)
                    ])
                else:
                    raise ValueError(f"Nested dictionary for '{key}' must have exactly two keys.")
            else:  # Handle simple key-value pairs
                table_data.append([
                    Paragraph(key, normal_style),
                    Paragraph(value, normal_style),
                    ""
                ])  # Add a single value with an empty "Candidate" cell

        # Create a BytesIO buffer for the PDF
        pdf_buffer = BytesIO()

        # Set up the PDF document with landscape orientation
        pdf = SimpleDocTemplate(
            pdf_buffer, pagesize=landscape(letter),
            rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20
        )

        # Dynamically calculate column widths based on page width
        page_width = landscape(letter)[0] - 40  # Adjust for margins
        col_widths = [0.2 * page_width, 0.4 * page_width, 0.4 * page_width]  # Distribute width proportionally

        # Create the table
        table = Table(table_data, colWidths=col_widths, repeatRows=1)

        # Add style to the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)

        # Build the PDF
        pdf.build([table])

        # Seek to the beginning of the buffer
        pdf_buffer.seek(0)

        return pdf_buffer
    except Exception as e:
        raise ValueError(f"Error generating PDF table: {str(e)}")


# Example usage
input_json = """
{
    "Job Title": "Email Campaign Developer",
    "Candidate Name": "Anuhya Siliveru",
    "Total Years of Experience": {
        "Required": "3 - 6 Years",
        "Candidate": "9+ years"
    },
    "Key Skills": {
        "Required": "Digital Marketing, Emarsys, excel, SQL",
        "Candidate": "Spark, AWS, Snowflake, JIRA, Confluence, Python, Hive, Scala, Java, Struts, JavaScript, Ajax"
    },
    "Education": {
        "Required": "Not Mentioned",
        "Candidate": "Master of Science in Computers"
    },
    "Certifications": {
        "Required": "Not Mentioned",
        "Candidate": "Not Mentioned"
    },
    "Location": {
        "Job": "Not Mentioned",
        "Candidate": "Not Mentioned"
    },
    "Remote Eligible": {
        "Required": "Not Mentioned",
        "Candidate": "Not Mentioned"
    },
    "Salary": {
        "Range": "Not Mentioned",
        "Expected": "Not Mentioned"
    },
    "Responsibilities Match": "Candidate has extensive experience in software development and data management, but no specific experience in email campaign development.",
    "Language Proficiency": {
        "Required": "Not Mentioned",
        "Candidate": "Not Mentioned"
    },
    "Cultural Fit Indicators": "Not Mentioned",
    "Availability": {
        "Required": "Not Mentioned",
        "Candidate": "Not Mentioned"
    },
    "Resume Gaps": "None",
    "Overall Match Percentage": "50%"
}
"""

# Generate the PDF
pdf_bytes = parse_nested_json_to_pdf_table(input_json)

# Save the PDF to a file (optional)
with open("output_wrapped_fitting_table.pdf", "wb") as f:
    f.write(pdf_bytes.getvalue())