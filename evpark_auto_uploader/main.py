import time
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 네이버 로그인
def naver_login(driver, username, password):
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(2)
    driver.find_element(By.ID, "id").send_keys(username)
    driver.find_element(By.ID, "pw").send_keys(password)
    driver.find_element(By.ID, "log.login").click()
    time.sleep(5)

# 네이버 카페 크롤링 (제목, 본문, 이미지)
def crawl_naver_cafe(driver, cafe_url):
    driver.get(cafe_url)
    time.sleep(3)

    posts = driver.find_elements(By.CSS_SELECTOR, ".article-board .article")
    post_data = []
    
    for post in posts[:20]:  # 최근 20개 글 가져오기
        try:
            title = post.find_element(By.CSS_SELECTOR, ".article-title").text
            link = post.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            driver.get(link)
            time.sleep(2)
            
            content = driver.find_element(By.CSS_SELECTOR, ".article-viewer").text
            images = [img.get_attribute("src") for img in driver.find_elements(By.CSS_SELECTOR, ".article-viewer img")]

            post_data.append({"title": title, "content": content, "images": images})
        except:
            continue

    return post_data

# 와플보드 로그인
def evpark_login(driver, username, password):
    driver.get("https://www.evpark.co.kr/login")
    time.sleep(2)
    driver.find_element(By.NAME, "user_id").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)

# 와플보드 글쓰기
def post_to_evpark(driver, post, board_url):
    driver.get(board_url)
    time.sleep(2)

    driver.find_element(By.NAME, "title").send_keys(post["title"])
    driver.find_element(By.NAME, "content").send_keys(post["content"])

    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()
    time.sleep(3)

# 실행 코드
if __name__ == "__main__":
    # 설정 불러오기
    with open("config.json", "r") as file:
        config = json.load(file)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # 네이버 크롤링
    naver_login(driver, config["naver"]["id"], config["naver"]["password"])
    all_posts = []
    
    for board in config["naver"]["boards"]:
        posts = crawl_naver_cafe(driver, board["url"])
        all_posts.extend([(post, board["evpark_url"]) for post in posts])

    # 와플보드 업로드
    for idx, (post, board_url) in enumerate(all_posts):
        evpark_login(driver, config["evpark"]["accounts"][idx % len(config["evpark"]["accounts"])]["id"],
                     config["evpark"]["accounts"][idx % len(config["evpark"]["accounts"])]["password"])
        post_to_evpark(driver, post, board_url)
        time.sleep(random.randint(60, 300))  # 랜덤 딜레이

    driver.quit()
