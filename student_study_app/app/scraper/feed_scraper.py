from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import requests
from app.utils.logger import logger

class FeedScraper:
    def __init__(self, config):
        self.config = config
        self.driver = webdriver.Chrome()
        self.session = requests.Session()

    def login(self):
        logger.info("Logging in...")
        self.driver.get(self.config['urls']['login_page'])
        time.sleep(2)
        
        self.driver.find_element(By.ID, "session_email").send_keys(self.config['login']['username'])
        password_input = self.driver.find_element(By.ID, "session_password")
        password_input.send_keys(self.config['login']['password'])
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

    def fetch_all_feeds(self, max_pages=10):
        logger.info("Fetching feeds...")
        feeds = []
        for page in range(1, max_pages + 1):
            url = f"{self.config['urls']['feeds_base']}?page={page}"
            r = self.session.get(url)
            if r.status_code != 200:
                logger.warning(f"Page {page}: HTTP {r.status_code}")
                break
            soup = BeautifulSoup(r.text, 'lxml')
            posts = soup.select("div.feed-show.feed-main.feed-box")
            logger.info(f"Page {page}: Found {len(posts)} posts")
            for post in posts:
                title = post.select_one('div.feed-title a.description-link span').text.strip()
                content = post.select_one('div.description, div.expanded-text').text.strip()
                feeds.append({'title': title, 'content': content})
            # check if no next page
            next_link = soup.select_one('li.next a[rel=next]')
            if not next_link:
                break
        return feeds

    def close(self):
        self.driver.quit()