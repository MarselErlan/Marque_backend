"""
Market-Aware User Payment Method Models
Handles different payment logic for KG and US markets
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db.market_db import get_base, Market, MarketConfig
from typing import Optional

# KG Market User Payment Method Model
KGBase = get_base(Market.KG)

class UserPaymentMethodKG(KGBase):
    """User payment methods for Kyrgyzstan market"""
    __tablename__ = "user_payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    payment_type = Column(String(20), nullable=False, default="card")  # card, cash_on_delivery, bank_transfer
    card_type = Column(String(20), nullable=True)  # visa, mastercard, elcard (local KG card)
    card_number_masked = Column(String(20), nullable=True)  # **** **** 2352
    card_holder_name = Column(String(100), nullable=True)  # Card holder name
    expiry_month = Column(String(2), nullable=True)  # MM
    expiry_year = Column(String(4), nullable=True)  # YYYY
    bank_name = Column(String(100), nullable=True)  # Bank name for KG market
    is_default = Column(Boolean, default=False)  # Default payment method
    is_active = Column(Boolean, default=True)
    market = Column(String(10), default="kg", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # TODO: Re-enable when UserKG model relationships are fixed
    # user = relationship("UserKG", back_populates="payment_methods")

    def __repr__(self):
        return f"<UserPaymentMethodKG(id={self.id}, user_id={self.user_id}, type='{self.payment_type}')>"

    @property
    def display_name(self):
        """Get display name for payment method in KG market"""
        if self.payment_type == "card" and self.card_number_masked:
            if self.card_type == "elcard":
                return f"Элкарт **** **** {self.card_number_masked}"
            else:
                card_type_name = self.card_type.title() if self.card_type else "Банковская карта"
                return f"{card_type_name} **** **** {self.card_number_masked}"
        elif self.payment_type == "cash_on_delivery":
            return "Наличные при доставке"
        elif self.payment_type == "bank_transfer":
            return f"Банковский перевод ({self.bank_name})"
        return f"Способ оплаты {self.id}"

    @property
    def card_type_display(self):
        """Get card type display name for KG market"""
        card_types = {
            "visa": "Visa",
            "mastercard": "Mastercard",
            "elcard": "Элкарт"
        }
        return card_types.get(self.card_type, "Банковская карта")

    def set_as_default(self, session):
        """Set this payment method as default (unset others)"""
        # Unset all other default payment methods for this user
        session.query(UserPaymentMethodKG).filter(
            UserPaymentMethodKG.user_id == self.user_id,
            UserPaymentMethodKG.id != self.id
        ).update({"is_default": False})
        
        # Set this payment method as default
        self.is_default = True
        session.commit()

    @classmethod
    def get_default_payment_method(cls, session, user_id):
        """Get user's default payment method for KG market"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_default == True,
            cls.is_active == True,
            cls.market == "kg"
        ).first()

    @classmethod
    def get_user_payment_methods(cls, session, user_id):
        """Get all active payment methods for user in KG market"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_active == True,
            cls.market == "kg"
        ).order_by(cls.is_default.desc(), cls.created_at.desc()).all()

    @classmethod
    def create_card(cls, session, user_id, card_number, card_holder_name, expiry_month, expiry_year, bank_name=None):
        """Create new card payment method for KG market"""
        # Mask card number (show only last 4 digits)
        card_number_masked = card_number[-4:] if len(card_number) >= 4 else card_number
        
        # Determine card type for KG market
        card_type = None
        if card_number.startswith("4"):
            card_type = "visa"
        elif card_number.startswith("5") or card_number.startswith("2"):
            card_type = "mastercard"
        elif card_number.startswith("9"):  # Elcard typically starts with 9
            card_type = "elcard"
        
        payment_method = cls(
            user_id=user_id,
            payment_type="card",
            card_type=card_type,
            card_number_masked=card_number_masked,
            card_holder_name=card_holder_name,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            bank_name=bank_name,
            market="kg"
        )
        
        session.add(payment_method)
        session.commit()
        session.refresh(payment_method)
        
        return payment_method

    @classmethod
    def create_cash_on_delivery(cls, session, user_id):
        """Create cash on delivery payment method for KG market"""
        payment_method = cls(
            user_id=user_id,
            payment_type="cash_on_delivery",
            market="kg"
        )
        
        session.add(payment_method)
        session.commit()
        session.refresh(payment_method)
        
        return payment_method

    @classmethod
    def create_bank_transfer(cls, session, user_id, bank_name):
        """Create bank transfer payment method for KG market"""
        payment_method = cls(
            user_id=user_id,
            payment_type="bank_transfer",
            bank_name=bank_name,
            market="kg"
        )
        
        session.add(payment_method)
        session.commit()
        session.refresh(payment_method)
        
        return payment_method

# US Market User Payment Method Model
USBase = get_base(Market.US)

class UserPaymentMethodUS(USBase):
    """User payment methods for United States market"""
    __tablename__ = "user_payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    payment_type = Column(String(20), nullable=False, default="card")  # card, paypal, apple_pay, google_pay
    card_type = Column(String(20), nullable=True)  # visa, mastercard, amex, discover
    card_number_masked = Column(String(20), nullable=True)  # **** **** 2352
    card_holder_name = Column(String(100), nullable=True)  # Card holder name
    expiry_month = Column(String(2), nullable=True)  # MM
    expiry_year = Column(String(4), nullable=True)  # YYYY
    paypal_email = Column(String(255), nullable=True)  # PayPal email
    is_default = Column(Boolean, default=False)  # Default payment method
    is_active = Column(Boolean, default=True)
    market = Column(String(10), default="us", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # TODO: Re-enable when UserUS model relationships are fixed
    # user = relationship("UserUS", back_populates="payment_methods")

    def __repr__(self):
        return f"<UserPaymentMethodUS(id={self.id}, user_id={self.user_id}, type='{self.payment_type}')>"

    @property
    def display_name(self):
        """Get display name for payment method in US market"""
        if self.payment_type == "card" and self.card_number_masked:
            card_type_name = self.card_type.title() if self.card_type else "Bank Card"
            return f"{card_type_name} **** **** {self.card_number_masked}"
        elif self.payment_type == "paypal":
            return f"PayPal ({self.paypal_email})"
        elif self.payment_type == "apple_pay":
            return "Apple Pay"
        elif self.payment_type == "google_pay":
            return "Google Pay"
        return f"Payment Method {self.id}"

    @property
    def card_type_display(self):
        """Get card type display name for US market"""
        card_types = {
            "visa": "Visa",
            "mastercard": "Mastercard",
            "amex": "American Express",
            "discover": "Discover"
        }
        return card_types.get(self.card_type, "Bank Card")

    def set_as_default(self, session):
        """Set this payment method as default (unset others)"""
        # Unset all other default payment methods for this user
        session.query(UserPaymentMethodUS).filter(
            UserPaymentMethodUS.user_id == self.user_id,
            UserPaymentMethodUS.id != self.id
        ).update({"is_default": False})
        
        # Set this payment method as default
        self.is_default = True
        session.commit()

    @classmethod
    def get_default_payment_method(cls, session, user_id):
        """Get user's default payment method for US market"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_default == True,
            cls.is_active == True,
            cls.market == "us"
        ).first()

    @classmethod
    def get_user_payment_methods(cls, session, user_id):
        """Get all active payment methods for user in US market"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_active == True,
            cls.market == "us"
        ).order_by(cls.is_default.desc(), cls.created_at.desc()).all()

    @classmethod
    def create_card(cls, session, user_id, card_number, card_holder_name, expiry_month, expiry_year):
        """Create new card payment method for US market"""
        # Mask card number (show only last 4 digits)
        card_number_masked = card_number[-4:] if len(card_number) >= 4 else card_number
        
        # Determine card type for US market
        card_type = None
        if card_number.startswith("4"):
            card_type = "visa"
        elif card_number.startswith("5") or card_number.startswith("2"):
            card_type = "mastercard"
        elif card_number.startswith("3"):
            card_type = "amex"
        elif card_number.startswith("6"):
            card_type = "discover"
        
        payment_method = cls(
            user_id=user_id,
            payment_type="card",
            card_type=card_type,
            card_number_masked=card_number_masked,
            card_holder_name=card_holder_name,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            market="us"
        )
        
        session.add(payment_method)
        session.commit()
        session.refresh(payment_method)
        
        return payment_method

    @classmethod
    def create_paypal(cls, session, user_id, paypal_email):
        """Create PayPal payment method for US market"""
        payment_method = cls(
            user_id=user_id,
            payment_type="paypal",
            paypal_email=paypal_email,
            market="us"
        )
        
        session.add(payment_method)
        session.commit()
        session.refresh(payment_method)
        
        return payment_method

    @classmethod
    def create_apple_pay(cls, session, user_id):
        """Create Apple Pay payment method for US market"""
        payment_method = cls(
            user_id=user_id,
            payment_type="apple_pay",
            market="us"
        )
        
        session.add(payment_method)
        session.commit()
        session.refresh(payment_method)
        
        return payment_method

    @classmethod
    def create_google_pay(cls, session, user_id):
        """Create Google Pay payment method for US market"""
        payment_method = cls(
            user_id=user_id,
            payment_type="google_pay",
            market="us"
        )
        
        session.add(payment_method)
        session.commit()
        session.refresh(payment_method)
        
        return payment_method

# Factory functions
def get_user_payment_method_model(market: Market):
    """Get the correct UserPaymentMethod model for a market"""
    if market == Market.KG:
        return UserPaymentMethodKG
    elif market == Market.US:
        return UserPaymentMethodUS
    else:
        raise ValueError(f"Unsupported market: {market}")

def create_payment_method_for_market(session, market: Market, user_id: int, payment_type: str, **kwargs):
    """Create payment method with market-specific logic"""
    payment_model = get_user_payment_method_model(market)
    
    if payment_type == "card":
        return payment_model.create_card(session, user_id, **kwargs)
    elif payment_type == "cash_on_delivery" and market == Market.KG:
        return payment_model.create_cash_on_delivery(session, user_id)
    elif payment_type == "bank_transfer" and market == Market.KG:
        return payment_model.create_bank_transfer(session, user_id, **kwargs)
    elif payment_type == "paypal" and market == Market.US:
        return payment_model.create_paypal(session, user_id, **kwargs)
    elif payment_type == "apple_pay" and market == Market.US:
        return payment_model.create_apple_pay(session, user_id)
    elif payment_type == "google_pay" and market == Market.US:
        return payment_model.create_google_pay(session, user_id)
    else:
        raise ValueError(f"Unsupported payment type {payment_type} for market {market}")
