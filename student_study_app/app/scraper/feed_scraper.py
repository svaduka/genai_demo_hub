import os
from datetime import datetime, timedelta, timezone
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
    TEACHERS_LIST,
    LOOK_BACK_PERIOD
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

    def _get_feed_page(self, page):
        url = f"{self.urls['feeds_base']}?page={page}"
        response = self.session.get(url)
        if response.status_code != 200:
            logger.warning(f"Page {page}: HTTP {response.status_code}")
            return None
        logger.info(f"Page {page}: Successfully fetched")
        return BeautifulSoup(response.text, 'lxml')

    def _parse_post(self, post, cutoff_date):
        from_zone = timezone.utc

        date_element = post.select_one("span.time-ago")
        post_date = None
        if date_element and date_element.has_attr("data-timestamp"):
            post_date = datetime.fromisoformat(date_element["data-timestamp"])
            if post_date < cutoff_date:
                return None

        author_element = post.select_one(".feed-metadata a.user-name")
        subject_element = post.select_one("div.subject span[role=heading]")
        expanded_element = post.select_one("div.expanded-text .description")
        content_element = expanded_element or post.select_one("div.description")

        if not author_element or not content_element:
            logger.debug("Skipping post due to missing author or content")
            return None

        author = author_element.text.strip()
        if TEACHERS_LIST != ["ALL"] and not any(teacher.lower() in author.lower() for teacher in TEACHERS_LIST):
            logger.debug(f"Skipping post by {author} - not in TEACHERS_LIST")
            return None
        logger.debug(f"Found post by {author} - which are in TEACHERS_LIST {TEACHERS_LIST}")
        content = content_element.get_text(strip=True)
        subject = subject_element.text.strip() if subject_element else "No Subject"

        return {
            "author": author,
            "subject": subject,
            "content": content,
            "post_date": post_date.astimezone().isoformat() if post_date else "Unknown"
        }

    def _collect_all_posts(self, cutoff_date):
        page = 1
        all_posts = []
        while True:
            soup = self._get_feed_page(page)
            if not soup:
                break

            posts = soup.select("div.feed-show.feed-main.feed-box")
            logger.info(f"Page {page}: Found {len(posts)} posts")

            for post in posts:
                parsed = self._parse_post(post, cutoff_date)
                if parsed:
                    all_posts.append(parsed)

            next_link = soup.select_one('li.next a[rel=next]')
            if not next_link:
                logger.info("No more pages to fetch.")
                break
            page += 1
        return all_posts

    def fetch_all_feeds(self):
        logger.info("Fetching feeds...")
        try:
            look_back_weeks = int(LOOK_BACK_PERIOD)
            if look_back_weeks <= 0:
                raise ValueError
        except (ValueError, TypeError):
            logger.warning("Invalid LOOK_BACK_PERIOD. Defaulting to 1 week.")
            look_back_weeks = 1
        cutoff_date = datetime.now(timezone.utc) - timedelta(weeks=look_back_weeks)
        logger.info(f"Filtering posts after: {cutoff_date.isoformat()}")

        feeds = self._collect_all_posts(cutoff_date)

        output_dir = Path(__file__).resolve().parent.parent.parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "feeds.json"

        import json
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(feeds, f, indent=2)
        logger.info(f"Saved {len(feeds)} feeds to {output_file}")
        return feeds

    def close(self):
        logger.info("Closing browser")
        self.driver.quit()