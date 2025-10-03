from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ...db import Base


class SKU(Base):
    """Stock Keeping Unit model representing specific product variants"""
    __tablename__ = "skus"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    sku_code = Column(String(50), nullable=False, unique=True, index=True)
    size = Column(String(20), nullable=False)
    color = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Relationships
    product = relationship("Product", back_populates="skus")
    # TODO: Re-enable when CartItem model is properly integrated
    # cart_items = relationship("CartItem", back_populates="sku")

    def __repr__(self):
        return f"<SKU(id={self.id}, sku_code='{self.sku_code}', size='{self.size}', color='{self.color}')>"

    @property
    def is_in_stock(self):
        """Check if SKU is available in stock"""
        return self.is_active and self.stock > 0

    @property
    def formatted_price(self):
        """Return formatted price with currency"""
        return f"{self.price} сом"

    def reduce_stock(self, quantity):
        """Reduce stock by specified quantity"""
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False

    def increase_stock(self, quantity):
        """Increase stock by specified quantity"""
        self.stock += quantity

    def deactivate(self):
        """Deactivate SKU (mark as unavailable)"""
        self.is_active = False

    def activate(self):
        """Activate SKU (mark as available)"""
        self.is_active = True
