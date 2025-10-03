from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from .. import models
from ..db import get_db
from ..schemas.product import ProductSchema, ProductSearchResponse
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.get("/products", response_model=List[ProductSchema])
def get_products(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by product name, description, or brand"),
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    brand: Optional[str] = None,
    sort_by: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    query = db.query(models.products.product.Product).options(
        joinedload(models.products.product.Product.brand),
        joinedload(models.products.product.Product.category),
        joinedload(models.products.product.Product.subcategory),
        joinedload(models.products.product.Product.skus),
        joinedload(models.products.product.Product.assets),
        joinedload(models.products.product.Product.reviews)
    )

    # Search functionality - search in title, description, and brand name
    if search:
        search_term = f"%{search}%"
        query = query.outerjoin(models.products.product.Product.brand).filter(
            or_(
                models.products.product.Product.title.ilike(search_term),
                models.products.product.Product.description.ilike(search_term),
                models.products.brand.Brand.name.ilike(search_term)
            )
        )

    if category:
        query = query.join(models.products.product.Product.category).filter(models.products.category.Category.slug == category)
    
    if subcategory:
        query = query.join(models.products.product.Product.subcategory).filter(models.products.category.Subcategory.slug == subcategory)

    if brand:
        query = query.join(models.products.product.Product.brand).filter(models.products.brand.Brand.slug == brand)

    # Sorting logic
    if sort_by == "newest":
        query = query.order_by(models.products.product.Product.created_at.desc())
    elif sort_by == "popular":
        query = query.order_by(models.products.product.Product.sold_count.desc())
    elif sort_by == "price_high_to_low":
        query = query.join(models.products.product.Product.skus).order_by(models.products.sku.SKU.price.desc())
    elif sort_by == "price_low_to_high":
        query = query.join(models.products.product.Product.skus).order_by(models.products.sku.SKU.price.asc())

    # Pagination
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
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

@router.get("/products/search", response_model=ProductSearchResponse)
def search_products(
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=1, description="Search query (min 1 character)"),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    brand: Optional[str] = Query(None, description="Filter by brand slug"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    sort_by: Optional[str] = Query(None, description="Sort: newest, popular, price_low, price_high, relevance"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Advanced product search with filters
    Searches in: product title, description, brand name
    """
    # Base query with relationships
    base_query = db.query(models.products.product.Product).options(
        joinedload(models.products.product.Product.brand),
        joinedload(models.products.product.Product.category),
        joinedload(models.products.product.Product.subcategory),
        joinedload(models.products.product.Product.skus),
        joinedload(models.products.product.Product.assets),
        joinedload(models.products.product.Product.reviews)
    )

    # Search in title, description, and brand
    search_term = f"%{q}%"
    query = base_query.outerjoin(models.products.product.Product.brand).filter(
        or_(
            models.products.product.Product.title.ilike(search_term),
            models.products.product.Product.description.ilike(search_term),
            models.products.brand.Brand.name.ilike(search_term)
        )
    )

    # Category filter
    if category:
        query = query.join(models.products.product.Product.category).filter(
            models.products.category.Category.slug == category
        )

    # Brand filter
    if brand:
        query = query.join(models.products.product.Product.brand).filter(
            models.products.brand.Brand.slug == brand
        )

    # Price range filter
    if min_price is not None or max_price is not None:
        query = query.join(models.products.product.Product.skus)
        if min_price is not None:
            query = query.filter(models.products.sku.SKU.price >= min_price)
        if max_price is not None:
            query = query.filter(models.products.sku.SKU.price <= max_price)

    # Get total count before pagination
    total_count = query.distinct().count()

    # Sorting
    if sort_by == "newest":
        query = query.order_by(models.products.product.Product.created_at.desc())
    elif sort_by == "popular":
        query = query.order_by(models.products.product.Product.sold_count.desc())
    elif sort_by == "price_low":
        query = query.join(models.products.product.Product.skus).order_by(models.products.sku.SKU.price.asc())
    elif sort_by == "price_high":
        query = query.join(models.products.product.Product.skus).order_by(models.products.sku.SKU.price.desc())
    elif sort_by == "relevance":
        # Simple relevance: prioritize title matches over description
        query = query.order_by(
            func.case(
                (models.products.product.Product.title.ilike(search_term), 1),
                else_=2
            )
        )
    else:
        # Default: relevance
        query = query.order_by(
            func.case(
                (models.products.product.Product.title.ilike(search_term), 1),
                else_=2
            )
        )

    # Pagination
    offset = (page - 1) * limit
    products = query.distinct().offset(offset).limit(limit).all()

    # Format response
    response_products = []
    for p in products:
        skus = p.skus
        images = [asset.url for asset in p.assets if asset.type == 'image']
        
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
            features=[]
        ))

    total_pages = (total_count + limit - 1) // limit

    return ProductSearchResponse(
        query=q,
        results=response_products,
        total=total_count,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_more=page < total_pages
    )

@router.get("/products/{product_id}", response_model=ProductSchema)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(models.products.product.Product).options(
        joinedload(models.products.product.Product.brand),
        joinedload(models.products.product.Product.category),
        joinedload(models.products.product.Product.subcategory),
        joinedload(models.products.product.Product.skus),
        joinedload(models.products.product.Product.assets),
        joinedload(models.products.product.Product.reviews)
    ).filter(models.products.product.Product.id == product_id).first()
    
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    skus = p.skus
    images = [asset.url for asset in p.assets if asset.type == 'image']
    
    price = skus[0].price if skus else 0
    original_price = skus[0].original_price if skus and skus[0].original_price else None
    discount = int(((original_price - price) / original_price) * 100) if original_price and price and original_price > price else 0

    return ProductSchema(
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
        features=[]
    )
