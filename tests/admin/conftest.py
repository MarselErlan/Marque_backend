"""
Admin Test Fixtures
Fixtures for testing SQLAdmin functionality
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from src.app_01.main import app
from src.app_01.models.admins.admin import Admin
from src.app_01.core.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(scope="function")
def admin_client() -> TestClient:
    """
    Create a test client for the admin interface.
    This ensures that the admin routes are properly mounted.
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def authenticated_admin_client(admin_client: TestClient, db_session: Session) -> TestClient:
    """
    Provides an admin client with a pre-configured session (bypass login).
    """
    # 1. Create the admin user for this test function
    hashed_password = pwd_context.hash("python123")
    
    # Check if admin already exists (to avoid UNIQUE constraint error)
    existing_admin = db_session.query(Admin).filter_by(username="test_admin").first()
    if existing_admin:
        db_session.delete(existing_admin)
        db_session.commit()
    
    admin = Admin(
        username="test_admin",
        hashed_password=hashed_password,
        is_super_admin=True,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    # 2. Manually set up the session to simulate a logged-in admin (bypass actual login)
    with admin_client as client:
        with client.session_transaction() as session:
            session["token"] = "test-token"
            session["admin_id"] = admin.id
            session["market"] = "kg"
    
    return admin_client


@pytest.fixture(scope="function")
async def authenticated_content_admin_client(admin_client: TestClient, db_session: Session) -> TestClient:
    """
    Provides a content admin client that is already authenticated.
    """
    # 1. Create the content admin user
    hashed_password = pwd_context.hash("contentpassword")
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

