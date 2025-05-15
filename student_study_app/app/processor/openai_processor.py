import json
from openai import OpenAI
from app.utils.logger import logger
from app.utils.load_secets import OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)


educational_multi_shot_prompt = """
You are an expert educational content generator for CMS (Charlotte-Mecklenburg Schools). Given a JSON input with content, grade, author, and date, extract and organize learning material into a strict JSON structure with clarity for students and educators. Ensure that all topics mentioned in the input are covered comprehensively.

-----------------------
📋 OUTPUT FORMAT (JSON)
-----------------------

{{
  "subject_name": "<Subject Name>",
  "teacher_name": "<Teacher Name or 'Class Teacher'>",
  "date": "<Date in YYYY-MM-DD format or blank>",
  "topics": [
    {{
      "topic_name": "<Reworded concise topic name>",
      "section_1_is_table": true | false,
      "section_1_name": "Reading Material",
      "section_1_content": "Detailed study material in multiple paragraphs covering all relevant aspects of the topic.",
      "section_2_is_table": true | false,
      "section_2_name": "Real World Examples",
      "section_2_content": "At least five meaningful real-world examples that illustrate the topic.",
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
  ],
  "is_educational": true
}}

-----------------------
OUTPUT INSTRUCTIONS

- Output must be a raw JSON object.
- Do not use markdown formatting. Do not wrap the response in triple backticks or any other symbols.
- Only return the JSON object. Do not include explanations, comments, or extra text.
- Ensure the JSON is directly parsable by Python's json.loads().
- Derive subject and topic more clearly from the context.
- Use unique subject names like "Understanding Variable" as subject names.
- Use concise descriptors like "Understanding Variables and Expressions" as topic names.
- Normalize subject names with the first letter capitalized.
- Include teacher name from input or use "Class Teacher" if missing.
- Include date from input or leave blank if missing.
- Nest multiple topics under the "topics" array within the subject object.
- If multiple subjects are present, return multiple top-level JSON objects, one per subject.
- Preserve vocabulary entries or links exactly.
-----------------------
📌 SPECIAL RULES
-----------------------

1. Ignore non-educational content completely. If no learning content is found, return a single object with {{"is_educational": false}} and nothing else.

2. For educational content:
   - Identify the subject based on topic and assign a unique subject name (e.g., "Understanding Variable", not "Understanding Variables and Expressions").
   - If multiple topics are found within a subject, return a separate topic block for each under the same subject.

3. Each JSON block should follow this nested format:

{{
  "subject_name": "<Subject Name>",
  "teacher_name": "<Teacher Name or 'Class Teacher'>",
  "date": "<Date in YYYY-MM-DD format or blank>",
  "topics": [
    {{
      "topic_name": "...",
      "section_1_is_table": true | false,
      "section_1_name": "Reading Material",
      "section_1_content": "Detailed study material in multiple paragraphs covering all relevant aspects of the topic.",
      "section_2_is_table": true | false,
      "section_2_name": "Real World Examples",
      "section_2_content": "At least five meaningful real-world examples that illustrate the topic.",
      "section_3_is_table": false,
      "section_3_name": "Quizzes",
      "section_3_content": {{
        "current_grade": [...],
        "next_grade": [...]
      }}
    }}
  ],
  "is_educational": true
}}

4. Preserve vocabulary entries or links exactly. If the content has a vocabulary list, return it in table format under appropriate section content.

5. If the input contains multiple subjects or multiple topic groups, return multiple top-level JSON objects—one per subject.

6. Always return only JSON objects. No markdown, no explanation, no extra symbols or arrays wrapping JSON blocks.
-----------------------
✍️ INPUT
-----------------------

Input JSON:
{{
  "content": {{text}},
  "grade": {{grade}},
  "author": "Teacher name here",
  "date": "2025-05-14"
}}

-----------------------
📚 EXAMPLES
-----------------------

✅ Example Input: Reading Practice
{{
  "content": "If you are looking for a way to support your child at home with EOG style questions and passages I have a great resource for you! Go to readtheory.org...",
  "grade": "3rd Grade",
  "author": "Rebecca Anastos",
  "date": "2025-05-09"
}}

✅ Output:
{{
  "subject_name": "Reading Comprehension",
  "teacher_name": "Rebecca Anastos",
  "date": "2025-05-09",
  "topics": [
    {{
      "topic_name": "Improving Reading Stamina",
      "section_1_is_table": false,
      "section_1_name": "Reading Material",
      "section_1_content": "Practice reading short passages daily with a focus on identifying main ideas and supporting details. Explore longer passages with multi-step inference questions, and practice note-taking strategies.",
      "section_2_is_table": false,
      "section_2_name": "Real World Examples",
      "section_2_content": "Use newspaper articles to practice summarizing. Compare main ideas across multiple news stories. Read book reviews to understand opinions. Analyze advertisements for persuasive language. Discuss news reports in class.",
      "section_3_is_table": false,
      "section_3_name": "Quizzes",
      "section_3_content": {{
        "current_grade": [
          {{"question": "What is the main idea of a paragraph?", "answer": "It tells what the paragraph is mostly about."}}
        ],
        "next_grade": [
          {{"question": "What strategy helps locate key details?", "answer": "Underline supporting sentences in the passage."}}
        ]
      }}
    }}
  ],
  "is_educational": true
}}

✅ Example Input: Vocabulary
{{
  "content": "ideal-something that is perfect, advertise-to give info, secluded-a place that is quiet...",
  "grade": "3rd Grade",
  "author": "Rebecca Anastos",
  "date": "2025-05-08"
}}

✅ Output:
{{
  "subject_name": "Vocabulary Development",
  "teacher_name": "Rebecca Anastos",
  "date": "2025-05-08",
  "topics": [
    {{
      "topic_name": "Vocabulary Word List",
      "section_1_is_table": true,
      "section_1_name": "Reading Material",
      "section_1_content": [
        {{"name": "ideal", "meaning": "something that is perfect", "example": "This vacation is ideal for relaxing."}},
        {{"name": "secluded", "meaning": "quiet and out of sight", "example": "The cabin was in a secluded area."}}
      ],
      "section_2_is_table": true,
      "section_2_name": "Real World Examples",
      "section_2_content": [
        {{"name": "advertise", "meaning": "announce or promote", "example": "They advertise shoes on TV."}},
        {{"name": "promote", "meaning": "support or encourage", "example": "Schools promote reading every day."}},
        {{"name": "market", "meaning": "to sell or trade", "example": "Farmers market fresh produce."}},
        {{"name": "brand", "meaning": "a type of product made by a company", "example": "Nike is a popular brand."}},
        {{"name": "campaign", "meaning": "a planned series of actions", "example": "The campaign raised awareness."}}
      ],
      "section_3_is_table": false,
      "section_3_name": "Quizzes",
      "section_3_content": {{
        "current_grade": [
          {{"question": "What does 'jovial' mean?", "answer": "Always laughing and in a good mood"}}
        ],
        "next_grade": []
      }}
    }}
  ],
  "is_educational": true
}}
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
                    logger.info("Parsed JSON with topic: %s", parsed.get("topics", [{"topic_name": fallback_topic[:30]}])[0].get("topic_name", fallback_topic[:30]))
                    results.append(parsed)
                else:
                    logger.info("Skipped non-educational block #%d", i + 1)
        except Exception as e:
            logger.error("Failed to parse multiple JSON responses: %s", e)

        return results