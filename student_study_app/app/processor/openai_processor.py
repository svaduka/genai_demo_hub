import json
import logging
from openai import OpenAI
from app.utils.logger import log_msg
from app.utils.load_secets import OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)

educational_multi_shot_prompt = """
You are a CMS educational assistant. Given a list of feed JSON objects and a grade level, extract ONLY educational content and transform them into well-structured JSON output for the specified grade. Use the format and rules below to build rich and engaging learning content for students.

---

INPUT FORMAT (list of objects):

[
    {{
      "author": "string (e.g., 'Rebecca Anastos')",
      "subject": "string",
      "content": "string",
      "post_date": "ISO format datetime, e.g., '2025-05-08T15:00:00-04:00'"
    }},
    ...
]

A separate field `grade` will be provided as context (e.g., `"grade": "3"`). This defines the current grade of the student. You should write content that supports **both the given grade and next grade concepts** in a unified and student-friendly manner.

---

Your responsibilities:

1. Ignore any feeds that are not educational (e.g., announcements about donations, celebrations, hats, countdowns).
2. For each valid feed:
   - Set `subject_name` based on the feed topic (e.g., "Math Concepts", "Vocabulary Development"), Subject Name should be precise.
   - Group all educational feeds under their corresponding subject using `subject_name`. If multiple feeds share the same subject (e.g., math topics like 'Area', 'Fractions', 'Elapsed Time'), they must be merged under a single `subject_name` with multiple `topic` entries.
   - For each feed, create one or more `topic` blocks depending on the number of unique instructional areas it covers.
   - If a single feed includes multiple instructional concepts within the same subject (e.g., 'Area, Perimeter, and Fractions'), split them into separate `topic` blocks such as 'Area', 'Perimeter', and 'Fractions'.
   - Each topic must have its own reading material, real world examples, and quizzes.
   - Final output should organize all related topics under a shared `subject_name`.
   - Create one or more `topic` blocks based on themes found in the content or group multiple feeds if they belong to same subject.
   - If a feed includes multiple topics in a single subject (e.g., 'Area, Perimeter, and Fractions'), split it into distinct topic blocks such as 'Area', 'Perimeter', and 'Fractions'. Each topic must have its own reading material, examples, and quizzes. Group them under a shared subject_name.
   - For vocabulary: use `section_1_is_table: true`, with entries that include:
     - `name` (vocabulary word)
     - `meaning` (child-friendly definition)
     - `example` (clear usage example)
   - For concept/lesson-based feeds:
     - Set `section_1_is_table: false`
     - Write **age-appropriate reading material** follow below approach
        -- When it comes to deriving material for edge cases, it's important to create content that is tailored for both the current grade level and the next grade. Here's a step-by-step approach:
        -- **Identify the Grade Levels**: Start by defining the current grade and the next grade. Understanding the curriculum requirements for each grade helps in crafting appropriate material.
        -- **Focus on Key Concepts**: For both grades, identify key concepts that students should grasp. Create a list that includes not only foundational material for the current grade but also introduces advanced concepts relevant to the next grade level.
        -- **Create Detailed Explanations**: Develop comprehensive paragraphs that thoroughly explain each concept. Use examples that relate directly to students' experiences to ensure better understanding. For instance, if discussing fractions, show real-life applications like sharing pizza.
        -- **Include Edge Cases**: Delve into edge case scenarios that help illustrate nuances in the concepts. These might include exceptions to rules, such as how fractions can be part of a larger whole, which might not be explicitly stated in standard curriculums.
        -- **Progressive Learning**: Make sure the content transitions smoothly from the current grade concepts to the next grade material. This can involve introducing more complex problems as practice after the basic concepts have been mastered.
        -- **Use Clear Language**: Maintain easy-to-understand language throughout. Avoid jargon unless it's defined in a straightforward manner, ensuring students at both levels can follow along with confidence.
        -- **Incorporate Questions and Activities**: Add practice questions and interactive activities that challenge students to apply their knowledge. This will reinforce learning and prepare them for the next grade’s expectations.
        By integrating these elements, you'll be able to derive edge case material that is both detailed and beneficial for students, catering effectively to both their current and future academic needs. 
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
    {{
        "subject_name": "Derived subject name",
        "teacher_name": "From input or 'Class Teacher'",
        "date": "YYYY-MM-DD or blank",
        "topics": [
            {{
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
                    {{"question": "string", "answer": "string" }},
                    ...
                ]
            }}
        ],
        "is_educational": true
    }},
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
7. Ouput should not include the input related information

IMPORTANT: 
- Output must be only a valid JSON array or JSON object.
- Do NOT wrap the output in triple backticks or label it with json.
- Do NOT return any markdown formatting or instructional commentary.
- Just emit raw, parsable JSON as response content. 

---

EXAMPLES

INPUT:

{{
    "feeds": [
    {{
      "author": "Rebecca Anastos",
    "subject": "IMPORTANT- Thursday Folders- Scores",
    "content": "Hello 3rd grade families,Happy Friday Eve! \u00a0Wanted to let you know about some things coming home in Communication Folders today:A packet that contains:Ayellow paperwith the EOY benchmark test scores (for iReady and MVPA) and the correlating EOG score predictions based on these scoresiReady score reportThe work paper your child used during the tests (if the paper is blank or there are no work papers attached, it means your child didn't use the paper to show work)A reflection sheet or card with a \"glow\" (something they were proud of or felt really confident about on the test) and a \"grow\" (something they want to work on or something they wish they knew more about for the actual EOG)Please review andsign and returnthe yellow paper; however, you may want to take a picture of the back of the yellow paper for ideas on how to help your child grow their skills at home.Have a wonderful rest of your day! \u00a0So close to the weekend!-Mrs. A",
    "post_date": "2025-05-08T14:48:03-04:00"
  }},
        {{
          "author": "Rebecca Anastos",
            "subject": "Vocabulary",
            "content": "Today's essential vocabulary words include 'ideal', 'advertise', 'secluded', 'jovial', 'queasy', and 'loaf'. Understanding these words will help enhance your communication skills.",
            "post_date": "2025-05-08T15:00:00-04:00"
        }},
        {{
          "author": "Ellen Stenzler Whitford",
            "subject": "Math",
            "content": "In this lesson, we will explore 'Area', 'Perimeter', and 'Fractions'. Understanding these concepts is crucial for solving problems and making connections to real-world scenarios.",
            "post_date": "2025-05-11T10:00:00-04:00"
        }}
    ],
    "grade": "3"
}}

EXPECTED OUTPUT:

[
    {{
        "subject_name": "Vocabulary Development",
        "teacher_name": "Rebecca Anastos",
        "date": "2025-05-08",
        "topics": [
            {{
                "topic_name": "Essential Vocabulary Words",
                "section_1_is_table": true,
                "section_1_name": "Reading Material",
                "section_1_content": [
                    {{ "name": "ideal", "meaning": "something that is perfect", "example": "This vacation is ideal for relaxing." }},
                    {{ "name": "advertise", "meaning": "to announce or promote", "example": "They advertise toys on TV." }},
                    {{ "name": "secluded", "meaning": "quiet and away from others", "example": "The cabin was in a secluded forest." }},
                    {{ "name": "jovial", "meaning": "always in a good mood and laughing", "example": "He is jovial and friendly to everyone." }},
                    {{ "name": "queasy", "meaning": "feeling sick to your stomach", "example": "She felt queasy on the bus." }},
                    {{ "name": "loaf", "meaning": "to spend time relaxing and doing nothing", "example": "I like to loaf around on Sundays." }}
                ],
                "section_2_is_table": false,
                "section_2_name": "Real World Examples",
                "section_2_content": "1. Using 'ideal' to describe weather for a picnic.\n2. Seeing advertisements on YouTube or billboards.\n3. Visiting a quiet, secluded cabin.\n4. Talking with jovial classmates.\n5. Feeling queasy after a roller coaster.\n6. Loafing on the couch after school.",
                "section_3_is_table": false,
                "section_3_name": "Quizzes",
                "section_3_content": [
                    {{ "question": "What does 'secluded' mean?", "answer": "A place that is quiet and private" }},
                    {{ "question": "What does 'jovial' describe?", "answer": "Someone who is always cheerful" }},
                    {{ "question": "What happens when you 'advertise'?", "answer": "You promote or announce something" }},
                    {{ "question": "Use 'queasy' in a sentence.", "answer": "I felt queasy before the test" }},
                    {{ "question": "What is the meaning of 'loaf'?", "answer": "To relax or do nothing" }}
                ]
            }}
        ],
        "is_educational": true
    }},
    {{
        "subject_name": "Math Concepts",
        "teacher_name": "Ellen Stenzler Whitford",
        "date": "2025-05-11",
        "topics": [
            {{
                "topic_name": "Area",
                "section_1_is_table": false,
                "section_1_name": "Reading Material",
                "section_1_content": "Very detailed material , more than this example Area is the space inside a shape. To find the area of a rectangle, multiply its length by its width. Understanding area helps in solving real-world problems like determining how much carpet is needed for a room.",
                "section_2_is_table": false,
                "section_2_name": "Real World Examples",
                "section_2_content": "1. Calculating the area of a garden to determine how many plants can fit.\n2. Measuring the area of a wall to know how much paint is needed.\n3. Finding the area of a tablecloth to cover a dining table.\n4. Determining the area of a playground.\n5. Calculating the area of a parking lot to plan the number of cars it can hold.",
                "section_3_is_table": false,
                "section_3_name": "Quizzes",
                "section_3_content": [
                    {{ "question": "How do you calculate the area of a rectangle?", "answer": "Multiply the length by the width" }},
                    {{ "question": "If a room is 5 meters long and 4 meters wide, what is its area?", "answer": "20 square meters" }},
                    {{ "question": "What is the area of a square with sides of 3 meters?", "answer": "9 square meters" }},
                    {{ "question": "Why is knowing the area important?", "answer": "It helps in planning and using space efficiently" }},
                    {{ "question": "How can you find the area of a triangle?", "answer": "Multiply the base by the height and divide by 2" }}
                ]
            }},
            {{
                "topic_name": "Perimeter",
                "section_1_is_table": false,
                "section_1_name": "Reading Material",
                "section_1_content": "Very detailed material , more than this example  Perimeter is the total distance around a shape. To find the perimeter of a rectangle, add up the lengths of all its sides. Knowing perimeter is useful for tasks like fencing a yard.",
                "section_2_is_table": false,
                "section_2_name": "Real World Examples",
                "section_2_content": "1. Calculating the perimeter of a garden to buy enough fencing.\n2. Measuring the perimeter of a picture frame.\n3. Determining the perimeter of a sports field.\n4. Finding the perimeter of a swimming pool.\n5. Measuring the perimeter of a room to install baseboards.",
                "section_3_is_table": false,
                "section_3_name": "Quizzes",
                "section_3_content": [
                    {{ "question": "How do you find the perimeter of a rectangle?", "answer": "Add the lengths of all four sides" }},
                    {{ "question": "What is the perimeter of a square with sides of 5 meters?", "answer": "20 meters" }},
                    {{ "question": "If a rectangle has sides of 6 meters and 4 meters, what is its perimeter?", "answer": "20 meters" }},
                    {{ "question": "Why is knowing the perimeter important?", "answer": "It helps in calculating the boundary length for enclosing spaces" }},
                    {{ "question": "How can you find the perimeter of a triangle?", "answer": "Add the lengths of all three sides" }}
                ]
            }},
            {{
                "topic_name": "Fractions",
                "section_1_is_table": false,
                "section_1_name": "Reading Material",
                "section_1_content": "Very detailed material , more than this example  Fractions represent parts of a whole. Understanding fractions is important for dividing things into equal parts and comparing sizes. For example, 1/2 is the same as 2/4.",
                "section_2_is_table": false,
                "section_2_name": "Real World Examples",
                "section_2_content": "1. Splitting a pizza into equal slices.\n2. Measuring ingredients for a recipe.\n3. Dividing a candy bar among friends.\n4. Comparing the sizes of different pieces of pie.\n5. Understanding half-time in sports.",
                "section_3_is_table": false,
                "section_3_name": "Quizzes",
                "section_3_content": [
                    {{ "question": "What is 1/2 equivalent to?", "answer": "2/4" }},
                    {{ "question": "How can you represent 3/4 on a number line?", "answer": "Divide a line into 4 equal parts and mark 3 parts" }},
                    {{ "question": "What fraction of a pizza is left if you eat 3 out of 8 slices?", "answer": "5/8" }},
                    {{ "question": "Why are fractions useful?", "answer": "They help in dividing things into equal parts and making comparisons" }},
                    {{ "question": "How can you add 1/4 and 2/4?", "answer": "By adding the numerators: 1 + 2 = 3/4" }}
                ]
            }}
        ],
        "is_educational": true
    }}
]

-----------------------
✍️ INPUT
-----------------------
{{
  "feeds": {feeds},
  "grade": {grade}
}}
"""

class OpenAIProcessor:

    def generate_educational_content(self, text: str, grade: str) -> list:
        log_msg(f"Generating educational content")
        prompt = educational_multi_shot_prompt.format(feeds=text, grade=grade)
        # log_msg(f"Prompt {prompt}")
        response_content = self._build_completion(prompt)
        log_msg(f"Response content : {response_content}")
        return self._parse_json_response(response_content, fallback_topic=text)

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
                model="gpt-4o",
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