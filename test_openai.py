# test_openai.py
import openai
from config import Config

def test_openai_connection():
    config = Config()
    openai.api_key = config.OPENAI_API_KEY
    
    try:
        # Simple test call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use cheaper model for testing
            messages=[
                {"role": "user", "content": "Hello, are you working?"}
            ],
            max_tokens=50
        )
        
        print("OpenAI Response:", response.choices[0].message.content)
        print("✅ OpenAI API working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return False

if __name__ == "__main__":
    test_openai_connection()
