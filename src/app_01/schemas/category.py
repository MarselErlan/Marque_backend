from pydantic import BaseModel, Field
from typing import List, Optional


class SubCategorySchema(BaseModel):
    """Basic subcategory schema"""
    id: str
    name: str

    class Config:
        orm_mode = True


class CategorySchema(BaseModel):
    """Basic category schema"""
    id: str
    name: str
    subcategories: List[SubCategorySchema] = []

    class Config:
        orm_mode = True


# Enhanced schemas for catalog navigation
class SubcategoryWithCountSchema(BaseModel):
    """Subcategory with product count"""
    id: int
    name: str
    slug: str
    image_url: Optional[str] = None
    product_count: int
    is_active: bool = True
    sort_order: int = 0

    class Config:
        orm_mode = True


class CategoryWithCountSchema(BaseModel):
    """Category with product count"""
    id: int
    name: str
    slug: str
    icon: Optional[str] = None
    image_url: Optional[str] = None  # Category image/logo
    product_count: int
    is_active: bool = True
    sort_order: int = 0

    class Config:
        orm_mode = True


class CategoryDetailSchema(BaseModel):
    """Detailed category with subcategories"""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    image_url: Optional[str] = None  # Category image/logo
    product_count: int
    subcategories: List[SubcategoryWithCountSchema] = []
    is_active: bool = True
    sort_order: int = 0

    class Config:
        orm_mode = True


class CategoriesListResponse(BaseModel):
    """Response for listing all categories"""
    categories: List[CategoryWithCountSchema]


class SubcategoriesListResponse(BaseModel):
    """Response for listing subcategories"""
    subcategories: List[SubcategoryWithCountSchema]
