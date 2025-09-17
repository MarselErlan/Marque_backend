"""
Application Configuration
Settings for the multi-market authentication system
"""

import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings
    database_url_kg: str = "postgresql://user:password@localhost/marque_kg_db"
    database_url_us: str = "postgresql://user:password@localhost/marque_us_db"
    
    # JWT settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # SMS settings (for production)
    sms_api_key: Optional[str] = None
    sms_api_url: Optional[str] = None
    sms_sender_name: str = "Marque"
    
    # Rate limiting
    max_verification_attempts: int = 3
    verification_attempts_window: int = 15  # minutes
    
    # Application settings
    app_name: str = "Marque Multi-Market Auth"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Market settings
    default_market: str = "kg"
    supported_markets: list[str] = ["kg", "us"]
    
    # Security settings
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
