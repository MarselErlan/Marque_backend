from pydantic import BaseModel
from typing import List, Optional

class CartItemSchema(BaseModel):
    id: int
    sku_id: int
    quantity: int
    name: str
    price: float
    image: str

    class Config:
        orm_mode = True

class CartSchema(BaseModel):
    id: int
    user_id: int
    items: List[CartItemSchema]
    total_items: int
    total_price: float

    class Config:
        orm_mode = True

class AddToCartRequest(BaseModel):
    user_id: int
    sku_id: int
    quantity: int = 1

class GetCartRequest(BaseModel):
    user_id: int

class RemoveFromCartRequest(BaseModel):
    user_id: int
    cart_item_id: int

class UpdateCartItemRequest(BaseModel):
    user_id: int
    cart_item_id: int
    quantity: int

class ClearCartRequest(BaseModel):
    user_id: int
