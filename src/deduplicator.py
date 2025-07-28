# src/deduplicator_optimized.py - Fast version
import json
from openai import OpenAI
from collections import defaultdict
from config import Config
import time

class OptimizedTopicDeduplicator:
    def __init__(self):
        self.config = Config()
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        self.topic_taxonomy = {}
    
    def batch_merge_topics(self, topics_list):
        """Batch process multiple topics at once to reduce API calls"""
        
        if len(topics_list) <= 5:
            return {}  # Skip deduplication for small sets
        
        # Create prompt for batch processing
        topics_text = "\n".join([f"{i+1}. {topic}" for i, topic in enumerate(topics_list)])
        
        prompt = f"""
Analyze these {len(topics_list)} topics and identify groups that should be merged due to semantic similarity:

TOPICS:
{topics_text}

GROUP similar topics together. Only merge topics that are semantically the same issue/request.

Examples of what SHOULD be grouped:
- "App crashes" and "App keeps crashing" 
- "Delivery late" and "Late delivery"
- "Bad food quality" and "Food quality poor"

Examples of what should NOT be grouped:
- "App crashes" and "App slow" (different issues)
- "Food quality" and "Delivery issue" (different categories)

Respond with JSON only:
{{
  "groups": [
    {{
      "canonical_name": "App crashes frequently",
      "members": [1, 5, 12]
    }},
    {{
      "canonical_name": "Late delivery", 
      "members": [3, 8]
    }}
  ]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at semantic grouping. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean response
            if content.startswith('```json'):
                content = content[7:]  # Remove ```
            elif content.startswith('```'):
                content = content[3:]  # Remove ```
            if content.endswith('```'):
                content = content[:-3]  # Remove closing ```
                
            content = content.strip()
            
            result = json.loads(content)
            
            # Convert to taxonomy mapping
            taxonomy = {}
            for group in result.get('groups', []):
                canonical = group.get('canonical_name', '')
                members = group.get('members', [])
                
                for member_idx in members:
                    if 1 <= member_idx <= len(topics_list):
                        original_topic = topics_list[member_idx - 1]
                        taxonomy[original_topic] = canonical
            
            return taxonomy
            
        except Exception as e:
            print(f"Error in batch topic merging: {e}")
            return {}
    
    def build_topic_taxonomy(self, all_topics):
        """Build taxonomy using batch processing - MUCH FASTER"""
        
        topic_list = list(all_topics)
        print(f"🔄 Batch deduplicating {len(topic_list)} topics...")
        
        if len(topic_list) <= 5:
            print("⚠️ Too few topics to deduplicate")
            return {}
        
        # Process in batches to avoid token limits
        batch_size = 20
        consolidated_taxonomy = {}
        
        for i in range(0, len(topic_list), batch_size):
            batch = topic_list[i:i+batch_size]
            print(f"🔄 Processing batch {i//batch_size + 1} ({len(batch)} topics)...")
            
            batch_taxonomy = self.batch_merge_topics(batch)
            consolidated_taxonomy.update(batch_taxonomy)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        merges = len([k for k, v in consolidated_taxonomy.items() if k != v])
        print(f"📊 Batch deduplication complete: {merges} topics merged")
        
        return consolidated_taxonomy















# # src/deduplicator.py - Simple corrected version

# import json
# from openai import OpenAI
# from collections import defaultdict
# from config import Config

# class TopicDeduplicator:
#     def __init__(self):
#         self.config = Config()
#         self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
#         self.topic_taxonomy = {}
    
#     def should_merge_topics(self, topic1, topic2):
#         """Use LLM to determine if two topics should be merged"""
        
#         if topic1.lower().strip() == topic2.lower().strip():
#             return {"should_merge": True, "canonical_name": topic1, "reasoning": "Identical topics"}
        
#         prompt = f"""
# Compare these two topics and determine if they should be merged:

# Topic 1: "{topic1}"
# Topic 2: "{topic2}"

# Respond with valid JSON only:
# {{
#   "should_merge": true,
#   "canonical_name": "preferred name",
#   "reasoning": "explanation"
# }}
# """
        
#         try:
#             response = self.client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.1,
#                 max_tokens=150
#             )
            
#             content = response.choices[0].message.content.strip()
            
#             # Simple cleanup - CORRECTED
#             content = content.replace('``````', '').strip()
            
#             return json.loads(content)
        
#         except Exception as e:
#             print(f"Error comparing topics: {e}")
#             return {"should_merge": False, "canonical_name": topic1, "reasoning": "Error occurred"}
    
#     def build_topic_taxonomy(self, all_topics):
#         """Build consolidated taxonomy of topics"""
#         topic_list = list(all_topics)
#         consolidated_taxonomy = {}
        
#         print(f"🔄 Deduplicating {len(topic_list)} topics...")
        
#         for i in range(len(topic_list)):
#             for j in range(i+1, len(topic_list)):
#                 topic1, topic2 = topic_list[i], topic_list[j]
                
#                 merge_decision = self.should_merge_topics(topic1, topic2)
                
#                 if merge_decision.get('should_merge', False):
#                     canonical = merge_decision.get('canonical_name', topic1)
#                     consolidated_taxonomy[topic1] = canonical
#                     consolidated_taxonomy[topic2] = canonical
        
#         return consolidated_taxonomy
