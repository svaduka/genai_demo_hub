import json
import logging
from openai import OpenAI
from app.utils.logger import log_msg
from app.utils.load_secets import OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)

educational_multi_shot_prompt = f"""
You are a CMS educational assistant. Given a list of feed JSON objects and a grade level, extract ONLY educational content and transform them into well-structured JSON output for the specified grade. Use the format and rules below to build rich and engaging learning content for students.

---

INPUT FORMAT (list of objects):

[
    {{{{
        "author": "string (e.g., 'Rebecca Anastos')",
        "subject": "string",
        "content": "string",
        "post_date": "ISO format datetime, e.g., '2025-05-08T15:00:00-04:00'"
    }}}},
    ...
]

A separate field `grade` will be provided as context (e.g., `"grade": "3"`). This defines the current grade of the student. You should write content that supports **both the given grade and next grade concepts** in a unified and student-friendly manner.

---

Your responsibilities:

1. Ignore any feeds that are not educational (e.g., announcements about donations, celebrations, hats, countdowns).
2. For each valid feed:
   - Set `subject_name` based on the feed topic (e.g., "Math Concepts", "Vocabulary Development"), Subject Name should be precise.
   - Create one or more `topic` blocks based on themes found in the content or group multiple feeds if they belong to same subject.
   - For vocabulary: use `section_1_is_table: true`, with entries that include:
     - `name` (vocabulary word)
     - `meaning` (child-friendly definition)
     - `example` (clear usage example)
   - For concept/lesson-based feeds:
     - Set `section_1_is_table: false`
     - Write **age-appropriate reading material** in paragraph form
     - Expand explanations with both current and next grade insights
     - Always generate at least 5 real-world examples
     - Generate at least 5–10 quizzes as `question/answer` pairs
3. Use `post_date` to extract the `date` field in `"YYYY-MM-DD"` format
4. If `author` is missing, use `"Class Teacher"` as the fallback
5. If no `post_date`, set `date` to an empty string
6. The quizzes (`section_3_content`) must be returned as a **flat array of objects**
7. Ensure the final output is **strict JSON only** – no markdown, no comments, no explanation

---

OUTPUT FORMAT:

[
    {{{{
        "subject_name": "Derived subject name",
        "teacher_name": "From input or 'Class Teacher'",
        "date": "YYYY-MM-DD or blank",
        "topics": [
            {{{{
                "topic_name": "Short topic title",
                "section_1_is_table": true | false,
                "section_1_name": "Reading Material",
                "section_1_content": "...string or array of objects...",
                "section_2_is_table": false,
                "section_2_name": "Real World Examples",
                "section_2_content": "...string with 5+ enumerated examples...",
                "section_3_is_table": false,
                "section_3_name": "Quizzes",
                "section_3_content": [
                    {{{{ "question": "string", "answer": "string" }}}},
                    ...
                ]
            }}}}
        ],
        "is_educational": true
    }}}},
    ...
]

For non-educational feeds, ignore feed

---

=========================
🧠 OUTPUT RULES
=========================

1. Always return a perfect JSON, no addition pre or post text. No text, markdown, or explanation.
2. Use structured format strictly. It must work with Python’s `json.loads()`.
3. Generate `section_1_content` and `section_2_content` as arrays only if `section_1_is_table` or `section_2_is_table` is true.
4. Include at least 5 real-world examples in section 2 for valid educational topics.
5. Vocabulary content must be in table format with "name", "meaning", and "example".
6. Include both current and next grade quiz questions based on Bloom’s taxonomy (basic → application).

IMPORTANT: 
- Do not include any explanations, examples, or descriptions in the response.
- Output must be only a valid JSON array or JSON object.
- Do NOT wrap the output in triple backticks or label it with json.
- Do NOT return any markdown formatting or instructional commentary.
- Just emit raw, parsable JSON as response content. 

---

EXAMPLES

INPUT:

{{{{ 
  "grade": "3",
  "feeds": [{{{{feeds}}}}]
}}}}

EXPECTED OUTPUT:

[
  {{{{
    "subject_name": "Math Concepts",
    "teacher_name": "Ellen Stenzler Whitford",
    "date": "2025-05-11",
    "topics": [
      {{{{
        "topic_name": "Area, Perimeter, and Fractions",
        "section_1_is_table": false,
        "section_1_name": "Reading Material",
        "section_1_content": "This topic covers area and perimeter calculations, the distributive property for arrays, time calculations, and understanding equivalent fractions. Area refers to the space inside a shape (calculated as length × width), while perimeter is the total distance around the shape (sum of all sides). The distributive property helps break multiplication into parts. Time skills include reading analog clocks and calculating elapsed time. Students also study fractions with visual models and number lines, including benchmarks like 1/2 = 2/4 = 4/8. These skills are essential for both current and higher-level math thinking.",
        "section_2_is_table": false,
        "section_2_name": "Real World Examples",
        "section_2_content": "1. Measuring tiles to find how much area covers a kitchen floor.\n2. Calculating the amount of fencing for a backyard.\n3. Splitting a chocolate bar into equal parts to represent fractions.\n4. Determining time passed from 9:15 to 10:00 AM.\n5. Understanding why 2/4 of a pizza equals 1/2.\n6. Breaking 7 × 6 into (7×3) + (7×3) using the distributive property.\n7. Finding the area of a school desk.\n8. Drawing fractions on a number line.\n9. Using clocks to find how long a movie lasted.\n10. Estimating classroom perimeter using foot-long rulers.",
        "section_3_is_table": false,
        "section_3_name": "Quizzes",
        "section_3_content": [
          {{{{ "question": "How do you calculate the area of a rectangle?", "answer": "Multiply the length by the width" }}}},
          {{{{ "question": "What is the perimeter of a shape with sides 5, 3, 5, 3?", "answer": "5 + 3 + 5 + 3 = 16" }}}},
          {{{{ "question": "What is the distributive form of 6 × 7?", "answer": "(6 × 3) + (6 × 4)" }}}},
          {{{{ "question": "If a clock shows 1:30 and class ends at 2:15, how long is left?", "answer": "45 minutes" }}}},
          {{{{ "question": "What is an equivalent of 2/4?", "answer": "1/2" }}}},
          {{{{ "question": "How can you show 3/6 on a number line?", "answer": "Mark 3 points out of 6 equal sections between 0 and 1" }}}},
          {{{{ "question": "What does 'elapsed time' mean?", "answer": "The amount of time that has passed between two moments" }}}},
          {{{{ "question": "What is the area of a 4 × 6 rectangle?", "answer": "24 square units" }}}}
        ]
      }}}}
    ],
    "is_educational": true
  }}}},
  {{{{
    "subject_name": "Vocabulary Development",
    "teacher_name": "Rebecca Anastos",
    "date": "2025-05-08",
    "topics": [
      {{{{
        "topic_name": "Essential Vocabulary Words",
        "section_1_is_table": true,
        "section_1_name": "Reading Material",
        "section_1_content": [
          {{{{ "name": "ideal", "meaning": "something that is perfect", "example": "This vacation is ideal for relaxing." }}}},
          {{{{ "name": "advertise", "meaning": "to announce or promote", "example": "They advertise toys on TV." }}}},
          {{{{ "name": "secluded", "meaning": "quiet and away from others", "example": "The cabin was in a secluded forest." }}}},
          {{{{ "name": "jovial", "meaning": "always in a good mood and laughing", "example": "He is jovial and friendly to everyone." }}}},
          {{{{ "name": "queasy", "meaning": "feeling sick to your stomach", "example": "She felt queasy on the bus." }}}},
          {{{{ "name": "loaf", "meaning": "to spend time relaxing and doing nothing", "example": "I like to loaf around on Sundays." }}}},
          {{{{ "name": "interview", "meaning": "to ask questions to learn something", "example": "She interviewed the mayor for her project." }}}}
        ],
        "section_2_is_table": false,
        "section_2_name": "Real World Examples",
        "section_2_content": "1. Using 'ideal' to describe weather for a picnic.\n2. Seeing advertisements on YouTube or billboards.\n3. Visiting a quiet, secluded cabin.\n4. Talking with jovial classmates.\n5. Feeling queasy after a roller coaster.\n6. Loafing on the couch after school.\n7. Preparing for an interview with a school guest.",
        "section_3_is_table": false,
        "section_3_name": "Quizzes",
        "section_3_content": [
          {{{{ "question": "What does 'secluded' mean?", "answer": "A place that is quiet and private" }}}},
          {{{{ "question": "What does 'jovial' describe?", "answer": "Someone who is always cheerful" }}}},
          {{{{ "question": "What happens when you 'advertise'?", "answer": "You promote or announce something" }}}},
          {{{{ "question": "Use 'queasy' in a sentence.", "answer": "I felt queasy before the test" }}}},
          {{{{ "question": "What is the meaning of 'loaf'?", "answer": "To relax or do nothing" }}}},
          {{{{ "question": "How would you use 'ideal'?", "answer": "A sunny day is ideal for a hike" }}}}
        ]
      }}}}
    ],
    "is_educational": true
  }}}}
]

-----------------------
✍️ INPUT
-----------------------
{{{{ 
  "feeds": {{{{feeds}}}},
  "grade": {{{{grade}}}}
}}}}
"""

