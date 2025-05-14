import json
from openai import OpenAI
from app.utils.logger import logger
from app.utils.load_secets import OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)


educational_multi_shot_prompt = """
You are an expert educational content generator for CMS (Charlotte-Mecklenburg Schools). Given a subject and topic text, extract and organize learning material into a strict JSON structure with clarity for students and educators. Ensure that all topics mentioned in the input are covered comprehensively.

-----------------------
📋 OUTPUT FORMAT (JSON)
-----------------------

{{
  "subject_name": "<Subject>",
  "topic_name": "<Reworded concise topic name>",
  "section_1_is_table": true | false,
  "section_1_name": "Reading Material",
  "section_1_content": {{
    "current_grade": "...", 
    "next_grade": "..."
  }} OR [
    {{"name": "...", "meaning": "...", "example": "..."}},
    ...
  ],
  "section_2_is_table": true | false,
  "section_2_name": "Real World Examples",
  "section_2_content": {{
    "current_grade": "...", 
    "next_grade": "..."
  }} OR [
    {{"name": "...", "meaning": "...", "example": "..."}},
    ...
  ],
  "section_3_is_table": false,
  "section_3_name": "Quizzes",
  "section_3_content": {{
    "current_grade": [
      {{"question": "...", "answer": "..."}},
      ...
    ],
    "next_grade": [
      {{"question": "...", "answer": "..."}},
      ...
    ]
  }}
}}

-----------------------
OUTPUT INSTRUCTIONS

- Output must be a raw JSON object.
- Do not use markdown formatting. Do not wrap the response in triple backticks or any other symbols.
- Only return the JSON object. Do not include explanations, comments, or extra text.
- Ensure the JSON is directly parsable by Python's json.loads().
- Derive subject and topic more clearly from the context.
- Use general category names like "Basic Algebra" as subject names.
- Use concise descriptors like "Understanding Variables and Expressions" as topic names.
- Normalize subject names with the first letter capitalized.
-----------------------
📌 SPECIAL RULES
-----------------------

1. If the topic relates to vocabulary or grammar keywords, then:
   - section_1_is_table = true
   - section_2_is_table = true
   - section_3_is_table = false
   - Generate table entries for name, meaning, and example. Use definitions from the input if present, otherwise generate.

2. If not vocabulary/grammar-related:
   - Provide clear written paragraphs for section_1_content and section_2_content for the current grade and next grade with very precisely exhaustive list of materials for the students, examples, and quizes which will cover all the scenarios

3. Section_3 should always include quiz questions and answers for both current and next grade levels.
4. If identified multiple subjects or Topic Name for the same subject or different subject extract the content as a seperate JSON content and embedded as multiple JSON Objects
5. Always ensure the "subject_name" and "topic_name" fields are uniquely defined. Use category-level names like "Basic Algebra" instead of vague or redundant names (e.g., prefer "Basic Algebra" over "Math: Variables and Expressions"). Use "Understanding Variables and Expressions" for topic_name if the input discusses those ideas. Ensure the names are reusable for grouping.

6. You must extract and generate educational content for all relevant topics from the input text without skipping any part. Ensure comprehensive study material coverage for every topic, including detailed reading material, real-world examples, and quizzes where appropriate.

7. If the input contains a topic or multiple topics, extract and generate topic-specific educational material for each one.

8. If the input is already written as reading material, use it as-is for "section_1_content" and supplement with additional material.

9. If the reading material contains links (e.g., to PDFs, videos), retain those links exactly and add them to the appropriate section without modification.

10. If the input is reading material, intelligently infer and populate the "subject_name" and "topic_name" fields based on the context.

11. If the input includes vocabulary content or tables, preserve the vocabulary data exactly and return it in structured JSON format, ensuring nothing is omitted.
-----------------------
✍️ INPUT
-----------------------

Topic Description: {{text}}
Grade: {{grade}}

Also, intelligently identify the subject name based on the topic content and include it as "subject_name" in the JSON.

If the input contains multiple topics or multiple subjects, split and generate a separate JSON object for each topic.

If the input is not relevant to any academic or educational learning topic, return an empty JSON object like this: {{}} and take no further action.

Always return one or more top-level JSON objects. No lists or extra wrapping.

Each object MUST include a boolean key "is_educational" to clearly indicate whether the topic is educationally relevant.
If it is not, set "is_educational": false and return the object with no additional content fields.
"""

class OpenAIProcessor:

    def generate_educational_content(self, text: str, grade: str) -> list:
        logger.info("Generating educational content for topic preview: %s", text[:50])
        prompt = educational_multi_shot_prompt.format(text=text, grade=grade)
        response_content = self._build_completion(prompt)
        return self._parse_json_response(response_content, fallback_topic=text)

    def _build_completion(self, prompt: str) -> str:
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a CMS-aligned assistant that returns educational content in strict JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="gpt-4o",
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error("OpenAI completion failed: %s", e)
            return ""

    def _parse_json_response(self, content: str, fallback_topic: str = "") -> list:
        results = []
        try:
            json_blocks = content.split("\n}\n{")
            for i, block in enumerate(json_blocks):
                if not block.strip().startswith("{"):
                    block = "{" + block
                if not block.strip().endswith("}"):
                    block = block + "}"
                parsed = json.loads(block)
                if parsed.get("is_educational", False):
                    logger.info("Parsed JSON with topic: %s", parsed.get("topic_name", fallback_topic[:30]))
                    results.append(parsed)
                else:
                    logger.info("Skipped non-educational block #%d", i + 1)
        except Exception as e:
            logger.error("Failed to parse multiple JSON responses: %s", e)

        return results