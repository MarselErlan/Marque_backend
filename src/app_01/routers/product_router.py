from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models
from ..db import get_db
from ..schemas.product import ProductSchema
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.get("/products", response_model=List[ProductSchema])
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.products.product.Product).options(
        joinedload(models.products.product.Product.brand),
        joinedload(models.products.product.Product.category),
        joinedload(models.products.product.Product.subcategory),
        joinedload(models.products.product.Product.skus),
        joinedload(models.products.product.Product.assets),
        joinedload(models.products.product.Product.reviews)
    ).all()
    
    response_products = []
    for p in products:
        skus = p.skus
        images = [asset.url for asset in p.assets if asset.type == 'image']
        
        # Simplified price logic, can be improved
        price = skus[0].price if skus else 0
        original_price = skus[0].original_price if skus and skus[0].original_price else None
        discount = int(((original_price - price) / original_price) * 100) if original_price and price and original_price > price else 0

        response_products.append(ProductSchema(
            id=str(p.id),
            name=p.title,
            brand=p.brand.name if p.brand else "",
            price=price,
            originalPrice=original_price,
            discount=discount,
            image=images[0] if images else "",
            images=images,
            category=p.category.name if p.category else "",
            subcategory=p.subcategory.name if p.subcategory else "",
            sizes=list(set(s.size for s in skus if s.size)),
            colors=list(set(s.color for s in skus if s.color)),
            rating=p.rating_avg,
            reviews=p.rating_count,
            salesCount=p.sold_count,
            inStock=p.is_in_stock,
            description=p.description,
            features=[] # No features in backend model yet
        ))
    return response_products
