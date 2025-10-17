from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Index
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
    description = Column(Text, nullable=True)  # Detailed description
    sort_order = Column(Integer, default=0)  # For ordering in UI
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)  # Featured attributes
    usage_count = Column(Integer, default=0)  # Track how many products use this
    created_by_admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by = relationship("Admin")
    
    # INDEXES for performance
    __table_args__ = (
        Index('idx_product_attr_type_active', 'attribute_type', 'is_active'),
        Index('idx_product_attr_type_featured', 'attribute_type', 'is_featured'),
        Index('idx_product_attr_usage', 'usage_count'),
    )

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
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
    
    def decrement_usage(self):
        """Decrement usage count"""
        if self.usage_count > 0:
            self.usage_count -= 1
    
    @classmethod
    def get_featured_attributes(cls, session, attribute_type=None):
        """Get featured attributes"""
        query = session.query(cls).filter(
            cls.is_featured == True,
            cls.is_active == True
        )
        if attribute_type:
            query = query.filter(cls.attribute_type == attribute_type)
        return query.order_by(cls.sort_order, cls.display_name).all()
    
    @classmethod
    def get_most_used_attributes(cls, session, attribute_type, limit=10):
        """Get most popular attributes by usage"""
        return session.query(cls).filter(
            cls.attribute_type == attribute_type,
            cls.is_active == True
        ).order_by(cls.usage_count.desc()).limit(limit).all()
