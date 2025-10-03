from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class UserAddress(Base):
    """User delivery addresses"""
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
    postal_code = Column(String(20), nullable=True)  # Postal code
    country = Column(String(100), nullable=True, default="Kyrgyzstan")  # Country
    is_default = Column(Boolean, default=False)  # Default address
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # TODO: Re-enable when User model relationships are fixed
    # user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"<UserAddress(id={self.id}, user_id={self.user_id}, title='{self.title}')>"

    @property
    def display_address(self):
        """Get formatted address for display"""
        parts = [self.street, self.building, self.apartment]
        return ", ".join([part for part in parts if part])

    def set_as_default(self, session):
        """Set this address as default (unset others)"""
        # Unset all other default addresses for this user
        session.query(UserAddress).filter(
            UserAddress.user_id == self.user_id,
            UserAddress.id != self.id
        ).update({"is_default": False})
        
        # Set this address as default
        self.is_default = True
        session.commit()

    @classmethod
    def get_default_address(cls, session, user_id):
        """Get user's default address"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_default == True,
            cls.is_active == True
        ).first()

    @classmethod
    def get_user_addresses(cls, session, user_id):
        """Get all active addresses for user"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_active == True
        ).order_by(cls.is_default.desc(), cls.created_at.desc()).all()

    @classmethod
    def create_address(cls, session, user_id, title, full_address, **kwargs):
        """Create new user address"""
        address = cls(
            user_id=user_id,
            title=title,
            full_address=full_address,
            **kwargs
        )
        
        session.add(address)
        session.commit()
        session.refresh(address)
        
        return address
