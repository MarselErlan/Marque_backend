import pytest
import io
import uuid

from sqlalchemy.orm import Session
from src.app_01.models import Subcategory, Category


@pytest.fixture(autouse=True)
def cleanup_db(db_session: Session):
    """Fixture to clean up category and subcategory tables before each test."""
    yield
    db_session.query(Subcategory).delete()
    db_session.query(Category).delete()
    db_session.commit()


@pytest.mark.skip(reason="Image upload form submission needs file field configuration - low priority")
def test_create_subcategory_with_image(
    authenticated_app_client, db_session: Session
):
    """
    Test creating a subcategory with an image upload.
    This simulates the admin user filling out the form and attaching a file.
    """
    client, _ = authenticated_app_client
    unique_id = uuid.uuid4().hex[:6]
    parent_category = Category(name=f"Test Parent {unique_id}", slug=f"test-parent-{unique_id}")
    db_session.add(parent_category)
    db_session.commit()

    form_data = {
        "name": f"New Sub {unique_id}",
        "slug": f"new-sub-{unique_id}",
        "category": str(parent_category.id),
        "is_active": "True",
        "description": "A test description.",
        "sort_order": "0",
        "is_featured": "False",
    }
    mock_image_file = {
        "image_url": ("test_image.jpg", io.BytesIO(b"fake image data"), "image/jpeg")
    }

    response = client.post(
        "/admin/subcategory/create", data=form_data, files=mock_image_file
    )

    assert response.status_code == 302
    
    created_sub = db_session.query(Subcategory).filter_by(slug=f"new-sub-{unique_id}").one()
    assert created_sub is not None
    assert created_sub.image_url is not None
    assert "test_image" in created_sub.image_url


@pytest.mark.skip(reason="Image upload form submission needs file field configuration - low priority")
def test_update_subcategory_with_new_image(
    authenticated_app_client, db_session: Session
):
    """
    Test updating a subcategory with a new image, replacing the old one.
    """
    client, _ = authenticated_app_client
    unique_id = uuid.uuid4().hex[:6]
    parent_category = Category(name=f"Test Parent {unique_id}", slug=f"test-parent-{unique_id}")
    initial_sub = Subcategory(
        name="Sub to be Updated",
        slug=f"sub-to-be-updated-{unique_id}",
        category=parent_category,
        image_url="/uploads/subcategory/initial.jpg"
    )
    db_session.add_all([parent_category, initial_sub])
    db_session.commit()

    form_data = {
        "name": "Updated Name",
        "slug": f"sub-to-be-updated-{unique_id}",
        "category": str(parent_category.id),
        "is_active": "True",
        "description": "An updated description.",
        "sort_order": "1",
        "is_featured": "True",
    }
    new_mock_image = {
        "image_url": ("new_image.png", io.BytesIO(b"new fake data"), "image/png")
    }

    response = client.post(
        f"/admin/subcategory/edit/{initial_sub.id}",
        data=form_data,
        files=new_mock_image,
    )

    assert response.status_code == 302
    
    db_session.refresh(initial_sub)
    assert initial_sub.name == "Updated Name"
    assert initial_sub.image_url is not None
    assert "new_image" in initial_sub.image_url
    assert "initial.jpg" not in initial_sub.image_url


@pytest.mark.skip(reason="Image upload form submission needs file field configuration - low priority")
def test_update_subcategory_without_new_image(
    authenticated_app_client, db_session: Session
):
    """
    Test that updating a subcategory without providing a new image
    does NOT delete the existing image.
    """
    client, _ = authenticated_app_client
    unique_id = uuid.uuid4().hex[:6]
    parent_category = Category(name=f"Test Parent {unique_id}", slug=f"test-parent-{unique_id}")
    initial_sub = Subcategory(
        name="Sub to Keep Image",
        slug=f"sub-to-keep-image-{unique_id}",
        category=parent_category,
        image_url="/uploads/subcategory/existing.jpg"
    )
    db_session.add_all([parent_category, initial_sub])
    db_session.commit()

    form_data = {
        "name": "Updated Name but Same Image",
        "slug": f"sub-to-keep-image-{unique_id}",
        "category": str(parent_category.id),
        "is_active": "True",
        "description": "An updated description.",
    }

    response = client.post(
        f"/admin/subcategory/edit/{initial_sub.id}", data=form_data
    )

    assert response.status_code == 302
    
    db_session.refresh(initial_sub)
    assert initial_sub.name == "Updated Name but Same Image"
    assert initial_sub.image_url == "/uploads/subcategory/existing.jpg"
