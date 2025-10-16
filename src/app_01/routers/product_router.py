from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from .. import models
from ..db import get_db
from ..schemas.product import (
    ProductSchema, ProductDetailSchema,
    BrandSchema, CategoryBreadcrumbSchema, SubcategoryBreadcrumbSchema,
    ProductImageSchema, SKUDetailSchema, ReviewSchema, BreadcrumbSchema,
    SimilarProductSchema, ProductListItemSchema, ProductListResponse
)
from sqlalchemy.orm import joinedload
import math

router = APIRouter()


@router.get("/products/best-sellers", response_model=List[ProductListItemSchema])
def get_best_selling_products(
    db: Session = Depends(get_db),
    limit: Optional[int] = Query(None, ge=1, le=500, description="Limit number of products (optional, default: all)")
):
    """
    Get all products sorted by most sold (best sellers first) for main page
    No filters - just pure best sellers across all categories
    """
    # Base query: all active products with SKUs
    query = db.query(models.products.product.Product).options(
        joinedload(models.products.product.Product.brand),
        joinedload(models.products.product.Product.skus),
        joinedload(models.products.product.Product.assets)
    ).filter(
        models.products.product.Product.is_active == True
    )
    
    # Join SKUs to ensure product has variants
    query = query.join(models.products.product.Product.skus).group_by(models.products.product.Product.id)
    
    # Sort by most sold (best sellers first)
    query = query.order_by(models.products.product.Product.sold_count.desc())
    
    # Apply limit if provided
    if limit:
        query = query.limit(limit)
    
    products = query.all()
    
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
        
        # Get main image from new fields or fallback to old assets
        main_image = None
        if product.main_image:
            main_image = product.main_image
        elif product.assets and len(product.assets) > 0:
            main_image = product.assets[0].url
        
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
    
    return product_list


