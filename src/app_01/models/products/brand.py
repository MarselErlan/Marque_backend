from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class Brand(Base):
    """Product brands (H&M, Zara, Nike, etc.)"""
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # "H&M", "Zara"
    slug = Column(String(100), unique=True, nullable=False, index=True)  # "hm", "zara"
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)  # Brand logo image
    website_url = Column(String(500), nullable=True)  # Brand website
    country = Column(String(50), nullable=True, index=True)  # Country of origin, indexed for filtering
    is_active = Column(Boolean, default=True, index=True)  # Indexed for filtering
    is_featured = Column(Boolean, default=False)  # Featured brands for homepage
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Composite indexes
    __table_args__ = (
        Index('idx_brand_active_sort', 'is_active', 'sort_order'),
    )

    # Relationships
    products = relationship("Product", back_populates="brand")

    def __repr__(self):
        return f"<Brand(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    @property
    def product_count(self):
        """Get total number of products for this brand"""
        return len(self.products) if self.products else 0

    @property
    def active_products(self):
        """Get only active products for this brand"""
        # Assuming Product has an is_active field
        return [product for product in self.products if hasattr(product, 'is_active') and product.is_active]

    @classmethod
    def get_by_slug(cls, session, slug):
        """Get brand by slug"""
        return session.query(cls).filter(cls.slug == slug, cls.is_active == True).first()

    @classmethod
    def get_all_active(cls, session):
        """Get all active brands ordered by sort_order"""
        return session.query(cls).filter(cls.is_active == True).order_by(cls.sort_order, cls.name).all()

    @classmethod
    def search_by_name(cls, session, name):
        """Search brands by name"""
        return session.query(cls).filter(
            cls.name.ilike(f"%{name}%"),
            cls.is_active == True
        ).order_by(cls.name).all()

    @classmethod
    def get_popular_brands(cls, session, limit=10):
        """Get brands with most products (need to join with products and count)"""
        from sqlalchemy import func as sql_func
        from .product import Product
        
        return session.query(cls, sql_func.count(Product.id).label('product_count')).join(
            Product, cls.id == Product.brand_id
        ).filter(
            cls.is_active == True,
            Product.is_active == True
        ).group_by(cls.id).order_by(sql_func.count(Product.id).desc()).limit(limit).all()
    
    @classmethod
    def get_featured_brands(cls, session):
        """Get featured brands"""
        return session.query(cls).filter(
            cls.is_active == True,
            cls.is_featured == True
        ).order_by(cls.sort_order, cls.name).all()
    
    @classmethod
    def get_brands_by_country(cls, session, country):
        """Get brands from specific country"""
        return session.query(cls).filter(
            cls.is_active == True,
            cls.country == country
        ).order_by(cls.name).all()

    def deactivate(self):
        """Deactivate brand"""
        self.is_active = False

    def activate(self):
        """Activate brand"""
        self.is_active = True
    
    def feature(self):
        """Mark brand as featured"""
        self.is_featured = True
    
    def unfeature(self):
        """Remove featured status"""
        self.is_featured = False
