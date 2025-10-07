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
    from src.app_01.models.products.brand import Brand
    from src.app_01.models.products.category import Category, Subcategory
    
    # Create brand
    brand = Brand(name="Test Brand", slug="test-brand")
    admin_test_db.add(brand)
    admin_test_db.commit()
    admin_test_db.refresh(brand)
    
    # Create category
    category = Category(name="Test Category", slug="test-category")
    admin_test_db.add(category)
    admin_test_db.commit()
    admin_test_db.refresh(category)
    
    # Create subcategory
    subcategory = Subcategory(
        name="Test Subcategory",
        slug="test-subcategory",
        category_id=category.id
    )
    admin_test_db.add(subcategory)
    admin_test_db.commit()
    admin_test_db.refresh(subcategory)
    
    # Create product
    product = Product(
        brand_id=brand.id,
        category_id=category.id,
        subcategory_id=subcategory.id,
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
def sample_products_for_admin(admin_test_db, sample_product_for_admin):
    """Create multiple sample products for admin testing"""
    products = [sample_product_for_admin]  # Include the base product
    
    # Get the brand, category, subcategory from the base product
    brand_id = sample_product_for_admin.brand_id
    category_id = sample_product_for_admin.category_id
    subcategory_id = sample_product_for_admin.subcategory_id
    
    for i in range(4):  # Create 4 more products (total 5)
        product = Product(
            brand_id=brand_id,
            category_id=category_id,
            subcategory_id=subcategory_id,
            title=f"Test Product {i+2}",
            slug=f"test-product-{i}",
            description=f"Test product {i} for admin",
            sold_count=i * 10,
            rating_avg=4.0 + (i * 0.1),
            rating_count=i * 5
        )
        admin_test_db.add(product)
    
    admin_test_db.commit()
    
    # Query fresh instances to ensure they're attached to session
    products = admin_test_db.query(Product).filter(
        Product.slug.like('test-product-%')
    ).all()
    
    return products


@pytest.fixture
def many_products_for_admin(admin_test_db):
    """Create many products to test pagination"""
    for i in range(25):
        product = Product(
            brand=f"Brand {i}",
            title=f"Product {i:03d}",
            slug=f"product-{i:03d}",
            description=f"Product {i} description",
            sold_count=i,
            rating_avg=3.0 + (i % 5) * 0.5,
            rating_count=i * 2
        )
        admin_test_db.add(product)
    
    admin_test_db.commit()
    
    # Query fresh instances
    products = admin_test_db.query(Product).filter(
        Product.slug.like('product-%')
    ).all()
    
    return products


@pytest.fixture
def product_with_skus_for_admin(admin_test_db):
    """Create product with associated SKUs"""
    from src.app_01.models.products.sku import SKU
    
    # Create product with unique slug
    product = Product(
        brand="SKU Test Brand",
        title="Product with SKUs",
        slug="product-with-skus-test",
        description="Product for SKU testing",
        sold_count=0,
        rating_avg=0.0,
        rating_count=0
    )
    admin_test_db.add(product)
    admin_test_db.commit()
    admin_test_db.refresh(product)
    
    # Create SKUs for the product
    for i, size in enumerate(["S", "M", "L"]):
        sku = SKU(
            product_id=product.id,
            size=size,
            color="Blue",
            price=29.99 + (i * 5),
            original_price=39.99 + (i * 5),
            quantity=10 + i,
            sku_code=f"SKU-{product.id}-{size}"
        )
        admin_test_db.add(sku)
    
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