@router.get("/products/search", response_model=ProductListResponse)
def search_products(
    query: str = Query(..., min_length=1, max_length=200, description="Search query"),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query("relevance", description="Sort by: relevance, price_asc, price_desc, newest, popular, rating"),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    sizes: Optional[str] = Query(None, description="Comma-separated sizes: M,L,XL"),
    colors: Optional[str] = Query(None, description="Comma-separated colors: black,white"),
    brands: Optional[str] = Query(None, description="Comma-separated brand slugs: nike,adidas"),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory slug")
):
    """
    Global product search with filters, sorting, and pagination.
    Returns products in the same format as subcategory pages.
    
    Search across ALL products (not limited to one subcategory).
    Results can be filtered by category, subcategory, brand, price, size, color.
    """
    # Base query: all active products with SKUs
    search_query = db.query(models.products.product.Product).options(
        joinedload(models.products.product.Product.brand),
        joinedload(models.products.product.Product.skus),
        joinedload(models.products.product.Product.assets),
        joinedload(models.products.product.Product.category),
        joinedload(models.products.product.Product.subcategory)
    ).filter(
        models.products.product.Product.is_active == True
    )
    
    # Join SKUs (required for filtering and to ensure products have variants)
    search_query = search_query.join(models.products.product.Product.skus).filter(
        models.products.sku.SKU.is_active == True
    )
    
    # Full-text search on title and description
    search_term = f"%{query}%"
    search_query = search_query.filter(
        or_(
            models.products.product.Product.title.ilike(search_term),
            models.products.product.Product.description.ilike(search_term)
        )
    )
    
    # Category filter
    if category:
        search_query = search_query.join(models.products.product.Product.category).filter(
            models.products.category.Category.slug == category
        )
    
    # Subcategory filter
    if subcategory:
        search_query = search_query.join(models.products.product.Product.subcategory).filter(
            models.products.category.Subcategory.slug == subcategory
        )
    
    # Price filters
    if price_min is not None:
        search_query = search_query.filter(models.products.sku.SKU.price >= price_min)
    if price_max is not None:
        search_query = search_query.filter(models.products.sku.SKU.price <= price_max)
    
    # Size filter
    if sizes:
        size_list = [s.strip() for s in sizes.split(",")]
        search_query = search_query.filter(models.products.sku.SKU.size.in_(size_list))
    
    # Color filter
    if colors:
        color_list = [c.strip() for c in colors.split(",")]
        search_query = search_query.filter(models.products.sku.SKU.color.in_(color_list))
    
    # Brand filter
    if brands:
        brand_slugs = [b.strip() for b in brands.split(",")]
        search_query = search_query.join(models.products.product.Product.brand).filter(
            models.products.brand.Brand.slug.in_(brand_slugs)
        )
    
    # Group by product to avoid duplicates from SKU joins
    search_query = search_query.group_by(models.products.product.Product.id)
    
    # Sorting
    valid_sorts = ["relevance", "price_asc", "price_desc", "newest", "popular", "rating"]
    if sort_by not in valid_sorts:
        sort_by = "relevance"
    
    if sort_by == "price_asc":
        search_query = search_query.order_by(func.min(models.products.sku.SKU.price).asc())
    elif sort_by == "price_desc":
        search_query = search_query.order_by(func.min(models.products.sku.SKU.price).desc())
    elif sort_by == "popular":
        search_query = search_query.order_by(models.products.product.Product.sold_count.desc())
    elif sort_by == "rating":
        search_query = search_query.order_by(models.products.product.Product.rating_avg.desc())
    elif sort_by == "newest":
        search_query = search_query.order_by(models.products.product.Product.created_at.desc())
    else:  # relevance (default)
        # For relevance, prioritize title matches over description matches
        # This is a simple relevance: title match = higher priority
        search_query = search_query.order_by(
            models.products.product.Product.title.ilike(search_term).desc(),
            models.products.product.Product.sold_count.desc()
        )
    
    # Get total count before pagination
    total = search_query.count()
    
    # Pagination
    offset = (page - 1) * limit
    total_pages = math.ceil(total / limit) if total > 0 else 0
    has_more = page < total_pages
    
    # Apply pagination
    products = search_query.offset(offset).limit(limit).all()
    
    # Build response (same format as subcategory pages)
    product_list = []
    for product in products:
        # Get main image from new fields or fallback to old assets
        main_image = None
        if product.main_image:
            main_image = product.main_image
        elif product.assets:
            image_assets = sorted([a for a in product.assets if a.is_image], key=lambda x: x.order)
            if image_assets:
                main_image = image_assets[0].url
        
        # Get price range from SKUs
        if product.skus:
            prices = [sku.price for sku in product.skus if sku.stock > 0]
            if not prices:
                prices = [sku.price for sku in product.skus]
            
            price_min = min(prices) if prices else 0.0
            price_max = max(prices) if prices else 0.0
            
            # Get original price for discount calculation
            original_prices = [sku.original_price for sku in product.skus if sku.original_price and sku.original_price > 0]
            original_price_min = min(original_prices) if original_prices else None
            
            discount_percent = None
            if original_price_min and original_price_min > price_min:
                discount_percent = int(((original_price_min - price_min) / original_price_min) * 100)
            
            in_stock = any(sku.stock > 0 for sku in product.skus)
        else:
            price_min = 0.0
            price_max = 0.0
            original_price_min = None
            discount_percent = None
            in_stock = False
        
        product_list.append(ProductListItemSchema(
            id=product.id,
            title=product.title,
            slug=product.slug,
            brand_name=product.brand.name if product.brand else "Unknown",
            brand_slug=product.brand.slug if product.brand else "unknown",
            image=main_image,
            price_min=price_min,
            price_max=price_max,
            original_price_min=original_price_min,
            discount_percent=discount_percent,
            rating_avg=product.rating_avg or 0.0,
            rating_count=product.rating_count or 0,
            sold_count=product.sold_count or 0,
            in_stock=in_stock
        ))
    
    return ProductListResponse(
        products=product_list,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_more=has_more
    )


