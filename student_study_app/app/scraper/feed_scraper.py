from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import requests
from pathlib import Path
from app.utils.logger import logger
from app.utils.load_secets import (
    PARENTSQUARE_USERNAME,
    PARENTSQUARE_PASSWORD,
    PARENTSQUARE_LOGIN_URL,
    PARENTSQUARE_FEEDS_URL,
    TEACHERS_LIST
)

class FeedScraper:
    def __init__(self):
        self.username = PARENTSQUARE_USERNAME
        self.password = PARENTSQUARE_PASSWORD
        self.urls = {
            'login_page': PARENTSQUARE_LOGIN_URL,
            'feeds_base': PARENTSQUARE_FEEDS_URL
        }
        self.driver = webdriver.Chrome()
        self.session = requests.Session()

    def login(self):
        logger.info("Logging in...")
        self.driver.get(self.urls['login_page'])
        time.sleep(2)
        
        self.driver.find_element(By.ID, "session_email").send_keys(self.username)
        password_input = self.driver.find_element(By.ID, "session_password")
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)

        if "feeds" in self.driver.current_url:
            logger.info("Login successful!")
            cookies = self.driver.get_cookies()
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
        else:
            logger.error("Login failed. URL: %s", self.driver.current_url)
            raise Exception("Login failed")

    def fetch_all_feeds(self):
        logger.info("Fetching feeds...")
        feeds = []
        page = 1
        while True:
            url = f"{self.urls['feeds_base']}?page={page}"
            r = self.session.get(url)
            if r.status_code != 200:
                logger.warning(f"Page {page}: HTTP {r.status_code}")
                break
            soup = BeautifulSoup(r.text, 'lxml')
            posts = soup.select("div.feed-show.feed-main.feed-box")
            logger.info(f"Page {page}: Found {len(posts)} posts")
            for post in posts:
                author_element = post.select_one(".feed-metadata a.user-name")
                if author_element and (TEACHERS_LIST == ["ALL"] or any(teacher.lower() in author_element.text.lower() for teacher in TEACHERS_LIST)):
                    content_element = post.select_one('div.description, div.expanded-text')
                    content = content_element.text.strip() if content_element else "No Content Found"
                    feeds.append({'author': author_element.text.strip(), 'content': content})
                    found_teacher_post = True
                    break
            next_link = soup.select_one('li.next a[rel=next]')
            if not next_link:
                break
            page += 1

        output_dir = Path(__file__).resolve().parent.parent.parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "feeds.json"
        import json
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(feeds, f, indent=2)
        logger.info(f"Saved feeds to {output_file}")
        return feeds

    def close(self):
        logger.info("Closing browser")
        self.driver.quit()