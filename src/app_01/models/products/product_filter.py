from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class ProductFilter(Base):
    """Product filter options for catalog filtering"""
    __tablename__ = "product_filters"

    id = Column(Integer, primary_key=True, index=True)
    filter_type = Column(String(50), nullable=False, index=True)  # size, color, brand, season, material, style
    filter_value = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=True)  # Human-readable name
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)  # Track filter popularity
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # INDEXES for performance
    __table_args__ = (
        Index('idx_product_filter_type_active', 'filter_type', 'is_active'),
        Index('idx_product_filter_usage', 'usage_count'),
    )

    def __repr__(self):
        return f"<ProductFilter(id={self.id}, type='{self.filter_type}', value='{self.filter_value}')>"

    @classmethod
    def get_filters_by_type(cls, session, filter_type):
        """Get all active filters of a specific type"""
        return session.query(cls).filter(
            cls.filter_type == filter_type,
            cls.is_active == True
        ).order_by(cls.sort_order, cls.display_name).all()

    @classmethod
    def get_all_filter_types(cls, session):
        """Get all available filter types"""
        return session.query(cls.filter_type).distinct().filter(
            cls.is_active == True
        ).all()
    
    @classmethod
    def get_popular_filters(cls, session, filter_type, limit=10):
        """Get most used filters"""
        return session.query(cls).filter(
            cls.filter_type == filter_type,
            cls.is_active == True
        ).order_by(cls.usage_count.desc()).limit(limit).all()
    
    def increment_usage(self):
        """Track filter usage"""
        self.usage_count += 1


class ProductSeason(Base):
    """Product seasons (Лето, Зима, Мульти, etc.)"""
    __tablename__ = "product_seasons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)  # "Лето", "Зима", "Мульти"
    slug = Column(String(50), unique=True, nullable=False, index=True)  # "summer", "winter", "multi"
    description = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    product_count = Column(Integer, default=0)  # Track products in this season
    is_featured = Column(Boolean, default=False)  # Featured seasons
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # INDEXES for performance
    __table_args__ = (
        Index('idx_product_season_active', 'is_active'),
        Index('idx_product_season_featured', 'is_featured'),
        Index('idx_product_season_count', 'product_count'),
    )

    def __repr__(self):
        return f"<ProductSeason(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    @classmethod
    def get_all_active(cls, session):
        """Get all active seasons"""
        return session.query(cls).filter(cls.is_active == True).order_by(cls.sort_order, cls.name).all()
    
    @classmethod
    def get_featured_seasons(cls, session):
        """Get featured seasons"""
        return session.query(cls).filter(
            cls.is_featured == True,
            cls.is_active == True
        ).order_by(cls.sort_order).all()
    
    @classmethod
    def get_popular_seasons(cls, session, limit=5):
        """Get seasons with most products"""
        return session.query(cls).filter(
            cls.is_active == True
        ).order_by(cls.product_count.desc()).limit(limit).all()


class ProductMaterial(Base):
    """Product materials (Хлопок, Полиэстер, Шерсть, etc.)"""
    __tablename__ = "product_materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # "Хлопок", "Полиэстер"
    slug = Column(String(100), unique=True, nullable=False, index=True)  # "cotton", "polyester"
    description = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    product_count = Column(Integer, default=0)  # Track products with this material
    is_featured = Column(Boolean, default=False)  # Featured materials
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # INDEXES for performance
    __table_args__ = (
        Index('idx_product_material_active', 'is_active'),
        Index('idx_product_material_featured', 'is_featured'),
        Index('idx_product_material_count', 'product_count'),
    )

    def __repr__(self):
        return f"<ProductMaterial(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    @classmethod
    def get_all_active(cls, session):
        """Get all active materials"""
        return session.query(cls).filter(cls.is_active == True).order_by(cls.sort_order, cls.name).all()
    
    @classmethod
    def get_featured_materials(cls, session):
        """Get featured materials"""
        return session.query(cls).filter(
            cls.is_featured == True,
            cls.is_active == True
        ).order_by(cls.sort_order).all()
    
    @classmethod
    def get_popular_materials(cls, session, limit=10):
        """Get materials with most products"""
        return session.query(cls).filter(
            cls.is_active == True
        ).order_by(cls.product_count.desc()).limit(limit).all()


class ProductStyle(Base):
    """Product styles (Спортивный, Классический, Повседневный, etc.)"""
    __tablename__ = "product_styles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # "Спортивный", "Классический"
    slug = Column(String(100), unique=True, nullable=False, index=True)  # "sport", "classic"
    description = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    product_count = Column(Integer, default=0)  # Track products with this style
    is_featured = Column(Boolean, default=False)  # Featured styles
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # INDEXES for performance
    __table_args__ = (
        Index('idx_product_style_active', 'is_active'),
        Index('idx_product_style_featured', 'is_featured'),
        Index('idx_product_style_count', 'product_count'),
    )

    def __repr__(self):
        return f"<ProductStyle(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    @classmethod
    def get_all_active(cls, session):
        """Get all active styles"""
        return session.query(cls).filter(cls.is_active == True).order_by(cls.sort_order, cls.name).all()
    
    @classmethod
    def get_featured_styles(cls, session):
        """Get featured styles"""
        return session.query(cls).filter(
            cls.is_featured == True,
            cls.is_active == True
        ).order_by(cls.sort_order).all()
    
    @classmethod
    def get_popular_styles(cls, session, limit=10):
        """Get styles with most products"""
        return session.query(cls).filter(
            cls.is_active == True
        ).order_by(cls.product_count.desc()).limit(limit).all()


