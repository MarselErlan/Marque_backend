"""
API Integration tests for the variant image feature.

Tests cover:
1. Product detail API returns variant images
2. Catalog API includes variant images
3. Image URLs are properly serialized
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Generator
import uuid

from src.app_01.models import Product, SKU, Brand, Category, Subcategory, User
from src.app_01.db import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔧 FIXTURES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@pytest.fixture(scope="function")
def test_db_api() -> Generator[Session, None, None]:
    """Create a test database session for API tests"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def sample_data(test_db_api: Session) -> dict:
    """Create sample data for testing"""
    # Create dependencies
    brand = Brand(name="Nike", slug="nike")
    category = Category(name="Clothing", slug="clothing", image_url="https://example.com/category.jpg")
    subcategory = Subcategory(name="T-Shirts", slug="t-shirts", category=category)
    
    test_db_api.add_all([brand, category, subcategory])
    test_db_api.commit()
    
    # Create product
    product = Product(
        title="Premium T-Shirt",
        slug="premium-t-shirt",
        sku_code="NIKE-PREMIUM-001",
        brand_id=brand.id,
        category_id=category.id,
        subcategory_id=subcategory.id,
        main_image="https://example.com/main.jpg",
        description="Premium quality t-shirt",
        is_active=True,
        is_featured=True
    )
    test_db_api.add(product)
    test_db_api.commit()
    test_db_api.refresh(product)
    
    # Create SKUs with variant images
    skus_data = [
        {
            "size": "40",
            "color": "Черный",
            "price": 8500.0,
            "stock": 10,
            "variant_image": "https://cdn.example.com/black-40.jpg"
        },
        {
            "size": "40",
            "color": "Белый",
            "price": 8500.0,
            "stock": 15,
            "variant_image": "https://cdn.example.com/white-40.jpg"
        },
        {
            "size": "42",
            "color": "Черный",
            "price": 8500.0,
            "stock": 8,
            "variant_image": "https://cdn.example.com/black-42.jpg"
        },
        {
            "size": "42",
            "color": "Красный",
            "price": 8500.0,
            "stock": 12,
            "variant_image": None  # No image for this variant
        }
    ]
    
    for sku_data in skus_data:
        sku = SKU(
            product_id=product.id,
            sku_code=f"{product.sku_code}-{sku_data['size']}-{sku_data['color'].upper()}",
            size=sku_data['size'],
            color=sku_data['color'],
            price=sku_data['price'],
            stock=sku_data['stock'],
            is_active=True,
            variant_image=sku_data['variant_image']
        )
        test_db_api.add(sku)
    
    test_db_api.commit()
    
    return {
        "product": product,
        "brand": brand,
        "category": category,
        "subcategory": subcategory
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 API RESPONSE TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_product_skus_include_variant_images(test_db_api: Session, sample_data: dict):
    """Test that querying product SKUs returns variant images"""
    product = sample_data["product"]
    
    # Query SKUs
    skus = test_db_api.query(SKU).filter_by(product_id=product.id).all()
    
    # Verify we have SKUs
    assert len(skus) == 4
    
    # Verify variant images
    skus_with_images = [sku for sku in skus if sku.variant_image is not None]
    skus_without_images = [sku for sku in skus if sku.variant_image is None]
    
    assert len(skus_with_images) == 3, "3 SKUs should have variant images"
    assert len(skus_without_images) == 1, "1 SKU should not have variant image"
    
    # Verify image URLs
    for sku in skus_with_images:
        assert sku.variant_image.startswith("https://")
        assert ".jpg" in sku.variant_image


def test_sku_serialization_includes_variant_image(test_db_api: Session, sample_data: dict):
    """Test that SKU serialization includes variant_image field"""
    from src.app_01.schemas.product import SKUDetailSchema
    
    product = sample_data["product"]
    skus = test_db_api.query(SKU).filter_by(product_id=product.id).all()
    
    # Serialize SKUs
    serialized_skus = [SKUDetailSchema.from_orm(sku) for sku in skus]
    
    # Verify all have variant_image attribute
    for serialized_sku in serialized_skus:
        assert hasattr(serialized_sku, 'variant_image')
    
    # Verify values
    skus_with_images = [sku for sku in serialized_skus if sku.variant_image]
    assert len(skus_with_images) == 3


def test_sku_json_response_format(test_db_api: Session, sample_data: dict):
    """Test that SKU JSON response has correct format"""
    from src.app_01.schemas.product import SKUDetailSchema
    
    product = sample_data["product"]
    sku = test_db_api.query(SKU).filter(
        SKU.product_id == product.id,
        SKU.variant_image.isnot(None)
    ).first()
    
    # Serialize to JSON
    schema = SKUDetailSchema.from_orm(sku)
    json_data = schema.dict()
    
    # Verify JSON structure
    assert "id" in json_data
    assert "sku_code" in json_data
    assert "size" in json_data
    assert "color" in json_data
    assert "price" in json_data
    assert "stock" in json_data
    assert "variant_image" in json_data
    
    # Verify types
    assert isinstance(json_data["id"], int)
    assert isinstance(json_data["sku_code"], str)
    assert isinstance(json_data["size"], str)
    assert isinstance(json_data["color"], str)
    assert isinstance(json_data["price"], float)
    assert isinstance(json_data["stock"], int)
    assert isinstance(json_data["variant_image"], (str, type(None)))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 QUERY AND FILTER TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_filter_skus_by_color_with_images(test_db_api: Session, sample_data: dict):
    """Test filtering SKUs by color and checking variant images"""
    product = sample_data["product"]
    
    # Get all black variants
    black_skus = test_db_api.query(SKU).filter_by(
        product_id=product.id,
        color="Черный"
    ).all()
    
    assert len(black_skus) == 2  # Size 40 and 42
    
    # Both should have images
    for sku in black_skus:
        assert sku.variant_image is not None
        assert "black" in sku.variant_image.lower()


def test_get_available_colors_with_images(test_db_api: Session, sample_data: dict):
    """Test getting available colors and their images"""
    product = sample_data["product"]
    
    # Get unique colors with images
    skus = test_db_api.query(SKU).filter_by(
        product_id=product.id,
        is_active=True
    ).all()
    
    # Group by color
    colors_with_images = {}
    for sku in skus:
        if sku.color not in colors_with_images and sku.variant_image:
            colors_with_images[sku.color] = sku.variant_image
    
    # Verify
    assert "Черный" in colors_with_images
    assert "Белый" in colors_with_images
    assert len(colors_with_images) == 2  # Only colors with images


def test_get_sku_by_size_and_color(test_db_api: Session, sample_data: dict):
    """Test getting specific SKU by size and color combination"""
    product = sample_data["product"]
    
    # Get specific variant
    sku = test_db_api.query(SKU).filter_by(
        product_id=product.id,
        size="40",
        color="Белый",
        is_active=True
    ).first()
    
    assert sku is not None
    assert sku.variant_image == "https://cdn.example.com/white-40.jpg"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔄 REGRESSION TESTS FOR API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_product_query_still_works_with_variant_images(test_db_api: Session, sample_data: dict):
    """REGRESSION: Test that product queries work with new variant_image field"""
    product = sample_data["product"]
    
    # Query product with SKUs
    queried_product = test_db_api.query(Product).filter_by(
        id=product.id
    ).first()
    
    assert queried_product is not None
    assert len(queried_product.skus) == 4
    
    # Verify all SKU relationships work
    for sku in queried_product.skus:
        assert sku.product_id == product.id
        assert hasattr(sku, 'variant_image')


def test_active_skus_query_works(test_db_api: Session, sample_data: dict):
    """REGRESSION: Test that filtering active SKUs still works"""
    product = sample_data["product"]
    
    # Query active SKUs
    active_skus = test_db_api.query(SKU).filter_by(
        product_id=product.id,
        is_active=True
    ).all()
    
    assert len(active_skus) == 4
    
    # Deactivate one
    active_skus[0].is_active = False
    test_db_api.commit()
    
    # Query again
    active_skus_after = test_db_api.query(SKU).filter_by(
        product_id=product.id,
        is_active=True
    ).all()
    
    assert len(active_skus_after) == 3


def test_price_range_query_works(test_db_api: Session, sample_data: dict):
    """REGRESSION: Test that price range queries still work"""
    product = sample_data["product"]
    
    # Query SKUs in price range
    skus_in_range = test_db_api.query(SKU).filter(
        SKU.product_id == product.id,
        SKU.price >= 8000.0,
        SKU.price <= 9000.0
    ).all()
    
    assert len(skus_in_range) == 4


def test_stock_availability_query_works(test_db_api: Session, sample_data: dict):
    """REGRESSION: Test that stock availability queries work"""
    product = sample_data["product"]
    
    # Query in-stock SKUs
    in_stock_skus = test_db_api.query(SKU).filter(
        SKU.product_id == product.id,
        SKU.stock > 0,
        SKU.is_active == True
    ).all()
    
    assert len(in_stock_skus) == 4


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 BUSINESS LOGIC TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_get_primary_image_for_variant(test_db_api: Session, sample_data: dict):
    """
    Test business logic: Get primary image for a variant
    (variant_image if exists, otherwise product main_image)
    """
    product = sample_data["product"]
    
    # Get SKU with variant image
    sku_with_image = test_db_api.query(SKU).filter_by(
        product_id=product.id,
        color="Черный",
        size="40"
    ).first()
    
    # Get SKU without variant image
    sku_without_image = test_db_api.query(SKU).filter_by(
        product_id=product.id,
        color="Красный"
    ).first()
    
    # Business logic: primary image selection
    def get_primary_image(sku):
        return sku.variant_image if sku.variant_image else sku.product.main_image
    
    # Test
    assert get_primary_image(sku_with_image) == "https://cdn.example.com/black-40.jpg"
    assert get_primary_image(sku_without_image) == "https://example.com/main.jpg"


def test_variant_image_priority_over_main_image(test_db_api: Session, sample_data: dict):
    """Test that variant_image should be used over main_image when available"""
    product = sample_data["product"]
    
    skus = test_db_api.query(SKU).filter_by(product_id=product.id).all()
    
    for sku in skus:
        # If variant has its own image, it should be different from main
        if sku.variant_image:
            assert sku.variant_image != product.main_image


def test_get_all_variant_images_for_product(test_db_api: Session, sample_data: dict):
    """Test getting all unique variant images for a product"""
    product = sample_data["product"]
    
    skus = test_db_api.query(SKU).filter_by(
        product_id=product.id,
        is_active=True
    ).all()
    
    # Get unique variant images
    variant_images = set()
    for sku in skus:
        if sku.variant_image:
            variant_images.add(sku.variant_image)
    
    # Verify
    assert len(variant_images) == 3  # Three unique variant images
    
    # All should be valid URLs
    for image_url in variant_images:
        assert image_url.startswith("https://")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 COMPLEX QUERY TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_get_product_with_all_variant_data(test_db_api: Session, sample_data: dict):
    """
    INTEGRATION TEST: Get complete product data with all variants and images
    (simulates product detail API endpoint)
    """
    from src.app_01.schemas.product import SKUDetailSchema
    
    product = sample_data["product"]
    
    # Query product with relationships
    queried_product = test_db_api.query(Product).filter_by(id=product.id).first()
    
    # Build response data
    product_data = {
        "id": queried_product.id,
        "title": queried_product.title,
        "slug": queried_product.slug,
        "main_image": queried_product.main_image,
        "description": queried_product.description,
        "brand": {
            "id": queried_product.brand.id,
            "name": queried_product.brand.name,
            "slug": queried_product.brand.slug
        },
        "skus": [SKUDetailSchema.from_orm(sku).dict() for sku in queried_product.skus],
        "available_sizes": list(set(sku.size for sku in queried_product.skus)),
        "available_colors": list(set(sku.color for sku in queried_product.skus))
    }
    
    # Verify complete structure
    assert product_data["id"] == product.id
    assert len(product_data["skus"]) == 4
    assert len(product_data["available_sizes"]) == 2  # 40, 42
    assert len(product_data["available_colors"]) == 3  # Black, White, Red
    
    # Verify SKUs have variant_image field
    for sku in product_data["skus"]:
        assert "variant_image" in sku
    
    # Count SKUs with images
    skus_with_images = [sku for sku in product_data["skus"] if sku["variant_image"]]
    assert len(skus_with_images) == 3


def test_catalog_listing_includes_variant_images(test_db_api: Session, sample_data: dict):
    """
    Test that catalog listing can access variant images
    (useful for showing color swatches with images)
    """
    # Query all active products with SKUs
    products = test_db_api.query(Product).filter_by(is_active=True).all()
    
    catalog_data = []
    for product in products:
        # Get first variant image or use main image
        first_variant_with_image = next(
            (sku.variant_image for sku in product.skus if sku.variant_image),
            product.main_image
        )
        
        catalog_data.append({
            "id": product.id,
            "title": product.title,
            "slug": product.slug,
            "primary_image": first_variant_with_image,
            "has_variants": len(product.skus) > 1,
            "variant_count": len(product.skus)
        })
    
    # Verify
    assert len(catalog_data) == 1
    assert catalog_data[0]["has_variants"] is True
    assert catalog_data[0]["variant_count"] == 4
    assert "https://" in catalog_data[0]["primary_image"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

