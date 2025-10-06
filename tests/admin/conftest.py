"""
Admin Test Fixtures
Fixtures for testing SQLAdmin functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app_01.db import Base
from src.app_01.models.admins.admin import Admin
from src.app_01.models.products.product import Product
from src.app_01.models.products.sku import SKU
from src.app_01.models.users.market_user import UserKG, UserUS


@pytest.fixture(scope="function")
def admin_test_db():
    """Create in-memory test database for admin tests"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_admin_user(admin_test_db):
    """Create sample admin user for testing"""
    from src.app_01.models.admins.admin import Admin
    from passlib.hash import bcrypt
    
    admin = Admin(
        username="admin",
        email="admin@marque.com",
        hashed_password=bcrypt.hash("admin123"),
        full_name="Test Admin",
        is_super_admin=True,
        is_active=True
    )
    admin_test_db.add(admin)
    admin_test_db.commit()
    admin_test_db.refresh(admin)
    
    return admin


@pytest.fixture
def sample_content_admin(admin_test_db):
    """Create content admin with limited permissions"""
    from src.app_01.models.admins.admin import Admin
    from passlib.hash import bcrypt
    
    admin = Admin(
        username="content_admin",
        email="content@marque.com",
        hashed_password=bcrypt.hash("content123"),
        full_name="Content Admin",
        is_super_admin=False,
        is_active=True
    )
    admin_test_db.add(admin)
    admin_test_db.commit()
    admin_test_db.refresh(admin)
    
    return admin


@pytest.fixture
def sample_product_for_admin(admin_test_db):
    """Create sample product for admin testing"""
    product = Product(
        brand="Test Brand",
        title="Test Product",
        slug="test-product",
        description="Test product for admin",
        sold_count=0,
        rating_avg=0.0,
        rating_count=0
    )
    admin_test_db.add(product)
    admin_test_db.commit()
    admin_test_db.refresh(product)
    
    return product


@pytest.fixture
def admin_client(admin_test_db):
    """Create test client for admin routes"""
    from src.app_01.main import app
    from src.app_01.db.market_db import db_manager, Market
    from unittest.mock import patch
    
    # Mock the database session to return our test database
    def mock_get_db_session(market):
        yield admin_test_db
    
    # Patch the db_manager to use test database
    with patch.object(db_manager, 'get_db_session', mock_get_db_session):
        # Create test client
        client = TestClient(app)
        yield client


@pytest.fixture
def authenticated_admin_client(admin_client, sample_admin_user):
    """Create authenticated admin test client"""
    # Login as admin (follow redirects to handle 302)
    response = admin_client.post("/admin/login", data={
        "username": "admin",
        "password": "admin123"
    }, follow_redirects=True)
    
    # Verify login succeeded
    assert response.status_code == 200, f"Admin login failed with status {response.status_code}"
    
    yield admin_client


@pytest.fixture
def authenticated_content_admin_client(admin_client, sample_content_admin):
    """Create authenticated content admin test client"""
    # Login as content admin (follow redirects to handle 302)
    response = admin_client.post("/admin/login", data={
        "username": "content_admin",
        "password": "content123"
    }, follow_redirects=True)
    
    # Verify login succeeded
    assert response.status_code == 200, f"Content admin login failed with status {response.status_code}"
    
    yield admin_client