class OpenAIProcessor:

    def generate_educational_content(self, feeds: str, grade: str) -> list:
        log_msg(f"Generating educational content")
        prompt = educational_multi_shot_prompt.format(feeds=feeds, grade=grade)
        response_content = self._build_completion(prompt)
        log_msg(f"Response content : {response_content}")
        return self._parse_json_response(response_content, fallback_topic=feeds)

    def _build_completion(self, prompt: str) -> str:
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a CMS-aligned assistant that returns only valid raw JSON content. Never include markdown, explanations, code blocks, or commentary. Your only task is to parse the educational input and return valid JSON per the schema provided. The output must be directly parsable with Python's `json.loads()`. Do not wrap responses in ```json or use markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="gpt-4",
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            log_msg(f"OpenAI completion failed: {e}\n{tb}", level=logging.ERROR)
            return ""

    def _parse_json_response(self, content: str, fallback_topic: str = "") -> list:
        results = []
        try:
            parsed_json = json.loads(content)
            if isinstance(parsed_json, list):
                for i, block in enumerate(parsed_json):
                    if isinstance(block, dict):
                        if block.get("is_educational", False):
                            topic_name = (
                                block.get("topics", [{}])[0].get("topic_name", fallback_topic[:30])
                                if block.get("topics") else fallback_topic[:30]
                            )
                            log_msg(f"Parsed JSON with topic: {topic_name}")
                            results.append(block)
                        else:
                            log_msg(f"Skipped non-educational block #{i + 1}")
            elif isinstance(parsed_json, dict):
                if parsed_json.get("is_educational", False):
                    topic_name = (
                        parsed_json.get("topics", [{}])[0].get("topic_name", fallback_topic[:30])
                        if parsed_json.get("topics") else fallback_topic[:30]
                    )
                    log_msg(f"Parsed JSON with topic: {topic_name}")
                    results.append(parsed_json)
                else:
                    log_msg("Skipped non-educational block")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            log_msg(f"Failed to parse JSON response: {e}\n{tb}", level=logging.ERROR)

        return results