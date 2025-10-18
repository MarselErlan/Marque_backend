"""
Admin Test Fixtures
Fixtures for testing SQLAdmin functionality
"""

import pytest
import bcrypt
from httpx import AsyncClient
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from src.app_01.main import app
from src.app_01.models.admins.admin import Admin
from src.app_01.core.config import settings


@pytest.fixture(scope="function")
def admin_client() -> TestClient:
    """
    Create a test client for the admin interface.
    This ensures that the admin routes are properly mounted.
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def sample_admin_user(db_session: Session) -> Admin:
    """
    Create a sample admin user for testing.
    """
    # Use the same bcrypt hashing method as the authentication system
    password_bytes = "admin123".encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    # Check if admin already exists (to avoid UNIQUE constraint error)
    existing_admin = db_session.query(Admin).filter_by(username="admin").first()
    if existing_admin:
        db_session.delete(existing_admin)
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
def authenticated_admin_client(admin_client: TestClient, sample_admin_user: Admin) -> TestClient:
    """
    Provides an admin client with a pre-configured session (bypass login).
    Note: FastAPI TestClient doesn't support session_transaction, so we'll use cookies instead.
    """
    # Simulate login by setting session cookies directly
    # This is a workaround since TestClient doesn't have session_transaction
    
    # First, perform actual login to get proper session
    login_response = admin_client.post("/admin/login", data={
        "username": "admin",
        "password": "admin123",
        "market": "kg"
    }, follow_redirects=False)
    
    # The session should now be set via cookies
    return admin_client


@pytest.fixture(scope="function")
def admin_test_db(db_session: Session) -> Session:
    """
    Alias for db_session for admin tests.
    """
    return db_session


@pytest.fixture(scope="function")
async def authenticated_content_admin_client(admin_client: TestClient, db_session: Session) -> TestClient:
    """
    Provides a content admin client that is already authenticated.
    """
    # 1. Create the content admin user
    password_bytes = "contentpassword".encode('utf-8')
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    admin = Admin(
        username="content_admin",
        hashed_password=hashed_password,
        is_super_admin=False,
    )
    db_session.add(admin)
    db_session.commit()

    # 2. Log in as the created user
    login_data = {
        "username": "content_admin",
        "password": "contentpassword",
    }
    response = admin_client.post("/admin/login", data=login_data)
    
    assert response.status_code == 302, "Content admin login failed"
    
    return admin_client

