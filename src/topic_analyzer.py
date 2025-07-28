# src/topic_analyzer.py - Updated for OpenAI v1.0+
import json
import re
import os
from openai import OpenAI
from config import Config

class AgenticTopicAnalyzer:
    def __init__(self):
        self.config = Config()
        # Initialize OpenAI client with new API
        self.client = OpenAI(
            api_key=self.config.OPENAI_API_KEY
        )
        self.canonical_topics = set(self.config.SEED_TOPICS)
    
    def create_topic_extraction_prompt(self, reviews_batch, existing_topics):
        """Create improved prompt for LLM to extract and categorize topics"""
        
        existing_topics_str = "\n".join([f"- {topic}" for topic in existing_topics])
        
        prompt = f"""
You are an expert AI agent analyzing Zomato food delivery app reviews to identify issues, requests, and feedback topics.

EXISTING CANONICAL TOPICS:
{existing_topics_str}

CRITICAL INSTRUCTIONS:
1. EVERY review must have at least ONE topic identified
2. For positive reviews, use topics like "Food quality good", "Service excellent", "App working well"
3. For negative reviews, identify the specific issue
4. Map similar issues to existing canonical topics when possible
5. If no clear issue exists, categorize as "General feedback"

IMPORTANT: Respond ONLY with valid JSON. No additional text or explanations.

OUTPUT FORMAT (JSON):
{{
  "review_analysis": [
    {{
      "review_id": "actual_review_id_here", 
      "identified_topics": ["Delivery issue"],
      "confidence": 0.90
    }}
  ],
  "new_canonical_topics": [],
  "topic_mappings": {{}}
}}

REVIEWS TO ANALYZE:
"""
        
        for i, review in enumerate(reviews_batch):
            content = review['cleaned_content'][:200] if review['cleaned_content'] else "No content"
            prompt += f"\nReview {i+1} (ID: {review['reviewId']}): \"{content}\"\n"
        
        return prompt
    
    def extract_json_from_response(self, response_text):
        """Extract JSON from response with better error handling"""
        try:
            # Clean the response text
            response_text = response_text.strip()
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to find JSON within the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group().strip()
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            print(f"Could not parse JSON. Raw response: {response_text[:500]}")
            return {
                "review_analysis": [],
                "new_canonical_topics": [],
                "topic_mappings": {}
            }
    
    def extract_topics_with_llm(self, reviews_batch):
        """Use LLM to extract topics from reviews batch - NEW OpenAI API"""
        
        if not reviews_batch:
            return {"review_analysis": [], "new_canonical_topics": [], "topic_mappings": {}}
        
        prompt = self.create_topic_extraction_prompt(reviews_batch, self.canonical_topics)
        
        try:
            # NEW OpenAI v1.0+ API usage
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing app reviews. Always identify at least one topic per review. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            # NEW: Access response content using pydantic model attributes
            response_content = response.choices[0].message.content
            
            print(f"Raw LLM Response: {response_content[:200]}...")
            
            # Parse the JSON response
            result = self.extract_json_from_response(response_content)
            
            # Validate and fix empty topics
            if result.get('review_analysis'):
                for analysis in result['review_analysis']:
                    if not analysis.get('identified_topics') or len(analysis['identified_topics']) == 0:
                        analysis['identified_topics'] = ['General feedback']
                        analysis['confidence'] = 0.5
            
            # Update canonical topics
            if result.get('new_canonical_topics'):
                self.canonical_topics.update(result['new_canonical_topics'])
            
            return result
        
        except Exception as e:
            print(f"Error in LLM topic extraction: {e}")
            # Return structured fallback
            fallback_result = {
                "review_analysis": [],
                "new_canonical_topics": [],
                "topic_mappings": {}
            }
            
            for i, review in enumerate(reviews_batch):
                fallback_result["review_analysis"].append({
                    "review_id": review['reviewId'],
                    "identified_topics": ["General feedback"],
                    "confidence": 0.5
                })
            
            return fallback_result
    
    def process_daily_reviews(self, date_str, batch_size=10):
        """Process all reviews for a specific date"""
        from src.preprocessor import ReviewPreprocessor
        
        preprocessor = ReviewPreprocessor()
        reviews = preprocessor.load_daily_reviews(date_str)
        
        if not reviews:
            print(f"No reviews found for {date_str}")
            return []
        
        all_results = []
        
        # Process in smaller batches for efficiency and cost management
        for i in range(0, len(reviews), batch_size):
            batch = reviews[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1} ({len(batch)} reviews) for {date_str}...")
            batch_result = self.extract_topics_with_llm(batch)
            
            # Extract the review_analysis from the batch_result
            if isinstance(batch_result, dict) and 'review_analysis' in batch_result:
                all_results.extend(batch_result['review_analysis'])
            elif isinstance(batch_result, list):
                all_results.extend(batch_result)
        
        print(f"Completed processing {len(all_results)} reviews for {date_str}")
        return all_results
