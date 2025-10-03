from pydantic import BaseModel, Field
from typing import List, Optional

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
