# test_end_to_end.py - Updated for new OpenAI API
from src.data_collector import ReviewDataCollector
from src.preprocessor import ReviewPreprocessor
from src.topic_analyzer import AgenticTopicAnalyzer
from datetime import datetime, timedelta

def test_small_batch():
    print("Testing end-to-end with new OpenAI API...")
    
    test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"Using test date: {test_date}")
    
    # Step 1: Collect and Save Data
    collector = ReviewDataCollector()
    print("Step 1: Collecting reviews...")
    reviews = collector.collect_daily_reviews_gps("com.application.zomato", test_date)
    print(f"Collected {len(reviews)} reviews")
    
    print("Step 1b: Saving reviews to file...")
    collector.save_daily_data(reviews, test_date)
    print(f"✅ Saved {len(reviews)} reviews to file")
    
    # Step 2: Preprocess
    print("Step 2: Preprocessing reviews...")
    preprocessor = ReviewPreprocessor()
    processed = preprocessor.load_daily_reviews(test_date)
    print(f"✅ Preprocessed {len(processed)} reviews")
    
    if processed:
        print(f"Sample processed review:")
        print(f"Original: {processed[0]['original_content'][:50]}...")
        print(f"Cleaned: {processed[0]['cleaned_content'][:50]}...")
    
    # Step 3: Analyze topics with NEW OpenAI API
    print("Step 3: Analyzing topics with new OpenAI API...")
    analyzer = AgenticTopicAnalyzer()
    small_batch = processed[:3]  # Test with 3 reviews
    
    print("Sending batch to LLM for topic analysis...")
    results = analyzer.extract_topics_with_llm(small_batch)
    print(f"✅ Topic analysis complete!")
    
    # Display results
    if results.get('review_analysis'):
        print("\nTopic Analysis Results:")
        for i, analysis in enumerate(results['review_analysis']):
            topics = analysis.get('identified_topics', [])
            confidence = analysis.get('confidence', 'N/A')
            review_id = analysis.get('review_id', f'review_{i+1}')
            print(f"Review {i+1} ({review_id[:8]}...): {topics} (confidence: {confidence})")
    
    if results.get('new_canonical_topics'):
        print(f"\nNew topics discovered: {results['new_canonical_topics']}")

if __name__ == "__main__":
    test_small_batch()
