"""
Application Configuration
Settings for the multi-market authentication system
"""

from typing import Optional
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""

    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore'
    )

    # Database settings
    database_url_kg: str = "postgresql://user:password@localhost/marque_kg_db"
    database_url_us: str = "postgresql://user:password@localhost/marque_us_db"

    # JWT settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # SMS service settings (optional)
    sms_api_key: Optional[str] = None
    sms_service_url: Optional[str] = None

    # CORS settings
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True


# Global settings instance
settings = Settings()
