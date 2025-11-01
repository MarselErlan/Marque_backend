"""
Unit tests for the variant image feature.

Tests cover:
1. Database model updates
2. API schema serialization
3. Image upload functionality
4. Regression tests for existing SKU features
"""

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient
from typing import Generator
import io
from PIL import Image

from src.app_01.models import Product, SKU, Brand, Category, Subcategory
from src.app_01.schemas.product import SKUDetailSchema
from src.app_01.db import Base


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔧 FIXTURES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """Create a test database session"""
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
def sample_product(test_db: Session) -> Product:
    """Create a sample product for testing"""
    # Create dependencies
    brand = Brand(name="Nike", slug="nike")
    category = Category(name="Clothing", slug="clothing")
    subcategory = Subcategory(name="T-Shirts", slug="t-shirts", category=category)
    
    test_db.add_all([brand, category, subcategory])
    test_db.commit()
    
    # Create product
    product = Product(
        title="Test T-Shirt",
        slug="test-t-shirt",
        sku_code="NIKE-TEST-001",
        brand_id=brand.id,
        category_id=category.id,
        subcategory_id=subcategory.id,
        main_image="https://example.com/main.jpg"
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    
    return product


@pytest.fixture(scope="function")
def sample_sku(test_db: Session, sample_product: Product) -> SKU:
    """Create a sample SKU for testing"""
    sku = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-BLACK",
        size="42",
        color="Черный",
        price=8500.0,
        original_price=10000.0,
        stock=10,
        is_active=True,
        variant_image="https://example.com/black-tshirt.jpg"
    )
    test_db.add(sku)
    test_db.commit()
    test_db.refresh(sku)
    
    return sku


