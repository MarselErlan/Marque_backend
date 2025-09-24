from pydantic import BaseModel
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
