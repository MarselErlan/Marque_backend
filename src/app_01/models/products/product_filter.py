from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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


class ProductSeason(Base):
    """Product seasons (Лето, Зима, Мульти, etc.)"""
    __tablename__ = "product_seasons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)  # "Лето", "Зима", "Мульти"
    slug = Column(String(50), unique=True, nullable=False, index=True)  # "summer", "winter", "multi"
    description = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ProductSeason(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    @classmethod
    def get_all_active(cls, session):
        """Get all active seasons"""
        return session.query(cls).filter(cls.is_active == True).order_by(cls.sort_order, cls.name).all()


class ProductMaterial(Base):
    """Product materials (Хлопок, Полиэстер, Шерсть, etc.)"""
    __tablename__ = "product_materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # "Хлопок", "Полиэстер"
    slug = Column(String(100), unique=True, nullable=False, index=True)  # "cotton", "polyester"
    description = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ProductMaterial(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    @classmethod
    def get_all_active(cls, session):
        """Get all active materials"""
        return session.query(cls).filter(cls.is_active == True).order_by(cls.sort_order, cls.name).all()


class ProductStyle(Base):
    """Product styles (Спортивный, Классический, Повседневный, etc.)"""
    __tablename__ = "product_styles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # "Спортивный", "Классический"
    slug = Column(String(100), unique=True, nullable=False, index=True)  # "sport", "classic"
    description = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ProductStyle(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    @classmethod
    def get_all_active(cls, session):
        """Get all active styles"""
        return session.query(cls).filter(cls.is_active == True).order_by(cls.sort_order, cls.name).all()


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
        
        now = func.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        
        return True


class ProductSearch(Base):
    """Product search functionality and analytics"""
    __tablename__ = "product_searches"

    id = Column(Integer, primary_key=True, index=True)
    search_term = Column(String(255), nullable=False, index=True)
    search_count = Column(Integer, default=1)
    last_searched = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ProductSearch(id={self.id}, term='{self.search_term}', count={self.search_count})>"

    @classmethod
    def get_popular_searches(cls, session, limit=10):
        """Get most popular search terms"""
        return session.query(cls).order_by(cls.search_count.desc()).limit(limit).all()

    @classmethod
    def record_search(cls, session, search_term):
        """Record a search term"""
        search = session.query(cls).filter(cls.search_term == search_term).first()
        if search:
            search.search_count += 1
            search.last_searched = func.now()
        else:
            search = cls(search_term=search_term, search_count=1)
            session.add(search)
        session.commit()
        return search
