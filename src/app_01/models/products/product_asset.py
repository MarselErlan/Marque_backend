from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
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

    # Relationships
    product = relationship("Product", back_populates="assets")

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
