
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        sys.exit(1)

def check_environment():
    """Check if environment is properly configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    scraper_key = os.getenv('SCRAPER_API_KEY')
    
    if not openai_key:
        print("⚠️ WARNING: OPENAI_API_KEY not found in .env file")
    
    if not scraper_key:
        print("⚠️ WARNING: SCRAPER_API_KEY not found in .env file")
    
    if openai_key and scraper_key:
        print("✅ Environment configured correctly!")
    else:
        print("💡 Make sure to set your API keys in the .env file")

def main():
    print("🚀 Starting AI Review Trend Analyzer...")
    
    print("📦 Installing requirements...")
    install_requirements()
    
    print("🔧 Checking environment...")
    check_environment()
    
    print("🌟 Launching Streamlit app...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false"
    ])

if __name__ == "__main__":
    main()
