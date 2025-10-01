"""
Banner Schemas
Request and response models for banners
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime
from enum import Enum

class BannerType(str, Enum):
    """Banner types"""
    SALE = "sale"
    MODEL = "model"

# Request Schemas
class BannerCreate(BaseModel):
    """Schema for creating a new banner"""
    title: str = Field(..., min_length=1, max_length=255, description="Banner title")
    description: Optional[str] = Field(None, max_length=500, description="Banner description")
    image_url: str = Field(..., description="Banner image URL")
    banner_type: BannerType = Field(..., description="Banner type (sale or model)")
    link_url: Optional[str] = Field(None, description="Link URL when banner is clicked")
    is_active: bool = Field(default=True, description="Whether banner is active")
    display_order: int = Field(default=0, description="Display order (lower = first)")
    start_date: Optional[datetime] = Field(None, description="When to start showing banner")
    end_date: Optional[datetime] = Field(None, description="When to stop showing banner")

class BannerUpdate(BaseModel):
    """Schema for updating a banner"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = None
    banner_type: Optional[BannerType] = None
    link_url: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# Response Schemas
class BannerResponse(BaseModel):
    """Schema for banner response"""
    id: int
    title: str
    description: Optional[str]
    image_url: str
    banner_type: BannerType
    link_url: Optional[str]
    is_active: bool
    display_order: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class BannersListResponse(BaseModel):
    """Schema for list of banners"""
    sale_banners: list[BannerResponse] = Field(default_factory=list, description="Sale/promotional banners")
    model_banners: list[BannerResponse] = Field(default_factory=list, description="Model/product showcase banners")
    total: int = Field(..., description="Total number of banners")

class BannerActionResponse(BaseModel):
    """Schema for banner action responses (create, update, delete)"""
    success: bool
    message: str
    banner: Optional[BannerResponse] = None

