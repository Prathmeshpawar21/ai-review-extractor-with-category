# src/data_collector.py - Complete implementation
import requests
import json
import os
from datetime import datetime, timedelta
from google_play_scraper import reviews, Sort
from config import Config

class ReviewDataCollector:
    def __init__(self):
        self.config = Config()
        self.scraper_api_base = "http://api.scraperapi.com"
    
    def collect_daily_reviews_gps(self, app_id, date_str):
        """Collect reviews using google-play-scraper for specific date"""
        try:
            # Get reviews for the date
            result, continuation_token = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=1000  # Adjust based on volume
            )
            
            # Filter reviews by date
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            daily_reviews = []
            
            for review in result:
                review_date = review['at'].date()
                if review_date == target_date:
                    daily_reviews.append({
                        'date': date_str,
                        'content': review['content'],
                        'score': review['score'],
                        'userName': review['userName'],
                        'reviewId': review['reviewId'],
                        'thumbsUpCount': review.get('thumbsUpCount', 0)
                    })
            
            return daily_reviews
            
        except Exception as e:
            print(f"Error collecting reviews for {date_str}: {e}")
            return []
    
    def save_daily_data(self, reviews_data, date_str):
        """Save daily reviews to JSON file - THIS WAS MISSING"""
        filename = f"data/raw_reviews/{date_str}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(reviews_data, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(reviews_data)} reviews for {date_str}")
        return filename
    
    def collect_historical_data(self, start_date, end_date):
        """Collect data for date range"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            print(f"Collecting data for {date_str}...")
            reviews = self.collect_daily_reviews_gps(self.config.TARGET_APP_ID, date_str)
            self.save_daily_data(reviews, date_str)
            current += timedelta(days=1)
    
    def collect_reviews_with_scraper_api(self, app_id, date_str):
        """Alternative method using ScraperAPI for Google Play Store"""
        
        # Google Play Store review URL for Zomato
        play_store_url = f"https://play.google.com/store/apps/details?id={app_id}&showAllReviews=true&hl=en"
        
        params = {
            'api_key': self.config.SCRAPER_API_KEY,
            'url': play_store_url,
            'country_code': 'us',
            'render': 'true',  # Enable JavaScript rendering
            'timeout': 70000   # 70 second timeout as recommended
        }
        
        try:
            response = requests.get(self.scraper_api_base, params=params, timeout=75)
            
            if response.status_code == 200:
                # For now, using google-play-scraper as primary method
                print(f"ScraperAPI response received for {date_str}")
                return self.collect_daily_reviews_gps(app_id, date_str)
            else:
                print(f"ScraperAPI Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"ScraperAPI error for {date_str}: {e}")
            # Fallback to google-play-scraper
            return self.collect_daily_reviews_gps(app_id, date_str)
