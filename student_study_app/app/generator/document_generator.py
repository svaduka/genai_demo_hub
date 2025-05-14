from docx import Document
from app.utils.logger import logger
import os
from app.processor.openai_processor import OpenAIProcessor
import json

class DocumentGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.openai_proc = OpenAIProcessor()

    def generate_week_material(self, openai_proc, feeds, current_grade, week_num=1):
        logger.info("Generating document for week %s", week_num)
        subject_map = {}
        other_topics = []

        for feed in feeds:
            topic_text = feed["content"]
            raw_result = openai_proc.generate_educational_content(topic_text, current_grade)

            # Normalize result to list of dicts
            if isinstance(raw_result, str):
                try:
                    results = json.loads(raw_result)
                    if isinstance(results, dict):
                        results = [results]
                except json.JSONDecodeError:
                    results = []
            elif isinstance(raw_result, dict):
                results = [raw_result]
            elif isinstance(raw_result, list):
                results = []
                for item in raw_result:
                    if isinstance(item, str):
                        try:
                            parsed = json.loads(item)
                            if isinstance(parsed, dict):
                                results.append(parsed)
                        except json.JSONDecodeError:
                            continue
                    elif isinstance(item, dict):
                        results.append(item)
            else:
                results = []

            # Process valid results
            for enriched_json in results:
                if enriched_json.get("is_educational", False):
                    subject = enriched_json.get("subject_name", "General")
                    if subject not in subject_map:
                        subject_map[subject] = []
                    subject_map[subject].append((feed, enriched_json))
                else:
                    other_topics.append(feed["content"][:100])

        # Create document after all grouping is complete
        doc = Document()
        doc.add_heading(f"{current_grade} Grade Weekly Study Material - Week {week_num}", 0)

        for subject, items in subject_map.items():
            self._add_subject_section(doc, subject, items)

        self._add_other_topics_section(doc, other_topics)
        self._add_notes_section(doc, feeds)
        self._add_quiz_answers_section(doc, subject_map)

        filename = os.path.join(self.output_dir, f"week{week_num}_material.docx")
        os.makedirs(self.output_dir, exist_ok=True)
        doc.save(filename)
        logger.info("Saved material to %s", filename)
        return filename

    def _add_subject_section(self, doc, subject, items):
        logger.info("Adding subject section: %s", subject)
        doc.add_heading(subject, level=1)
        for feed, enriched in items:
            self._add_topic_content(doc, feed, enriched)

    def _add_topic_content(self, doc, feed, enriched):
        topic = enriched.get("topic_name", feed.get("subject", "Topic"))
        date_str = feed.get("post_date", "Unknown")
        teacher = feed.get("author", "Unknown")

        self._add_teacher_heading(doc, teacher)
        self._add_topic_header(doc, topic)
        doc.add_paragraph(f"Date: {date_str}", style='List Bullet')

        for i in range(1, 4):
            section_name = enriched.get(f"section_{i}_name", f"Section {i}")
            is_table = enriched.get(f"section_{i}_is_table", False)
            content = enriched.get(f"section_{i}_content", {})

            doc.add_heading(section_name, level=3)
            if is_table and isinstance(content, list):
                for row in content:
                    name = row.get("name", "")
                    meaning = row.get("meaning", "")
                    example = row.get("example", "")
                    doc.add_paragraph(f"- {name}: {meaning} | Example: {example}", style='List Bullet')
            elif isinstance(content, dict):
                # Special handling for Quizzes section
                if section_name.lower() == "quizzes":
                    for label in ("current_grade", "next_grade"):
                        questions = content.get(label, [])
                        if questions:
                            doc.add_paragraph(f"{label.replace('_', ' ').title()}:", style='List Bullet')
                            for i, q in enumerate(questions, 1):
                                doc.add_paragraph(f"{i}. {q.get('question')}", style='List Bullet')
                                doc.add_paragraph(f"A: {q.get('answer')}", style='List Bullet')
                else:
                    current = content.get("current_grade", "")
                    next_g = content.get("next_grade", "")
                    if current:
                        doc.add_paragraph("Current Grade:", style='List Bullet')
                        if isinstance(current, dict):
                            for k, v in current.items():
                                doc.add_paragraph(f"{k}: {v}", style='List Bullet')
                        else:
                            doc.add_paragraph(str(current))

                    if next_g:
                        doc.add_paragraph("Next Grade:", style='List Bullet')
                        if isinstance(next_g, dict):
                            for k, v in next_g.items():
                                doc.add_paragraph(f"{k}: {v}", style='List Bullet')
                        else:
                            doc.add_paragraph(str(next_g))

    def _add_teacher_heading(self, doc, teacher_name):
        doc.add_heading(f"Teacher: {teacher_name}", level=2)

    def _add_topic_header(self, doc, topic):
        doc.add_heading(f"Topic: {topic}", level=2)

    def _add_section(self, doc, section_title, content):
        doc.add_heading(section_title, level=3)
        if isinstance(content, list):
            for item in content:
                doc.add_paragraph(str(item), style='List Bullet')
        elif isinstance(content, str):
            doc.add_paragraph(content)

    def _add_quiz_section(self, doc, quiz):
        if quiz:
            doc.add_heading("Quizzes", level=3)
            for i, q in enumerate(quiz, 1):
                doc.add_paragraph(f"{i}. {q.get('question')}", style='List Bullet')
                answer = q.get("answer")
                if "___" not in q.get("question"):
                    doc.add_paragraph(f"A: {answer}", style='List Bullet')

    def _add_quiz_answers_section(self, doc, subject_map):
        doc.add_page_break()
        doc.add_heading("Appendix: Answers", level=1)
        for subject, items in subject_map.items():
            doc.add_heading(subject, level=2)
            for _, enriched in items:
                topic = enriched.get("topic_name", "Topic")
                quiz_section = enriched.get("section_3_content", {})
                doc.add_heading(f"Topic: {topic}", level=3)
                for level in ("current_grade", "next_grade"):
                    if level in quiz_section:
                        doc.add_heading(f"{level.replace('_', ' ').title()}:", level=4)
                        for i, q in enumerate(quiz_section[level], 1):
                            doc.add_paragraph(f"{i}. {q.get('answer', '')}", style='List Bullet')

    def _add_other_topics_section(self, doc, other_topics):
        if other_topics:
            logger.info("Adding Other Topics section with %d entries", len(other_topics))
            doc.add_heading("Other Topics", level=1)
            for topic in other_topics:
                doc.add_paragraph(f"• {topic}", style='List Bullet')

    def _add_notes_section(self, doc, feeds):
        notes = []
        for feed in feeds:
            if "note" in feed:
                notes.append(feed["note"])

        if notes:
            logger.info("Adding Important Notes section with %d notes", len(notes))
            doc.add_heading("Important Notes", level=1)
            for note in notes:
                doc.add_paragraph(f"• {note}", style='List Bullet')