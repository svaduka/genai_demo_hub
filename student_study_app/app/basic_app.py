from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests
from bs4 import BeautifulSoup

# Setup Chrome browser
driver = webdriver.Chrome()

# STEP 1: Go to login page
driver.get("https://www.parentsquare.com/signin")

# STEP 2: Wait for page to load
time.sleep(3)  # You may improve with WebDriverWait

# STEP 3: Fill in credentials
email_input = driver.find_element(By.ID, "session_email")
password_input = driver.find_element(By.ID, "session_password")

email_input.send_keys("sainagaraju.vaduka@gmail.com")
password_input.send_keys("Jaggani@123")
password_input.send_keys(Keys.RETURN)

# STEP 4: Wait for login to complete
time.sleep(5)

if "feeds" in driver.current_url:
    print("[+] Login successful and feeds page loaded!")
    
    # STEP 5: Transfer cookies from Selenium to requests
    selenium_cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in selenium_cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }
    
    feeds_url = "https://www.parentsquare.com/schools/24922/feeds"
    response = session.get(feeds_url, headers=headers)
    
    if response.status_code == 200:
        print("[+] Successfully fetched feeds page with requests!")
        
        soup = BeautifulSoup(response.text, "lxml")
        posts = soup.select("div.feed-show.feed-main.feed-box")
        print(f"Found {len(posts)} feed posts.")
        
        for idx, post in enumerate(posts, 1):
            title_tag = post.select_one('div.feed-title a.description-link span')
            title = title_tag.text.strip() if title_tag else "No Title"
            print(f"{idx}. {title}")
    else:
        print(f"[!] Failed to fetch feeds page. Status code: {response.status_code}")
else:
    print("[!] Login may have failed or redirected elsewhere.")
    print(f"Current URL: {driver.current_url}")

# STEP 6: Close browser
driver.quit()