# config_streamlit.py - Enhanced config for Streamlit
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class StreamlitConfig:
    """Enhanced configuration class for Streamlit app"""
    
    def __init__(self):
        # API Keys - try session state first, then environment
        self.OPENAI_API_KEY = (
            st.session_state.get('openai_key') or 
            os.getenv('OPENAI_API_KEY')
        )
        self.SCRAPER_API_KEY = (
            st.session_state.get('scraper_key') or 
            os.getenv('SCRAPER_API_KEY')
        )
    
    # App configurations
    SUPPORTED_APPS = {
        "Amazon Shopping": {
            "id": "com.amazon.mShop.android.shopping",
            "topics": [
                "Delivery issue", "Product quality poor", "App crashes frequently",
                "Search not working", "Payment issues", "Order cancellation problems",
                "Wrong item delivered", "Packaging damaged", "Late delivery",
                "Customer service poor", "Refund issues", "Prime membership issues",
                "Cart problems", "Checkout errors", "Wishlist not working",
                "Price discrepancy", "Account login issues"
            ]
        },
        "Zomato": {
            "id": "com.application.zomato",
            "topics": [
                "Delivery issue", "Food quality poor", "Delivery partner rude",
                "App crashes frequently", "Payment issues", 
                "Order cancellation problems", "Restaurant not available",
                "Wrong order delivered", "Food arrived cold", "Late delivery",
                "Customer service poor", "Refund issues"
            ]
        },
        "Prime Video": {
            "id": "com.amazon.avod.thirdpartyclient",
            "topics": [
                "Video quality poor", "App crashes frequently", "Login issues",
                "Streaming problems", "Download issues", "Payment issues",
                "Content not available", "Subtitles not working", "Audio issues"
            ]
        }
    }
    
    # Dynamic properties
    @property
    def TARGET_APP_ID(self):
        return getattr(self, '_target_app_id', 'com.amazon.mShop.android.shopping')
    
    @TARGET_APP_ID.setter
    def TARGET_APP_ID(self, value):
        self._target_app_id = value
    
    @property
    def APP_NAME(self):
        return getattr(self, '_app_name', 'Amazon Shopping')
    
    @APP_NAME.setter
    def APP_NAME(self, value):
        self._app_name = value
    
    @property
    def SEED_TOPICS(self):
        app_name = getattr(self, '_app_name', 'Amazon Shopping')
        return self.SUPPORTED_APPS.get(app_name, {}).get('topics', [])
    
    # Analysis settings
    BATCH_SIZE = 10
    DEFAULT_LOOKBACK_DAYS = 30
