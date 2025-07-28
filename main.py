# main.py - Complete AI agent pipeline
from datetime import datetime, timedelta
from pathlib import Path
import os

from config import Config
from src.data_collector import ReviewDataCollector
from src.report_generator import TrendReportGenerator

def daterange(start: str, end: str):
    """Generate date range between start and end dates"""
    current = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    while current <= end_date:
        yield current.strftime("%Y-%m-%d")
        current += timedelta(days=1)

def main():
    print("🚀 AI Agent for App Review Trend Analysis")
    print("=" * 60)
    
    cfg = Config()
    start_date = cfg.START_DATE
    target_date = cfg.TARGET_DATE
    
    print(f"📱 App: {cfg.APP_NAME}")
    print(f"🆔 App ID: {cfg.TARGET_APP_ID}")
    print(f"📅 Date range: {start_date} → {target_date}")
    print(f"🧠 AI Model: OpenAI GPT-3.5-turbo")
    print(f"🔄 Batch size: {cfg.BATCH_SIZE}")
    
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    
    # ================================================================
    # STEP 1: DATA COLLECTION
    # ================================================================
    print(f"\n📊 STEP 1: Data Collection")
    print("-" * 40)
    
    collector = ReviewDataCollector()
    total_collected = 0
    
    for date_str in daterange(start_date, target_date):
        print(f"📅 Collecting reviews for {date_str}...")
        reviews = collector.collect_daily_reviews_gps(cfg.TARGET_APP_ID, date_str)
        
        if reviews:
            collector.save_daily_data(reviews, date_str)
            total_collected += len(reviews)
            print(f"✅ Saved {len(reviews)} reviews")
        else:
            print(f"⚠️ No reviews found")
    
    print(f"\n📈 Total reviews collected: {total_collected}")
    
    if total_collected == 0:
        print("❌ No data collected. Cannot proceed with analysis.")
        return
    
    # ================================================================
    # STEP 2: AI ANALYSIS & TREND GENERATION
    # ================================================================
    print(f"\n🤖 STEP 2: AI Analysis & Trend Generation")
    print("-" * 40)
    print("This includes:")
    print("  • Text preprocessing & cleaning")
    print("  • AI topic extraction (OpenAI GPT)")
    print("  • Topic deduplication & consolidation") 
    print("  • Trend analysis calculation")
    
    generator = TrendReportGenerator(batch_size=cfg.BATCH_SIZE)
    trend_df = generator.generate_trend_table_range(start_date, target_date)
    
    if trend_df.empty:
        print("❌ No topics generated. Check:")
        print("  • OpenAI API key and credits")
        print("  • Review data quality")
        print("  • Date range validity")
        return
    
    # ================================================================
    # STEP 3: REPORT GENERATION & SAVE
    # ================================================================
    print(f"\n📊 STEP 3: Report Generation")
    print("-" * 40)
    
    # Save reports in multiple formats
    csv_file = generator.save_report(trend_df, start_date, target_date, fmt="csv")
    excel_file = generator.save_report(trend_df, start_date, target_date, fmt="xlsx")
    
    # ================================================================
    # STEP 4: RESULTS SUMMARY
    # ================================================================
    print(f"\n📈 RESULTS SUMMARY")
    print("=" * 60)
    
    # Show top trending topics
    print("🔥 Top Trending Topics:")
    print(trend_df.head(10).to_string(index=False))
    
    # Calculate date range stats
    date_columns = [col for col in trend_df.columns if col != 'Topic']
    total_topics = len(trend_df)
    total_mentions = trend_df[date_columns].sum().sum()
    
    print(f"\n📊 Analysis Statistics:")
    print(f"  • Total canonical topics identified: {total_topics}")
    print(f"  • Total topic mentions: {total_mentions}")
    print(f"  • Average mentions per topic: {total_mentions/total_topics:.1f}")
    print(f"  • Date range analyzed: {len(date_columns)} days")
    
    print(f"\n✅ Reports generated:")
    print(f"  📄 CSV: {csv_file}")
    print(f"  📊 Excel: {excel_file}")
    
    print(f"\n🎯 Pipeline completed successfully!")
    print("💡 The AI agent has processed reviews through the complete pipeline:")
    print("   Data Collection → Preprocessing → AI Analysis → Deduplication → Trending")

if __name__ == "__main__":
    main()
