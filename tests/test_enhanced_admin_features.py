import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Tuple, Generator

from src.app_01.models import AdminLog, Product, Category, Subcategory, Brand


@pytest.fixture(scope="function")
def setup_entities(authenticated_app_client: Tuple[TestClient, Session]) -> Generator[Tuple[int, int, int], None, None]:
    """Create necessary entities for product creation"""
    _, db_session = authenticated_app_client
    brand = Brand(name="Test Brand", slug="test-brand")
    category = Category(name="Test Category", slug="test-category")
    subcategory = Subcategory(name="Test Subcategory", slug="test-subcategory", category=category)
    db_session.add_all([brand, category, subcategory])
    db_session.commit()
    yield brand.id, category.id, subcategory.id


def test_create_action_logs_to_db(
    authenticated_app_client: Tuple[TestClient, Session],
    setup_entities: Tuple[int, int, int]
):
    """
    Test that creating a new entity via the admin panel creates an audit log.
    """
    client, db_session = authenticated_app_client
    brand_id, category_id, subcategory_id = setup_entities
    
    # Action: Create a new product
    product_data = {
        "title": "New Test Product",
        "slug": "new-test-product",
        "brand": str(brand_id),
        "category": str(category_id),
        "subcategory": str(subcategory_id),
        "is_active": "y",
    }
    
    response = client.post(
        "/admin/product/new",
        data=product_data,
        allow_redirects=True,
    )
    
    assert response.status_code == 200
    assert "Product was successfully created." in response.text
    
    # Verification: Check for the audit log
    log_entry = db_session.query(AdminLog).filter(AdminLog.action == "create").first()
    
    assert log_entry is not None
    assert log_entry.action == "create"
    assert log_entry.entity_type == "product"
    assert "Created new Product" in log_entry.description
    assert log_entry.admin.username == "test_admin"


def test_edit_action_logs_to_db(
    authenticated_app_client: Tuple[TestClient, Session],
    setup_entities: Tuple[int, int, int]
):
    """
    Test that editing an entity via the admin panel creates an audit log.
    """
    client, db_session = authenticated_app_client
    brand_id, category_id, subcategory_id = setup_entities

    # Setup: Create a product to edit
    product = Product(
        title="Editable Product", 
        slug="editable-product",
        brand_id=brand_id,
        category_id=category_id,
        subcategory_id=subcategory_id
    )
    db_session.add(product)
    db_session.commit()
    product_id = product.id

    # Action: Edit the product
    edit_data = {
        "title": "Updated Product Title",
        "slug": "editable-product",
        "brand": str(brand_id),
        "category": str(category_id),
        "subcategory": str(subcategory_id),
    }

    response = client.post(
        f"/admin/product/edit/{product_id}",
        data=edit_data,
        allow_redirects=True,
    )

    assert response.status_code == 200
    assert "Product was successfully edited." in response.text
    
    # Verification: Check for the audit log
    log_entry = db_session.query(AdminLog).filter(AdminLog.action == "update").first()
    
    assert log_entry is not None
    assert log_entry.action == "update"
    assert log_entry.entity_type == "product"
    assert log_entry.entity_id == product_id
    assert "Updated Product" in log_entry.description
    assert log_entry.admin.username == "test_admin"
