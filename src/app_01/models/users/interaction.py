from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class Interaction(Base):
    """User interactions model for tracking user behavior"""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nullable for anonymous users
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    interaction_type = Column(String(50), nullable=False)  # 'view', 'wishlist', 'search', 'click'
    metadata_json = Column(String(500), nullable=True)  # Additional data like search query, page url, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="interactions")
    product = relationship("Product")

    def __repr__(self):
        return f"<Interaction(id={self.id}, user_id={self.user_id}, type='{self.interaction_type}')>"
