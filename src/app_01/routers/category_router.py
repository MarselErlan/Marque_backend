from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import List, Optional
from .. import models
from ..db import get_db
from ..schemas.category import (
    CategorySchema, SubCategorySchema,
    CategoriesListResponse, CategoryWithCountSchema,
    CategoryDetailSchema, SubcategoryWithCountSchema,
    SubcategoriesListResponse
)
from ..schemas.product import ProductListItemSchema, ProductListResponse
from sqlalchemy.orm import joinedload
import math

router = APIRouter()


@router.get("/categories", response_model=CategoriesListResponse)
def get_all_categories(db: Session = Depends(get_db)):
    """
    Get all active main categories with product counts
    """
    # Query categories with product count
    categories = db.query(
        models.products.category.Category,
        func.count(models.products.product.Product.id).label('product_count')
    ).outerjoin(
        models.products.product.Product,
        models.products.category.Category.id == models.products.product.Product.category_id
    ).filter(
        models.products.category.Category.is_active == True
    ).group_by(
        models.products.category.Category.id
    ).order_by(
        models.products.category.Category.sort_order,
        models.products.category.Category.name
    ).all()
    
    # Build response
    category_list = []
    for category, product_count in categories:
        category_list.append(CategoryWithCountSchema(
            id=category.id,
            name=category.name,
            slug=category.slug,
            icon=category.icon,
            image_url=category.image_url,  # Include category image
            product_count=product_count,
            is_active=category.is_active,
            sort_order=category.sort_order
        ))
    
    return CategoriesListResponse(categories=category_list)


