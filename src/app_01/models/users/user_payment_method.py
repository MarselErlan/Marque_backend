from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class UserPaymentMethod(Base):
    """User payment methods (bank cards, etc.)"""
    __tablename__ = "user_payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    payment_type = Column(String(20), nullable=False, default="card")  # card, wallet, cash
    card_type = Column(String(20), nullable=True)  # visa, mastercard, mir
    card_number_masked = Column(String(20), nullable=True)  # **** **** 2352
    card_holder_name = Column(String(100), nullable=True)  # Card holder name
    expiry_month = Column(String(2), nullable=True)  # MM
    expiry_year = Column(String(4), nullable=True)  # YYYY
    is_default = Column(Boolean, default=False)  # Default payment method
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="payment_methods")

    def __repr__(self):
        return f"<UserPaymentMethod(id={self.id}, user_id={self.user_id}, type='{self.payment_type}')>"

    @property
    def display_name(self):
        """Get display name for payment method"""
        if self.payment_type == "card" and self.card_number_masked:
            card_type_name = self.card_type.title() if self.card_type else "Банковская карта"
            return f"{card_type_name} **** **** {self.card_number_masked}"
        return f"Способ оплаты {self.id}"

    @property
    def card_type_display(self):
        """Get card type display name"""
        card_types = {
            "visa": "Visa",
            "mastercard": "Mastercard",
            "mir": "МИР"
        }
        return card_types.get(self.card_type, "Банковская карта")

    def set_as_default(self, session):
        """Set this payment method as default (unset others)"""
        # Unset all other default payment methods for this user
        session.query(UserPaymentMethod).filter(
            UserPaymentMethod.user_id == self.user_id,
            UserPaymentMethod.id != self.id
        ).update({"is_default": False})
        
        # Set this payment method as default
        self.is_default = True
        session.commit()

    @classmethod
    def get_default_payment_method(cls, session, user_id):
        """Get user's default payment method"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_default == True,
            cls.is_active == True
        ).first()

    @classmethod
    def get_user_payment_methods(cls, session, user_id):
        """Get all active payment methods for user"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_active == True
        ).order_by(cls.is_default.desc(), cls.created_at.desc()).all()

    @classmethod
    def create_card(cls, session, user_id, card_number, card_holder_name, expiry_month, expiry_year):
        """Create new card payment method"""
        # Mask card number (show only last 4 digits)
        card_number_masked = card_number[-4:] if len(card_number) >= 4 else card_number
        
        # Determine card type
        card_type = None
        if card_number.startswith("4"):
            card_type = "visa"
        elif card_number.startswith("5") or card_number.startswith("2"):
            card_type = "mastercard"
        elif card_number.startswith("2"):
            card_type = "mir"
        
        payment_method = cls(
            user_id=user_id,
            payment_type="card",
            card_type=card_type,
            card_number_masked=card_number_masked,
            card_holder_name=card_holder_name,
            expiry_month=expiry_month,
            expiry_year=expiry_year
        )
        
        session.add(payment_method)
        session.commit()
        session.refresh(payment_method)
        
        return payment_method
