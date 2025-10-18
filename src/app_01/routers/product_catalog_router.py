"""
Product Catalog Router

API endpoints for catalog management:
- Attributes (sizes, colors, brands)
- Filters
- Seasons (Summer, Winter, Multi)
- Materials (Cotton, Polyester, Wool)
- Styles (Sport, Classic, Casual)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..db import get_db
from ..models.products.product_attribute import ProductAttribute
from ..models.products.product_filter import (
    ProductFilter,
    ProductSeason,
    ProductMaterial,
    ProductStyle
)

router = APIRouter(prefix="/api/v1/catalog", tags=["Product Catalog"])


# ========================
# PYDANTIC SCHEMAS
# ========================

class AttributeResponse(BaseModel):
    """Product attribute response"""
    id: int
    attribute_type: str
    attribute_value: str
    display_name: str
    is_featured: bool
    usage_count: int
    sort_order: int
    
    class Config:
        from_attributes = True


class FilterResponse(BaseModel):
    """Product filter response"""
    id: int
    filter_type: str
    filter_value: str
    display_name: Optional[str]
    usage_count: int
    sort_order: int
    
    class Config:
        from_attributes = True


class SeasonResponse(BaseModel):
    """Season response"""
    id: int
    name: str
    slug: str
    description: Optional[str]
    product_count: int = 0
    is_featured: bool = False
    is_active: bool = True
    sort_order: int = 0
    
    class Config:
        from_attributes = True


class MaterialResponse(BaseModel):
    """Material response"""
    id: int
    name: str
    slug: str
    description: Optional[str]
    product_count: int = 0
    is_featured: bool = False
    is_active: bool = True
    sort_order: int = 0
    
    class Config:
        from_attributes = True


class StyleResponse(BaseModel):
    """Style response"""
    id: int
    name: str
    slug: str
    description: Optional[str]
    product_count: int = 0
    is_featured: bool = False
    is_active: bool = True
    sort_order: int = 0
    
    class Config:
        from_attributes = True


# ========================
# PRODUCT ATTRIBUTES API
# ========================

@router.get("/attributes/sizes", response_model=List[AttributeResponse])
def get_sizes(
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all available sizes
    
    **Args:**
    - `featured_only`: Only return featured sizes
    
    **Returns:** List of size attributes sorted by usage
    """
    if featured_only:
        sizes = ProductAttribute.get_featured_attributes(db, "size")
    else:
        sizes = ProductAttribute.get_sizes(db)
    
    return [AttributeResponse.from_orm(s) for s in sizes]


