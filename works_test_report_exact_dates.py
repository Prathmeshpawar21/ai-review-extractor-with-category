# test_report_exact_dates.py - Test with exact config dates
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


def test_with_exact_config_dates():
    """Test report generation using exact START_DATE and TARGET_DATE from config"""
    print("🧪 Testing with EXACT config dates (not 30-day window)...")
    
    config = Config()
    start_date = config.START_DATE
    target_date = config.TARGET_DATE
    
    print(f"📅 Start Date (from config): {start_date}")
    print(f"📅 Target Date (from config): {target_date}")
    
    # Check data availability for the exact range
    available_dates, missing_dates = check_data_availability(start_date, target_date)
    
    print(f"\n📊 Data Availability Check:")
    print(f"✅ Available dates: {len(available_dates)}")
    print(f"❌ Missing dates: {len(missing_dates)}")
    
    if available_dates:
        print(f"📝 Available dates: {available_dates}")
    else:
        print("\n⚠️ NO DATA FOUND for your config date range!")
        print("You need to collect data first. Run:")
        print("python collect_specific_dates.py")
        return
    
    if missing_dates:
        print(f"📝 Missing dates: {missing_dates[:10]}...")  # Show first 10
    
    # Create a custom report generator that uses exact dates
    print(f"\n🤖 Generating report for exact date range...")
    print(f"📊 Using {len(available_dates)} days of data")
    
    try:
        # Create custom trend report for exact date range
        trend_data = generate_custom_trend_report(available_dates, start_date, target_date)
        
        if trend_data:
            print("\n--- CUSTOM TREND REPORT (Exact Dates) ---")
            for topic, date_counts in trend_data.items():
                print(f"{topic}: {date_counts}")
            
            # Save custom report
            save_custom_report(trend_data, start_date, target_date)
        else:
            print("\n⚠️ No trend data generated")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")

def generate_custom_trend_report(available_dates, start_date, target_date):
    """Generate trend report for exact date range"""
    from src.topic_analyzer import AgenticTopicAnalyzer
    from collections import defaultdict
    
    analyzer = AgenticTopicAnalyzer()
    topic_frequency = defaultdict(lambda: defaultdict(int))
    
    print("🔄 Processing available dates...")
    
    for date_str in available_dates:
        print(f"📊 Processing {date_str}...")
        
        try:
            # Process reviews for this date
            daily_analysis = analyzer.process_daily_reviews(date_str, batch_size=20)  # Small batches
            
            # Count topics for this date
            for analysis in daily_analysis:
                topics = analysis.get('identified_topics', [])
                for topic in topics:
                    topic_frequency[topic][date_str] += 1
            
            print(f"✅ Processed {len(daily_analysis)} reviews for {date_str}")
            
        except Exception as e:
            print(f"❌ Error processing {date_str}: {e}")
    
    return dict(topic_frequency)

def save_custom_report(trend_data, start_date, target_date):
    """Save custom trend report"""
    import pandas as pd
    
    # Convert to DataFrame
    all_dates = []
    current = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(target_date, "%Y-%m-%d")
    
    while current <= end:
        all_dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    # Build DataFrame
    report_data = []
    for topic, date_counts in trend_data.items():
        row = {'Topic': topic}
        for date in all_dates:
            row[date] = date_counts.get(date, 0)
        report_data.append(row)
    
    if report_data:
        df = pd.DataFrame(report_data)
        
        # Sort by total frequency
        df['Total'] = df.iloc[:, 1:].sum(axis=1)
        df = df.sort_values('Total', ascending=False).drop('Total', axis=1)
        
        # Save report
        filename = f"output/custom_trend_report_{start_date}_to_{target_date}.csv"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        
        print(f"\n✅ Custom report saved: {filename}")
        print("\nReport Preview:")
        print(df.head())
    else:
        print("⚠️ No data to save")




def collect_and_test_few_days():
    """Collect data for just a few days and test"""
    print("🧪 Quick test: Collect few days and generate report...")
    
    config = Config()
    collector = ReviewDataCollector()
    
    # Use just 3 recent days for quick testing
    end_date = datetime.now() - timedelta(days=1)
    dates_to_collect = []
    
    for i in range(3):  # Last 3 days
        date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
        dates_to_collect.append(date)
    
    print(f"📅 Test dates: {dates_to_collect}")
    
    # Collect data
    for date_str in dates_to_collect:
        print(f"📊 Collecting {date_str}...")
        reviews = collector.collect_daily_reviews_gps(config.TARGET_APP_ID, date_str)
        if reviews:
            collector.save_daily_data(reviews, date_str)
            print(f"✅ {len(reviews)} reviews")
        else:
            print("⚠️ No reviews")
    
    # Generate report for these dates
    trend_data = generate_custom_trend_report(dates_to_collect, dates_to_collect[-1], dates_to_collect[0])
    
    if trend_data:
        print("\n--- QUICK TEST REPORT ---")
        for topic, counts in list(trend_data.items())[:5]:  # Show top 5
            total = sum(counts.values())
            print(f"{topic}: {total} total occurrences")

if __name__ == "__main__":
    print("Choose test method:")
    print("1. Test with exact config dates (START_DATE to TARGET_DATE)")
    print("2. Quick test: collect few recent days and generate report")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        collect_and_test_few_days()
    else:
        test_with_exact_config_dates()
