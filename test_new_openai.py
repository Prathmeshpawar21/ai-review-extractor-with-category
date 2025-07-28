# test_openai_new.py - Test new OpenAI API
from openai import OpenAI
from config import Config

def test_new_openai_api():
    config = Config()
    
    # NEW: Initialize client
    client = OpenAI(
        api_key=config.OPENAI_API_KEY
    )
    
    try:
        # NEW: Use client.chat.completions.create()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, are you working with the new API?"}
            ],
            max_tokens=50
        )
        
        # NEW: Access response using pydantic model attributes
        response_content = response.choices[0].message.content
        print("OpenAI Response:", response_content)
        
        # NEW: Convert to dict if needed
        response_dict = response.model_dump()
        print("Usage:", response_dict.get('usage'))
        
        print("✅ New OpenAI API working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ New OpenAI API Error: {e}")
        return False

if __name__ == "__main__":
    test_new_openai_api()