@router.get("/attributes/colors", response_model=List[AttributeResponse])
def get_colors(
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all available colors
    
    **Args:**
    - `featured_only`: Only return featured colors
    
    **Returns:** List of color attributes
    """
    if featured_only:
        colors = ProductAttribute.get_featured_attributes(db, "color")
    else:
        colors = ProductAttribute.get_colors(db)
    
    return [AttributeResponse.from_orm(c) for c in colors]


@router.get("/attributes/brands", response_model=List[AttributeResponse])
def get_attribute_brands(
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all brand attributes
    
    **Args:**
    - `featured_only`: Only return featured brands
    
    **Returns:** List of brand attributes
    """
    if featured_only:
        brands = ProductAttribute.get_featured_attributes(db, "brand")
    else:
        brands = ProductAttribute.get_brands(db)
    
    return [AttributeResponse.from_orm(b) for b in brands]


@router.get("/attributes/most-used/{attribute_type}", response_model=List[AttributeResponse])
def get_most_used_attributes(
    attribute_type: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get most popular attributes by usage
    
    **Great for:**
    - Popular sizes section
    - Trending colors
    - Top brands
    
    **Args:**
    - `attribute_type`: size, color, brand, or category
    - `limit`: Number of results (1-50)
    
    **Returns:** Most used attributes sorted by popularity
    """
    attrs = ProductAttribute.get_most_used_attributes(db, attribute_type, limit)
    return [AttributeResponse.from_orm(a) for a in attrs]


# ========================
# PRODUCT FILTERS API
# ========================

@router.get("/filters/{filter_type}", response_model=List[FilterResponse])
def get_filters_by_type(
    filter_type: str,
    db: Session = Depends(get_db)
):
    """
    Get all filters of a specific type
    
    **Filter types:**
    - size
    - color
    - brand
    - season
    - material
    - style
    - price_range
    
    **Args:**
    - `filter_type`: Type of filter
    
    **Returns:** List of filter options
    """
    filters = ProductFilter.get_filters_by_type(db, filter_type)
    return [FilterResponse.from_orm(f) for f in filters]


@router.get("/filters/popular/{filter_type}", response_model=List[FilterResponse])
def get_popular_filters(
    filter_type: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get most popular filters by customer usage
    
    **Use for:**
    - Show most-clicked filters
    - Optimize filter ordering
    - Identify customer preferences
    
    **Args:**
    - `filter_type`: Type of filter
    - `limit`: Number of results
    
    **Returns:** Most used filters
    """
    filters = ProductFilter.get_popular_filters(db, filter_type, limit)
    return [FilterResponse.from_orm(f) for f in filters]


@router.get("/filters", response_model=dict)
def get_all_filter_types(db: Session = Depends(get_db)):
    """
    Get all available filter types
    
    **Returns:** Dictionary of filter type names
    """
    types = ProductFilter.get_all_filter_types(db)
    return {
        "filter_types": [t[0] for t in types],
        "count": len(types)
    }


# ========================
# SEASONS API
# ========================

@router.get("/seasons", response_model=List[SeasonResponse])
def get_seasons(
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all product seasons
    
    **Examples:**
    - Лето (Summer)
    - Зима (Winter)
    - Мульти (Multi-season)
    
    **Args:**
    - `featured_only`: Only return featured seasons
    
    **Returns:** List of seasons with product counts
    """
    if featured_only:
        seasons = ProductSeason.get_featured_seasons(db)
    else:
        seasons = ProductSeason.get_all_active(db)
    
    return [SeasonResponse.from_orm(s) for s in seasons]


@router.get("/seasons/popular", response_model=List[SeasonResponse])
def get_popular_seasons(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Get seasons with most products
    
    **Use for:**
    - Homepage seasonal collections
    - Marketing campaigns
    
    **Args:**
    - `limit`: Number of seasons
    
    **Returns:** Seasons sorted by product count
    """
    seasons = ProductSeason.get_popular_seasons(db, limit)
    return [SeasonResponse.from_orm(s) for s in seasons]


@router.get("/seasons/{slug}", response_model=SeasonResponse)
def get_season_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get season by slug
    
    **Args:**
    - `slug`: Season slug (e.g., "summer", "winter")
    
    **Returns:** Season details with product count
    """
    season = db.query(ProductSeason).filter(
        ProductSeason.slug == slug,
        ProductSeason.is_active == True
    ).first()
    
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    
    return SeasonResponse.from_orm(season)


# ========================
# MATERIALS API
# ========================

@router.get("/materials", response_model=List[MaterialResponse])
def get_materials(
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all product materials
    
    **Examples:**
    - Хлопок (Cotton)
    - Полиэстер (Polyester)
    - Шерсть (Wool)
    
    **Args:**
    - `featured_only`: Only return featured materials
    
    **Returns:** List of materials with product counts
    """
    if featured_only:
        materials = ProductMaterial.get_featured_materials(db)
    else:
        materials = ProductMaterial.get_all_active(db)
    
    return [MaterialResponse.from_orm(m) for m in materials]


@router.get("/materials/popular", response_model=List[MaterialResponse])
def get_popular_materials(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get materials with most products
    
    **Use for:**
    - Material-based collections
    - Filter suggestions
    
    **Args:**
    - `limit`: Number of materials
    
    **Returns:** Materials sorted by product count
    """
    materials = ProductMaterial.get_popular_materials(db, limit)
    return [MaterialResponse.from_orm(m) for m in materials]


@router.get("/materials/{slug}", response_model=MaterialResponse)
def get_material_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get material by slug
    
    **Args:**
    - `slug`: Material slug (e.g., "cotton", "polyester")
    
    **Returns:** Material details
    """
    material = db.query(ProductMaterial).filter(
        ProductMaterial.slug == slug,
        ProductMaterial.is_active == True
    ).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    return MaterialResponse.from_orm(material)


# ========================
# STYLES API
# ========================

@router.get("/styles", response_model=List[StyleResponse])
def get_styles(
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all product styles
    
    **Examples:**
    - Спортивный (Sport)
    - Классический (Classic)
    - Повседневный (Casual)
    
    **Args:**
    - `featured_only`: Only return featured styles
    
    **Returns:** List of styles with product counts
    """
    if featured_only:
        styles = ProductStyle.get_featured_styles(db)
    else:
        styles = ProductStyle.get_all_active(db)
    
    return [StyleResponse.from_orm(s) for s in styles]


@router.get("/styles/popular", response_model=List[StyleResponse])
def get_popular_styles(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get styles with most products
    
    **Use for:**
    - Style-based collections
    - Homepage sections
    
    **Args:**
    - `limit`: Number of styles
    
    **Returns:** Styles sorted by product count
    """
    styles = ProductStyle.get_popular_styles(db, limit)
    return [StyleResponse.from_orm(s) for s in styles]


@router.get("/styles/{slug}", response_model=StyleResponse)
def get_style_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get style by slug
    
    **Args:**
    - `slug`: Style slug (e.g., "sport", "classic")
    
    **Returns:** Style details
    """
    style = db.query(ProductStyle).filter(
        ProductStyle.slug == slug,
        ProductStyle.is_active == True
    ).first()
    
    if not style:
        raise HTTPException(status_code=404, detail="Style not found")
    
    return StyleResponse.from_orm(style)


# ========================
# CATALOG OVERVIEW API
# ========================

@router.get("/overview")
def get_catalog_overview(db: Session = Depends(get_db)):
    """
    Get complete catalog overview
    
    **Returns:**
    - Total counts for all categories
    - Featured collections
    - Popular items
    
    **Use for:**
    - Dashboard
    - Homepage data
    - Quick stats
    """
    from sqlalchemy import func
    
    return {
        "attributes": {
            "total_sizes": db.query(func.count(ProductAttribute.id)).filter(
                ProductAttribute.attribute_type == "size",
                ProductAttribute.is_active == True
            ).scalar(),
            "total_colors": db.query(func.count(ProductAttribute.id)).filter(
                ProductAttribute.attribute_type == "color",
                ProductAttribute.is_active == True
            ).scalar(),
            "total_brands": db.query(func.count(ProductAttribute.id)).filter(
                ProductAttribute.attribute_type == "brand",
                ProductAttribute.is_active == True
            ).scalar()
        },
        "seasons": {
            "total": db.query(func.count(ProductSeason.id)).filter(
                ProductSeason.is_active == True
            ).scalar(),
            "featured": db.query(func.count(ProductSeason.id)).filter(
                ProductSeason.is_active == True,
                ProductSeason.is_featured == True
            ).scalar()
        },
        "materials": {
            "total": db.query(func.count(ProductMaterial.id)).filter(
                ProductMaterial.is_active == True
            ).scalar(),
            "featured": db.query(func.count(ProductMaterial.id)).filter(
                ProductMaterial.is_active == True,
                ProductMaterial.is_featured == True
            ).scalar()
        },
        "styles": {
            "total": db.query(func.count(ProductStyle.id)).filter(
                ProductStyle.is_active == True
            ).scalar(),
            "featured": db.query(func.count(ProductStyle.id)).filter(
                ProductStyle.is_active == True,
                ProductStyle.is_featured == True
            ).scalar()
        }
    }

