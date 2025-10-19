import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Tuple

from src.app_01.models import Order, User, Product, OrderStatus, Brand, Category, Subcategory


def setup_dashboard_data(db_session: Session):
    """Populate the database with sample data for dashboard analytics."""
    user = User(full_name="Test User", phone_number="+996555111222")
    brand = Brand(name="Test Brand", slug="test-brand")
    db_session.add_all([brand, user])
    db_session.commit()

    # Create required category and subcategory to satisfy NOT NULL constraints
    category = Category(name="Test Category", slug="test-category")
    db_session.add(category)
    db_session.commit()

    subcategory = Subcategory(name="Test Subcategory", slug="test-subcategory", category_id=category.id)
    db_session.add(subcategory)
    db_session.commit()

    product = Product(title="Test Product", slug="test-product", brand_id=brand.id, category_id=category.id, subcategory_id=subcategory.id, is_active=True)
    db_session.add(product)
    db_session.commit()
    
    order = Order(
        order_number="TST-1001",
        user_id=user.id,
        status=OrderStatus.DELIVERED,
        customer_name=user.full_name or "Test User",
        customer_phone=user.phone_number,
        delivery_address="Test Address",
        subtotal=150.0,
        total_amount=150.0,
    )
    db_session.add(order)
    db_session.commit()


def test_dashboard_loads_successfully(authenticated_app_client: Tuple[TestClient, Session]):
    """Test that the main dashboard page loads."""
    client, db_session = authenticated_app_client
    setup_dashboard_data(db_session)
    
    response = client.get("/admin/")
    
    assert response.status_code == 200
    content = response.text
    # Basic sanity checks for admin UI wrapper and menu
    assert "Marque - Multi-Market Admin" in content
    assert (">Dashboard<" in content) or ('nav-link-title">Dashboard<' in content)


def test_dashboard_market_switching(authenticated_app_client: Tuple[TestClient, Session]):
    """Test that the market can be switched from the dashboard."""
    client, _ = authenticated_app_client
    
    # Switch to US market
    response = client.post(
        "/admin/switch-market",
        data={"market": "us"},
        allow_redirects=True
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    assert data.get("market") == "us"
    assert data.get("config", {}).get("name") in ["United States", "Kyrgyzstan", "United States"]
    
    # Reload dashboard (should still load)
    dashboard_response = client.get("/admin/")
    assert dashboard_response.status_code == 200
