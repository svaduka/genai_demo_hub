from docx import Document
from app.utils.logger import logger
import os

class DocumentGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def generate_week_material(self, topics_by_subject, week_num=1):
        logger.info("Generating document for week %s", week_num)
        doc = Document()
        doc.add_heading(f"3rd Grade Weekly Study Material - Week {week_num}", 0)

        subjects = topics_by_subject.get("subjects", {})
        for subject, topics in subjects.items():
            doc.add_heading(subject, level=1)
            for topic in topics:
                doc.add_paragraph(f"• {topic}", style='List Bullet')

        notes = topics_by_subject.get("important_notes", [])
        if notes:
            doc.add_heading("Important Notes", level=1)
            for note in notes:
                doc.add_paragraph(f"• {note}", style='List Bullet')

        filename = os.path.join(self.output_dir, f"week{week_num}_material.docx")
        os.makedirs(self.output_dir, exist_ok=True)
        doc.save(filename)
        logger.info("Saved material to %s", filename)
        return filename