from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ...db import Base


class OrderStatus(enum.Enum):
    """Order status enumeration"""
    PENDING = "pending"  # В обработке
    CONFIRMED = "confirmed"  # Подтвержден
    PROCESSING = "processing"  # Обрабатывается
    SHIPPED = "shipped"  # Отправлен
    DELIVERED = "delivered"  # Доставлен
    CANCELLED = "cancelled"  # Отменен
    RETURNED = "returned"  # Возвращен


class Order(Base):
    """Main order model for order management"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., #1021
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    
    # Customer information
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(255), nullable=True)
    
    # Delivery information
    delivery_address = Column(String(500), nullable=False)
    delivery_city = Column(String(100), nullable=True)
    delivery_notes = Column(String(500), nullable=True)
    
    # Financial information
    subtotal = Column(Float, nullable=False)
    shipping_cost = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="KGS")
    
    # Order tracking
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_date = Column(DateTime(timezone=True), nullable=True)
    shipped_date = Column(DateTime(timezone=True), nullable=True)
    delivered_date = Column(DateTime(timezone=True), nullable=True)
    cancelled_date = Column(DateTime(timezone=True), nullable=True)
    
    # Admin tracking
    created_by_admin = Column(Integer, ForeignKey("admins.id"), nullable=True)
    notes = Column(String(1000), nullable=True)  # Admin notes
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    created_by = relationship("Admin")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', status='{self.status.value}')>"

    @property
    def is_pending(self):
        """Check if order is pending"""
        return self.status == OrderStatus.PENDING

    @property
    def is_confirmed(self):
        """Check if order is confirmed"""
        return self.status == OrderStatus.CONFIRMED

    @property
    def is_processing(self):
        """Check if order is processing"""
        return self.status == OrderStatus.PROCESSING

    @property
    def is_shipped(self):
        """Check if order is shipped"""
        return self.status == OrderStatus.SHIPPED

    @property
    def is_delivered(self):
        """Check if order is delivered"""
        return self.status == OrderStatus.DELIVERED

    @property
    def is_cancelled(self):
        """Check if order is cancelled"""
        return self.status == OrderStatus.CANCELLED

    @property
    def total_items(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.order_items)

    @property
    def status_display(self):
        """Get display name for status"""
        status_names = {
            OrderStatus.PENDING: "В обработке",
            OrderStatus.CONFIRMED: "Подтвержден",
            OrderStatus.PROCESSING: "Обрабатывается",
            OrderStatus.SHIPPED: "Отправлен",
            OrderStatus.DELIVERED: "Доставлен",
            OrderStatus.CANCELLED: "Отменен",
            OrderStatus.RETURNED: "Возвращен"
        }
        return status_names.get(self.status, self.status.value)

    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PROCESSING]

    def can_be_shipped(self):
        """Check if order can be shipped"""
        return self.status in [OrderStatus.CONFIRMED, OrderStatus.PROCESSING]

    def confirm_order(self):
        """Confirm the order"""
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.CONFIRMED
            self.confirmed_date = func.now()

    def ship_order(self):
        """Mark order as shipped"""
        if self.can_be_shipped():
            self.status = OrderStatus.SHIPPED
            self.shipped_date = func.now()

    def deliver_order(self):
        """Mark order as delivered"""
        if self.status == OrderStatus.SHIPPED:
            self.status = OrderStatus.DELIVERED
            self.delivered_date = func.now()

    def cancel_order(self):
        """Cancel the order"""
        if self.can_be_cancelled():
            self.status = OrderStatus.CANCELLED
            self.cancelled_date = func.now()
