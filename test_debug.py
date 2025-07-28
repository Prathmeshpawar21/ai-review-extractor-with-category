# debug_test.py
from src.topic_analyzer import AgenticTopicAnalyzer
from src.preprocessor import ReviewPreprocessor
from datetime import datetime, timedelta

def debug_topic_analysis():
    print("Debug: Testing topic analysis with detailed output...")
    
    # Load some test data
    test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    preprocessor = ReviewPreprocessor()
    reviews = preprocessor.load_daily_reviews(test_date)
    
    if not reviews:
        print("No reviews found!")
        return
    
    # Test with just 2 reviews
    analyzer = AgenticTopicAnalyzer()
    test_batch = reviews[:2]
    
    print(f"Testing with {len(test_batch)} reviews:")
    for i, review in enumerate(test_batch):
        print(f"Review {i+1}: {review['cleaned_content'][:100]}...")
    
    print("\nSending to LLM...")
    result = analyzer.extract_topics_with_llm(test_batch)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    debug_topic_analysis()
