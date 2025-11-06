"""
Market-Aware User Model
Handles different user logic for KG and US markets
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db.market_db import get_base, Market, MarketConfig, detect_market_from_phone, format_phone_for_market
from typing import Optional
import re

class MarketUser:
    """Base class for market-aware user functionality"""
    
    @staticmethod
    def validate_phone_number(phone_number: str, market: Market) -> bool:
        """Validate phone number for specific market"""
        config = MarketConfig.get_config(market)
        pattern = config["phone_validation_pattern"]
        return bool(re.match(pattern, phone_number))
    
    @staticmethod
    def format_phone_number(phone_number: str, market: Market) -> str:
        """Format phone number for specific market"""
        return format_phone_for_market(phone_number, market)
    
    @staticmethod
    def get_default_country(market: Market) -> str:
        """Get default country for market"""
        config = MarketConfig.get_config(market)
        return config["country"]
    
    @staticmethod
    def get_default_language(market: Market) -> str:
        """Get default language for market"""
        config = MarketConfig.get_config(market)
        return config["default_language"]
    
    @staticmethod
    def get_currency(market: Market) -> str:
        """Get currency for market"""
        config = MarketConfig.get_config(market)
        return config["currency"]
    
    @staticmethod
    def get_currency_code(market: Market) -> str:
        """Get currency code for market"""
        config = MarketConfig.get_config(market)
        return config["currency_code"]

# KG Market User Model
KGBase = get_base(Market.KG)

class UserKG(KGBase):
    """User model for Kyrgyzstan market"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)  # +996 XXX XXX XXX
    full_name = Column(String(255), nullable=True)  # Анна Ахматова
    profile_image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    market = Column(String(10), default="kg", nullable=False)
    language = Column(String(10), default="ru", nullable=False)
    country = Column(String(100), default="Kyrgyzstan", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Legacy fields (optional, for migration)
    email = Column(String(255), unique=True, nullable=True, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=True)

    def __init__(self, **kwargs):
        """Initialize user with default values"""
        # Set defaults for fields not provided
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_verified', False)
        kwargs.setdefault('market', 'kg')
        kwargs.setdefault('language', 'ru')
        kwargs.setdefault('country', 'Kyrgyzstan')
        if 'created_at' not in kwargs:
            from datetime import datetime
            kwargs['created_at'] = datetime.utcnow()
        if 'updated_at' not in kwargs:
            from datetime import datetime
            kwargs['updated_at'] = datetime.utcnow()
        super().__init__(**kwargs)

    # Relationships
    # TODO: Re-enable when market-specific models are properly integrated
    # Note: These relationships reference models with different Base instances
    # and need proper circular import handling
    # reviews = relationship("ReviewKG", back_populates="user")
    # cart_orders = relationship("CartOrderKG", back_populates="user")
    # interactions = relationship("InteractionKG", back_populates="user")
    # orders = relationship("OrderKG", back_populates="user")
    # addresses = relationship("UserAddressKG", back_populates="user", cascade="all, delete-orphan")
    # payment_methods = relationship("UserPaymentMethodKG", back_populates="user", cascade="all, delete-orphan")
    # notifications = relationship("UserNotificationKG", back_populates="user", cascade="all, delete-orphan")
    # phone_verifications = relationship("PhoneVerificationKG", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserKG(id={self.id}, phone_number='{self.phone_number}', full_name='{self.full_name}')>"

    @property
    def display_name(self):
        """Get display name for user"""
        return self.full_name or f"User {self.phone_number}"

    @property
    def formatted_phone(self):
        """Get formatted phone number for KG market"""
        return format_phone_for_market(self.phone_number, Market.KG)

    @property
    def currency(self):
        """Get currency for KG market"""
        return "сом"

    @property
    def currency_code(self):
        """Get currency code for KG market"""
        return "KGS"

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = func.now()

    @classmethod
    def get_by_phone(cls, session, phone_number):
        """Get user by phone number"""
        return session.query(cls).filter(cls.phone_number == phone_number).first()

    @classmethod
    def create_user(cls, session, phone_number, full_name=None, market=None):
        """Create new user for KG market"""
        # Validate phone number for KG market
        if not MarketUser.validate_phone_number(phone_number, Market.KG):
            raise ValueError(f"Invalid KG phone number format: {phone_number}")
        
        # Use provided market or default to "kg"
        user_market = market if market is not None else "kg"
        
        user = cls(
            phone_number=phone_number,
            full_name=full_name,
            is_verified=False,
            market=user_market,
            language="ru",
            country="Kyrgyzstan"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

# US Market User Model
USBase = get_base(Market.US)

class UserUS(USBase):
    """User model for United States market"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)  # +1 (XXX) XXX-XXXX
    full_name = Column(String(255), nullable=True)  # John Smith
    profile_image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    market = Column(String(10), default="us", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    country = Column(String(100), default="United States", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Legacy fields (optional, for migration)
    email = Column(String(255), unique=True, nullable=True, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=True)

    def __init__(self, **kwargs):
        """Initialize user with default values"""
        # Set defaults for fields not provided
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_verified', False)
        kwargs.setdefault('market', 'us')
        kwargs.setdefault('language', 'en')
        kwargs.setdefault('country', 'United States')
        if 'created_at' not in kwargs:
            from datetime import datetime
            kwargs['created_at'] = datetime.utcnow()
        if 'updated_at' not in kwargs:
            from datetime import datetime
            kwargs['updated_at'] = datetime.utcnow()
        super().__init__(**kwargs)

    # Relationships
    # TODO: Re-enable when market-specific models are properly integrated
    # Note: These relationships reference models with different Base instances
    # and need proper circular import handling
    # reviews = relationship("ReviewUS", back_populates="user")
    # cart_orders = relationship("CartOrderUS", back_populates="user")
    # interactions = relationship("InteractionUS", back_populates="user")
    # orders = relationship("OrderUS", back_populates="user")
    # addresses = relationship("UserAddressUS", back_populates="user", cascade="all, delete-orphan")
    # payment_methods = relationship("UserPaymentMethodUS", back_populates="user", cascade="all, delete-orphan")
    # notifications = relationship("UserNotificationUS", back_populates="user", cascade="all, delete-orphan")
    # phone_verifications = relationship("PhoneVerificationUS", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserUS(id={self.id}, phone_number='{self.phone_number}', full_name='{self.full_name}')>"

    @property
    def display_name(self):
        """Get display name for user"""
        return self.full_name or f"User {self.phone_number}"

    @property
    def formatted_phone(self):
        """Get formatted phone number for US market"""
        return format_phone_for_market(self.phone_number, Market.US)

    @property
    def currency(self):
        """Get currency for US market"""
        return "$"

    @property
    def currency_code(self):
        """Get currency code for US market"""
        return "USD"

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = func.now()

    @classmethod
    def get_by_phone(cls, session, phone_number):
        """Get user by phone number"""
        return session.query(cls).filter(cls.phone_number == phone_number).first()

    @classmethod
    def create_user(cls, session, phone_number, full_name=None, market=None):
        """Create new user for US market"""
        # Validate phone number for US market
        if not MarketUser.validate_phone_number(phone_number, Market.US):
            raise ValueError(f"Invalid US phone number format: {phone_number}")
        
        # Use provided market or default to "us"
        user_market = market if market is not None else "us"
        
        user = cls(
            phone_number=phone_number,
            full_name=full_name,
            is_verified=False,
            market=user_market,
            language="en",
            country="United States"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

# Factory function to get the correct User model for a market
def get_user_model(market: Market):
    """Get the correct User model for a market"""
    if market == Market.KG:
        return UserKG
    elif market == Market.US:
        return UserUS
    else:
        raise ValueError(f"Unsupported market: {market}")

# Factory function to get user by phone with market detection
def get_user_by_phone_with_market_detection(phone_number: str):
    """Get user by phone number with automatic market detection"""
    try:
        market = detect_market_from_phone(phone_number)
        user_model = get_user_model(market)
        return user_model, market
    except ValueError:
        raise ValueError(f"Cannot detect market for phone number: {phone_number}")
