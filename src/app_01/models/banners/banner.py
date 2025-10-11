"""
Banner Model
Main page banners for sales and promotions
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from ...db import Base
from enum import Enum


class BannerType(str, Enum):
    """Banner types"""
    HERO = "hero"           # Main hero/carousel banner
    PROMO = "promo"         # Promotional/discount banner
    CATEGORY = "category"   # Category showcase banner


class Banner(Base):
    """
    Banner model for homepage
    Supports hero, promotional, and category showcase banners
    """
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    
    # Banner details
    title = Column(String(255), nullable=False)
    subtitle = Column(String(500), nullable=True)  # Secondary text
    description = Column(String(1000), nullable=True)  # Full description
    
    # Images
    image_url = Column(String(500), nullable=False)  # Main banner image
    mobile_image_url = Column(String(500), nullable=True)  # Optional mobile-optimized image
    
    # Banner type
    banner_type = Column(SQLEnum(BannerType), nullable=False, default=BannerType.HERO, index=True)
    
    # Call to action
    cta_text = Column(String(100), nullable=True)  # Button text (e.g., "Shop Now", "Learn More")
    cta_url = Column(String(500), nullable=True)  # Button/link URL
    
    # Display settings
    is_active = Column(Boolean, default=True, index=True)  # Show/hide banner
    display_order = Column(Integer, default=0)  # Order of display (lower = first)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Optional: Scheduling
    start_date = Column(DateTime(timezone=True), nullable=True)  # When to start showing
    end_date = Column(DateTime(timezone=True), nullable=True)    # When to stop showing

    def __repr__(self):
        return f"<Banner(id={self.id}, type='{self.banner_type}', title='{self.title}', active={self.is_active})>"
    
    @property
    def is_currently_active(self):
        """Check if banner should be displayed based on dates and active status"""
        from datetime import datetime
        
        if not self.is_active:
            return False
        
        now = datetime.utcnow()
        
        # Check start date
        if self.start_date and now < self.start_date:
            return False
        
        # Check end date
        if self.end_date and now > self.end_date:
            return False
        
        return True

