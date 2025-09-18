from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class PhoneVerification(Base):
    """Phone number verification codes for authentication"""
    __tablename__ = "phone_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nullable for new users
    phone_number = Column(String(20), nullable=False, index=True)  # +996 505 23 12 55
    verification_code = Column(String(10), nullable=False)  # 4-6 digit code
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="phone_verifications")

    def __repr__(self):
        return f"<PhoneVerification(id={self.id}, phone='{self.phone_number}', code='{self.verification_code}')>"

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
        """Create new verification code"""
        import random
        import secrets
        from datetime import datetime, timedelta
        
        # Generate 6-digit verification code
        verification_code = str(random.randint(100000, 999999))
        
        # Set expiration time (10 minutes from now)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        verification = cls(
            user_id=user_id,
            phone_number=phone_number,
            verification_code=verification_code,
            expires_at=expires_at
        )
        
        session.add(verification)
        session.commit()
        session.refresh(verification)
        
        return verification

    @classmethod
    def verify_code(cls, session, phone_number, verification_code):
        """Verify phone number with code"""
        verification = session.query(cls).filter(
            cls.phone_number == phone_number,
            cls.verification_code == verification_code,
            cls.is_used == False,
            cls.expires_at > func.now()
        ).first()
        
        if verification:
            verification.mark_as_used()
            session.commit()
            return verification
        
        return None

    @classmethod
    def get_latest_code(cls, session, phone_number):
        """Get latest verification code for phone number"""
        return session.query(cls).filter(
            cls.phone_number == phone_number,
            cls.is_used == False,
            cls.expires_at > func.now()
        ).order_by(cls.created_at.desc()).first()

    @classmethod
    def cleanup_expired(cls, session):
        """Clean up expired verification codes"""
        session.query(cls).filter(
            cls.expires_at < func.now()
        ).delete()
        session.commit()