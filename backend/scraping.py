import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re


class AmazonReviewScraper:
    def __init__(self, headers=None):
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

    def extract_asin(self, url):
        """Extracts the 10-character Amazon Standard Identification Number."""
        asin_match = re.search(r"/[dp|gp/product|product-reviews]+/(?P<asin>[a-zA-Z0-9]{10})", url)
        return asin_match.group("asin") if asin_match else None

    def get_reviews(self, url, max_pages=3):
        asin = self.extract_asin(url)
        if not asin:
            return pd.DataFrame()

        all_reviews = []

        for page in range(1, max_pages + 1):
            # Direct request to the review pagination URL
            target_url = f"https://www.amazon.com/product-reviews/{asin}/ref=cm_cr_arp_d_paging_btm_next_{page}?pageNumber={page}"

            try:
                response = requests.get(target_url, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    break

                soup = BeautifulSoup(response.content, 'html.parser')
                review_elements = soup.find_all('div', {'data-hook': 'review'})

                if not review_elements:
                    break

                for item in review_elements:
                    # 1. account_id
                    profile = item.find('a', class_='a-profile')
                    acc_id = profile.get('href').split('/profile/')[1].split('/')[
                        0] if profile and '/profile/' in profile.get('href') else "Unknown"

                    # 2. time
                    r_date = item.find('span', {'data-hook': 'review-date'})
                    time_val = r_date.get_text(strip=True) if r_date else None

                    # 3. rating
                    r_star = item.find('i', {'data-hook': 'review-star-rating'})
                    rating_val = r_star.get_text(strip=True).split(' ')[0] if r_star else None

                    # 4. review_text
                    r_body = item.find('span', {'data-hook': 'review-body'})
                    text_val = r_body.get_text(strip=True) if r_body else None

                    all_reviews.append({
                        'account_id': acc_id,
                        'time': time_val,
                        'rating': rating_val,
                        'review_text': text_val
                    })

                # Respectful delay to avoid getting your IP banned mid-hackathon
                time.sleep(1.2)

            except Exception as e:
                print(f"Error on page {page}: {e}")
                break

        return pd.DataFrame(all_reviews)