from docx import Document
from app.utils.logger import logger
import os
from app.processor.openai_processor import OpenAIProcessor

class DocumentGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.openai_proc = OpenAIProcessor()

    def generate_week_material(self, topics_by_subject, week_num=1):
        logger.info("Generating document for week %s", week_num)
        doc = Document()
        doc.add_heading(f"3rd Grade Weekly Study Material - Week {week_num}", 0)

        subjects = topics_by_subject.get("subjects", {})

        other_topics = []

        for subject, topics in subjects.items():
            doc.add_heading(subject, level=1)
            for topic in topics:
                enriched_json = self.openai_proc.generate_steam_content(topic)
                if isinstance(enriched_json, str):
                    import json
                    enriched_json = json.loads(enriched_json)

                if enriched_json.get("is_educational", False):
                    date_str = enriched_json.get("post_date", "Unknown")
                    doc.add_paragraph(f"Date: {date_str}", style='List Bullet')
                    doc.add_heading(f"Topic: {topic}", level=2)

                    explanation = enriched_json.get("student_friendly_explanation", "No explanation provided.")
                    doc.add_paragraph(explanation)

                    reading = enriched_json.get("reading_material")
                    if reading:
                        doc.add_paragraph("Reading Material:")
                        doc.add_paragraph(reading)

                    examples = enriched_json.get("real_world_examples", [])
                    if examples:
                        doc.add_paragraph("Examples:")
                        for ex in examples:
                            doc.add_paragraph(f"- {ex}", style='List Bullet')

                    quiz = enriched_json.get("quiz", [])
                    if quiz:
                        doc.add_paragraph("Quiz:")
                        for q in quiz:
                            doc.add_paragraph(f"Q ({q.get('level', 'basic')}): {q.get('question')}", style='List Bullet')
                            doc.add_paragraph(f"A: {q.get('answer')}", style='List Bullet')
                            if q.get("explanation"):
                                doc.add_paragraph(f"Why: {q.get('explanation')}", style='List Bullet')

                    links = enriched_json.get("youtube_links", [])
                    if links:
                        doc.add_paragraph("YouTube Links:")
                        for link in links:
                            doc.add_paragraph(link, style='List Bullet')

                    images = enriched_json.get("image_ideas", [])
                    if images:
                        doc.add_paragraph("Image Ideas:")
                        for img in images:
                            doc.add_paragraph(img, style='List Bullet')
                else:
                    other_topics.append(topic)

        if other_topics:
            doc.add_heading("Other Topics", level=1)
            for topic in other_topics:
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