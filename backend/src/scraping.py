import re
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pandas import DataFrame

def get_asin(url):
    pattern = r"/([A-Z0-9]{10})(?:[/?]|$)"
    match = re.search(pattern, url)

    if match:
        return match.group(1)
    else:
        return None
def get_aliId(url):
    pattern = r"(?:\/item\/|productId=)(\d+)"
    match = re.search(pattern, url)

    if match:
        return match.group(1)
    else:
        return None
def get_steamId(url):
    pattern = r"store\.steampowered\.com/app/(\d+)"
    match = re.search(pattern, url)

    if match:
        return match.group(1)
    else:
        return None


MAX_REVIEWS = 50

# options = Options()
# options.add_argument("--headless")
# options.add_argument("--start-maximized")
# options.add_argument("--disable-gpu")

# driver = webdriver.Chrome(options=options)

# https://www.amazon.com/dp/{ASIN}
# cm_cr_top_reviews_to_arp_button
# cm_cr_top_reviews_to_arp_button
#https://www.amazon.com/dp/B0FJSL5MWD/?th=1

#comet-v2-btn comet-v2-btn-slim comet-v2-btn-large v3--btn--KaygomA comet-v2-btn-important

def fetch_reviews(user_url: str):
    print(user_url)
    ID = get_steamId(user_url)
    if ID is None:
        return None
    url = f"https://store.steampowered.com/appreviews/{ID}"
    params = {
        "json": 1,
        "language": "english",
        "filter": "recent",
        "num_per_page": 100
    }

    try:
        res = requests.get(url, params)
        res.raise_for_status()
        data = res.json()
        print(url)
        print(data["reviews"][0])

        reviews = [
            {
                "review_text": review["review"],
                "time": review["timestamp_updated"],
                "account_id": review["author"]["steamid"], 
                "rating": review["weighted_vote_score"]
            } for review in data["reviews"] if review["review"] is not None
        ]

        return reviews
            
    except requests.exceptions.HTTPError as err: 
        print("there was an error w the request yo")
        print(err)
        return None


    
    #signed in


# fetch_reviews("https://store.steampowered.com/app/1451480/The_Greatest_Penguin_Heist_of_All_Time/")

def get_data(user_url: str):
    ASIN = get_asin(user_url)
    url = f"https://www.amazon.com/product-reviews/{ASIN}/?sortBy=recent"
    driver.get(url)

    reviews = []

    while len(reviews) < MAX_REVIEWS:

        WebDriverWait(driver, 10)

        print(driver.current_url)
        print(driver.page_source[:1000])

        WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-hook='review']"))
        )

        review_elements = driver.find_elements(By.CSS_SELECTOR, "[data-hook='review']")
        i = 0
        for review in review_elements:
            i += 1
            try:
                text = review.find_element(By.CSS_SELECTOR, "[data-hook='review-body']").text
                rating = review.find_element(By.CSS_SELECTOR, "[data-hook='review-star-rating']").text
                date = review.find_element(By.CSS_SELECTOR, "[data-hook='review-date']").text

                reviews.append({
                    "account_id": i,
                    "review_text": text,
                    "rating": rating,
                    "time": date
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
    return DataFrame(reviews)