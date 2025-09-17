from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from ...db import Base


class OrderItem(Base):
    """Order items model - individual products in an order"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False, index=True)
    
    # Product details at time of order (snapshot)
    product_name = Column(String(255), nullable=False)
    sku_code = Column(String(50), nullable=False)
    size = Column(String(20), nullable=False)
    color = Column(String(50), nullable=False)
    
    # Pricing
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    sku = relationship("SKU")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, product='{self.product_name}', quantity={self.quantity})>"

    @property
    def formatted_unit_price(self):
        """Get formatted unit price with currency"""
        return f"{self.unit_price} KGS"

    @property
    def formatted_total_price(self):
        """Get formatted total price with currency"""
        return f"{self.total_price} KGS"

    def calculate_total(self):
        """Calculate total price for this item"""
        self.total_price = self.unit_price * self.quantity
        return self.total_price

    @classmethod
    def create_from_sku(cls, order_id, sku, quantity):
        """Create order item from SKU"""
        return cls(
            order_id=order_id,
            sku_id=sku.id,
            product_name=sku.product.title,
            sku_code=sku.sku_code,
            size=sku.size,
            color=sku.color,
            unit_price=sku.price,
            quantity=quantity,
            total_price=sku.price * quantity
        )
