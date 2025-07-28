# collect_specific_dates.py - Collect data for exact config dates
from src.data_collector import ReviewDataCollector
from datetime import datetime, timedelta
from config import Config
import os

def collect_config_date_range():
    """Collect data for the exact date range specified in config"""
    print("🔄 Collecting data for exact config date range...")
    
    config = Config()
    collector = ReviewDataCollector()
    
    start_date = config.START_DATE
    target_date = config.TARGET_DATE
    
    print(f"📅 Start Date (from config): {start_date}")
    print(f"📅 Target Date (from config): {target_date}")
    
    # Parse dates
    start_obj = datetime.strptime(start_date, "%Y-%m-%d")
    target_obj = datetime.strptime(target_date, "%Y-%m-%d")
    
    # Calculate total days
    total_days = (target_obj - start_obj).days + 1
    print(f"📊 Total days to collect: {total_days}")
    
    if total_days > 10:
        confirm = input(f"⚠️ This will collect {total_days} days of data. Continue? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Collection cancelled.")
            return
    
    # Collect data for each day in the range
    current = start_obj
    collected_count = 0
    failed_count = 0
    
    while current <= target_obj:
        date_str = current.strftime("%Y-%m-%d")
        print(f"\n📊 Collecting reviews for {date_str}...")
        
        try:
            reviews = collector.collect_daily_reviews_gps(config.TARGET_APP_ID, date_str)
            
            if reviews:
                collector.save_daily_data(reviews, date_str)
                print(f"✅ Saved {len(reviews)} reviews for {date_str}")
                collected_count += 1
            else:
                print(f"⚠️ No reviews found for {date_str}")
                failed_count += 1
        
        except Exception as e:
            print(f"❌ Error collecting data for {date_str}: {e}")
            failed_count += 1
        
        current += timedelta(days=1)
    
    print(f"\n🎯 Data Collection Summary:")
    print(f"✅ Successfully collected: {collected_count} days")
    print(f"❌ Failed/No data: {failed_count} days")
    print(f"📁 Data saved in: data/raw_reviews/")

def collect_test_range():
    """Collect data for just a few test days"""
    print("🧪 Collecting data for test range (few days only)...")
    
    config = Config()
    collector = ReviewDataCollector()
    
    # Get just a few recent days for testing
    end_date = datetime.now() - timedelta(days=1)  # Yesterday
    start_date = end_date - timedelta(days=2)      # 3 days total
    
    print(f"📅 Test Start: {start_date.strftime('%Y-%m-%d')}")
    print(f"📅 Test End: {end_date.strftime('%Y-%m-%d')}")
    print("📊 This will collect 3 days of data for testing")
    
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        print(f"\n📊 Collecting reviews for {date_str}...")
        
        try:
            reviews = collector.collect_daily_reviews_gps(config.TARGET_APP_ID, date_str)
            
            if reviews:
                collector.save_daily_data(reviews, date_str)
                print(f"✅ Saved {len(reviews)} reviews for {date_str}")
            else:
                print(f"⚠️ No reviews found for {date_str}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        current += timedelta(days=1)
    
    print(f"\n🎯 Test data collection complete!")
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

if __name__ == "__main__":
    print("Choose collection method:")
    print("1. Collect for exact config dates (START_DATE to TARGET_DATE)")
    print("2. Collect just a few recent days for testing")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        collect_config_date_range()
    else:
        collect_test_range()