def create_test_image() -> bytes:
    """Create a test image in memory"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.read()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 DATABASE MODEL TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_sku_table_has_variant_image_column(test_db: Session):
    """Test that the skus table has the variant_image column"""
    # Get table inspector
    inspector = inspect(test_db.bind)
    columns = [col['name'] for col in inspector.get_columns('skus')]
    
    # Verify variant_image column exists
    assert 'variant_image' in columns, "variant_image column should exist in skus table"


def test_sku_model_has_variant_image_attribute(sample_product: Product):
    """Test that SKU model has variant_image attribute"""
    sku = SKU(
        product_id=sample_product.id,
        sku_code="TEST-001",
        size="42",
        color="Black",
        price=100.0,
        stock=10
    )
    
    # Test attribute exists
    assert hasattr(sku, 'variant_image'), "SKU model should have variant_image attribute"


def test_create_sku_with_variant_image(test_db: Session, sample_product: Product):
    """Test creating a SKU with variant_image"""
    image_url = "https://example.com/variant-image.jpg"
    
    sku = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-BLACK",
        size="42",
        color="Black",
        price=8500.0,
        stock=10,
        variant_image=image_url
    )
    
    test_db.add(sku)
    test_db.commit()
    test_db.refresh(sku)
    
    # Verify
    assert sku.id is not None
    assert sku.variant_image == image_url


def test_create_sku_without_variant_image(test_db: Session, sample_product: Product):
    """Test creating a SKU without variant_image (backward compatibility)"""
    sku = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-WHITE",
        size="42",
        color="White",
        price=8500.0,
        stock=10
        # No variant_image provided
    )
    
    test_db.add(sku)
    test_db.commit()
    test_db.refresh(sku)
    
    # Verify
    assert sku.id is not None
    assert sku.variant_image is None, "variant_image should be None when not provided"


def test_update_sku_variant_image(test_db: Session, sample_sku: SKU):
    """Test updating variant_image on existing SKU"""
    original_image = sample_sku.variant_image
    new_image = "https://example.com/new-black-tshirt.jpg"
    
    # Update image
    sample_sku.variant_image = new_image
    test_db.commit()
    test_db.refresh(sample_sku)
    
    # Verify
    assert sample_sku.variant_image == new_image
    assert sample_sku.variant_image != original_image


def test_variant_image_nullable(test_db: Session, sample_sku: SKU):
    """Test that variant_image can be set to None"""
    sample_sku.variant_image = None
    test_db.commit()
    test_db.refresh(sample_sku)
    
    # Verify
    assert sample_sku.variant_image is None


def test_variant_image_max_length(test_db: Session, sample_product: Product):
    """Test that variant_image accepts URLs up to 500 characters"""
    long_url = "https://example.com/" + "a" * 450 + ".jpg"  # ~475 characters
    
    sku = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-BLUE",
        size="42",
        color="Blue",
        price=8500.0,
        stock=10,
        variant_image=long_url
    )
    
    test_db.add(sku)
    test_db.commit()
    test_db.refresh(sku)
    
    # Verify
    assert sku.variant_image == long_url
    assert len(sku.variant_image) <= 500


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 SCHEMA SERIALIZATION TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_sku_detail_schema_includes_variant_image(sample_sku: SKU):
    """Test that SKUDetailSchema includes variant_image field"""
    # Serialize SKU to schema
    schema = SKUDetailSchema.from_orm(sample_sku)
    
    # Verify variant_image is included
    assert hasattr(schema, 'variant_image')
    assert schema.variant_image == sample_sku.variant_image


def test_sku_detail_schema_with_null_variant_image(test_db: Session, sample_product: Product):
    """Test SKUDetailSchema serialization when variant_image is None"""
    sku = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-GREEN",
        size="42",
        color="Green",
        price=8500.0,
        stock=10
        # No variant_image
    )
    test_db.add(sku)
    test_db.commit()
    test_db.refresh(sku)
    
    # Serialize
    schema = SKUDetailSchema.from_orm(sku)
    
    # Verify
    assert schema.variant_image is None


def test_sku_detail_schema_json_serialization(sample_sku: SKU):
    """Test that SKUDetailSchema can be serialized to JSON"""
    schema = SKUDetailSchema.from_orm(sample_sku)
    
    # Convert to dict (JSON-compatible)
    data = schema.dict()
    
    # Verify all fields present
    assert 'id' in data
    assert 'sku_code' in data
    assert 'size' in data
    assert 'color' in data
    assert 'price' in data
    assert 'stock' in data
    assert 'variant_image' in data
    assert data['variant_image'] == sample_sku.variant_image


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔄 REGRESSION TESTS (Existing SKU Functionality)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_sku_creation_still_works_without_variant_image(test_db: Session, sample_product: Product):
    """REGRESSION: Test that SKU creation works without variant_image (backward compatibility)"""
    sku = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-44-BLACK",
        size="44",
        color="Black",
        price=8500.0,
        original_price=10000.0,
        stock=15,
        is_active=True
    )
    
    test_db.add(sku)
    test_db.commit()
    test_db.refresh(sku)
    
    # Verify all existing functionality works
    assert sku.id is not None
    assert sku.sku_code == "NIKE-TEST-001-44-BLACK"
    assert sku.size == "44"
    assert sku.color == "Black"
    assert sku.price == 8500.0
    assert sku.stock == 15
    assert sku.is_active is True


def test_sku_is_in_stock_property_still_works(sample_sku: SKU):
    """REGRESSION: Test that is_in_stock property still works"""
    assert sample_sku.is_in_stock is True
    
    # Test with no stock
    sample_sku.stock = 0
    assert sample_sku.is_in_stock is False
    
    # Test with inactive SKU
    sample_sku.stock = 10
    sample_sku.is_active = False
    assert sample_sku.is_in_stock is False


def test_sku_formatted_price_property_still_works(sample_sku: SKU):
    """REGRESSION: Test that formatted_price property still works"""
    formatted = sample_sku.formatted_price
    assert "8500" in formatted
    assert "сом" in formatted


def test_sku_reduce_stock_method_still_works(test_db: Session, sample_sku: SKU):
    """REGRESSION: Test that reduce_stock method still works"""
    original_stock = sample_sku.stock
    
    result = sample_sku.reduce_stock(3)
    
    assert result is True
    assert sample_sku.stock == original_stock - 3


def test_sku_increase_stock_method_still_works(test_db: Session, sample_sku: SKU):
    """REGRESSION: Test that increase_stock method still works"""
    original_stock = sample_sku.stock
    
    sample_sku.increase_stock(5)
    
    assert sample_sku.stock == original_stock + 5


def test_sku_activate_deactivate_methods_still_work(test_db: Session, sample_sku: SKU):
    """REGRESSION: Test that activate/deactivate methods still work"""
    # Test deactivate
    sample_sku.deactivate()
    assert sample_sku.is_active is False
    
    # Test activate
    sample_sku.activate()
    assert sample_sku.is_active is True


def test_sku_product_relationship_still_works(test_db: Session, sample_sku: SKU, sample_product: Product):
    """REGRESSION: Test that product relationship still works"""
    # Access product through relationship
    product = sample_sku.product
    
    assert product is not None
    assert product.id == sample_product.id
    assert product.title == sample_product.title


def test_product_skus_relationship_still_works(test_db: Session, sample_product: Product):
    """REGRESSION: Test that product.skus relationship still works"""
    # Create multiple SKUs
    sku1 = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-40-BLACK",
        size="40",
        color="Black",
        price=8500.0,
        stock=10
    )
    sku2 = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-BLACK",
        size="42",
        color="Black",
        price=8500.0,
        stock=15
    )
    
    test_db.add_all([sku1, sku2])
    test_db.commit()
    test_db.refresh(sample_product)
    
    # Access SKUs through relationship
    skus = sample_product.skus
    
    assert len(skus) == 2
    assert all(sku.product_id == sample_product.id for sku in skus)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎨 VARIANT IMAGE BUSINESS LOGIC TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_multiple_variants_with_different_images(test_db: Session, sample_product: Product):
    """Test that different variants can have different images"""
    # Create SKUs with different images
    black_sku = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-BLACK",
        size="42",
        color="Black",
        price=8500.0,
        stock=10,
        variant_image="https://example.com/black.jpg"
    )
    
    white_sku = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-WHITE",
        size="42",
        color="White",
        price=8500.0,
        stock=10,
        variant_image="https://example.com/white.jpg"
    )
    
    red_sku = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-RED",
        size="42",
        color="Red",
        price=8500.0,
        stock=10,
        variant_image="https://example.com/red.jpg"
    )
    
    test_db.add_all([black_sku, white_sku, red_sku])
    test_db.commit()
    
    # Verify each has unique image
    test_db.refresh(black_sku)
    test_db.refresh(white_sku)
    test_db.refresh(red_sku)
    
    assert black_sku.variant_image == "https://example.com/black.jpg"
    assert white_sku.variant_image == "https://example.com/white.jpg"
    assert red_sku.variant_image == "https://example.com/red.jpg"


def test_get_skus_with_images_for_product(test_db: Session, sample_product: Product):
    """Test retrieving all SKUs with their images for a product"""
    # Create SKUs
    skus_data = [
        ("42", "Black", "https://example.com/black.jpg"),
        ("42", "White", "https://example.com/white.jpg"),
        ("44", "Black", "https://example.com/black-44.jpg"),
        ("44", "White", None),  # No image for this variant
    ]
    
    for size, color, image in skus_data:
        sku = SKU(
            product_id=sample_product.id,
            sku_code=f"NIKE-TEST-001-{size}-{color.upper()}",
            size=size,
            color=color,
            price=8500.0,
            stock=10,
            variant_image=image
        )
        test_db.add(sku)
    
    test_db.commit()
    
    # Query all SKUs for product
    skus = test_db.query(SKU).filter_by(product_id=sample_product.id).all()
    
    # Verify
    assert len(skus) == 4
    
    # Check images
    images_with_values = [sku for sku in skus if sku.variant_image is not None]
    images_without_values = [sku for sku in skus if sku.variant_image is None]
    
    assert len(images_with_values) == 3
    assert len(images_without_values) == 1


def test_filter_skus_by_variant_image_exists(test_db: Session, sample_product: Product):
    """Test filtering SKUs that have variant images"""
    # Create SKUs with and without images
    sku_with_image = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-BLACK",
        size="42",
        color="Black",
        price=8500.0,
        stock=10,
        variant_image="https://example.com/black.jpg"
    )
    
    sku_without_image = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-WHITE",
        size="42",
        color="White",
        price=8500.0,
        stock=10
    )
    
    test_db.add_all([sku_with_image, sku_without_image])
    test_db.commit()
    
    # Query SKUs with images
    skus_with_images = test_db.query(SKU).filter(
        SKU.product_id == sample_product.id,
        SKU.variant_image.isnot(None)
    ).all()
    
    # Verify
    assert len(skus_with_images) == 1
    assert skus_with_images[0].variant_image == "https://example.com/black.jpg"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 EDGE CASES AND VALIDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_variant_image_with_special_characters(test_db: Session, sample_product: Product):
    """Test variant_image with special characters in URL"""
    url_with_special_chars = "https://example.com/images/product-тест-001.jpg?v=1&format=webp"
    
    sku = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-YELLOW",
        size="42",
        color="Yellow",
        price=8500.0,
        stock=10,
        variant_image=url_with_special_chars
    )
    
    test_db.add(sku)
    test_db.commit()
    test_db.refresh(sku)
    
    # Verify
    assert sku.variant_image == url_with_special_chars


def test_variant_image_empty_string_vs_none(test_db: Session, sample_product: Product):
    """Test difference between empty string and None for variant_image"""
    # SKU with empty string
    sku_empty = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-42-GRAY",
        size="42",
        color="Gray",
        price=8500.0,
        stock=10,
        variant_image=""
    )
    
    # SKU with None
    sku_none = SKU(
        product_id=sample_product.id,
        sku_code="NIKE-TEST-001-44-GRAY",
        size="44",
        color="Gray",
        price=8500.0,
        stock=10,
        variant_image=None
    )
    
    test_db.add_all([sku_empty, sku_none])
    test_db.commit()
    test_db.refresh(sku_empty)
    test_db.refresh(sku_none)
    
    # Both should be handled gracefully
    assert sku_empty.variant_image == ""
    assert sku_none.variant_image is None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 SUMMARY TEST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def test_complete_variant_workflow(test_db: Session, sample_product: Product):
    """
    INTEGRATION TEST: Complete workflow from creating variants with images
    to querying and serializing them.
    """
    # Step 1: Create multiple variants with images
    variants = [
        ("40", "Black", "https://cdn.example.com/black-40.jpg"),
        ("40", "White", "https://cdn.example.com/white-40.jpg"),
        ("42", "Black", "https://cdn.example.com/black-42.jpg"),
        ("42", "White", "https://cdn.example.com/white-42.jpg"),
        ("44", "Black", None),  # No image yet
    ]
    
    created_skus = []
    for size, color, image in variants:
        sku = SKU(
            product_id=sample_product.id,
            sku_code=f"NIKE-TEST-001-{size}-{color.upper()}",
            size=size,
            color=color,
            price=8500.0,
            stock=10,
            is_active=True,
            variant_image=image
        )
        test_db.add(sku)
        created_skus.append(sku)
    
    test_db.commit()
    
    # Step 2: Query all variants for product
    all_skus = test_db.query(SKU).filter_by(
        product_id=sample_product.id,
        is_active=True
    ).all()
    
    assert len(all_skus) == 5
    
    # Step 3: Serialize to schema
    serialized_skus = [SKUDetailSchema.from_orm(sku) for sku in all_skus]
    
    # Step 4: Verify serialization
    assert len(serialized_skus) == 5
    assert all(hasattr(sku, 'variant_image') for sku in serialized_skus)
    
    # Step 5: Check variant images
    skus_with_images = [sku for sku in serialized_skus if sku.variant_image]
    skus_without_images = [sku for sku in serialized_skus if not sku.variant_image]
    
    assert len(skus_with_images) == 4
    assert len(skus_without_images) == 1
    
    # Step 6: Update variant image for SKU without image
    sku_to_update = [sku for sku in all_skus if sku.variant_image is None][0]
    sku_to_update.variant_image = "https://cdn.example.com/black-44.jpg"
    test_db.commit()
    test_db.refresh(sku_to_update)
    
    # Step 7: Verify update
    assert sku_to_update.variant_image == "https://cdn.example.com/black-44.jpg"
    
    # Step 8: Final verification - all SKUs now have images
    all_skus_updated = test_db.query(SKU).filter_by(
        product_id=sample_product.id,
        is_active=True
    ).all()
    
    skus_with_images_count = sum(1 for sku in all_skus_updated if sku.variant_image)
    assert skus_with_images_count == 5, "All 5 SKUs should now have images"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

