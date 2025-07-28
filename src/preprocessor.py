# src/preprocessor.py - Enhanced version
import re
import json
from datetime import datetime

class ReviewPreprocessor:
    def __init__(self):
        pass
    
    def clean_text(self, text):
        """Clean and normalize review text for LLM processing"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\$$\$$,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Remove very short words (likely noise)
        words = text.split()
        words = [word for word in words if len(word) > 1]
        text = ' '.join(words)
        
        # Basic normalization
        text = text.strip().lower()
        
        # Remove if text is too short to be meaningful
        if len(text) < 10:
            return ""
        
        return text
    
    def load_daily_reviews(self, date_str):
        """Load and preprocess daily reviews"""
        filename = f"data/raw_reviews/{date_str}.json"
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                raw_reviews = json.load(f)
            
            processed_reviews = []
            for review in raw_reviews:
                cleaned_content = self.clean_text(review['content'])
                
                # Skip reviews with empty content after cleaning
                if not cleaned_content:
                    continue
                
                processed_review = {
                    'date': review['date'],
                    'original_content': review['content'],
                    'cleaned_content': cleaned_content,
                    'score': review['score'],
                    'reviewId': review['reviewId']
                }
                processed_reviews.append(processed_review)
            
            print(f"📊 Preprocessed {len(processed_reviews)} valid reviews from {len(raw_reviews)} total")
            return processed_reviews
            
        except FileNotFoundError:
            print(f"No data file found for {date_str}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file for {date_str}: {e}")
            return []
