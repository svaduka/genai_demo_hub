import json
from openai import AsyncOpenAI
from app.utils.logger import logger

client = AsyncOpenAI()

multi_shot_prompt = """
You are a highly accurate educational assistant tasked with parsing long-form weekly school updates (often exceeding 3000 words) into structured JSON, suitable for academic tracking and syllabus generation.

Your job is to extract all meaningful educational content and teacher communications for a 3rd-grade student from a teacher’s newsletter, announcement, or weekly feed post.

You must generate all the content without missing any information in the output.

-----------------------
📌 TASK REQUIREMENTS
-----------------------

Given the text below, generate a JSON structure with the following keys:

1. "subjects": A dictionary where:
   - Each key is the name of a subject (e.g., "Math", "Science", "Reading", "Writing", "Social Studies", "Grammar", "Vocabulary", "Spelling", "Art", "Physical Education", etc.).
   - Each value is a list of **topics** (i.e., lessons, concepts, skills, activities) covered for that subject during the week. Include worksheet names, activity types, page numbers, and specific goals mentioned by the teacher.

   ❗️ If subjects are mentioned implicitly (e.g., "Today we worked on long division" → Math), include them accurately.
   ❗️ Ensure **no subjects or topics are missed**, even if the structure in the text is inconsistent or interleaved.

2. "important_notes": A list of all major messages, administrative updates, reminders, behavior or health-related notes, test/quiz info, deadlines, or parent instructions not tied to a subject. Include:
   - Field trip notices
   - Testing dates
   - Classroom policies
   - Absence policies
   - Materials needed
   - Special events
   - PowerSchool or grade-related updates
   - Teacher personal messages to parents

-----------------------
📋 OUTPUT RULES
-----------------------

✅ Output must be a **raw valid JSON object**. No markdown, no triple backticks, no explanations — just clean JSON.
✅ The JSON must be parsable by Python's `json.loads()`.
✅ Normalize subject names with the first letter capitalized.
✅ If no items exist in a section, return it as an empty dictionary or list.

-----------------------
✍️ INPUT TEXT:
-----------------------

{text}
"""

class OpenAIProcessor:
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def extract_topics(self, text: str, api_key: str = None) -> dict:
        import textwrap
        chunk_size = 5000
        text_chunks = textwrap.wrap(text, chunk_size, break_long_words=False, replace_whitespace=False)
        aggregated_subjects = {}
        aggregated_notes = set()

        for chunk in text_chunks:
            response = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that returns structured syllabus and notes in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": multi_shot_prompt.format(text=chunk)
                    }
                ],
                model="gpt-4o",
                temperature=0.3
            )
            parsed = json.loads(response.choices[0].message.content)
            subjects = parsed.get("subjects", {})
            for subj, topics in subjects.items():
                if subj not in aggregated_subjects:
                    aggregated_subjects[subj] = set()
                aggregated_subjects[subj].update(topics)
            for note in parsed.get("important_notes", []):
                aggregated_notes.add(json.dumps(note) if isinstance(note, dict) else str(note))

        # Convert sets back to lists
        final_subjects = {k: list(v) for k, v in aggregated_subjects.items()}
        final_notes = list(aggregated_notes)

        return {
            "subjects": final_subjects,
            "important_notes": final_notes
        }