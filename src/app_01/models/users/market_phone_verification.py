"""
Market-Aware Phone Verification Models
Handles different phone verification logic for KG and US markets
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db.market_db import get_base, Market, MarketConfig, detect_market_from_phone
from datetime import datetime, timedelta
import random

# KG Market Phone Verification Model
KGBase = get_base(Market.KG)

class PhoneVerificationKG(KGBase):
    """Phone verification for Kyrgyzstan market"""
    __tablename__ = "phone_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)  # +996 XXX XXX XXX
    verification_code = Column(String(10), nullable=False)  # 4-6 digit code
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    market = Column(String(10), default="kg", nullable=False)

    # Relationships
    user = relationship("UserKG", back_populates="phone_verifications")

    def __repr__(self):
        return f"<PhoneVerificationKG(id={self.id}, phone='{self.phone_number}', code='{self.verification_code}')>"

    @property
    def is_expired(self):
        """Check if verification code is expired"""
        return func.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if verification code is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired

    def mark_as_used(self):
        """Mark verification code as used"""
        self.is_used = True
        self.verified_at = func.now()

    @classmethod
    def create_verification(cls, session, phone_number, user_id=None):
        """Create new verification code for KG market"""
        # Generate 6-digit verification code
        verification_code = str(random.randint(100000, 999999))
        
        # Set expiration time (10 minutes from now)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        verification = cls(
            user_id=user_id,
            phone_number=phone_number,
            verification_code=verification_code,
            expires_at=expires_at,
            market="kg"
        )
        
        session.add(verification)
        session.commit()
        session.refresh(verification)
        
        return verification

    @classmethod
    def verify_code(cls, session, phone_number, verification_code):
        """Verify phone number with code for KG market"""
        verification = session.query(cls).filter(
            cls.phone_number == phone_number,
            cls.verification_code == verification_code,
            cls.is_used == False,
            cls.expires_at > func.now(),
            cls.market == "kg"
        ).first()
        
        if verification:
            verification.mark_as_used()
            session.commit()
            return verification
        
        return None

    @classmethod
    def get_latest_code(cls, session, phone_number):
        """Get latest verification code for phone number in KG market"""
        return session.query(cls).filter(
            cls.phone_number == phone_number,
            cls.is_used == False,
            cls.expires_at > func.now(),
            cls.market == "kg"
        ).order_by(cls.created_at.desc()).first()

    @classmethod
    def cleanup_expired(cls, session):
        """Clean up expired verification codes for KG market"""
        session.query(cls).filter(
            cls.expires_at < func.now(),
            cls.market == "kg"
        ).delete()
        session.commit()

# US Market Phone Verification Model
USBase = get_base(Market.US)

class PhoneVerificationUS(USBase):
    """Phone verification for United States market"""
    __tablename__ = "phone_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)  # +1 (XXX) XXX-XXXX
    verification_code = Column(String(10), nullable=False)  # 4-6 digit code
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    market = Column(String(10), default="us", nullable=False)

    # Relationships
    user = relationship("UserUS", back_populates="phone_verifications")

    def __repr__(self):
        return f"<PhoneVerificationUS(id={self.id}, phone='{self.phone_number}', code='{self.verification_code}')>"

    @property
    def is_expired(self):
        """Check if verification code is expired"""
        return func.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if verification code is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired

    def mark_as_used(self):
        """Mark verification code as used"""
        self.is_used = True
        self.verified_at = func.now()

    @classmethod
    def create_verification(cls, session, phone_number, user_id=None):
        """Create new verification code for US market"""
        # Generate 6-digit verification code
        verification_code = str(random.randint(100000, 999999))
        
        # Set expiration time (15 minutes from now - longer for US market)
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        verification = cls(
            user_id=user_id,
            phone_number=phone_number,
            verification_code=verification_code,
            expires_at=expires_at,
            market="us"
        )
        
        session.add(verification)
        session.commit()
        session.refresh(verification)
        
        return verification

    @classmethod
    def verify_code(cls, session, phone_number, verification_code):
        """Verify phone number with code for US market"""
        verification = session.query(cls).filter(
            cls.phone_number == phone_number,
            cls.verification_code == verification_code,
            cls.is_used == False,
            cls.expires_at > func.now(),
            cls.market == "us"
        ).first()
        
        if verification:
            verification.mark_as_used()
            session.commit()
            return verification
        
        return None

    @classmethod
    def get_latest_code(cls, session, phone_number):
        """Get latest verification code for phone number in US market"""
        return session.query(cls).filter(
            cls.phone_number == phone_number,
            cls.is_used == False,
            cls.expires_at > func.now(),
            cls.market == "us"
        ).order_by(cls.created_at.desc()).first()

    @classmethod
    def cleanup_expired(cls, session):
        """Clean up expired verification codes for US market"""
        session.query(cls).filter(
            cls.expires_at < func.now(),
            cls.market == "us"
        ).delete()
        session.commit()

# Factory functions
def get_phone_verification_model(market: Market):
    """Get the correct PhoneVerification model for a market"""
    if market == Market.KG:
        return PhoneVerificationKG
    elif market == Market.US:
        return PhoneVerificationUS
    else:
        raise ValueError(f"Unsupported market: {market}")

def create_verification_for_market(session, phone_number, user_id=None):
    """Create verification code with automatic market detection"""
    try:
        market = detect_market_from_phone(phone_number)
        verification_model = get_phone_verification_model(market)
        return verification_model.create_verification(session, phone_number, user_id)
    except ValueError:
        raise ValueError(f"Cannot detect market for phone number: {phone_number}")

def verify_code_for_market(session, phone_number, verification_code):
    """Verify code with automatic market detection"""
    try:
        market = detect_market_from_phone(phone_number)
        verification_model = get_phone_verification_model(market)
        return verification_model.verify_code(session, phone_number, verification_code)
    except ValueError:
        raise ValueError(f"Cannot detect market for phone number: {phone_number}")
