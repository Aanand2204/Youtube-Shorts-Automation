import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", os.path.join("credentials", "client_secrets.json"))
    # Add other configuration keys

if not Config.GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY environment variable not set. LLM features may fail.")
