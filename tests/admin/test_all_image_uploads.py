"""
Comprehensive tests for ALL image upload functionality across the admin panel.
Tests Category, Brand, Banner, and Product image uploads.
"""
import pytest
import io
import os
import shutil
from PIL import Image as PILImage
from sqlalchemy.orm import Session

from src.app_01.models import Category, Subcategory, Brand
from src.app_01.models.banners.banner import Banner, BannerType
from src.app_01.models.products.product import Product
from src.app_01.utils.image_upload import image_uploader
from fastapi import UploadFile
import asyncio


# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def cleanup_uploads():
    """Fixture to clean up ALL uploads directories before and after tests."""
    upload_dirs = [
        "static/uploads/category",
        "static/uploads/subcategory",
        "static/uploads/brand",
        "static/uploads/banner",
        "static/uploads/product"
    ]
    
    # Clean up before tests
    for upload_dir in upload_dirs:
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
        os.makedirs(upload_dir, exist_ok=True)
    
    yield
    
    # Clean up after tests
    for upload_dir in upload_dirs:
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)


def create_test_image(filename="test.jpg", size=(100, 100), color="red"):
    """Helper to create a test image file."""
    img = PILImage.new('RGB', size, color=color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return UploadFile(filename=filename, file=img_bytes)


# ===== CATEGORY IMAGE TESTS =====

def test_category_image_upload(db_session: Session):
    """Test that Category image upload works correctly."""
    # Create a category with an image
    upload_file = create_test_image("category_test.jpg")
    
    # Upload image
    image_url = asyncio.run(image_uploader.save_image(upload_file, category="category"))
    
    # Create category with the image
    category = Category(
        name="Test Category",
        slug="test-category",
        image_url=image_url
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Assert
    assert category.id is not None
    assert category.image_url is not None
    assert "category" in category.image_url
    assert os.path.exists(f"static{category.image_url}")
    print(f"✅ Category image test passed! Image URL: {category.image_url}")


# ===== SUBCATEGORY IMAGE TESTS =====

def test_subcategory_image_upload(db_session: Session):
    """Test that Subcategory image upload works correctly."""
    # Create parent category
    parent_category = Category(name="Parent Category", slug="parent-category")
    db_session.add(parent_category)
    db_session.commit()
    
    # Upload image
    upload_file = create_test_image("subcategory_test.jpg")
    image_url = asyncio.run(image_uploader.save_image(upload_file, category="subcategory"))
    
    # Create subcategory with the image
    subcategory = Subcategory(
        name="Test Subcategory",
        slug="test-subcategory",
        category=parent_category,
        image_url=image_url
    )
    db_session.add(subcategory)
    db_session.commit()
    db_session.refresh(subcategory)
    
    # Assert
    assert subcategory.id is not None
    assert subcategory.image_url is not None
    assert "subcategory" in subcategory.image_url
    assert os.path.exists(f"static{subcategory.image_url}")
    print(f"✅ Subcategory image test passed! Image URL: {subcategory.image_url}")


# ===== BRAND LOGO TESTS =====

def test_brand_logo_upload(db_session: Session):
    """Test that Brand logo upload works correctly."""
    # Upload logo
    upload_file = create_test_image("brand_logo.jpg")
    logo_url = asyncio.run(image_uploader.save_image(upload_file, category="brand"))
    
    # Create brand with the logo
    brand = Brand(
        name="Test Brand",
        slug="test-brand",
        logo_url=logo_url
    )
    db_session.add(brand)
    db_session.commit()
    db_session.refresh(brand)
    
    # Assert
    assert brand.id is not None
    assert brand.logo_url is not None
    assert "brand" in brand.logo_url
    assert os.path.exists(f"static{brand.logo_url}")
    print(f"✅ Brand logo test passed! Logo URL: {brand.logo_url}")


# ===== BANNER IMAGE TESTS =====

def test_banner_image_upload(db_session: Session):
    """Test that Banner image uploads work correctly (desktop + mobile)."""
    # Upload desktop image
    desktop_file = create_test_image("banner_desktop.jpg", size=(1200, 400))
    desktop_url = asyncio.run(image_uploader.save_image(desktop_file, category="banner"))
    
    # Upload mobile image
    mobile_file = create_test_image("banner_mobile.jpg", size=(800, 600))
    mobile_url = asyncio.run(image_uploader.save_image(mobile_file, category="banner"))
    
    # Create banner with both images
    banner = Banner(
        title="Test Banner",
        banner_type=BannerType.HERO,
        image_url=desktop_url,
        mobile_image_url=mobile_url,
        is_active=True
    )
    db_session.add(banner)
    db_session.commit()
    db_session.refresh(banner)
    
    # Assert
    assert banner.id is not None
    assert banner.image_url is not None
    assert banner.mobile_image_url is not None
    assert "banner" in banner.image_url
    assert "banner" in banner.mobile_image_url
    assert os.path.exists(f"static{banner.image_url}")
    assert os.path.exists(f"static{banner.mobile_image_url}")
    print(f"✅ Banner image test passed! Desktop: {banner.image_url}, Mobile: {banner.mobile_image_url}")


# ===== PRODUCT IMAGE TESTS =====

def test_product_image_upload(db_session: Session):
    """Test that Product image uploads work correctly (main + additional)."""
    # Create required parent models
    category = Category(name="Product Test Category", slug="product-test-cat")
    db_session.add(category)
    db_session.commit()
    
    subcategory = Subcategory(name="Product Test Subcat", slug="product-test-subcat", category=category)
    db_session.add(subcategory)
    db_session.commit()
    
    brand = Brand(name="Product Test Brand", slug="product-test-brand")
    db_session.add(brand)
    db_session.commit()
    
    # Upload main image
    main_file = create_test_image("product_main.jpg")
    main_url = asyncio.run(image_uploader.save_image(main_file, category="product"))
    
    # Upload additional images
    additional_urls = []
    for i in range(3):
        additional_file = create_test_image(f"product_additional_{i}.jpg")
        additional_url = asyncio.run(image_uploader.save_image(additional_file, category="product"))
        additional_urls.append(additional_url)
    
    # Create product with images
    product = Product(
        brand_id=brand.id,
        category_id=category.id,
        subcategory_id=subcategory.id,
        title="Test Product",
        slug="test-product",
        description="Test product description",
        main_image=main_url,
        additional_images=additional_urls
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Assert
    assert product.id is not None
    assert product.main_image is not None
    assert product.additional_images is not None
    assert len(product.additional_images) == 3
    assert "product" in product.main_image
    assert os.path.exists(f"static{product.main_image}")
    
    for additional_url in product.additional_images:
        assert "product" in additional_url
        assert os.path.exists(f"static{additional_url}")
    
    print(f"✅ Product image test passed! Main: {product.main_image}, Additional: {len(product.additional_images)} images")


# ===== IMAGE VALIDATION TESTS =====

def test_image_validation_rejects_invalid_format():
    """Test that invalid image formats are rejected."""
    # Create a fake "image" that's actually text
    fake_image = io.BytesIO(b"This is not an image file")
    upload_file = UploadFile(filename="fake.jpg", file=fake_image)
    
    # This should fail during Pillow validation
    with pytest.raises(Exception):
        asyncio.run(image_uploader.save_image(upload_file, category="test"))
    
    print("✅ Image validation test passed! Invalid formats are rejected")


def test_image_resize_works():
    """Test that image resizing works correctly."""
    # Create a large image
    large_image = create_test_image("large.jpg", size=(2000, 2000))
    
    # Upload with medium resize
    image_url = asyncio.run(image_uploader.save_image(large_image, category="test", resize_to="medium"))
    
    # Check that file was resized
    saved_image = PILImage.open(f"static{image_url}")
    assert saved_image.size[0] <= 500  # Medium size is 500x500
    assert saved_image.size[1] <= 500
    
    print(f"✅ Image resize test passed! Original: (2000, 2000), Resized: {saved_image.size}")


# ===== INTEGRATION TEST =====

def test_complete_catalog_with_images(db_session: Session):
    """Integration test: Create a complete catalog with all images."""
    # 1. Create Category with image
    cat_file = create_test_image("cat.jpg")
    cat_url = asyncio.run(image_uploader.save_image(cat_file, category="category"))
    category = Category(name="Clothing", slug="clothing", image_url=cat_url)
    db_session.add(category)
    db_session.commit()
    
    # 2. Create Subcategory with image
    subcat_file = create_test_image("subcat.jpg")
    subcat_url = asyncio.run(image_uploader.save_image(subcat_file, category="subcategory"))
    subcategory = Subcategory(name="T-Shirts", slug="t-shirts", category=category, image_url=subcat_url)
    db_session.add(subcategory)
    db_session.commit()
    
    # 3. Create Brand with logo
    brand_file = create_test_image("brand.jpg")
    brand_url = asyncio.run(image_uploader.save_image(brand_file, category="brand"))
    brand = Brand(name="Nike", slug="nike", logo_url=brand_url)
    db_session.add(brand)
    db_session.commit()
    
    # 4. Create Product with images
    main_file = create_test_image("product.jpg")
    main_url = asyncio.run(image_uploader.save_image(main_file, category="product"))
    product = Product(
        brand_id=brand.id,
        category_id=category.id,
        subcategory_id=subcategory.id,
        title="Nike T-Shirt",
        slug="nike-tshirt",
        main_image=main_url
    )
    db_session.add(product)
    db_session.commit()
    
    # 5. Assert everything is linked correctly
    db_session.refresh(category)
    db_session.refresh(subcategory)
    db_session.refresh(brand)
    db_session.refresh(product)
    
    assert category.image_url is not None
    assert subcategory.image_url is not None
    assert brand.logo_url is not None
    assert product.main_image is not None
    
    print(f"✅ Complete catalog integration test passed!")
    print(f"   Category: {category.name} ({category.image_url})")
    print(f"   Subcategory: {subcategory.name} ({subcategory.image_url})")
    print(f"   Brand: {brand.name} ({brand.logo_url})")
    print(f"   Product: {product.title} ({product.main_image})")

