from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class CartOrder(Base):
    """Shopping cart and order management model
    NOTE: This model seems to duplicate Cart functionality.
    Consider consolidating with Cart model for better architecture.
    """
    __tablename__ = "cart_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False)  # Price at time of adding to cart
    is_ordered = Column(Boolean, default=False)  # True when order is placed
    order_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # TODO: Re-enable when User model relationships are fixed
    # user = relationship("User", back_populates="cart_orders")
    # TODO: Re-enable when SKU model relationships are fixed
    # sku = relationship("SKU", back_populates="cart_orders")
    
    # INDEXES for performance
    __table_args__ = (
        Index('idx_cart_order_user_ordered', 'user_id', 'is_ordered'),
        Index('idx_cart_order_sku', 'sku_id'),
        Index('idx_cart_order_created', 'created_at'),
    )

    def __repr__(self):
        return f"<CartOrder(id={self.id}, user_id={self.user_id}, sku_id={self.sku_id}, quantity={self.quantity})>"

    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        return self.price * self.quantity

    @property
    def formatted_total_price(self):
        """Get formatted total price with currency"""
        return f"{self.total_price} сом"

    def place_order(self):
        """Mark this cart item as ordered"""
        self.is_ordered = True
        self.order_date = func.now()

    def can_be_ordered(self):
        """Check if item can be ordered (has stock)"""
        return self.sku.is_in_stock and self.quantity <= self.sku.stock
