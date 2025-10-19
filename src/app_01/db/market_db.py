"""
Multi-Market Database Configuration
Handles different databases and configurations for KG and US markets
with production-ready connection pooling
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from typing import Generator, Dict, Any
from dotenv import load_dotenv
from enum import Enum

from src.app_01.core.config import settings

load_dotenv()

# Create a base class for all models
Base = declarative_base()

class Market(Enum):
    """Supported markets"""
    KG = "kg"  # Kyrgyzstan
    US = "us"  # United States

class MarketConfig:
    """Market-specific configuration"""
    
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
        "default_language": "ru"
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
        "default_language": "en"
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

class MarketDatabaseManager:
    """Manages multiple market databases"""
    
    def __init__(self):
        self.engines: Dict[Market, Any] = {}
        self.session_factories: Dict[Market, Any] = {}
        self.bases: Dict[Market, Any] = {}
        self._initialize_databases()
    
    def _initialize_databases(self):
        """Initialize database connections for all markets"""
        for market in Market:
            self._setup_market_database(market)
    
    def _setup_market_database(self, market: Market):
        """Setup database for specific market with production-ready connection pool"""
        # Get database URL from environment
        if market == Market.KG:
            database_url = settings.database.url_kg
        else:  # US
            database_url = settings.database.url_us
        
        # Create engine with production-ready connection pool settings
        engine = create_engine(
            database_url,
            # Connection Pool Settings
            poolclass=QueuePool,           # Use QueuePool for connection management
            pool_size=10,                  # Base connection pool size (10 concurrent connections)
            max_overflow=20,               # Allow up to 20 extra connections for traffic spikes
            pool_timeout=30,               # Wait up to 30 seconds for available connection
            pool_recycle=3600,             # Recycle connections after 1 hour (prevents stale connections)
            pool_pre_ping=True,            # Test connections before using (prevents "gone away" errors)
            # Performance Settings
            echo=False,                    # Disable SQL logging for performance
            echo_pool=False,               # Disable pool checkout/checkin logging
            # Connection Settings
            connect_args={
                "connect_timeout": 10,     # TCP connection timeout
            }
        )
        self.engines[market] = engine
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.session_factories[market] = SessionLocal
        
        # Create a new Base for this market to avoid metadata conflicts
        base = declarative_base()
        self.bases[market] = base
    
    def get_engine(self, market: Market):
        """Get database engine for market"""
        return self.engines[market]
    
    def get_session_factory(self, market: Market):
        """Get session factory for market"""
        return self.session_factories[market]
    
    def get_base(self, market: Market):
        """Get SQLAlchemy base for market"""
        return self.bases[market]
    
    def get_supported_markets(self) -> list:
        """Get list of supported market configurations"""
        return [MarketConfig.get_config(m) for m in Market]

    def get_db_session(self, market: Market) -> Generator:
        """Get database session for market"""
        SessionLocal = self.session_factories[market]
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Global database manager instance
db_manager = MarketDatabaseManager()

# Convenience functions for backward compatibility
def get_engine(market: Market = Market.KG):
    """Get database engine for market (defaults to KG)"""
    return db_manager.get_engine(market)

def get_session_factory(market: Market = Market.KG):
    """Get session factory for market (defaults to KG)"""
    return db_manager.get_session_factory(market)

def get_base(market: Market = Market.KG):
    """Get SQLAlchemy base for market (defaults to KG)"""
    return db_manager.get_base(market)

def get_db(market: Market = Market.KG) -> Generator:
    """Get database session for market (defaults to KG)"""
    SessionLocal = db_manager.get_session_factory(market)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Market detection utilities
def detect_market_from_phone(phone_number: str) -> Market:
    """
    Detect market from phone number
    Supports formats: +996XXX, 996XXX, +1XXX, 1XXX, and formats with spaces
    """
    # Normalize phone number - remove spaces and special characters
    clean_phone = phone_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Add '+' if missing
    if not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone
    
    # Detect market
    if clean_phone.startswith("+996"):
        return Market.KG
    elif clean_phone.startswith("+1"):
        return Market.US
    else:
        raise ValueError(f"Cannot detect market for phone number: {phone_number}")

def detect_market_from_domain(domain: str) -> Market:
    """Detect market from domain"""
    if "kg" in domain.lower() or "kyrgyzstan" in domain.lower():
        return Market.KG
    elif "us" in domain.lower() or "usa" in domain.lower() or "america" in domain.lower():
        return Market.US
    else:
        return Market.KG  # Default to KG

def format_phone_for_market(phone_number: str, market: Market) -> str:
    """Format phone number according to market standards"""
    config = MarketConfig.get_config(market)
    
    if market == Market.KG:
        # Format: +996 XXX XXX XXX
        if len(phone_number) == 13 and phone_number.startswith("+996"):
            return f"{phone_number[:4]} {phone_number[4:7]} {phone_number[7:10]} {phone_number[10:]}"
    elif market == Market.US:
        # Format: +1 (XXX) XXX-XXXX
        if len(phone_number) == 12 and phone_number.startswith("+1"):
            return f"+1 ({phone_number[2:5]}) {phone_number[5:8]}-{phone_number[8:]}"
    
    return phone_number

def format_price_for_market(amount: float, market: Market) -> str:
    """Format price according to market standards"""
    config = MarketConfig.get_config(market)
    return config["price_format"].format(amount=amount)

def get_market_config(market: Market) -> Dict[str, Any]:
    """Get configuration for market"""
    return MarketConfig.get_config(market)
