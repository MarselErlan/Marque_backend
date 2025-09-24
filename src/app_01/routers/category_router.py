from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models
from ..db import get_db
from ..schemas.category import CategorySchema, SubCategorySchema
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.get("/categories", response_model=List[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.products.category.Category).options(
        joinedload(models.products.category.Category.subcategories)
    ).all()
    
    response_categories = []
    for c in categories:
        response_categories.append(CategorySchema(
            id=str(c.id),
            name=c.name,
            subcategories=[SubCategorySchema(id=str(s.id), name=s.name) for s in c.subcategories]
        ))
    return response_categories
