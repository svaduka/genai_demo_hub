import json
from openai import OpenAI
from app.utils.logger import logger
from app.utils.load_secets import OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)

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
OUTPUT INSTRUCTIONS

- Output must be a raw JSON object.
- Do not use markdown formatting. Do not wrap the response in triple backticks or any other symbols.
- Only return the JSON object. Do not include explanations, comments, or extra text.
- Ensure the JSON is directly parsable by Python's json.loads().
- Normalize subject names with the first letter capitalized.
- If no items exist in a section, return it as an empty dictionary or list.
-----------------------
✍️ INPUT TEXT:
-----------------------

{text}
"""

steam_multi_shot_prompt = """
You are an expert educational content generator working for CMS (Charlotte-Mecklenburg Schools). Given a paragraph or topic description, your job is to identify if it's educational, and produce very detailed structured material for instructional use.

Your output must include comprehensive student material suitable for 3rd to 5th graders, diverse real-world examples including edge-case scenarios, multi-level quizzes (basic, intermediate, challenge) with explanations, and thorough coverage of the topic including edge cases in both explanation and examples.

-----------------------
✅ OUTPUT GUIDELINES
-----------------------

- Output must be a raw JSON object.
- Do not use markdown formatting. Do not wrap the response in triple backticks or any other symbols.
- Only return the JSON object. Do not include explanations, comments, or extra text.
- Ensure the JSON is directly parsable by Python's json.loads().

Return the following structure:

{{
  "is_educational": true,
  "domain": "Science" | "Technology" | "Engineering" | "Arts" | "Math" | "Social Studies" | "Health" | "General",
  "student_friendly_explanation": "Very detailed explanation suitable for 3rd to 5th graders",
  "reading_material": "Long-form material that explains the topic from first principles, with diagrams (describe them), definitions, and use cases",
  "real_world_examples": ["diverse and edge-case scenarios"],
  "quiz": [
    {{
      "level": "basic" | "intermediate" | "challenge",
      "question": "string",
      "answer": "string",
      "explanation": "Explain why the answer is correct"
    }}
  ],
  "youtube_links": ["https://youtube.com/...", "..."],
  "image_ideas": ["description of image 1", "description of image 2"]
}}

If it is NOT educational in nature, return:

{{
  "is_educational": false,
  "topic": "Concise topic title or label",
  "message_summary": "Brief summary of the main message",
  "intended_audience": "Students" | "Parents" | "Teachers" | "General",
  "action_items": ["action step 1", "action step 2"]
}}

-----------------------
✍️ INPUT TEXT:
-----------------------

{text}
"""

class OpenAIProcessor:

    def generate_steam_content(self, text: str) -> str:
        logger.info("Generating educational content for topic input")
        prompt = steam_multi_shot_prompt.format(text=text)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a CMS-aligned assistant that creates structured STEAM learning materials."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="gpt-4o",
            temperature=0.5
        )
        try:
            content = response.choices[0].message.content.strip()
            json_preview = json.loads(content)
            logger.info(f"Received content for domain: {json_preview.get('domain', 'Unknown')}")
        except Exception as e:
            logger.warning(f"Failed to parse JSON or extract domain: {e}")
        return response.choices[0].message.content.strip()

    def extract_topics(self, text: str) -> dict:
        import textwrap
        chunk_size = 5000
        text_chunks = textwrap.wrap(text, chunk_size, break_long_words=False, replace_whitespace=False)
        logger.info(f"Processing {len(text_chunks)} chunk(s) of input text")
        aggregated_subjects = {}
        aggregated_notes = set()

        for chunk in text_chunks:
            response = client.chat.completions.create(
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
            logger.debug(f"Parsed subjects: {list(subjects.keys())}")
            for subj, topics in subjects.items():
                if subj not in aggregated_subjects:
                    aggregated_subjects[subj] = set()
                aggregated_subjects[subj].update(topics)
            for note in parsed.get("important_notes", []):
                aggregated_notes.add(json.dumps(note) if isinstance(note, dict) else str(note))

        # Convert sets back to lists
        final_subjects = {k: list(v) for k, v in aggregated_subjects.items()}
        final_notes = list(aggregated_notes)

        logger.info(f"Extracted {len(final_subjects)} subject(s) and {len(final_notes)} note(s)")
        return {
            "subjects": final_subjects,
            "important_notes": final_notes
        }