"""
Admin Test Fixtures
Fixtures for testing SQLAdmin functionality
"""

import pytest
import bcrypt
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from src.app_01.main import app
from src.app_01.models.admins.admin import Admin
from src.app_01.core.config import settings
from src.app_01.db.market_db import db_manager


@pytest.fixture(scope="function")
def mock_db_manager(db_session: Session):
    """
    Mock the db_manager to use the test database session instead of real database files.
    This ensures all database operations in tests use the same in-memory test database.
    """
    # Save original method
    original_get_db_session = db_manager.get_db_session
    
    def mock_get_db_session(market):
        """Return an iterator that yields the test database session for ANY market"""
        # Always yield the same test database session regardless of market
        yield db_session
    
    # Patch the method
    db_manager.get_db_session = mock_get_db_session
    
    try:
        yield db_manager
    finally:
        # Restore original method
        db_manager.get_db_session = original_get_db_session


@pytest.fixture(scope="function")
def sample_admin_user(db_session: Session) -> Admin:
    """
    Create a sample admin user for testing.
    """
    # Use the same bcrypt hashing method as the authentication system
    password_bytes = "admin123".encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    # Clean up any existing admins to avoid conflicts
    db_session.query(Admin).delete()
    db_session.commit()
    
    admin = Admin(
        username="admin",
        hashed_password=hashed_password,
        is_super_admin=True,
        is_active=True,
        email="admin@marque.com",
        full_name="Test Admin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    return admin


@pytest.fixture(scope="function")
def admin_test_db(db_session: Session) -> Session:
    """
    Alias for db_session for admin tests.
    """
    return db_session


@pytest.fixture(scope="function")
def sample_product_for_admin(admin_test_db: Session):
    """
    Create a sample product for admin tests.
    """
    from src.app_01.models.products.product import Product
    from src.app_01.models.products.brand import Brand
    from src.app_01.models.products.category import Category, Subcategory
    import uuid
    
    # Clean up existing data to avoid conflicts
    admin_test_db.query(Product).delete()
    admin_test_db.query(Subcategory).delete()
    admin_test_db.query(Category).delete()
    admin_test_db.query(Brand).delete()
    admin_test_db.commit()
    
    # Create unique identifiers to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    
    # Create brand
    brand = Brand(name=f"Test Brand {unique_id}", slug=f"test-brand-{unique_id}")
    admin_test_db.add(brand)
    admin_test_db.commit()
    admin_test_db.refresh(brand)
    
    # Create category
    category = Category(name=f"Test Category {unique_id}", slug=f"test-category-{unique_id}")
    admin_test_db.add(category)
    admin_test_db.commit()
    admin_test_db.refresh(category)
    
    # Create subcategory (required for products)
    subcategory = Subcategory(
        name=f"Test Subcategory {unique_id}", 
        slug=f"test-subcategory-{unique_id}",
        category_id=category.id
    )
    admin_test_db.add(subcategory)
    admin_test_db.commit()
    admin_test_db.refresh(subcategory)
    
    # Create product
    product = Product(
        title=f"Test Product {unique_id}",
        slug=f"test-product-{unique_id}",
        sku_code=f"BASE-TEST-PROD-{unique_id}",
        description="Test product description",
        brand_id=brand.id,
        category_id=category.id,
        subcategory_id=subcategory.id,  # Required field
        is_active=True
    )
    admin_test_db.add(product)
    admin_test_db.commit()
    admin_test_db.refresh(product)
    
    return product

