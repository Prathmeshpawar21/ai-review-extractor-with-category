# src/report_generator.py - Fix the import
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import os

class TrendReportGenerator:
    def __init__(self, batch_size=10):
        from config import Config
        self.batch_size = batch_size or Config.BATCH_SIZE
        self.topic_frequency = defaultdict(lambda: defaultdict(int))

    def aggregate_topic_data_range(self, start_date: str, end_date: str):
        """Complete pipeline: preprocessing → topic analysis → deduplication"""
        from src.preprocessor import ReviewPreprocessor
        from src.topic_analyzer import AgenticTopicAnalyzer
        from src.deduplicator import OptimizedTopicDeduplicator  # ✅ FIXED IMPORT
        
        preprocessor = ReviewPreprocessor()
        analyzer = AgenticTopicAnalyzer()
        deduplicator = OptimizedTopicDeduplicator()  # ✅ FIXED CLASS NAME
        
        all_topics = set()
        daily_results = {}
        
        # Calculate total days for progress tracking
        start_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_obj = datetime.strptime(end_date, "%Y-%m-%d")
        total_days = (end_obj - start_obj).days + 1
        
        print(f"📅 Processing {total_days} days of data...")
        
        # Step 1: Process each day with AI analysis
        current = start_obj
        day_count = 0
        
        while current <= end_obj:
            date_str = current.strftime("%Y-%m-%d")
            day_count += 1
            
            print(f"🔄 Processing {date_str} ({day_count}/{total_days})...")
            
            # STEP 1: Load and preprocess reviews
            processed_reviews = preprocessor.load_daily_reviews(date_str)
            if not processed_reviews:
                print(f"⚠️ No reviews found for {date_str}")
                current += timedelta(days=1)
                continue
            
            print(f"📊 Preprocessed {len(processed_reviews)} reviews")
            
            # STEP 2: AI topic analysis
            daily_analysis = analyzer.process_daily_reviews(date_str, batch_size=self.batch_size)
            daily_results[date_str] = daily_analysis
            
            # Collect all topics for deduplication
            for analysis in daily_analysis:
                all_topics.update(analysis.get('identified_topics', []))
            
            print(f"✅ Analyzed {len(daily_analysis)} reviews, found {len(all_topics)} unique topics so far")
            current += timedelta(days=1)
        
        if not all_topics:
            print("❌ No topics found across all dates!")
            return
        
        # Step 2: Fast batch deduplication
        print(f"\n🚀 Fast deduplication of {len(all_topics)} topics...")
        topic_taxonomy = deduplicator.build_topic_taxonomy(all_topics)
        print(f"📋 Created taxonomy with {len(topic_taxonomy)} mappings")
        
        # Step 3: Aggregate frequencies with canonical topics
        for date_str, analyses in daily_results.items():
            for analysis in analyses:
                for topic in analysis.get('identified_topics', []):
                    # Map to canonical topic
                    canonical_topic = topic_taxonomy.get(topic, topic)
                    self.topic_frequency[canonical_topic][date_str] += 1
        
        print(f"📈 Final analysis: {len(self.topic_frequency)} canonical topics")

    def generate_trend_table_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate trend table with full AI pipeline"""
        print(f"\n🤖 Running complete AI pipeline for {start_date} to {end_date}")
        
        # Run the complete pipeline
        self.aggregate_topic_data_range(start_date, end_date)

        # Build ordered date list
        all_dates = []
        current = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current <= end_date_obj:
            all_dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

        # Create DataFrame
        rows = []
        for topic, date_counts in self.topic_frequency.items():
            row = {"Topic": topic}
            for date in all_dates:
                row[date] = date_counts.get(date, 0)
            rows.append(row)

        df = pd.DataFrame(rows)
        if not df.empty:
            # Sort by total frequency (most trending topics first)
            df["Total"] = df.iloc[:, 1:].sum(axis=1)
            df = df.sort_values("Total", ascending=False).drop(columns="Total")
        
        return df

    def save_report(self, df, start_date, end_date, fmt="csv"):
        """Save the trend analysis report"""
        if df.empty:
            print("⚠️ No data to save – dataframe is empty.")
            return None
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        filename = f"output/trend_report_{start_date}_to_{end_date}.{fmt}"
        
        try:
            if fmt == "csv":
                df.to_csv(filename, index=False)
            elif fmt == "xlsx":
                df.to_excel(filename, index=False, engine='openpyxl')
            
            print(f"✅ Report saved → {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return None
