from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class UserNotification(Base):
    """User notifications (orders, promotions, etc.)"""
    __tablename__ = "user_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    notification_type = Column(String(20), nullable=False, index=True)  # order, promotion, system
    title = Column(String(200), nullable=False)  # "Заказ №123 подтверждён"
    message = Column(Text, nullable=True)  # Detailed message
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)  # Related order
    is_read = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    metadata_json = Column(JSON, nullable=True)  # Additional data (images, links, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    # TODO: Re-enable when User model relationships are fixed
    # user = relationship("User", back_populates="notifications")
    order = relationship("Order")

    def __repr__(self):
        return f"<UserNotification(id={self.id}, user_id={self.user_id}, type='{self.notification_type}', title='{self.title}')>"

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = func.now()

    @classmethod
    def create_notification(cls, session, user_id, notification_type, title, message=None, order_id=None, metadata=None):
        """Create new notification"""
        notification = cls(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            order_id=order_id,
            metadata_json=metadata
        )
        
        session.add(notification)
        session.commit()
        session.refresh(notification)
        
        return notification

    @classmethod
    def get_user_notifications(cls, session, user_id, notification_type=None, unread_only=False):
        """Get user notifications"""
        query = session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_active == True
        )
        
        if notification_type:
            query = query.filter(cls.notification_type == notification_type)
        
        if unread_only:
            query = query.filter(cls.is_read == False)
        
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_unread_count(cls, session, user_id):
        """Get count of unread notifications for user"""
        return session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_read == False,
            cls.is_active == True
        ).count()

    @classmethod
    def mark_all_as_read(cls, session, user_id, notification_type=None):
        """Mark all notifications as read for user"""
        query = session.query(cls).filter(
            cls.user_id == user_id,
            cls.is_read == False,
            cls.is_active == True
        )
        
        if notification_type:
            query = query.filter(cls.notification_type == notification_type)
        
        query.update({
            "is_read": True,
            "read_at": func.now()
        })
        session.commit()

    @classmethod
    def create_order_notification(cls, session, user_id, order_id, notification_type, title, message=None):
        """Create order-related notification"""
        return cls.create_notification(
            session=session,
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            order_id=order_id,
            metadata={"order_id": order_id}
        )

    @classmethod
    def create_promotion_notification(cls, session, user_id, title, message=None, metadata=None):
        """Create promotion notification"""
        return cls.create_notification(
            session=session,
            user_id=user_id,
            notification_type="promotion",
            title=title,
            message=message,
            metadata_json=metadata
        )
