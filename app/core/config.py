import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Kings AI System"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ENV: str = os.getenv("ENV", "development")

settings = Settings()