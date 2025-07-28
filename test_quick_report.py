# quick_report_test_fixed.py - Fixed version with data validation
from src.report_generator import TrendReportGenerator
from src.data_collector import ReviewDataCollector
from datetime import datetime, timedelta
from config import Config
import os

def check_data_availability(start_date, end_date):
    """Check which dates have available data"""
    available_dates = []
    missing_dates = []
    
    current = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        data_file = f"data/raw_reviews/{date_str}.json"
        
        if os.path.exists(data_file):
            available_dates.append(date_str)
        else:
            missing_dates.append(date_str)
        
        current += timedelta(days=1)
    
    return available_dates, missing_dates

def test_quick_report_with_data_check():
    print("Testing quick trend report generation with data validation...")
    
    config = Config()
    target_date = config.TARGET_DATE
    
    # Calculate analysis window
    target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
    analysis_start = (target_date_obj - timedelta(days=config.ANALYSIS_WINDOW_DAYS)).strftime("%Y-%m-%d")
    
    print(f"📅 Target date: {target_date}")
    print(f"📅 Analysis window: {analysis_start} to {target_date}")
    
    # Check data availability
    available_dates, missing_dates = check_data_availability(analysis_start, target_date)
    
    print(f"\n📊 Data Availability Check:")
    print(f"✅ Available dates: {len(available_dates)}")
    print(f"❌ Missing dates: {len(missing_dates)}")
    
    if available_dates:
        print(f"📝 First few available dates: {available_dates[:5]}")
    
    if len(available_dates) == 0:
        print("\n⚠️ NO DATA FOUND! You need to collect data first.")
        print("Options:")
        print("1. Run: python collect_data_first.py")
        print("2. Or change TARGET_DATE in config.py to a recent date")
        print(f"3. Or use: {(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')} (yesterday)")
        return
    
    # Generate report with available data
    print(f"\n🤖 Generating report with {len(available_dates)} days of data...")
    
    try:
        report_generator = TrendReportGenerator()
        trend_df = report_generator.generate_trend_table(target_date)
        
        if not trend_df.empty:
            print("\n--- QUICK TREND REPORT ---")
            print(trend_df)
            
            # Save the report
            csv_file = report_generator.save_report(trend_df, target_date, 'csv')
            print(f"\n✅ Report saved: {csv_file}")
        else:
            print("\n⚠️ Generated report is empty. This might be due to:")
            print("- No reviews in the collected data")
            print("- Issues with topic analysis")
            print("- Date range problems")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")

def collect_and_test():
    """Collect recent data and then test report generation"""
    print("🔄 Step 1: Collecting recent data...")
    
    config = Config()
    collector = ReviewDataCollector()
    
    # Use yesterday as target (most likely to have data)
    target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Collect just a few days of recent data
    for i in range(3):  # Last 3 days
        date = (datetime.now() - timedelta(days=i+1)).strftime("%Y-%m-%d")
        print(f"📊 Collecting for {date}...")
        
        reviews = collector.collect_daily_reviews_gps(config.TARGET_APP_ID, date)
        if reviews:
            collector.save_daily_data(reviews, date)
            print(f"✅ Saved {len(reviews)} reviews")
        else:
            print(f"⚠️ No reviews found")
    
    print(f"\n🤖 Step 2: Testing report generation...")
    
    # Update config temporarily for testing
    original_target = config.TARGET_DATE
    config.TARGET_DATE = target_date
    
    try:
        report_generator = TrendReportGenerator()
        trend_df = report_generator.generate_trend_table(target_date)
        
        print("\n--- TEST REPORT ---")
        print(trend_df)
        
        if not trend_df.empty:
            csv_file = report_generator.save_report(trend_df, target_date, 'csv')
            print(f"\n✅ Test report saved: {csv_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Restore original config
        config.TARGET_DATE = original_target



if __name__ == "__main__":
    print("Choose an option:")
    print("1. Check data availability and try report generation")
    print("2. Collect recent data and test report generation")
    
    choice = input("Enter choice (1 or 2, or press Enter for option 1): ").strip()
    
    if choice == "2":
        collect_and_test()
    else:
        test_quick_report_with_data_check()
