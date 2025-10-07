"""
Pytest fixtures and configuration
Shared test fixtures for all tests
"""

import pytest
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Try starlette first, fall back to fastapi
try:
    from starlette.testclient import TestClient
except ImportError:
    from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app_01.db.market_db import Base, Market
from src.app_01.main import app
from src.app_01.models.banners.banner import Base as BannerBase
# Import Cart and Wishlist models to ensure their tables are created
from src.app_01.models.orders.cart import Cart, CartItem
from src.app_01.models.users.wishlist import Wishlist, WishlistItem


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine (in-memory SQLite)"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    BannerBase.metadata.create_all(bind=engine)  # Create banner tables
    yield engine
    Base.metadata.drop_all(bind=engine)
    BannerBase.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create a new database session for a test"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    from src.app_01.db.market_db import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# Sample data fixtures

@pytest.fixture
def sample_user_kg_data():
    """Sample KG user data"""
    return {
        "phone_number": "+996555123456",
        "full_name": "Test User KG",
        "email": "test.kg@example.com",
        "market": "KG"
    }


@pytest.fixture
def sample_user_us_data():
    """Sample US user data"""
    return {
        "phone_number": "+12125551234",
        "full_name": "Test User US",
        "email": "test.us@example.com",
        "market": "US"
    }


@pytest.fixture
def sample_product_data():
    """Sample product data"""
    return {
        "title": "Test Product",
        "description": "This is a test product description",
        "is_in_stock": True,
        "sold_count": 0,
        "rating_avg": 0.0,
        "rating_count": 0
    }


@pytest.fixture
def sample_banner_data():
    """Sample banner data"""
    return {
        "title": "Test Banner",
        "description": "Test banner description",
        "image_url": "https://example.com/banner.jpg",
        "link": "https://example.com",
        "banner_type": "sale",
        "is_active": True,
        "display_order": 1
    }


@pytest.fixture
def sample_brand_data():
    """Sample brand data"""
    return {
        "name": "Test Brand",
        "slug": "test-brand",
        "description": "Test brand description"
    }


@pytest.fixture
def sample_category_data():
    """Sample category data"""
    return {
        "name": "Test Category",
        "slug": "test-category",
        "description": "Test category description"
    }


@pytest.fixture
def mock_jwt_token():
    """Generate mock JWT token for testing"""
    import jwt
    from datetime import datetime, timedelta
    
    payload = {
        "user_id": "1",
        "phone_number": "+996555123456",
        "market": "KG",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    return jwt.encode(payload, "your-secret-key-here", algorithm="HS256")


@pytest.fixture
def auth_headers(mock_jwt_token):
    """Generate authorization headers for testing"""
    return {
        "Authorization": f"Bearer {mock_jwt_token}"
    }


# Market fixtures

@pytest.fixture(params=[Market.KG, Market.US])
def market(request):
    """Parametrize tests for both markets"""
    return request.param


@pytest.fixture
def kg_market():
    """KG market fixture"""
    return Market.KG


@pytest.fixture
def us_market():
    """US market fixture"""
    return Market.US


# Import catalog fixtures plugin
pytest_plugins = ["tests.fixtures.catalog_fixtures"]

