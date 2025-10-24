from pydantic import BaseModel
from typing import List, Optional
from .product import ProductSchema

class WishlistItemSchema(BaseModel):
    id: int
    product: ProductSchema

    class Config:
        orm_mode = True

class WishlistSchema(BaseModel):
    id: int
    user_id: int
    items: List[WishlistItemSchema]

    class Config:
        orm_mode = True

class AddToWishlistRequest(BaseModel):
    user_id: int
    product_id: int

class RemoveFromWishlistRequest(BaseModel):
    user_id: int
    product_id: int

class GetWishlistRequest(BaseModel):
    user_id: int

class ClearWishlistRequest(BaseModel):
    user_id: int
