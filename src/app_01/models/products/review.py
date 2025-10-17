from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, CheckConstraint, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class Review(Base):
    """Product reviews model"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False, index=True)  # 1-5, indexed for sorting
    text = Column(Text)
    
    # Review status
    is_verified_purchase = Column(Boolean, default=False)  # Did user actually buy this?
    is_approved = Column(Boolean, default=True)  # For moderation
    is_featured = Column(Boolean, default=False)  # Highlight good reviews
    
    # Helpfulness tracking
    helpful_count = Column(Integer, default=0)  # How many found this helpful
    unhelpful_count = Column(Integer, default=0)  # How many found this not helpful
    
    # Admin response
    admin_response = Column(Text, nullable=True)  # Store admin response
    admin_response_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="reviews")
    # TODO: Re-enable when User model relationships are fixed
    # user = relationship("User", back_populates="reviews")

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        Index('idx_review_product_rating', 'product_id', 'rating'),
        Index('idx_review_approved', 'is_approved'),
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
    
    @property
    def helpfulness_score(self):
        """Calculate helpfulness score"""
        total = self.helpful_count + self.unhelpful_count
        if total == 0:
            return 0
        return (self.helpful_count / total) * 100
    
    @property
    def has_admin_response(self):
        """Check if review has admin response"""
        return self.admin_response is not None and len(self.admin_response) > 0
    
    def mark_helpful(self):
        """Increment helpful count"""
        self.helpful_count += 1
    
    def mark_unhelpful(self):
        """Increment unhelpful count"""
        self.unhelpful_count += 1
    
    def add_admin_response(self, response_text):
        """Add admin response to review"""
        self.admin_response = response_text
        self.admin_response_date = func.now()
    
    def approve(self):
        """Approve review for display"""
        self.is_approved = True
    
    def reject(self):
        """Reject/hide review"""
        self.is_approved = False
    
    def feature(self):
        """Mark review as featured"""
        self.is_featured = True
    
    @classmethod
    def get_approved_reviews_for_product(cls, session, product_id):
        """Get all approved reviews for a product"""
        return session.query(cls).filter(
            cls.product_id == product_id,
            cls.is_approved == True
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_featured_reviews(cls, session, product_id):
        """Get featured reviews for a product"""
        return session.query(cls).filter(
            cls.product_id == product_id,
            cls.is_approved == True,
            cls.is_featured == True
        ).order_by(cls.helpful_count.desc()).all()
    
    @classmethod
    def get_verified_reviews(cls, session, product_id):
        """Get verified purchase reviews"""
        return session.query(cls).filter(
            cls.product_id == product_id,
            cls.is_approved == True,
            cls.is_verified_purchase == True
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_top_helpful_reviews(cls, session, product_id, limit=5):
        """Get most helpful reviews"""
        return session.query(cls).filter(
            cls.product_id == product_id,
            cls.is_approved == True
        ).order_by(cls.helpful_count.desc()).limit(limit).all()
