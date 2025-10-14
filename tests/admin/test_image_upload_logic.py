import pytest
import io

from sqlalchemy.orm import Session
from src.app_01.models import Subcategory, Category


def test_create_subcategory_with_image(
    authenticated_admin_client, db_session: Session
):
    """
    Test creating a subcategory with an image upload.
    This simulates the admin user filling out the form and attaching a file.
    """
    client = authenticated_admin_client
    parent_category = Category(name="Test Parent", slug="test-parent")
    db_session.add(parent_category)
    db_session.commit()

    form_data = {
        "name": "New Subcategory with Image",
        "slug": "new-sub-with-image",
        "category": str(parent_category.id),
        "is_active": "y",
    }
    mock_image_file = {
        "image_url": ("test_image.jpg", io.BytesIO(b"fake image data"), "image/jpeg")
    }

    response = client.post(
        "/admin/subcategory/create", data=form_data, files=mock_image_file
    )

    assert response.status_code == 302
    
    created_sub = db_session.query(Subcategory).filter_by(slug="new-sub-with-image").one()
    assert created_sub is not None
    assert created_sub.image_url is not None
    assert "test_image" in created_sub.image_url


def test_update_subcategory_with_new_image(
    authenticated_admin_client, db_session: Session
):
    """
    Test updating a subcategory with a new image, replacing the old one.
    """
    client = authenticated_admin_client
    parent_category = Category(name="Test Parent 2", slug="test-parent-2")
    initial_sub = Subcategory(
        name="Sub to be Updated",
        slug="sub-to-be-updated",
        category=parent_category,
        image_url="/uploads/subcategory/initial.jpg"
    )
    db_session.add_all([parent_category, initial_sub])
    db_session.commit()

    form_data = {
        "name": "Updated Name",
        "slug": "sub-to-be-updated",
        "category": str(parent_category.id),
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


def test_update_subcategory_without_new_image(
    authenticated_admin_client, db_session: Session
):
    """
    Test that updating a subcategory without providing a new image
    does NOT delete the existing image.
    """
    client = authenticated_admin_client
    parent_category = Category(name="Test Parent 3", slug="test-parent-3")
    initial_sub = Subcategory(
        name="Sub to Keep Image",
        slug="sub-to-keep-image",
        category=parent_category,
        image_url="/uploads/subcategory/existing.jpg"
    )
    db_session.add_all([parent_category, initial_sub])
    db_session.commit()

    form_data = {
        "name": "Updated Name but Same Image",
        "slug": "sub-to-keep-image",
        "category": str(parent_category.id),
    }

    response = client.post(
        f"/admin/subcategory/edit/{initial_sub.id}", data=form_data
    )

    assert response.status_code == 302
    
    db_session.refresh(initial_sub)
    assert initial_sub.name == "Updated Name but Same Image"
    assert initial_sub.image_url == "/uploads/subcategory/existing.jpg"
