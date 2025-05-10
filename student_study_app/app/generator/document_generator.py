from docx import Document
from app.utils.logger import logger

class DocumentGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def generate_week_material(self, topics_by_subject, week_num=1):
        logger.info("Generating document for week %s", week_num)
        doc = Document()
        doc.add_heading(f"3rd Grade Weekly Study Material - Week {week_num}", 0)
        for subject, topics in topics_by_subject.items():
            doc.add_heading(subject, level=1)
            for topic in topics:
                doc.add_paragraph(f"- {topic}")
        filename = f"{self.output_dir}/week{week_num}_material.docx"
        doc.save(filename)
        logger.info("Saved material to %s", filename)
        return filename