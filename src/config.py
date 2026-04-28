import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DB_PATH = os.getenv("DB_PATH", "questions.db")
LOG_DIR = os.getenv("LOG_DIR", "logs")
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY not set in environment or .env file")
