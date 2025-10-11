"""
Banner Schemas
Request and response models for banners
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class BannerType(str, Enum):
    """Banner types"""
    HERO = "hero"
    PROMO = "promo"
    CATEGORY = "category"


# Request Schemas
class BannerCreate(BaseModel):
    """Schema for creating a new banner"""
    title: str = Field(..., min_length=1, max_length=255, description="Banner title")
    subtitle: Optional[str] = Field(None, max_length=500, description="Banner subtitle")
    description: Optional[str] = Field(None, max_length=1000, description="Full description")
    image_url: str = Field(..., description="Banner image URL (desktop)")
    mobile_image_url: Optional[str] = Field(None, description="Banner image URL (mobile)")
    banner_type: BannerType = Field(default=BannerType.HERO, description="Banner type")
    cta_text: Optional[str] = Field(None, max_length=100, description="Call-to-action button text")
    cta_url: Optional[str] = Field(None, description="Call-to-action URL")
    is_active: bool = Field(default=True, description="Whether banner is active")
    display_order: int = Field(default=0, description="Display order (lower = first)")
    start_date: Optional[datetime] = Field(None, description="When to start showing banner")
    end_date: Optional[datetime] = Field(None, description="When to stop showing banner")


class BannerUpdate(BaseModel):
    """Schema for updating a banner"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    image_url: Optional[str] = None
    mobile_image_url: Optional[str] = None
    banner_type: Optional[BannerType] = None
    cta_text: Optional[str] = Field(None, max_length=100)
    cta_url: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# Response Schemas
class BannerResponse(BaseModel):
    """Schema for banner response"""
    id: int
    title: str
    subtitle: Optional[str]
    description: Optional[str]
    image_url: str
    mobile_image_url: Optional[str]
    banner_type: BannerType
    cta_text: Optional[str]
    cta_url: Optional[str]
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
    hero_banners: list[BannerResponse] = Field(default_factory=list, description="Hero/carousel banners")
    promo_banners: list[BannerResponse] = Field(default_factory=list, description="Promotional banners")
    category_banners: list[BannerResponse] = Field(default_factory=list, description="Category showcase banners")
    total: int = Field(..., description="Total number of banners")


class BannerActionResponse(BaseModel):
    """Schema for banner action responses (create, update, delete)"""
    success: bool
    message: str
    banner: Optional[BannerResponse] = None

