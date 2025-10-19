from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from ...db import Base
from decimal import Decimal


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
    title = Column(String(255), nullable=False, index=True)  # Added index for search performance
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Image columns (Pillow-processed)
    main_image = Column(String(500), nullable=True)  # Main product image URL
    additional_images = Column(JSON, nullable=True)  # Array of additional image URLs (list of strings)
    
    # Business metrics
    sold_count = Column(Integer, default=0, index=True)  # Added index for sorting
    view_count = Column(Integer, default=0)  # Track product views for analytics
    rating_avg = Column(Float, default=0.0, index=True)  # Added index for sorting
    rating_count = Column(Integer, default=0)
    
    # Status flags
    is_active = Column(Boolean, default=True, index=True)  # Added index for filtering
    is_featured = Column(Boolean, default=False, index=True)  # Added index for homepage queries
    is_new = Column(Boolean, default=True)  # Mark as new product (auto-set based on created_at)
    is_trending = Column(Boolean, default=False)  # Manually curated trending products
    
    # SEO fields (CRITICAL for business!)
    meta_title = Column(String(255), nullable=True)  # SEO page title
    meta_description = Column(Text, nullable=True)  # SEO meta description
    meta_keywords = Column(Text, nullable=True)  # SEO keywords (comma-separated)
    
    # Business attributes
    attributes = Column(JSON, nullable=True)  # {gender, season, composition, article}
    tags = Column(JSON, nullable=True)  # Array of tags for better discoverability
    
    # Inventory alerts
    low_stock_threshold = Column(Integer, default=5)  # Alert when total stock below this
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # Added index for sorting
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_product_active_featured', 'is_active', 'is_featured'),
        Index('idx_product_category_active', 'category_id', 'is_active'),
        Index('idx_product_subcategory_active', 'subcategory_id', 'is_active'),
        Index('idx_product_brand_active', 'brand_id', 'is_active'),
        Index('idx_product_sold_count_desc', sold_count.desc()),
        Index('idx_product_rating_desc', rating_avg.desc()),
        Index('idx_product_created_desc', created_at.desc()),
    )

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
    # TODO: Re-enable when WishlistItem model is properly integrated
    # wishlist_items = relationship("WishlistItem", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, title='{self.title}', brand_id={self.brand_id})>"

    @property
    def available_skus(self):
        """Get only active SKUs for this product"""
        return [sku for sku in self.skus if sku.is_active]

    @property
    def in_stock_skus(self):
        """Get only SKUs that have stock available"""
        return [sku for sku in self.available_skus if sku.stock > 0]

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
    def display_price(self):
        """Get the primary display price (minimum price or first SKU price)"""
        if self.available_skus:
            return self.min_price
        return 0.0
    
    @property
    def original_price(self):
        """Get original price for discount calculation"""
        if not self.available_skus:
            return None
        original_prices = [sku.original_price for sku in self.available_skus if sku.original_price]
        if original_prices:
            return min(original_prices)
        return None
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.original_price and self.display_price:
            if self.original_price > self.display_price:
                return int(((self.original_price - self.display_price) / self.original_price) * 100)
        return 0

    @property
    def total_stock(self):
        """Get total stock across all SKUs"""
        return sum(sku.stock for sku in self.available_skus)
    
    @property
    def is_low_stock(self):
        """Check if product is running low on stock"""
        return 0 < self.total_stock <= self.low_stock_threshold
    
    @property
    def stock_status(self):
        """Get human-readable stock status"""
        stock = self.total_stock
        if stock == 0:
            return "out_of_stock"
        elif stock <= self.low_stock_threshold:
            return "low_stock"
        else:
            return "in_stock"

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
    
    def increment_view_count(self):
        """Increment product view count (call when product is viewed)"""
        self.view_count += 1
    
    def increment_sold_count(self, quantity=1):
        """Increment sold count when product is purchased"""
        self.sold_count += quantity
    
    def check_new_status(self, days_threshold=30):
        """Update is_new flag based on creation date"""
        if self.created_at:
            age_days = (datetime.now(self.created_at.tzinfo) - self.created_at).days
            self.is_new = age_days <= days_threshold
    
    def get_all_images(self):
        """Get all product images as a list"""
        images = []
        if self.main_image:
            images.append(self.main_image)
        if self.additional_images and isinstance(self.additional_images, list):
            images.extend(self.additional_images)
        return images
    
    def get_image_or_default(self, default_image="/static/images/no-image.png"):
        """Get main image or default placeholder"""
        return self.main_image if self.main_image else default_image
    
    def get_available_sizes(self):
        """Get list of unique available sizes"""
        return sorted(list(set(sku.size for sku in self.in_stock_skus)))
    
    def get_available_colors(self):
        """Get list of unique available colors"""
        return list(set(sku.color for sku in self.in_stock_skus))
    
    def validate_for_activation(self):
        """Validate if product can be activated (has required data)"""
        errors = []
        if not self.title:
            errors.append("Title is required")
        if not self.slug:
            errors.append("Slug is required")
        if not self.main_image:
            errors.append("Main image is required")
        if not self.skus or len(self.skus) == 0:
            errors.append("At least one SKU is required")
        if not self.brand_id:
            errors.append("Brand is required")
        if not self.category_id:
            errors.append("Category is required")
        return len(errors) == 0, errors

    @property
    def main_asset_image(self):
        """Get main product image from assets (legacy - use main_image column instead)"""
        main_assets = [asset for asset in self.assets if asset.type == "image" and asset.order == 1]
        return main_assets[0] if main_assets else None

    @property
    def all_asset_images(self):
        """Get all product images from assets (legacy - use additional_images column instead)"""
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
    def get_active_products(cls, session):
        """Get all active products"""
        return session.query(cls).filter(cls.is_active == True).all()
    
    @classmethod
    def get_featured_products(cls, session, limit=10):
        """Get featured products for homepage"""
        return session.query(cls).filter(
            cls.is_active == True,
            cls.is_featured == True
        ).order_by(cls.sold_count.desc()).limit(limit).all()
    
    @classmethod
    def get_new_products(cls, session, limit=20):
        """Get newest products"""
        return session.query(cls).filter(
            cls.is_active == True,
            cls.is_new == True
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_trending_products(cls, session, limit=10):
        """Get trending products"""
        return session.query(cls).filter(
            cls.is_active == True,
            cls.is_trending == True
        ).order_by(cls.sold_count.desc()).limit(limit).all()
    
    @classmethod
    def get_best_sellers(cls, session, limit=10):
        """Get best selling products"""
        return session.query(cls).filter(
            cls.is_active == True
        ).order_by(cls.sold_count.desc()).limit(limit).all()
    
    @classmethod
    def get_top_rated(cls, session, min_reviews=5, limit=10):
        """Get top rated products (with minimum reviews)"""
        return session.query(cls).filter(
            cls.is_active == True,
            cls.rating_count >= min_reviews
        ).order_by(cls.rating_avg.desc()).limit(limit).all()
    
    @classmethod
    def get_on_sale_products(cls, session):
        """Get products with discounts"""
        from .sku import SKU
        # Use distinct(cls.id) to avoid PostgreSQL JSON comparison issues
        return session.query(cls).join(SKU).filter(
            cls.is_active == True,
            SKU.original_price.isnot(None),
            SKU.original_price > SKU.price
        ).distinct(cls.id).all()
    
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
