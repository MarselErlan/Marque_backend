from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class ProductAttribute(Base):
    """Product attributes management (sizes, colors, categories)"""
    __tablename__ = "product_attributes"

    id = Column(Integer, primary_key=True, index=True)
    attribute_type = Column(String(50), nullable=False, index=True)  # size, color, category, brand
    attribute_value = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=True)  # Human-readable name
    sort_order = Column(Integer, default=0)  # For ordering in UI
    is_active = Column(Boolean, default=True)
    created_by_admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by = relationship("Admin")

    def __repr__(self):
        return f"<ProductAttribute(type='{self.attribute_type}', value='{self.attribute_value}')>"

    @property
    def formatted_display_name(self):
        """Get formatted display name"""
        return self.display_name or self.attribute_value

    @classmethod
    def get_sizes(cls, session):
        """Get all active sizes"""
        return session.query(cls).filter(
            cls.attribute_type == "size",
            cls.is_active == True
        ).order_by(cls.sort_order, cls.attribute_value).all()

    @classmethod
    def get_colors(cls, session):
        """Get all active colors"""
        return session.query(cls).filter(
            cls.attribute_type == "color",
            cls.is_active == True
        ).order_by(cls.sort_order, cls.attribute_value).all()

    @classmethod
    def get_categories(cls, session):
        """Get all active categories"""
        return session.query(cls).filter(
            cls.attribute_type == "category",
            cls.is_active == True
        ).order_by(cls.sort_order, cls.attribute_value).all()

    @classmethod
    def get_brands(cls, session):
        """Get all active brands"""
        return session.query(cls).filter(
            cls.attribute_type == "brand",
            cls.is_active == True
        ).order_by(cls.sort_order, cls.attribute_value).all()

    @classmethod
    def add_size(cls, session, size_value, display_name=None, admin_id=None):
        """Add a new size attribute"""
        return cls(
            attribute_type="size",
            attribute_value=size_value,
            display_name=display_name or size_value,
            created_by_admin_id=admin_id
        )

    @classmethod
    def add_color(cls, session, color_value, display_name=None, admin_id=None):
        """Add a new color attribute"""
        return cls(
            attribute_type="color",
            attribute_value=color_value,
            display_name=display_name or color_value,
            created_by_admin_id=admin_id
        )

    @classmethod
    def add_category(cls, session, category_value, display_name=None, admin_id=None):
        """Add a new category attribute"""
        return cls(
            attribute_type="category",
            attribute_value=category_value,
            display_name=display_name or category_value,
            created_by_admin_id=admin_id
        )

    @classmethod
    def add_brand(cls, session, brand_value, display_name=None, admin_id=None):
        """Add a new brand attribute"""
        return cls(
            attribute_type="brand",
            attribute_value=brand_value,
            display_name=display_name or brand_value,
            created_by_admin_id=admin_id
        )

    def deactivate(self):
        """Deactivate this attribute"""
        self.is_active = False

    def activate(self):
        """Activate this attribute"""
        self.is_active = True

    def update_sort_order(self, new_order):
        """Update sort order"""
        self.sort_order = new_order
