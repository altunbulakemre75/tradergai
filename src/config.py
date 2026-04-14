import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

NEWS_LOOKBACK_HOURS = 24
MAX_NEWS_ITEMS = 5
GEMINI_MODEL = "gemini-2.5-flash-lite"


def validate() -> None:
    missing = []
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if missing:
        raise RuntimeError(
            f".env eksik: {', '.join(missing)}. .env.example dosyasına bakın."
        )
