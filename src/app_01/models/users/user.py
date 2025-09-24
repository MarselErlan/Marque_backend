from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class User(Base):
    """User model for phone number authentication and user management"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)  # +996 505 23 12 55
    full_name = Column(String(255), nullable=True)  # Анна Ахматова
    profile_image_url = Column(String(500), nullable=True)  # Profile photo URL
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Phone number verified
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Legacy fields (optional, for migration)
    email = Column(String(255), unique=True, nullable=True, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=True)  # Keep for existing users

    # Relationships
    reviews = relationship("Review", back_populates="user")
    cart = relationship("Cart", back_populates="user", uselist=False)
    wishlist = relationship("Wishlist", back_populates="user", uselist=False)
    interactions = relationship("Interaction", back_populates="user")
    orders = relationship("Order", back_populates="user")
    admin_profile = relationship("Admin", back_populates="user", uselist=False)
    addresses = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
    payment_methods = relationship("UserPaymentMethod", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("UserNotification", back_populates="user", cascade="all, delete-orphan")
    phone_verifications = relationship("PhoneVerification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, phone_number='{self.phone_number}', full_name='{self.full_name}')>"

    @property
    def display_name(self):
        """Get display name for user"""
        return self.full_name or f"User {self.phone_number}"

    @property
    def formatted_phone(self):
        """Get formatted phone number"""
        return self.phone_number

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = func.now()

    @classmethod
    def get_by_phone(cls, session, phone_number):
        """Get user by phone number"""
        return session.query(cls).filter(cls.phone_number == phone_number).first()

    @classmethod
    def create_user(cls, session, phone_number, full_name=None):
        """Create new user with phone number"""
        user = cls(
            phone_number=phone_number,
            full_name=full_name,
            is_verified=False
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
