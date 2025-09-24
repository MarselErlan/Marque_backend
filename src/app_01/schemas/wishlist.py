from pydantic import BaseModel
from typing import List
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
    product_id: int
