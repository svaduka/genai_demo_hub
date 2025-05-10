# Student Study App

## Overview
**Student Study App** is an AI-powered educational assistant that automatically extracts, organizes, and presents study material and test content for students from school feeds. Built using **Streamlit**, **OpenAI GPT API**, and **BeautifulSoup/Requests**, it provides interactive reading material, quizzes, and weekly syllabus generation for 3rd-grade students and beyond.

---

## Features
- **Automated Feed Scraper**: Scrapes school feeds to extract syllabus, announcements, and relevant learning content.
- **AI-Powered Content Expansion**: Uses OpenAI GPT to generate detailed explanations, summaries, and test material from extracted topics.
- **Multimodal Content**: Supports extraction of image content via AI OCR and adds image descriptions to study material.
- **Daily Study Page**: Displays daily study material with subject-wise topics, fun facts, colorful tables, and structured explanations.
- **Daily Test Generator**: Creates test papers for each subject every day, auto-generated from the material.
- **Weekly Summary**: Generates a downloadable weekly study pack (PDF).
- **Video Recommendations**: Provides relevant YouTube video links on a separate page.
- **Student-Friendly UI**: Engaging, interactive interface with colors and visuals for children.
- **Admin Configuration Page**: Allows configuration of grade level, subjects, scraping settings, OpenAI parameters.

---

## Installation

### Prerequisites
- Python 3.10 or above
- Docker
- OpenAI API key
- (Optional) ChromeDriver if running scraper in headless mode without Docker

### Steps to Install
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/svaduka/genai_demo_hub.git
   cd genai_demo_hub/student_study_app
   ```

2. **Set Environment Variables:**
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

3. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **(Optional) Build Docker Image:**
   ```
   docker build -t student_study_app .
   ```

---

## Running the Application

### Option 1: Native
```
streamlit run app/app.py
```

### Option 2: Docker
```
docker run -p 8501:8501 --env-file .env student_study_app
```

---

## Project Structure
```
student_study_app/
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── routes/
│   ├── components/
│   ├── utils/
│   ├── tests/
│   └── config/
├── data/
├── logs/
├── Dockerfile
├── requirements.txt
├── README.md
└── .env
```

---

## How It Works

1. **Feeds Extraction**
   - Automatically scrapes feed pages across pagination.
   - Extracts syllabus, announcements, and attachments.

2. **Content Processing**
   - Cleans and parses text using BeautifulSoup.
   - AI generates detailed study material, colorful tables, fun explanations.

3. **Daily Study Page**
   - Student views daily page organized by subject.
   - Interactive with expandable sections, images, diagrams.

4. **Daily Tests**
   - Auto-generated tests per subject.
   - Students complete tests inside app; results are graded.

5. **Weekly Export**
   - Full week’s material exported as PDF.
   - Optionally emailed/downloadable.

6. **Video Links**
   - Relevant YouTube links for each topic appear on a separate "Videos" page.

---

## Configuration

- Admin can change settings via a UI under `/config` page.
- Settings stored in `config/config.yaml`.

---

## Logging
Logs are written to `logs/app.log` with rotation.

---

## Testing
Run unit tests:
```
pytest app/tests/
```

---

## License
MIT License.

## Author
Sainagaraju Vaduka