@router.get("/products/{slug}", response_model=ProductDetailSchema)
def get_product_detail(slug: str, db: Session = Depends(get_db)):
    """
    Get complete product details by slug
    """
    # Load product with all relationships
    product = db.query(models.products.product.Product).options(
        joinedload(models.products.product.Product.brand),
        joinedload(models.products.product.Product.category),
        joinedload(models.products.product.Product.subcategory),
        joinedload(models.products.product.Product.skus),
        joinedload(models.products.product.Product.assets),
        joinedload(models.products.product.Product.reviews)
    ).filter(
        models.products.product.Product.slug == slug,
        models.products.product.Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Build brand info
    brand_info = BrandSchema(
        id=product.brand.id,
        name=product.brand.name,
        slug=product.brand.slug
    )
    
    # Build category info
    category_info = CategoryBreadcrumbSchema(
        id=product.category.id,
        name=product.category.name,
        slug=product.category.slug
    )
    
    # Build subcategory info
    subcategory_info = SubcategoryBreadcrumbSchema(
        id=product.subcategory.id,
        name=product.subcategory.name,
        slug=product.subcategory.slug
    )
    
    # Build images list from new main_image and additional_images fields
    images = []
    
    # Add main image first (if exists)
    if product.main_image:
        images.append(ProductImageSchema(
            id=0,  # Main image
            url=product.main_image,
            alt_text=product.title,
            type='image',
            order=0
        ))
    
    # Add additional images (if exist)
    if product.additional_images and isinstance(product.additional_images, list):
        for idx, img_url in enumerate(product.additional_images, start=1):
            images.append(ProductImageSchema(
                id=idx,
                url=img_url,
                alt_text=f"{product.title} - изображение {idx}",
                type='image',
                order=idx
            ))
    
    # Fallback: If no images in new fields, try old assets (for backward compatibility)
    if not images and product.assets:
        images = [
            ProductImageSchema(
                id=asset.id,
                url=asset.url,
                alt_text=asset.alt_text,
                type=asset.type,
                order=asset.order
            )
            for asset in sorted(product.assets, key=lambda x: x.order)
        ]
    
    # Build SKUs list
    skus = [
        SKUDetailSchema(
            id=sku.id,
            sku_code=sku.sku_code,
            size=sku.size,
            color=sku.color,
            price=sku.price,
            original_price=sku.original_price,
            stock=sku.stock
        )
        for sku in product.skus
    ]
    
    # Get unique sizes and colors
    available_sizes = sorted(list(set(sku.size for sku in product.skus)))
    available_colors = list(set(sku.color for sku in product.skus))
    
    # Calculate price range
    prices = [sku.price for sku in product.skus]
    price_min = min(prices) if prices else 0.0
    price_max = max(prices) if prices else 0.0
    
    # Check stock availability
    in_stock = any(sku.stock > 0 for sku in product.skus)
    
    # Build reviews list
    reviews = [
        ReviewSchema(
            id=review.id,
            rating=review.rating,
            text=review.text,
            created_at=review.created_at
        )
        for review in product.reviews
    ]
    
    # Build breadcrumbs
    breadcrumbs = [
        BreadcrumbSchema(name="Главная", slug="/"),
        BreadcrumbSchema(name=product.category.name, slug=product.category.slug),
        BreadcrumbSchema(name=product.subcategory.name, slug=product.subcategory.slug),
        BreadcrumbSchema(name=product.title, slug=product.slug)
    ]
    
    # Get similar products (same subcategory, exclude current)
    similar_products_query = db.query(models.products.product.Product).options(
        joinedload(models.products.product.Product.skus),
        joinedload(models.products.product.Product.assets)
    ).filter(
        models.products.product.Product.subcategory_id == product.subcategory_id,
        models.products.product.Product.id != product.id,
        models.products.product.Product.is_active == True
    ).order_by(
        models.products.product.Product.rating_avg.desc()
    ).limit(4).all()
    
    similar_products = []
    for sim_product in similar_products_query:
        # Get first image from new fields or fallback to old assets
        first_image = None
        if sim_product.main_image:
            first_image = sim_product.main_image
        elif sim_product.assets and len(sim_product.assets) > 0:
            first_image = sim_product.assets[0].url
        
        # Get min price from SKUs
        sim_prices = [sku.price for sku in sim_product.skus]
        sim_price_min = min(sim_prices) if sim_prices else 0.0
        
        similar_products.append(SimilarProductSchema(
            id=sim_product.id,
            title=sim_product.title,
            slug=sim_product.slug,
            price_min=sim_price_min,
            image=first_image,
            rating_avg=sim_product.rating_avg
        ))
    
    # Build complete response
    return ProductDetailSchema(
        id=product.id,
        title=product.title,
        slug=product.slug,
        description=product.description,
        brand=brand_info,
        category=category_info,
        subcategory=subcategory_info,
        images=images,
        skus=skus,
        available_sizes=available_sizes,
        available_colors=available_colors,
        price_min=price_min,
        price_max=price_max,
        in_stock=in_stock,
        rating_avg=product.rating_avg,
        rating_count=product.rating_count,
        sold_count=product.sold_count,
        reviews=reviews,
        attributes=product.attributes or {},
        breadcrumbs=breadcrumbs,
        similar_products=similar_products
    )


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
        
        # Build images list from new main_image and additional_images fields
        images = []
        
        # Add main image first (if exists)
        if p.main_image:
            images.append(p.main_image)
        
        # Add additional images (if exist)
        if p.additional_images and isinstance(p.additional_images, list):
            images.extend(p.additional_images)
        
        # Fallback: If no images in new fields, try old assets (for backward compatibility)
        if not images and p.assets:
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
    
    # Build images list from new main_image and additional_images fields
    images = []
    
    # Add main image first (if exists)
    if p.main_image:
        images.append(p.main_image)
    
    # Add additional images (if exist)
    if p.additional_images and isinstance(p.additional_images, list):
        images.extend(p.additional_images)
    
    # Fallback: If no images in new fields, try old assets (for backward compatibility)
    if not images and p.assets:
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
