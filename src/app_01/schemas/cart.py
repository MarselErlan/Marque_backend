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
    sku_id: int
    quantity: int = 1
