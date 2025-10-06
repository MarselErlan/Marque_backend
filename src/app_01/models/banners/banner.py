"""
Banner Model
Main page banners for sales and model showcases
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

# Create a base for banners
Base = declarative_base()

class BannerType(str, Enum):
    """Banner types"""
    SALE = "sale"       # Promotional/discount banners
    MODEL = "model"     # Product/model showcase banners

class Banner(Base):
    """
    Banner model for main page
    Supports two types: sale banners and model banners
    """
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    
    # Banner details
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=False)  # Main banner image
    
    # Banner type (sale or model)
    banner_type = Column(SQLEnum(BannerType), nullable=False, index=True)
    
    # Link/action when banner is clicked
    link_url = Column(String(500), nullable=True)  # Optional link to product/category
    
    # Display settings
    is_active = Column(Boolean, default=True, index=True)  # Show/hide banner
    display_order = Column(Integer, default=0)  # Order of display (lower = first)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Optional: Scheduling
    start_date = Column(DateTime(timezone=True), nullable=True)  # When to start showing
    end_date = Column(DateTime(timezone=True), nullable=True)    # When to stop showing

    def __init__(self, **kwargs):
        """Initialize banner with default values"""
        # Handle 'link' as alias for 'link_url' for backward compatibility
        if 'link' in kwargs and 'link_url' not in kwargs:
            kwargs['link_url'] = kwargs.pop('link')
        
        # Set defaults for fields not provided
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('display_order', 0)
        if 'created_at' not in kwargs:
            from datetime import datetime
            kwargs['created_at'] = datetime.utcnow()
        if 'updated_at' not in kwargs:
            from datetime import datetime
            kwargs['updated_at'] = datetime.utcnow()
        super().__init__(**kwargs)

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

