from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base
from .order import OrderStatus


class OrderStatusHistory(Base):
    """Order status change history model"""
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    old_status = Column(Enum(OrderStatus), nullable=True)
    new_status = Column(Enum(OrderStatus), nullable=False)
    changed_by_admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="status_history")
    changed_by = relationship("Admin")

    def __repr__(self):
        return f"<OrderStatusHistory(id={self.id}, order_id={self.order_id}, status_change='{self.old_status}->{self.new_status}')>"

    @property
    def status_change_description(self):
        """Get human-readable status change description"""
        if not self.old_status:
            return f"Заказ создан со статусом: {self.new_status.value}"
        
        status_names = {
            OrderStatus.PENDING: "В обработке",
            OrderStatus.CONFIRMED: "Подтвержден", 
            OrderStatus.PROCESSING: "Обрабатывается",
            OrderStatus.SHIPPED: "Отправлен",
            OrderStatus.DELIVERED: "Доставлен",
            OrderStatus.CANCELLED: "Отменен",
            OrderStatus.RETURNED: "Возвращен"
        }
        
        old_name = status_names.get(self.old_status, self.old_status.value)
        new_name = status_names.get(self.new_status, self.new_status.value)
        
        return f"Статус изменен с '{old_name}' на '{new_name}'"

    @classmethod
    def create_status_change(cls, order_id, old_status, new_status, admin_id=None, notes=None):
        """Create a status change record"""
        return cls(
            order_id=order_id,
            old_status=old_status,
            new_status=new_status,
            changed_by_admin_id=admin_id,
            notes=notes
        )
