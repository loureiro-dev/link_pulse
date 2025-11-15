
import os
from dotenv import load_dotenv
load_dotenv()

# Telegram config (optional)
TOKEN = os.getenv("WL_TOKEN", "")
CHAT_ID = os.getenv("WL_CHAT_ID", "")

# File paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

# Selenium / scraping configuration
SELENIUM_TIMEOUT = int(os.getenv("WL_SELENIUM_TIMEOUT", "25"))
USER_AGENT = os.getenv("WL_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