class ProductDiscount(Base):
    """Product discount information"""
    __tablename__ = "product_discounts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    discount_type = Column(String(20), nullable=False)  # "percentage", "fixed"
    discount_value = Column(Float, nullable=False)  # 20 for 20% or 500 for 500 сом
    original_price = Column(Float, nullable=True)  # Original price before discount
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product")
    
    # INDEXES for performance
    __table_args__ = (
        Index('idx_product_discount_product_active', 'product_id', 'is_active'),
        Index('idx_product_discount_dates', 'start_date', 'end_date'),
        Index('idx_product_discount_active', 'is_active'),
    )

    def __repr__(self):
        return f"<ProductDiscount(id={self.id}, product_id={self.product_id}, type='{self.discount_type}', value={self.discount_value})>"

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.discount_type == "percentage":
            return self.discount_value
        elif self.discount_type == "fixed" and self.original_price:
            return (self.discount_value / self.original_price) * 100
        return 0

    @property
    def final_price(self):
        """Calculate final price after discount"""
        if not self.original_price:
            return None
        
        if self.discount_type == "percentage":
            return self.original_price * (1 - self.discount_value / 100)
        elif self.discount_type == "fixed":
            return max(0, self.original_price - self.discount_value)
        return self.original_price

    @property
    def savings_amount(self):
        """Calculate amount saved"""
        if not self.original_price:
            return 0
        
        if self.discount_type == "percentage":
            return self.original_price * (self.discount_value / 100)
        elif self.discount_type == "fixed":
            return self.discount_value
        return 0

    def is_discount_active(self):
        """Check if discount is currently active"""
        if not self.is_active:
            return False
        
        from datetime import datetime
        now = datetime.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    @classmethod
    def get_active_discounts(cls, session):
        """Get all currently active discounts"""
        from datetime import datetime
        now = datetime.now()
        return session.query(cls).filter(
            cls.is_active == True,
            (cls.start_date.is_(None)) | (cls.start_date <= now),
            (cls.end_date.is_(None)) | (cls.end_date >= now)
        ).all()
    
    @classmethod
    def get_best_discounts(cls, session, limit=10):
        """Get biggest discounts"""
        from datetime import datetime
        now = datetime.now()
        return session.query(cls).filter(
            cls.is_active == True,
            (cls.start_date.is_(None)) | (cls.start_date <= now),
            (cls.end_date.is_(None)) | (cls.end_date >= now),
            cls.discount_type == "percentage"
        ).order_by(cls.discount_value.desc()).limit(limit).all()


class ProductSearch(Base):
    """Product search functionality and analytics"""
    __tablename__ = "product_searches"

    id = Column(Integer, primary_key=True, index=True)
    search_term = Column(String(255), nullable=False, index=True)
    search_count = Column(Integer, default=1)
    result_count = Column(Integer, default=0)  # How many results were found
    last_searched = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # INDEXES for performance
    __table_args__ = (
        Index('idx_product_search_count', 'search_count'),
        Index('idx_product_search_term_count', 'search_term', 'search_count'),
        Index('idx_product_search_last_searched', 'last_searched'),
    )

    def __repr__(self):
        return f"<ProductSearch(id={self.id}, term='{self.search_term}', count={self.search_count})>"

    @classmethod
    def get_popular_searches(cls, session, limit=10):
        """Get most popular search terms"""
        return session.query(cls).order_by(cls.search_count.desc()).limit(limit).all()
    
    @classmethod
    def get_recent_searches(cls, session, limit=10):
        """Get most recent search terms"""
        return session.query(cls).order_by(cls.last_searched.desc()).limit(limit).all()
    
    @classmethod
    def get_zero_result_searches(cls, session, limit=10):
        """Get searches that returned no results (for improving catalog)"""
        return session.query(cls).filter(
            cls.result_count == 0
        ).order_by(cls.search_count.desc()).limit(limit).all()
    
    @classmethod
    def get_trending_searches(cls, session, days=7, limit=10):
        """Get trending searches from last N days"""
        from datetime import datetime, timedelta
        since = datetime.now() - timedelta(days=days)
        return session.query(cls).filter(
            cls.last_searched >= since
        ).order_by(cls.search_count.desc()).limit(limit).all()

    @classmethod
    def record_search(cls, session, search_term, result_count=0):
        """Record a search term with result count"""
        search = session.query(cls).filter(cls.search_term == search_term).first()
        if search:
            search.search_count += 1
            search.result_count = result_count  # Update with latest count
            search.last_searched = func.now()
        else:
            search = cls(search_term=search_term, search_count=1, result_count=result_count)
            session.add(search)
        session.commit()
        return search
