import json
import logging
from openai import OpenAI
from app.utils.logger import log_msg
from app.utils.load_secets import OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)

educational_multi_shot_prompt = """
You are an expert educational content generator for CMS (Charlotte-Mecklenburg Schools). 
Your task is to extract and generate structured educational content strictly in JSON format.

=========================
📥 INPUT STRUCTURE
=========================

You will be given a List of JSON input with the following fields 
{{
  "content": [{{
            "content": content of the topic or topic name details,
            "subject": This is derived from source but we cannot relay on this,
            "author": "Teacher name here",
            "date": "2025-05-14"
          }},
        {{
        "content": content of the topic or topic name details,
        "subject": This is derived from source but we cannot relay on this,
        "author": "Teacher name here",
        "date": "2025-05-14"
      }}],
      "grade": 3rd Grade
}}

-----------------------
✍️ INPUT
-----------------------
{{
  "content": {{text}},
  "grade": {{grade}}
}}

=========================
📤 OUTPUT FORMAT
=========================

You must return a **list of JSON objects** in the schema below for each input of content in the JSON input. The content in the input text consists of the list of JSONs, where each JSON represents a topic, material, or vocabulary content. 
- For each JSON, we need to generate the below JSON. If multiple JSONs correspond to the same subject, add the generated JSON to the list of topics.
- If it is material, we need to identify the subject (derived from the topic content), the topic name, and retain the section_1_content along with the material. In the quiz section, we need to generate the content.  
- If it is a topic, we need to generate both the topic and material, identify the subject (derived from the topic content), and include the material in the content section.  
-- If the input is vocabulary, we need to maintain the section_1_content with a table containing fields such as name, meaning, and example, and set section_1_table to true.


[{{
  "subject_name": "<Inferred subject name like 'Math Concepts'>",
  "teacher_name": "<From input or 'Class Teacher'>",
  "date": "<Same as input or blank>",
  "topics": [
    {{
      "topic_name": "<Concise and reworded topic>",
      "section_1_is_table": true | false,
      "section_1_name": "Reading Material",
      "section_1_content": "...or [...] if table",
      "section_2_is_table": true | false,
      "section_2_name": "Real World Examples",
      "section_2_content": "...or [...] if table",
      "section_3_is_table": false,
      "section_3_name": "Quizzes",
      "section_3_content": {{
        "current_grade": [{{"question": "...", "answer": "..."}}],
        "next_grade": [{{"question": "...", "answer": "..."}}]
      }}
    }}
  ],
  "is_educational": true
}}
]

If the input content is non-educational (announcements, donations, parties), return:
{{"is_educational": false}}

=========================
🧠 OUTPUT RULES
=========================

1. Always return a perfect JSON, no addition pre or post text. No text, markdown, or explanation.
2. Use structured format strictly. It must work with Python’s `json.loads()`.
3. Generate `section_1_content` and `section_2_content` as arrays only if `section_1_is_table` or `section_2_is_table` is true.
4. Include at least 5 real-world examples in section 2 for valid educational topics.
5. Vocabulary content must be in table format with "name", "meaning", and "example".
6. Include both current and next grade quiz questions based on Bloom’s taxonomy (basic → application).

=========================
📚 EXAMPLES
=========================

Example 1 – Vocabulary  
Input:
[{{
    "author": "Rebecca Anastos",
    "subject": "Vocabulary Words",
    "content": "\u200bBelow is a list of \u200bour current vocabulary words. We will take a quiz on these words next \u200bFriday, 5/16.ideal-something that is perfectadvertise-to give information or announce something is for salesecluded-a place that is quiet and out of sightqueasy-to feel sick to your stomachgleam-to shine or reflect a glow of lightharmony-working well with others, getting alongloaf-time spent relaxing, doing nothingobject-to disagreejovial-always laughing and in a good moodhardy-strong, able to survive in tough conditionsabbreviated-to write something in a shortened waytedious-boring or repetitivediminish-making smallerconvince-to persuade someone to think the way you dointerview-to ask someone questions",
    "post_date": "2025-05-08T15:00:00-04:00"
  }}
  ]

Output:
[{{
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
        {{"name": "advertise", "meaning": "announce or promote", "example": "They advertise toys on TV."}},
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
        "next_grade": [
          {{"question": "What is the difference between 'advertise' and 'promote'?", "answer": "'Advertise' is more public, while 'promote' can be more general support."}}
        ]
      }}
    }}
  ],
  "is_educational": true
}}
]
Example 2: Math

Example 3 – Non-educational  
Input:
[{{
  "content": "We’re planning a 10-day end-of-year celebration. Please bring in snacks, games, and tissues. Sign up link: https://...",
  "grade": "3rd Grade",
  "author": "Rebecca Anastos",
  "date": "2025-05-12"
}}
]

Output:
[{{
  "is_educational": false
}}
]

Example 5 – Multiple
Input:
[{{
  "content": "We’re planning a 10-day end-of-year celebration. Please bring in snacks, games, and tissues. Sign up link: https://...",
  "grade": "3rd Grade",
  "author": "Rebecca Anastos",
  "date": "2025-05-12"
}},
{{
    "author": "Rebecca Anastos",
    "subject": "Vocabulary Words",
    "content": "\u200bBelow is a list of \u200bour current vocabulary words. We will take a quiz on these words next \u200bFriday, 5/16.ideal-something that is perfectadvertise-to give information or announce something is for salesecluded-a place that is quiet and out of sightqueasy-to feel sick to your stomachgleam-to shine or reflect a glow of lightharmony-working well with others, getting alongloaf-time spent relaxing, doing nothingobject-to disagreejovial-always laughing and in a good moodhardy-strong, able to survive in tough conditionsabbreviated-to write something in a shortened waytedious-boring or repetitivediminish-making smallerconvince-to persuade someone to think the way you dointerview-to ask someone questions",
    "post_date": "2025-05-08T15:00:00-04:00"
  }}
]

Output:
[{{
  "is_educational": false
}},
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
        {{"name": "advertise", "meaning": "announce or promote", "example": "They advertise toys on TV."}},
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
        "next_grade": [
          {{"question": "What is the difference between 'advertise' and 'promote'?", "answer": "'Advertise' is more public, while 'promote' can be more general support."}}
        ]
      }}
    }}
  ],
  "is_educational": true
}}
]

IMPORTANT: 
- Do not include any explanations, examples, or descriptions in the response.
- Output must be only a valid JSON array or JSON object.
- Do NOT wrap the output in triple backticks or label it with json.
- Do NOT return any markdown formatting or instructional commentary.
- Just emit raw, parsable JSON as response content. 
"""

class OpenAIProcessor:

    def generate_educational_content(self, text: str, grade: str) -> list:
        log_msg(f"Generating educational content")
        prompt = educational_multi_shot_prompt.format(text=text, grade=grade)
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