@router.get("/categories/{category_slug}", response_model=CategoryDetailSchema)
def get_category_detail(category_slug: str, db: Session = Depends(get_db)):
    """
    Get category detail with subcategories and product counts
    """
    # Get category
    category = db.query(models.products.category.Category).filter(
        models.products.category.Category.slug == category_slug,
        models.products.category.Category.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get product count for this category
    category_product_count = db.query(
        func.count(models.products.product.Product.id)
    ).filter(
        models.products.product.Product.category_id == category.id
    ).scalar() or 0
    
    # Get subcategories with product counts
    subcategories_with_counts = db.query(
        models.products.category.Subcategory,
        func.count(models.products.product.Product.id).label('product_count')
    ).outerjoin(
        models.products.product.Product,
        models.products.category.Subcategory.id == models.products.product.Product.subcategory_id
    ).filter(
        models.products.category.Subcategory.category_id == category.id,
        models.products.category.Subcategory.is_active == True
    ).group_by(
        models.products.category.Subcategory.id
    ).order_by(
        models.products.category.Subcategory.sort_order,
        models.products.category.Subcategory.name
    ).all()
    
    # Build subcategory list
    subcategory_list = []
    for subcategory, product_count in subcategories_with_counts:
        subcategory_list.append(SubcategoryWithCountSchema(
            id=subcategory.id,
            name=subcategory.name,
            slug=subcategory.slug,
            image_url=subcategory.image_url,
            product_count=product_count,
            is_active=subcategory.is_active,
            sort_order=subcategory.sort_order
        ))
    
    return CategoryDetailSchema(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        icon=category.icon,
        image_url=category.image_url,  # Include category image
        product_count=category_product_count,
        subcategories=subcategory_list,
        is_active=category.is_active,
        sort_order=category.sort_order
    )


@router.get("/categories/{category_slug}/subcategories", response_model=SubcategoriesListResponse)
def get_subcategories_by_category(category_slug: str, db: Session = Depends(get_db)):
    """
    Get all subcategories for a specific category with product counts
    """
    # Verify category exists
    category = db.query(models.products.category.Category).filter(
        models.products.category.Category.slug == category_slug,
        models.products.category.Category.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Get subcategories with product counts
    subcategories_with_counts = db.query(
        models.products.category.Subcategory,
        func.count(models.products.product.Product.id).label('product_count')
    ).outerjoin(
        models.products.product.Product,
        models.products.category.Subcategory.id == models.products.product.Product.subcategory_id
    ).filter(
        models.products.category.Subcategory.category_id == category.id,
        models.products.category.Subcategory.is_active == True
    ).group_by(
        models.products.category.Subcategory.id
    ).order_by(
        models.products.category.Subcategory.sort_order,
        models.products.category.Subcategory.name
    ).all()
    
    # Build subcategory list
    subcategory_list = []
    for subcategory, product_count in subcategories_with_counts:
        subcategory_list.append(SubcategoryWithCountSchema(
            id=subcategory.id,
            name=subcategory.name,
            slug=subcategory.slug,
            image_url=subcategory.image_url,
            product_count=product_count,
            is_active=subcategory.is_active,
            sort_order=subcategory.sort_order
        ))
    
    return SubcategoriesListResponse(subcategories=subcategory_list)


@router.get("/subcategories/{subcategory_slug}/products", response_model=ProductListResponse)
def get_products_by_subcategory(
    subcategory_slug: str,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query("newest"),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    sizes: Optional[str] = Query(None),  # Comma-separated: "M,L,XL"
    colors: Optional[str] = Query(None),  # Comma-separated: "black,white"
    brands: Optional[str] = Query(None),  # Comma-separated: "nike,adidas"
    search: Optional[str] = Query(None)
):
    """
    Get products for a specific subcategory with filtering, sorting, and pagination
    """
    # Verify subcategory exists
    subcategory = db.query(models.products.category.Subcategory).filter(
        models.products.category.Subcategory.slug == subcategory_slug,
        models.products.category.Subcategory.is_active == True
    ).first()
    
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    
    # Base query: products in this subcategory
    query = db.query(models.products.product.Product).options(
        joinedload(models.products.product.Product.brand),
        joinedload(models.products.product.Product.skus),
        joinedload(models.products.product.Product.assets)
    ).filter(
        models.products.product.Product.subcategory_id == subcategory.id,
        models.products.product.Product.is_active == True
    )
    
    # Filter: Only products with SKUs
    query = query.join(models.products.product.Product.skus).group_by(models.products.product.Product.id)
    
    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(models.products.product.Product.title.ilike(search_term))
    
    # Price filter (check min price from SKUs)
    if price_min is not None:
        query = query.having(func.min(models.products.sku.SKU.price) >= price_min)
    
    if price_max is not None:
        query = query.having(func.min(models.products.sku.SKU.price) <= price_max)
    
    # Size filter
    if sizes:
        size_list = [s.strip() for s in sizes.split(",")]
        query = query.filter(models.products.sku.SKU.size.in_(size_list))
    
    # Color filter
    if colors:
        color_list = [c.strip() for c in colors.split(",")]
        query = query.filter(models.products.sku.SKU.color.in_(color_list))
    
    # Brand filter
    if brands:
        brand_slugs = [b.strip() for b in brands.split(",")]
        query = query.join(models.products.product.Product.brand).filter(
            models.products.brand.Brand.slug.in_(brand_slugs)
        )
    
    # Sorting (validate and default to newest for invalid values)
    valid_sorts = ["price_asc", "price_desc", "newest", "popular", "rating"]
    if sort_by not in valid_sorts:
        sort_by = "newest"  # Default for invalid values
    
    if sort_by == "price_asc":
        query = query.order_by(func.min(models.products.sku.SKU.price).asc())
    elif sort_by == "price_desc":
        query = query.order_by(func.min(models.products.sku.SKU.price).desc())
    elif sort_by == "popular":
        query = query.order_by(models.products.product.Product.sold_count.desc())
    elif sort_by == "rating":
        query = query.order_by(models.products.product.Product.rating_avg.desc())
    else:  # newest (default)
        query = query.order_by(models.products.product.Product.created_at.desc())
    
    # Get total count (before pagination)
    total = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total / limit) if total > 0 else 0
    offset = (page - 1) * limit
    
    # Apply pagination
    products = query.offset(offset).limit(limit).all()
    
    # Build response
    product_list = []
    for product in products:
        # Get min/max prices from SKUs
        sku_prices = [sku.price for sku in product.skus if sku.stock > 0]
        if not sku_prices:
            sku_prices = [sku.price for sku in product.skus]
        
        price_min_val = min(sku_prices) if sku_prices else 0.0
        price_max_val = max(sku_prices) if sku_prices else 0.0
        
        # Get original prices for discount calculation
        original_prices = [sku.original_price for sku in product.skus if sku.original_price and sku.original_price > 0]
        original_price_min_val = min(original_prices) if original_prices else None
        
        # Calculate discount percentage
        discount_percent = None
        if original_price_min_val and price_min_val < original_price_min_val:
            discount_percent = int(((original_price_min_val - price_min_val) / original_price_min_val) * 100)
        
        # Get main image (first asset)
        main_image = product.assets[0].url if product.assets else None
        
        product_list.append(ProductListItemSchema(
            id=product.id,
            title=product.title,
            slug=product.slug,
            price_min=price_min_val,
            price_max=price_max_val,
            original_price_min=original_price_min_val,
            discount_percent=discount_percent,
            image=main_image,
            rating_avg=product.rating_avg,
            rating_count=product.rating_count,
            sold_count=product.sold_count,
            brand_name=product.brand.name,
            brand_slug=product.brand.slug
        ))
    
    return ProductListResponse(
        products=product_list,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )
