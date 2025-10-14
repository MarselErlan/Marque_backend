"""
Unit tests for Subcategory image upload logic.
Tests the image upload functionality directly without going through the admin interface.
"""
import pytest
import io
from PIL import Image as PILImage
from sqlalchemy.orm import Session

from src.app_01.models import Subcategory, Category
from src.app_01.utils.image_upload import image_uploader
from fastapi import UploadFile


def test_subcategory_image_upload_saves_to_model(db_session: Session):
    """
    Test that when we save an image using the image_uploader utility,
    it works correctly and we can store the URL in the Subcategory model.
    """
    # 1. Create parent category
    parent_category = Category(name="Test Category", slug="test-category")
    db_session.add(parent_category)
    db_session.commit()
    
    # 2. Create a fake image file
    img = PILImage.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # 3. Create an UploadFile object
    upload_file = UploadFile(filename="test_image.jpg", file=img_bytes)
    
    # 4. Upload the image using the utility (this is what the admin panel should do)
    image_url = None
    try:
        # Use asyncio to run the async function
        import asyncio
        image_url = asyncio.run(image_uploader.save_image(upload_file, category="subcategory"))
    except Exception as e:
        pytest.fail(f"Image upload failed: {e}")
    
    # 5. Assert we got a URL back
    assert image_url is not None, "Image URL should not be None"
    assert "subcategory" in image_url, f"Image URL should contain 'subcategory', got: {image_url}"
    
    # 6. Create a subcategory with the uploaded image
    subcategory = Subcategory(
        name="Test Subcategory",
        slug="test-subcategory",
        category=parent_category,
        image_url=image_url
    )
    db_session.add(subcategory)
    db_session.commit()
    db_session.refresh(subcategory)
    
    # 7. Verify the subcategory was saved with the image URL
    assert subcategory.id is not None
    assert subcategory.image_url == image_url
    print(f"✅ Test passed! Subcategory created with image URL: {image_url}")


def test_subcategory_update_preserves_image_if_not_changed(db_session: Session):
    """
    Test that when we update a subcategory without changing the image,
    the original image URL is preserved.
    """
    # 1. Create parent category
    parent_category = Category(name="Test Category 2", slug="test-category-2")
    db_session.add(parent_category)
    db_session.commit()
    
    # 2. Create a subcategory with an existing image
    original_image_url = "/uploads/subcategory/existing_image.jpg"
    subcategory = Subcategory(
        name="Test Subcategory",
        slug="test-subcategory-2",
        category=parent_category,
        image_url=original_image_url
    )
    db_session.add(subcategory)
    db_session.commit()
    db_session.refresh(subcategory)
    
    # 3. Update the subcategory name (but not the image)
    subcategory.name = "Updated Name"
    db_session.commit()
    db_session.refresh(subcategory)
    
    # 4. Verify the image URL is still the same
    assert subcategory.image_url == original_image_url
    print(f"✅ Test passed! Image URL preserved after update: {original_image_url}")

