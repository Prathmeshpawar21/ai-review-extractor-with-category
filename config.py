# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── API KEYS ──────────────────────────────────────────────────────────────
    SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
    OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")

    # ── APP SELECTION ────────────────────────────────────────────────────────
    TARGET_APP_ID = "com.amazon.mShop.android.shopping"   # Amazon Shopping
    APP_NAME      = "Amazon Shopping"

    # ── DATE RANGE (⇣ main.py will honour these EXACTLY) ─────────────────────
    START_DATE  = "2025-07-26"    # first day to process  (inclusive)
    TARGET_DATE = "2025-07-27"    # last  day to process  (inclusive)

    # ── SEED TOPICS (add/edit freely) ────────────────────────────────────────
    SEED_TOPICS = [
        "Delivery issue", "Product quality poor", "App crashes frequently",
        "Search not working", "Payment issues", "Order cancellation problems",
        "Wrong item delivered", "Packaging damaged", "Late delivery",
        "Customer service poor", "Refund issues", "Prime membership issues",
        "Cart problems", "Checkout errors", "Wishlist not working",
        "Price discrepancy", "Account login issues"
    ]

    # ── LLM BATCH SIZE ───────────────────────────────────────────────────────
    BATCH_SIZE = 10        # reviews sent to the LLM per request
