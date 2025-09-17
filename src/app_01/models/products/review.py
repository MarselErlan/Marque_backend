from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class Review(Base):
    """Product reviews model"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5
    text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    # Constraints
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )

    def __repr__(self):
        return f"<Review(id={self.id}, rating={self.rating}, product_id={self.product_id})>"

    @property
    def is_positive(self):
        """Check if review is positive (4-5 stars)"""
        return self.rating >= 4

    @property
    def is_negative(self):
        """Check if review is negative (1-2 stars)"""
        return self.rating <= 2

    @property
    def is_neutral(self):
        """Check if review is neutral (3 stars)"""
        return self.rating == 3

    @property
    def rating_text(self):
        """Get text representation of rating"""
        rating_texts = {
            1: "Очень плохо",
            2: "Плохо", 
            3: "Нормально",
            4: "Хорошо",
            5: "Отлично"
        }
        return rating_texts.get(self.rating, "Неизвестно")

    def get_rating_stars(self):
        """Get rating as star symbols"""
        return "★" * self.rating + "☆" * (5 - self.rating)
