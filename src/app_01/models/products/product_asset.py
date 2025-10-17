from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ...db import Base


class ProductAsset(Base):
    """Product assets (images/videos) model"""
    __tablename__ = "product_assets"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    type = Column(String(20), nullable=False)  # 'image' or 'video'
    alt_text = Column(String(255), nullable=True)  # Alternative text for accessibility
    order = Column(Integer, default=0)  # Display order
    
    # NEW: Business improvements
    is_primary = Column(Boolean, default=False)  # Main product image
    is_active = Column(Boolean, default=True)  # Can hide without deleting
    width = Column(Integer, nullable=True)  # Image dimensions for optimization
    height = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)  # In bytes, for performance monitoring
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="assets")
    
    # INDEXES for performance
    __table_args__ = (
        Index('idx_product_asset_product_active', 'product_id', 'is_active'),
        Index('idx_product_asset_type', 'type'),
        Index('idx_product_asset_primary', 'is_primary'),
    )

    def __repr__(self):
        return f"<ProductAsset(id={self.id}, type='{self.type}', url='{self.url}')>"

    @property
    def is_image(self):
        """Check if asset is an image"""
        return self.type.lower() == 'image'

    @property
    def is_video(self):
        """Check if asset is a video"""
        return self.type.lower() == 'video'

    @property
    def file_extension(self):
        """Get file extension from URL"""
        return self.url.split('.')[-1].lower() if '.' in self.url else None

    def get_thumbnail_url(self):
        """Get thumbnail URL (assuming thumbnail service)"""
        if self.is_image:
            # Assuming thumbnail service that adds _thumb suffix
            base_url = self.url.rsplit('.', 1)[0]
            extension = self.url.rsplit('.', 1)[1]
            return f"{base_url}_thumb.{extension}"
        return self.url
    
    # NEW: Business methods
    @property
    def aspect_ratio(self):
        """Calculate aspect ratio"""
        if self.width and self.height:
            return round(self.width / self.height, 2)
        return None
    
    @property
    def is_landscape(self):
        """Check if image is landscape"""
        if self.width and self.height:
            return self.width > self.height
        return None
    
    @property
    def is_portrait(self):
        """Check if image is portrait"""
        if self.width and self.height:
            return self.height > self.width
        return None
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
    
    def set_as_primary(self, session):
        """Set this asset as the primary image"""
        # Unset other primary images for this product
        session.query(ProductAsset).filter(
            ProductAsset.product_id == self.product_id,
            ProductAsset.id != self.id
        ).update({"is_primary": False})
        self.is_primary = True
        session.commit()
    
    @classmethod
    def get_primary_image(cls, session, product_id):
        """Get the primary image for a product"""
        return session.query(cls).filter(
            cls.product_id == product_id,
            cls.is_primary == True,
            cls.is_active == True,
            cls.type == 'image'
        ).first()
    
    @classmethod
    def get_all_images(cls, session, product_id):
        """Get all active images for a product"""
        return session.query(cls).filter(
            cls.product_id == product_id,
            cls.is_active == True,
            cls.type == 'image'
        ).order_by(cls.order, cls.created_at).all()
    
    @classmethod
    def get_all_videos(cls, session, product_id):
        """Get all active videos for a product"""
        return session.query(cls).filter(
            cls.product_id == product_id,
            cls.is_active == True,
            cls.type == 'video'
        ).order_by(cls.order, cls.created_at).all()
