from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class Product(Base):
    """Product model representing items in the catalog"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=False, index=True)
    season_id = Column(Integer, ForeignKey("product_seasons.id"), nullable=True, index=True)
    material_id = Column(Integer, ForeignKey("product_materials.id"), nullable=True, index=True)
    style_id = Column(Integer, ForeignKey("product_styles.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    sold_count = Column(Integer, default=0)
    rating_avg = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    attributes = Column(JSON, nullable=True)  # {gender, season, composition, article}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    subcategory = relationship("Subcategory", back_populates="products")
    season = relationship("ProductSeason")
    material = relationship("ProductMaterial")
    style = relationship("ProductStyle")
    skus = relationship("SKU", back_populates="product", cascade="all, delete-orphan")
    assets = relationship("ProductAsset", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="product", cascade="all, delete-orphan")
    discounts = relationship("ProductDiscount", back_populates="product", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, title='{self.title}', brand_id={self.brand_id})>"

    @property
    def available_skus(self):
        """Get only active SKUs for this product"""
        return [sku for sku in self.skus if sku.is_active]

    @property
    def min_price(self):
        """Get minimum price from available SKUs"""
        if not self.available_skus:
            return None
        return min(sku.price for sku in self.available_skus)

    @property
    def max_price(self):
        """Get maximum price from available SKUs"""
        if not self.available_skus:
            return None
        return max(sku.price for sku in self.available_skus)

    @property
    def total_stock(self):
        """Get total stock across all SKUs"""
        return sum(sku.stock for sku in self.available_skus)

    def update_rating(self):
        """Update rating_avg and rating_count based on reviews"""
        if self.reviews:
            total_rating = sum(review.rating for review in self.reviews)
            self.rating_avg = round(total_rating / len(self.reviews), 1)
            self.rating_count = len(self.reviews)
        else:
            self.rating_avg = 0.0
            self.rating_count = 0

    @property
    def price_range(self):
        """Get price range as string"""
        min_p = self.min_price
        max_p = self.max_price
        if not min_p or not max_p:
            return "Цена не указана"
        if min_p == max_p:
            return f"{min_p} сом"
        return f"{min_p} - {max_p} сом"

    @property
    def is_in_stock(self):
        """Check if product has any stock"""
        return self.total_stock > 0

    @property
    def main_image(self):
        """Get main product image"""
        main_assets = [asset for asset in self.assets if asset.type == "image" and asset.order == 1]
        return main_assets[0] if main_assets else None

    @property
    def all_images(self):
        """Get all product images ordered by order"""
        return sorted([asset for asset in self.assets if asset.type == "image"], key=lambda x: x.order)

    @property
    def current_discount(self):
        """Get current active discount"""
        active_discounts = [d for d in self.discounts if d.is_discount_active()]
        return active_discounts[0] if active_discounts else None

    @property
    def is_on_sale(self):
        """Check if product is currently on sale"""
        return self.current_discount is not None

    def get_sku_by_attributes(self, size=None, color=None):
        """Get SKU by size and color attributes"""
        for sku in self.available_skus:
            if (not size or sku.size == size) and (not color or sku.color == color):
                return sku
        return None

    # Filter and search methods
    @classmethod
    def search_by_term(cls, session, search_term):
        """Search products by title, description, or brand"""
        from .brand import Brand
        return session.query(cls).join(Brand).filter(
            cls.is_active == True,
            (cls.title.ilike(f"%{search_term}%") |
             cls.description.ilike(f"%{search_term}%") |
             Brand.name.ilike(f"%{search_term}%"))
        ).all()

    @classmethod
    def filter_by_category(cls, session, category_slug):
        """Filter products by category"""
        from .category import Category
        return session.query(cls).join(Category).filter(
            Category.slug == category_slug,
            cls.is_active == True
        ).all()

    @classmethod
    def filter_by_subcategory(cls, session, category_slug, subcategory_slug):
        """Filter products by subcategory"""
        from .category import Category, Subcategory
        return session.query(cls).join(Category).join(Subcategory).filter(
            Category.slug == category_slug,
            Subcategory.slug == subcategory_slug,
            cls.is_active == True
        ).all()

    @classmethod
    def filter_by_brand(cls, session, brand_slug):
        """Filter products by brand"""
        from .brand import Brand
        return session.query(cls).join(Brand).filter(
            Brand.slug == brand_slug,
            cls.is_active == True
        ).all()

    @classmethod
    def filter_by_price_range(cls, session, min_price=None, max_price=None):
        """Filter products by price range"""
        from .sku import SKU
        query = session.query(cls).filter(cls.is_active == True)
        
        if min_price is not None:
            query = query.join(SKU).filter(SKU.price >= min_price)
        if max_price is not None:
            query = query.join(SKU).filter(SKU.price <= max_price)
            
        return query.distinct().all()

    @classmethod
    def filter_by_color(cls, session, color):
        """Filter products by color"""
        from .sku import SKU
        return session.query(cls).join(SKU).filter(
            SKU.color == color,
            cls.is_active == True
        ).distinct().all()

    @classmethod
    def filter_by_size(cls, session, size):
        """Filter products by size"""
        from .sku import SKU
        return session.query(cls).join(SKU).filter(
            SKU.size == size,
            cls.is_active == True
        ).distinct().all()

    @classmethod
    def sort_by_newest(cls, session, products=None):
        """Sort products by newest first"""
        if products is None:
            products = session.query(cls).filter(cls.is_active == True).all()
        return sorted(products, key=lambda p: p.created_at, reverse=True)

    @classmethod
    def sort_by_popular(cls, session, products=None):
        """Sort products by popularity (sold_count)"""
        if products is None:
            products = session.query(cls).filter(cls.is_active == True).all()
        return sorted(products, key=lambda p: p.sold_count, reverse=True)

    @classmethod
    def sort_by_price_high_to_low(cls, session, products=None):
        """Sort products by price high to low"""
        if products is None:
            products = session.query(cls).filter(cls.is_active == True).all()
        return sorted(products, key=lambda p: p.max_price or 0, reverse=True)

    @classmethod
    def sort_by_price_low_to_high(cls, session, products=None):
        """Sort products by price low to high"""
        if products is None:
            products = session.query(cls).filter(cls.is_active == True).all()
        return sorted(products, key=lambda p: p.min_price or 0)

    @classmethod
    def sort_by_discount(cls, session, products=None):
        """Sort products by discount amount"""
        if products is None:
            products = session.query(cls).filter(cls.is_active == True).all()
        return sorted(products, key=lambda p: p.current_discount.discount_percentage if p.current_discount else 0, reverse=True)

    @classmethod
    def sort_by_rating(cls, session, products=None):
        """Sort products by rating"""
        if products is None:
            products = session.query(cls).filter(cls.is_active == True).all()
        return sorted(products, key=lambda p: p.rating_avg, reverse=True)
