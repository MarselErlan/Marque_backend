"""
Integration test fixtures
Database setup, API client, and test data for integration tests
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
try:
    from starlette.testclient import TestClient
except ImportError:
    from fastapi.testclient import TestClient

from src.app_01.main import app
from src.app_01.db.market_db import Base, Market, db_manager
from src.app_01.models.users.market_user import UserKG, UserUS
from src.app_01.models.products.product import Product
from src.app_01.models.products.brand import Brand
from src.app_01.models.products.category import Category
from src.app_01.models.banners.banner import Banner, BannerType, Base as BannerBase


@pytest.fixture(scope="function")
def test_db():
    """Create test database for integration tests"""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    BannerBase.metadata.create_all(bind=engine)  # Create banner tables
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)
    BannerBase.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def api_client():
    """Create API test client"""
    # Use TestClient without database override for now
    # Tests will use the actual database or handle mocking differently
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_kg_user(test_db):
    """Create a sample KG user in the database"""
    user = UserKG(
        phone_number="+996555123456",
        full_name="Test User KG",
        email="test.kg@example.com",
        is_verified=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_us_user(test_db):
    """Create a sample US user in the database"""
    user = UserUS(
        phone_number="+12125551234",
        full_name="Test User US",
        email="test.us@example.com",
        is_verified=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_brand(test_db):
    """Create a sample brand in the database"""
    brand = Brand(
        name="Nike",
        slug="nike",
        description="Just Do It"
    )
    test_db.add(brand)
    test_db.commit()
    test_db.refresh(brand)
    return brand


@pytest.fixture
def sample_category(test_db):
    """Create a sample category in the database"""
    category = Category(
        name="Shoes",
        slug="shoes",
        description="Footwear"
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture
def sample_subcategory(test_db, sample_category):
    """Create a sample subcategory in the database"""
    from src.app_01.models.products.category import Subcategory
    subcategory = Subcategory(
        name="T-Shirts",
        slug="t-shirts",
        category_id=sample_category.id,
        description="Test subcategory",
        sort_order=1
    )
    test_db.add(subcategory)
    test_db.commit()
    test_db.refresh(subcategory)
    return subcategory


@pytest.fixture
def sample_product(test_db, sample_brand, sample_category, sample_subcategory):
    """Create a sample product in the database"""
    product = Product(
        title="Running Shoes",
        slug="running-shoes-test",
        description="Great running shoes",
        brand_id=sample_brand.id,
        category_id=sample_category.id,
        subcategory_id=sample_subcategory.id,
        # is_in_stock is not a Product field
        sold_count=10,
        rating_avg=4.5,
        rating_count=20,
        is_active=True
    )
    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)
    return product


@pytest.fixture
def sample_banner(test_db):
    """Create a sample banner in the database"""
    banner = Banner(
        title="Summer Sale",
        description="50% off all items",
        image_url="https://example.com/banner.jpg",
        banner_type=BannerType.SALE,
        is_active=True,
        display_order=1
    )
    test_db.add(banner)
    test_db.commit()
    test_db.refresh(banner)
    return banner


@pytest.fixture
def auth_token(api_client, sample_kg_user):
    """Create authentication token for testing"""
    import jwt
    from datetime import datetime, timedelta
    
    payload = {
        "user_id": str(sample_kg_user.id),
        "phone_number": sample_kg_user.phone_number,
        "market": "KG",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    token = jwt.encode(payload, "your-secret-key-here", algorithm="HS256")
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers for testing"""
    return {
        "Authorization": f"Bearer {auth_token}"
    }

