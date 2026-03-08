import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_asin(url):
    pattern = r"/([A-Z0-9]{10})(?:[/?]|$)"
    match = re.search(pattern, url)

    if match:
        return match.group(1)
    else:
        return None


ASIN = get_asin(url)
MAX_REVIEWS = 50

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)

url = f"https://www.amazon.com/product-reviews/{ASIN}/?sortBy=recent"
driver.get(url)

reviews = []

while len(reviews) < MAX_REVIEWS:

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-hook='review']"))
    )

    review_elements = driver.find_elements(By.CSS_SELECTOR, "[data-hook='review']")

    for review in review_elements:

        try:
            text = review.find_element(By.CSS_SELECTOR, "[data-hook='review-body']").text
            rating = review.find_element(By.CSS_SELECTOR, "[data-hook='review-star-rating']").text
            date = review.find_element(By.CSS_SELECTOR, "[data-hook='review-date']").text

            reviews.append({
                "text": text,
                "rating": rating,
                "date": date
            })

            if len(reviews) >= MAX_REVIEWS:
                break

        except:
            continue

    if len(reviews) >= MAX_REVIEWS:
        break


    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "li.a-last a")
        next_button.click()
        time.sleep(2)
    except:
        break

driver.quit()

print(f"Collected {len(reviews)} reviews\n")

for r in reviews[:5]:
    print(r)