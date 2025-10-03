"""
Market-Aware User Address Models
Handles different address logic for KG and US markets
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db.market_db import get_base, Market, MarketConfig
from typing import Optional

# KG Market User Address Model
KGBase = get_base(Market.KG)

class UserAddressKG(KGBase):
    """User delivery addresses for Kyrgyzstan market"""
    __tablename__ = "user_addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    address_type = Column(String(20), nullable=False, default="home")  # home, work, other
    title = Column(String(100), nullable=False)  # "Адрес ул. Юнусалиева, 34"
    full_address = Column(Text, nullable=False)  # Full address text
    street = Column(String(200), nullable=True)  # Street name
    building = Column(String(50), nullable=True)  # Building number
    apartment = Column(String(20), nullable=True)  # Apartment number
    city = Column(String(100), nullable=True)  # City name
    postal_code = Column(String(20), nullable=True)  # Postal code (optional for KG)
    country = Column(String(100), nullable=True, default="Kyrgyzstan")  # Country
    region = Column(String(100), nullable=True)  # Region/Oblast for KG
    district = Column(String(100), nullable=True)  # District/Rayon for KG
    is_default = Column(Boolean, default=False)  # Default address
    is_active = Column(Boolean, default=True)
    market = Column(String(10), default="kg", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # TODO: Re-enable when UserKG model relationships are fixed
    # user = relationship("UserKG", back_populates="addresses")

    def __repr__(self):
        return f"<UserAddressKG(id={self.id}, user_id={self.user_id}, title='{self.title}')>"

    @property
    def display_address(self):
        """Get formatted address for display in KG market"""
        parts = []
        if self.street:
            parts.append(self.street)
        if self.building:
            parts.append(self.building)
        if self.apartment:
            parts.append(f"кв. {self.apartment}")
        if self.city:
            parts.append(self.city)
        if self.region:
            parts.append(self.region)
        return ", ".join(parts)

    @property
    def full_display_address(self):
        """Get full formatted address for KG market"""
        parts = [self.display_address]
        if self.country and self.country != "Kyrgyzstan":
            parts.append(self.country)
        return ", ".join(parts)

    def set_as_default(self, session):
        """Set this address as default (unset others)"""
        # Unset all other default addresses for this user
        session.query(UserAddressKG).filter(
            UserAddressKG.user_id == self.user_id,
            UserAddressKG.id != self.id
        ).update({"is_default": False})
        
        # Set this address as default
        self.is_default = True
        session.commit()

    @classmethod
    def get_default_address(cls, session, user_id):
        """Get user's default address for KG market"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_default == True,
            cls.is_active == True,
            cls.market == "kg"
        ).first()

    @classmethod
    def get_user_addresses(cls, session, user_id):
        """Get all active addresses for user in KG market"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_active == True,
            cls.market == "kg"
        ).order_by(cls.is_default.desc(), cls.created_at.desc()).all()

    @classmethod
    def create_address(cls, session, user_id, title, full_address, **kwargs):
        """Create new user address for KG market"""
        address = cls(
            user_id=user_id,
            title=title,
            full_address=full_address,
            market="kg",
            country="Kyrgyzstan",
            **kwargs
        )
        
        session.add(address)
        session.commit()
        session.refresh(address)
        
        return address

# US Market User Address Model
USBase = get_base(Market.US)

class UserAddressUS(USBase):
    """User delivery addresses for United States market"""
    __tablename__ = "user_addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    address_type = Column(String(20), nullable=False, default="home")  # home, work, other
    title = Column(String(100), nullable=False)  # "123 Main St, New York, NY"
    full_address = Column(Text, nullable=False)  # Full address text
    street_address = Column(String(200), nullable=True)  # Street address
    street_number = Column(String(20), nullable=True)  # Street number
    street_name = Column(String(200), nullable=True)  # Street name
    apartment_unit = Column(String(20), nullable=True)  # Apartment/Unit number
    city = Column(String(100), nullable=True)  # City name
    state = Column(String(50), nullable=True)  # State (required for US)
    postal_code = Column(String(20), nullable=True)  # ZIP code (required for US)
    country = Column(String(100), nullable=True, default="United States")  # Country
    is_default = Column(Boolean, default=False)  # Default address
    is_active = Column(Boolean, default=True)
    market = Column(String(10), default="us", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # TODO: Re-enable when UserUS model relationships are fixed
    # user = relationship("UserUS", back_populates="addresses")

    def __repr__(self):
        return f"<UserAddressUS(id={self.id}, user_id={self.user_id}, title='{self.title}')>"

    @property
    def display_address(self):
        """Get formatted address for display in US market"""
        parts = []
        if self.street_address:
            parts.append(self.street_address)
        elif self.street_number and self.street_name:
            parts.append(f"{self.street_number} {self.street_name}")
        if self.apartment_unit:
            parts.append(f"Apt {self.apartment_unit}")
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.postal_code:
            parts.append(self.postal_code)
        return ", ".join(parts)

    @property
    def full_display_address(self):
        """Get full formatted address for US market"""
        parts = [self.display_address]
        if self.country and self.country != "United States":
            parts.append(self.country)
        return ", ".join(parts)

    def set_as_default(self, session):
        """Set this address as default (unset others)"""
        # Unset all other default addresses for this user
        session.query(UserAddressUS).filter(
            UserAddressUS.user_id == self.user_id,
            UserAddressUS.id != self.id
        ).update({"is_default": False})
        
        # Set this address as default
        self.is_default = True
        session.commit()

    @classmethod
    def get_default_address(cls, session, user_id):
        """Get user's default address for US market"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_default == True,
            cls.is_active == True,
            cls.market == "us"
        ).first()

    @classmethod
    def get_user_addresses(cls, session, user_id):
        """Get all active addresses for user in US market"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_active == True,
            cls.market == "us"
        ).order_by(cls.is_default.desc(), cls.created_at.desc()).all()

    @classmethod
    def create_address(cls, session, user_id, title, full_address, **kwargs):
        """Create new user address for US market"""
        address = cls(
            user_id=user_id,
            title=title,
            full_address=full_address,
            market="us",
            country="United States",
            **kwargs
        )
        
        session.add(address)
        session.commit()
        session.refresh(address)
        
        return address

# Factory functions
def get_user_address_model(market: Market):
    """Get the correct UserAddress model for a market"""
    if market == Market.KG:
        return UserAddressKG
    elif market == Market.US:
        return UserAddressUS
    else:
        raise ValueError(f"Unsupported market: {market}")

def create_address_for_market(session, market: Market, user_id: int, title: str, full_address: str, **kwargs):
    """Create address with market-specific logic"""
    address_model = get_user_address_model(market)
    return address_model.create_address(session, user_id, title, full_address, **kwargs)

def get_user_addresses_for_market(session, market: Market, user_id: int):
    """Get user addresses for specific market"""
    address_model = get_user_address_model(market)
    return address_model.get_user_addresses(session, user_id)
