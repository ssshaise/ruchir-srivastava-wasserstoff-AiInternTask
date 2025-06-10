import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

env_path = 'backend/.env'

load_dotenv(dotenv_path=env_path)

print("--- Running config.py ---")
print(f"Attempting to load .env from: {os.path.abspath(env_path)}")
api_key_from_os = os.getenv("GOOGLE_API_KEY")
print(f"Value of GOOGLE_API_KEY after load_dotenv: {'Found' if api_key_from_os else 'Not Found'}")

class Settings(BaseSettings):
    """Defines the application's settings."""
    GOOGLE_API_KEY: str

settings = Settings()