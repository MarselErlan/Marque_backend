from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProductSchema(BaseModel):
    id: str
    name: str
    brand: str
    price: float
    originalPrice: Optional[float] = None
    discount: Optional[int] = None
    image: str
    images: Optional[List[str]] = []
    category: str
    subcategory: Optional[str] = None
    sizes: Optional[List[str]] = []
    colors: Optional[List[str]] = []
    rating: Optional[float] = 0
    reviews: Optional[int] = 0
    salesCount: int = 0
    inStock: Optional[bool] = True
    description: Optional[str] = None
    features: Optional[List[str]] = []

    class Config:
        orm_mode = True

class ProductSearchResponse(BaseModel):
    """Response model for product search with pagination"""
    query: str = Field(..., description="The search query used")
    results: List[ProductSchema] = Field(default_factory=list, description="List of products matching the search")
    total: int = Field(..., description="Total number of products found")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_more: bool = Field(..., description="Whether there are more pages available")


# Product Detail Schemas

class BrandSchema(BaseModel):
    """Brand information"""
    id: int
    name: str
    slug: str

    class Config:
        orm_mode = True


class CategoryBreadcrumbSchema(BaseModel):
    """Category for breadcrumbs"""
    id: int
    name: str
    slug: str

    class Config:
        orm_mode = True


class SubcategoryBreadcrumbSchema(BaseModel):
    """Subcategory for breadcrumbs"""
    id: int
    name: str
    slug: str

    class Config:
        orm_mode = True


class ProductImageSchema(BaseModel):
    """Product image/asset"""
    id: int
    url: str
    alt_text: Optional[str] = None
    type: str
    order: int

    class Config:
        orm_mode = True


class SKUDetailSchema(BaseModel):
    """Detailed SKU information"""
    id: int
    sku_code: str
    size: str
    color: str
    price: float
    original_price: Optional[float] = None
    stock: int

    class Config:
        orm_mode = True


class ReviewSchema(BaseModel):
    """Product review"""
    id: int
    rating: int
    text: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class BreadcrumbSchema(BaseModel):
    """Navigation breadcrumb"""
    name: str
    slug: str


class SimilarProductSchema(BaseModel):
    """Similar product preview"""
    id: int
    title: str
    slug: str
    price_min: float
    image: Optional[str] = None
    rating_avg: float = 0.0

    class Config:
        orm_mode = True


class ProductDetailSchema(BaseModel):
    """Complete product detail response"""
    # Basic info
    id: int
    title: str
    slug: str
    description: Optional[str] = None
    
    # Related entities
    brand: BrandSchema
    category: CategoryBreadcrumbSchema
    subcategory: SubcategoryBreadcrumbSchema
    
    # Media
    images: List[ProductImageSchema] = []
    
    # Variants
    skus: List[SKUDetailSchema] = []
    available_sizes: List[str] = []
    available_colors: List[str] = []
    
    # Pricing
    price_min: float
    price_max: float
    
    # Stock
    in_stock: bool
    
    # Ratings & Reviews
    rating_avg: float = 0.0
    rating_count: int = 0
    sold_count: int = 0
    reviews: List[ReviewSchema] = []
    
    # Attributes
    attributes: Optional[Dict[str, Any]] = {}
    
    # Navigation
    breadcrumbs: List[BreadcrumbSchema] = []
    
    # Recommendations
    similar_products: List[SimilarProductSchema] = []

    class Config:
        orm_mode = True


# Product Listing Schemas

class ProductListItemSchema(BaseModel):
    """Product item in listing (grid view)"""
    id: int
    title: str
    slug: str
    
    # Pricing
    price_min: float
    price_max: float
    original_price_min: Optional[float] = None  # For discount calculation
    discount_percent: Optional[int] = None  # Calculated discount %
    
    # Main image
    image: Optional[str] = None
    
    # Rating & popularity
    rating_avg: float = 0.0
    rating_count: int = 0
    sold_count: int = 0
    
    # Brand
    brand_name: str
    brand_slug: str
    
    class Config:
        orm_mode = True


class ProductListResponse(BaseModel):
    """Paginated product listing response"""
    products: List[ProductListItemSchema]
    total: int
    page: int
    limit: int
    total_pages: int
