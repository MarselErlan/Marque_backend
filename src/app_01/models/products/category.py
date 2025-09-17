from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class Category(Base):
    """Main product categories (Мужчинам, Женщинам, Детям, etc.)"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)  # "Мужчинам", "Женщинам", "Детям"
    slug = Column(String(100), unique=True, nullable=False, index=True)  # "men", "women", "kids"
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)  # FontAwesome icon class
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    subcategories = relationship("Subcategory", back_populates="category", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    @property
    def product_count(self):
        """Get total number of products in this category"""
        return len(self.products) if self.products else 0

    @property
    def active_subcategories(self):
        """Get only active subcategories"""
        return [sub for sub in self.subcategories if sub.is_active]

    @classmethod
    def get_by_slug(cls, session, slug):
        """Get category by slug"""
        return session.query(cls).filter(cls.slug == slug, cls.is_active == True).first()

    @classmethod
    def get_all_active(cls, session):
        """Get all active categories ordered by sort_order"""
        return session.query(cls).filter(cls.is_active == True).order_by(cls.sort_order, cls.name).all()


class Subcategory(Base):
    """Product subcategories (Футболки и поло, Джинсы, etc.)"""
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)  # "Футболки и поло", "Джинсы"
    slug = Column(String(100), nullable=False, index=True)  # "t-shirts", "jeans"
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)  # Category image
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory")

    def __repr__(self):
        return f"<Subcategory(id={self.id}, name='{self.name}', category_id={self.category_id})>"

    @property
    def product_count(self):
        """Get total number of products in this subcategory"""
        return len(self.products) if self.products else 0

    @classmethod
    def get_by_category_slug(cls, session, category_slug):
        """Get all subcategories for a category by slug"""
        return session.query(cls).join(Category).filter(
            Category.slug == category_slug,
            Category.is_active == True,
            cls.is_active == True
        ).order_by(cls.sort_order, cls.name).all()

    @classmethod
    def get_by_slug(cls, session, category_slug, subcategory_slug):
        """Get subcategory by category and subcategory slugs"""
        return session.query(cls).join(Category).filter(
            Category.slug == category_slug,
            cls.slug == subcategory_slug,
            Category.is_active == True,
            cls.is_active == True
        ).first()

    @classmethod
    def get_all_active(cls, session):
        """Get all active subcategories ordered by category and sort_order"""
        return session.query(cls).join(Category).filter(
            Category.is_active == True,
            cls.is_active == True
        ).order_by(Category.sort_order, cls.sort_order, cls.name).all()
