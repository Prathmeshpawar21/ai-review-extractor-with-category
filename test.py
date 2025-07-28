# test_setup.py
from src.data_collector import ReviewDataCollector
from config import Config
from datetime import datetime, timedelta

def test_setup():
    print("Testing ScraperAPI and Zomato configuration...")
    
    config = Config()
    collector = ReviewDataCollector()
    
    # Test date (yesterday to ensure data exists)
    test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"Testing data collection for Zomato on {test_date}")
    
    # Test collection
    reviews = collector.collect_daily_reviews_gps(config.TARGET_APP_ID, test_date)
    
    print(f"Collected {len(reviews)} reviews for {test_date}")
    
    if reviews:
        print("Sample review:", reviews[0]['content'][:100] + "...")
        print("✅ Setup working correctly!")
    else:
        print("⚠️ No reviews found - this might be normal for recent dates")

if __name__ == "__main__":
    test_setup()
