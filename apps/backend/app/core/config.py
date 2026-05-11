from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database - SQLite by default (no Postgres needed!)
    DATABASE_URL: str = "sqlite+aiosqlite:///./debateai.db"

    # JWT
    SECRET_KEY: str = "argueai-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # AI APIs (optional - demo mode works without them)
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    SERPER_API_KEY: str = ""

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # App Settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
