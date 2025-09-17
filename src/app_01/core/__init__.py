"""
Core Configuration Management System
Handles application settings, environment variables, and market-specific configurations
"""

import os
from typing import List, Dict, Any, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Market(Enum):
    """Supported markets"""
    KG = "kg"
    US = "us"

class Environment(Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class DatabaseConfig(BaseSettings):
    """Database configuration"""
    url_kg: str = Field(default="postgresql://user:password@localhost/marque_kg_db", env="DATABASE_URL_MARQUE_KG")
    url_us: str = Field(default="postgresql://user:password@localhost/marque_us_db", env="DATABASE_URL_MARQUE_US")
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    echo: bool = Field(default=False, env="DATABASE_ECHO")

class SecurityConfig(BaseSettings):
    """Security configuration"""
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")

class RedisConfig(BaseSettings):
    """Redis configuration"""
    url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")

class ExternalServicesConfig(BaseSettings):
    """External services configuration"""
    sms_service_url: str = Field(default="", env="SMS_SERVICE_URL")
    sms_service_api_key: str = Field(default="", env="SMS_SERVICE_API_KEY")
    email_service_url: str = Field(default="", env="EMAIL_SERVICE_URL")
    email_service_api_key: str = Field(default="", env="EMAIL_SERVICE_API_KEY")
    file_storage_url: str = Field(default="", env="FILE_STORAGE_URL")
    file_storage_api_key: str = Field(default="", env="FILE_STORAGE_API_KEY")

class MarketConfig:
    """Market-specific configurations"""
    
    KG_CONFIG = {
        "currency": "сом",
        "currency_code": "KGS",
        "phone_prefix": "+996",
        "phone_format": "+996 XXX XXX XXX",
        "language": "ru",
        "country": "Kyrgyzstan",
        "country_code": "KG",
        "timezone": "Asia/Bishkek",
        "date_format": "DD.MM.YYYY",
        "price_format": "{amount} сом",
        "phone_validation_pattern": r"^\+996[0-9]{9}$",
        "postal_code_required": False,
        "tax_rate": 0.12,  # 12% VAT
        "shipping_zones": ["Бишкек", "Ош", "Джалал-Абад", "Токмок", "Каракол"],
        "payment_methods": ["card", "cash_on_delivery", "bank_transfer"],
        "default_language": "ru",
        "sms_expiry_minutes": 5,
        "verification_code_length": 6
    }
    
    US_CONFIG = {
        "currency": "$",
        "currency_code": "USD",
        "phone_prefix": "+1",
        "phone_format": "+1 (XXX) XXX-XXXX",
        "language": "en",
        "country": "United States",
        "country_code": "US",
        "timezone": "America/New_York",
        "date_format": "MM/DD/YYYY",
        "price_format": "${amount}",
        "phone_validation_pattern": r"^\+1[0-9]{10}$",
        "postal_code_required": True,
        "tax_rate": 0.08,  # 8% sales tax (varies by state)
        "shipping_zones": ["Continental US", "Alaska", "Hawaii", "Puerto Rico"],
        "payment_methods": ["card", "paypal", "apple_pay", "google_pay"],
        "default_language": "en",
        "sms_expiry_minutes": 10,
        "verification_code_length": 6
    }
    
    @classmethod
    def get_config(cls, market: Market) -> Dict[str, Any]:
        """Get configuration for specific market"""
        if market == Market.KG:
            return cls.KG_CONFIG
        elif market == Market.US:
            return cls.US_CONFIG
        else:
            raise ValueError(f"Unsupported market: {market}")
    
    @classmethod
    def get_currency_symbol(cls, market: Market) -> str:
        """Get currency symbol for market"""
        return cls.get_config(market)["currency"]
    
    @classmethod
    def get_language(cls, market: Market) -> str:
        """Get language for market"""
        return cls.get_config(market)["language"]
    
    @classmethod
    def get_phone_prefix(cls, market: Market) -> str:
        """Get phone prefix for market"""
        return cls.get_config(market)["phone_prefix"]

class RateLimitConfig(BaseSettings):
    """Rate limiting configuration"""
    enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    default_limit: int = Field(default=100, env="RATE_LIMIT_DEFAULT")
    default_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    auth_limit: int = Field(default=5, env="RATE_LIMIT_AUTH")
    auth_window: int = Field(default=300, env="RATE_LIMIT_AUTH_WINDOW")  # 5 minutes
    sms_limit: int = Field(default=3, env="RATE_LIMIT_SMS")
    sms_window: int = Field(default=3600, env="RATE_LIMIT_SMS_WINDOW")  # 1 hour

class LoggingConfig(BaseSettings):
    """Logging configuration"""
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    max_file_size: int = Field(default=10485760, env="LOG_MAX_FILE_SIZE")  # 10MB
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")

class Settings(BaseSettings):
    """Main application settings"""
    
    # Application
    app_name: str = Field(default="Marque E-commerce API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # Markets
    supported_markets: List[str] = Field(default=["kg", "us"], env="SUPPORTED_MARKETS")
    default_market: Market = Field(default=Market.KG, env="DEFAULT_MARKET")
    
    # Sub-configurations
    database: DatabaseConfig = DatabaseConfig()
    security: SecurityConfig = SecurityConfig()
    redis: RedisConfig = RedisConfig()
    external_services: ExternalServicesConfig = ExternalServicesConfig()
    rate_limit: RateLimitConfig = RateLimitConfig()
    logging: LoggingConfig = LoggingConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    @validator('supported_markets', pre=True)
    def parse_supported_markets(cls, v):
        if isinstance(v, str):
            return [market.strip() for market in v.split(',')]
        return v
    
    @validator('environment', pre=True)
    def parse_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @validator('default_market', pre=True)
    def parse_default_market(cls, v):
        if isinstance(v, str):
            return Market(v.lower())
        return v
    
    def get_market_config(self, market: Market) -> Dict[str, Any]:
        """Get market-specific configuration"""
        return MarketConfig.get_config(market)
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == Environment.PRODUCTION
    
    def get_database_url(self, market: Market) -> str:
        """Get database URL for specific market"""
        if market == Market.KG:
            return self.database.url_kg
        elif market == Market.US:
            return self.database.url_us
        else:
            raise ValueError(f"Unsupported market: {market}")

# Global settings instance
settings = Settings()

# Convenience functions
def get_settings() -> Settings:
    """Get application settings"""
    return settings

def get_market_config(market: Market) -> Dict[str, Any]:
    """Get market configuration"""
    return MarketConfig.get_config(market)

def get_database_url(market: Market) -> str:
    """Get database URL for market"""
    return settings.get_database_url(market)

def is_development() -> bool:
    """Check if in development mode"""
    return settings.is_development()

def is_production() -> bool:
    """Check if in production mode"""
    return settings.is_production()
