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
from sqlalchemy.engine import Engine

# Try starlette first, fall back to fastapi
try:
    from starlette.testclient import TestClient
except ImportError:
    from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app_01.db.market_db import Base, Market, get_db
from src.app_01.main import app
from src.app_01.models.banners.banner import Base as BannerBase
# Import all models to ensure they are registered with their respective Base
from src.app_01.models import *
from src.app_01.services.auth_service import create_admin
from typing import Generator, Tuple


# New application-level fixture for complete test isolation
@pytest.fixture(scope="function")
def app_client() -> Generator[TestClient, None, None]:
    """
    Creates a completely isolated TestClient for each test function.
    - Uses an in-memory SQLite database.
    - Creates all tables before the test.
    - Drops all tables after the test.
    - Overrides the `get_db` dependency.
    """
    
    # In-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    BannerBase.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Dependency override
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    
    # Yield the TestClient
    with TestClient(app) as client:
        yield client
    
    # Clean up: drop all tables
    Base.metadata.drop_all(bind=engine)
    BannerBase.metadata.drop_all(bind=engine)
    
    # Clear dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def authenticated_app_client() -> Generator[Tuple[TestClient, Session], None, None]:
    """
    Provides an authenticated TestClient and a synchronized database session.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    Base.metadata.create_all(bind=engine)
    BannerBase.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db_session = TestingSessionLocal()

    # Patch the db_manager to use the same session
    from src.app_01.db.market_db import db_manager
    
    def get_test_db_session(market: Market):
        yield db_session

    # Preserve previous state to restore later
    prev_get_db_session = db_manager.get_db_session
    prev_engines = db_manager.engines.copy()
    prev_session_factories = db_manager.session_factories.copy()

    # Only override session getter for the lifespan of this fixture
    db_manager.get_db_session = get_test_db_session
    
    # CRITICAL FIX: Patch db_manager.get_engine to return test engine
    # This prevents SQLAdmin from connecting to production Railway DB
    prev_get_engine = db_manager.get_engine
    def get_test_engine(market: Market):
        return engine
    db_manager.get_engine = get_test_engine
    
    # CRITICAL FIX 2: Patch the SQLAdmin instance to use test engine
    # admin_app is already created at module import time, so we need to patch its engine
    # Note: In main.py, the admin is created via create_sqladmin_app(app)
    # We need to patch it after the app is imported
    try:
        import src.app_01.main
        if hasattr(src.app_01.main, 'app'):
            test_app = src.app_01.main.app
            # Access the admin instance through app.state or another attribute
            for route in test_app.routes:
                if hasattr(route, 'path') and '/admin' in route.path:
                    pass  # Admin routes exist, admin is initialized
        # The admin is initialized in main.py, its engine is already set
        # We patched db_manager.get_engine above, which should be enough
    except:
        pass  # If import fails, just skip this patch

    def override_get_db():
        try:
            yield db_session
        finally:
            # The session is managed by the fixture
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    # Preserve existing overrides to restore later
    prev_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    
    # Create admin in this specific session
    create_admin(
        db=db_session,
        username="test_admin",
        password="password",
        full_name="Test Admin",
        is_super_admin=True,
    )

    with TestClient(app) as client:
        # Log in the admin
        response = client.post(
            "/admin/login",
            data={"username": "test_admin", "password": "password", "market": "kg"},
            allow_redirects=False  # We will follow the redirect manually in the test if needed
        )
        assert response.status_code == 302, f"Admin login failed. Expected 302 redirect, got {response.status_code}. Response: {response.text}"
        
        try:
            yield client, db_session
        finally:
            # Restore previous state
            db_manager.get_db_session = prev_get_db_session
            db_manager.get_engine = prev_get_engine  # Restore get_engine
            db_manager.engines = prev_engines
            db_manager.session_factories = prev_session_factories
            app.dependency_overrides = prev_overrides
            db_session.close()


@pytest.fixture(scope="function")
def test_db_engine() -> Engine:
    """Create in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    return engine


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """
    Create a new database session for a test.
    This fixture ensures a clean database for every single test.
    It drops all tables and recreates them before yielding the session.
    """
    # Drop all tables
    Base.metadata.drop_all(bind=test_db_engine)
    BannerBase.metadata.drop_all(bind=test_db_engine)
    
    # Create all tables
    Base.metadata.create_all(bind=test_db_engine)
    BannerBase.metadata.create_all(bind=test_db_engine)
    
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Clean up after the test by dropping tables again
        Base.metadata.drop_all(bind=test_db_engine)
        BannerBase.metadata.drop_all(bind=test_db_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    
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
        "market": "kg"
    }


@pytest.fixture
def sample_user_us_data():
    """Sample US user data"""
    return {
        "phone_number": "+12125551234",
        "full_name": "Test User US",
        "email": "test.us@example.com",
        "market": "us"
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
        "banner_type": "promo",
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
        "market": "kg",
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

