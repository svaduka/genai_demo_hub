from docx import Document
from app.utils.logger import logger
import os
from app.processor.openai_processor import OpenAIProcessor
import json

class DocumentGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.openai_proc = OpenAIProcessor()
        self.quiz_answers = []

    def generate_week_material(self, openai_proc, feeds, current_grade, week_num=1):
        logger.info("Generating document for week %s", week_num)
        subject_map = {}
        other_topics = []
        self.quiz_answers = []

        raw_results = openai_proc.generate_educational_content(feeds, current_grade)
#         raw_results = r"""
# [{
#   "subject_name": "Understanding Variables",
#   "teacher_name": "Class Teacher",
#   "date": "",
#   "topics": [
#     {
#       "topic_name": "Understanding Variables and Expressions",
#       "section_1_is_table": false,
#       "section_1_name": "Reading Material",
#       "section_1_content": "Variables are symbols used to represent unknown values or changing quantities in mathematical expressions and equations. They are essential in formulating equations that model real-world situations. Understanding how to manipulate variables and expressions is foundational for solving algebraic problems.",
#       "section_2_is_table": false,
#       "section_2_name": "Real World Examples",
#       "section_2_content": "1. In a recipe, 'x' could represent the number of cups of flour needed. 2. In budgeting, 'y' might represent the total amount of money saved each month. 3. In physics, 'v' could be used to denote velocity. 4. In computing, 'n' might represent the number of iterations in a loop. 5. In business, 'p' could represent profit over time.",
#       "section_3_is_table": false,
#       "section_3_name": "Quizzes",
#       "section_3_content": {
#         "current_grade": [
#           {
#             "question": "What is a variable in mathematics?",
#             "answer": "A symbol that represents an unknown value."
#           },
#           {
#             "question": "How are variables used in equations?",
#             "answer": "They are used to represent quantities that can change."
#           }
#         ],
#         "next_grade": [
#           {
#             "question": "What does it mean to solve for a variable?",
#             "answer": "To find the value of the variable that makes the equation true."
#           },
#           {
#             "question": "How can variables be used in real-life situations?",
#             "answer": "They can model scenarios such as financial planning or scientific experiments."
#           }
#         ]
#       }
#     }
#   ],
#   "is_educational": true
# }]
# """
        logger.info("Raw OpenAI results: %s", raw_results)

        # Normalize and zip with feeds
        results = []
        if isinstance(raw_results, str):
            try:
                parsed = json.loads(raw_results)
                if isinstance(parsed, list):
                    results = parsed
            except json.JSONDecodeError as e:
                print(e)
                results = []
        elif isinstance(raw_results, list):
            results = raw_results

        logger.info("Processing %d enriched results from OpenAI", len(results))

        for feed, enriched_json in zip(feeds, results):
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
        self._add_quiz_answers_section(doc)

        filename = os.path.join(self.output_dir, f"week{week_num}_material.docx")
        os.makedirs(self.output_dir, exist_ok=True)
        doc.save(filename)
        logger.info("Saved material to %s", filename)
        return filename

    def _add_subject_section(self, doc, subject, items):
        logger.info("Adding subject section: %s", subject)
        doc.add_heading(subject, level=1)
        for feed, enriched in items:
            self._add_topic_content(doc, feed, enriched, subject)

    def _add_topic_content(self, doc, feed, enriched, subject):
        topic = enriched.get("topic_name", feed.get("subject", "Topic"))
        date_str = feed.get("post_date", "Unknown")
        teacher = feed.get("author", "Unknown")

        self._add_teacher_heading(doc, teacher)
        self._add_topic_header(doc, topic)
        doc.add_paragraph(f"Date: {date_str}", style="List Bullet")

        # Collect combined content for current and next grade
        combined_current = []
        combined_next = []

        for topic_json in enriched.get("topics", []):
            topic_name = topic_json.get("topic_name", topic)
            self._add_topic_header(doc, topic_name)

            for i in range(1, 4):
                section_name = topic_json.get(f"section_{i}_name", f"Section {i}")
                is_table = topic_json.get(f"section_{i}_is_table", False)
                content = topic_json.get(f"section_{i}_content", {})
                doc.add_heading(section_name, level=3)
                self._render_section_content(doc, subject, topic_name, section_name, is_table, content)

    def _render_section_content(self, doc, subject, topic, section_name, is_table, content):
        if is_table and isinstance(content, list):
            for row in content:
                name = row.get("name", "")
                meaning = row.get("meaning", "")
                example = row.get("example", "")
                para_text = f"- {name}: {meaning}"
                if example:
                    para_text += f" | Example: {example}"
                doc.add_paragraph(para_text)
        elif isinstance(content, dict):
            if section_name.lower() == "quizzes":
                all_quizzes = []
                if "questions" in content:
                    all_quizzes = content["questions"]
                elif "current_grade" in content or "next_grade" in content:
                    all_quizzes = content.get("current_grade", []) + content.get("next_grade", [])
                for q in all_quizzes:
                    doc.add_paragraph(f"{q.get("question")}", style="List Bullet")
                    doc.add_paragraph("A: ", style="List Bullet")
                    self.quiz_answers.append((subject, topic, q.get("question"), q.get("answer", "")))
            else:
                for k, v in content.items():
                    if k.lower() == "example":
                        doc.add_paragraph(f"Example: {v}")
                    else:
                        doc.add_paragraph(f"{k}: {v}")
        elif isinstance(content, str):
            doc.add_paragraph(content)

    def _add_teacher_heading(self, doc, teacher_name):
        doc.add_heading(f"Teacher: {teacher_name}", level=2)

    def _add_topic_header(self, doc, topic):
        doc.add_heading(f"Topic: {topic}", level=2)

    def _add_section(self, doc, section_title, content):
        doc.add_heading(section_title, level=3)
        if isinstance(content, list):
            for item in content:
                doc.add_paragraph(str(item), style="List Bullet")
        elif isinstance(content, str):
            doc.add_paragraph(content)

    def _add_quiz_section(self, doc, quiz):
        if quiz:
            doc.add_heading("Quizzes", level=3)
            for i, q in enumerate(quiz, 1):
                doc.add_paragraph(f"{i}. {q.get("question")}", style="List Bullet")
                answer = q.get("answer")
                if "___" not in q.get("question"):
                    doc.add_paragraph("A: ", style="List Bullet")

    def _add_quiz_answers_section(self, doc):
        if not self.quiz_answers:
            return
        doc.add_page_break()
        doc.add_heading("Appendix: Answers", level=1)
        seen = set()
        for subject, topic, question, answer in self.quiz_answers:
            key = (subject, topic, question)
            if key in seen:
                continue
            seen.add(key)
            doc.add_heading(subject, level=2)
            doc.add_heading(f"Topic: {topic}", level=3)
            doc.add_paragraph(f"Q: {question}", style="List Bullet")
            doc.add_paragraph(f"A: {answer}", style="List Bullet")

    def _add_other_topics_section(self, doc, other_topics):
        if other_topics:
            logger.info("Adding Other Topics section with %d entries", len(other_topics))
            doc.add_heading("Other Topics", level=1)
            for topic in other_topics:
                doc.add_paragraph(f"• {topic}", style="List Bullet")

    def _add_notes_section(self, doc, feeds):
        notes = []
        for feed in feeds:
            if "note" in feed:
                notes.append(feed["note"])

        if notes:
            logger.info("Adding Important Notes section with %d notes", len(notes))
            doc.add_heading("Important Notes", level=1)
            for note in notes:
                doc.add_paragraph(f"• {note}", style="List Bullet")