from pydantic import BaseModel
from typing import List, Optional

class SubCategorySchema(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True

class CategorySchema(BaseModel):
    id: str
    name: str
    subcategories: List[SubCategorySchema] = []

    class Config:
        orm_mode = True
