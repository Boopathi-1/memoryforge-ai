import os
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH, encoding="utf-8-sig")

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    MODEL: str = "llama-3.3-70b-versatile"
    SHORT_TERM_LIMIT: int = 10       # last N messages kept verbatim
    SUMMARY_TRIGGER: int = 20        # summarise when history exceeds this
    MAX_TOKENS: int = 1024

settings = Settings()
