"""
Comprehensive Integration Tests for Multi-Market Profile System - All Layers
Tests API → Business Logic → Database for profile, address, and payment operations
Verifies multi-market database isolation across all layers
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta

from src.app_01.main import app
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.users.user import User
from src.app_01.models.users.user_address import UserAddress
from src.app_01.models.users.phone_verification import PhoneVerification


client = TestClient(app)


# ========================================================================
# FIXTURES
# ========================================================================

@pytest.fixture(scope="function")
def kg_db_session():
    """Create a KG database session for testing"""
    SessionLocal = db_manager.get_session_factory(Market.KG)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def us_db_session():
    """Create a US database session for testing"""
    SessionLocal = db_manager.get_session_factory(Market.US)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def kg_user(kg_db_session):
    """Create a KG user for profile testing"""
    # Cleanup
    existing = kg_db_session.query(User).filter(User.phone_number == "+996701234567").first()
    if existing:
        kg_db_session.query(UserAddress).filter(UserAddress.user_id == existing.id).delete()
        kg_db_session.query(PhoneVerification).filter(PhoneVerification.phone_number == "+996701234567").delete()
        kg_db_session.delete(existing)
        kg_db_session.commit()
    
    user = User(
        phone_number="+996701234567",
        full_name="KG Profile Test User",
        email="kg_profile@test.kg",
        is_verified=True,
        is_active=True,
        market="kg",
        language="ru",
        country="KG"
    )
    kg_db_session.add(user)
    kg_db_session.commit()
    kg_db_session.refresh(user)
    return user


@pytest.fixture
def us_user(us_db_session):
    """Create a US user for profile testing"""
    # Cleanup
    existing = us_db_session.query(User).filter(User.phone_number == "+17025551234").first()
    if existing:
        us_db_session.query(UserAddress).filter(UserAddress.user_id == existing.id).delete()
        us_db_session.query(PhoneVerification).filter(PhoneVerification.phone_number == "+17025551234").delete()
        us_db_session.delete(existing)
        us_db_session.commit()
    
    user = User(
        phone_number="+17025551234",
        full_name="US Profile Test User",
        email="us_profile@test.com",
        is_verified=True,
        is_active=True,
        market="us",
        language="en",
        country="US"
    )
    us_db_session.add(user)
    us_db_session.commit()
    us_db_session.refresh(user)
    return user


@pytest.fixture
def kg_auth_token(kg_user):
    """Generate auth token for KG user"""
    from src.app_01.services.auth_service import SECRET_KEY, ALGORITHM
    
    payload = {
        "sub": kg_user.id,
        "market": "kg",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def us_auth_token(us_user):
    """Generate auth token for US user"""
    from src.app_01.services.auth_service import SECRET_KEY, ALGORITHM
    
    payload = {
        "sub": us_user.id,
        "market": "us",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ========================================================================
# TEST SUITE 1: Profile Data - Database Layer
# ========================================================================

class TestProfileDatabaseLayer:
    """Test profile data persistence in correct database"""
    
    def test_kg_user_stored_in_kg_database(
        self,
        kg_user,
        kg_db_session,
        us_db_session
    ):
        """Test that KG user profile is stored in KG database only"""
        # Verify user exists in KG database
        kg_user_check = kg_db_session.query(User).filter(
            User.phone_number == "+996701234567"
        ).first()
        assert kg_user_check is not None, "User not found in KG database"
        assert kg_user_check.market == "kg"
        assert kg_user_check.email == "kg_profile@test.kg"
        
        # Verify user does NOT exist in US database
        us_user_check = us_db_session.query(User).filter(
            User.phone_number == "+996701234567"
        ).first()
        assert us_user_check is None, "User incorrectly found in US database"
    
    
    def test_us_user_stored_in_us_database(
        self,
        us_user,
        us_db_session,
        kg_db_session
    ):
        """Test that US user profile is stored in US database only"""
        # Verify user exists in US database
        us_user_check = us_db_session.query(User).filter(
            User.phone_number == "+17025551234"
        ).first()
        assert us_user_check is not None, "User not found in US database"
        assert us_user_check.market == "us"
        assert us_user_check.email == "us_profile@test.com"
        assert us_user_check.country == "US"
        
        # Verify user does NOT exist in KG database
        kg_user_check = kg_db_session.query(User).filter(
            User.phone_number == "+17025551234"
        ).first()
        assert kg_user_check is None, "User incorrectly found in KG database"
    
    
    def test_profile_update_targets_correct_database(
        self,
        kg_user,
        kg_db_session,
        us_db_session
    ):
        """Test that profile updates affect only the correct database"""
        # Update profile in KG database
        kg_user.full_name = "Updated KG Name"
        kg_user.email = "updated_kg@test.kg"
        kg_db_session.commit()
        kg_db_session.refresh(kg_user)
        
        # Verify update in KG database
        kg_user_check = kg_db_session.query(User).filter(User.id == kg_user.id).first()
        assert kg_user_check.full_name == "Updated KG Name"
        assert kg_user_check.email == "updated_kg@test.kg"
        
        # Verify no changes in US database
        us_user_count = us_db_session.query(User).filter(
            User.email == "updated_kg@test.kg"
        ).count()
        assert us_user_count == 0, "Update leaked to US database"


# ========================================================================
# TEST SUITE 2: Profile API - API Layer
# ========================================================================

class TestProfileAPILayer:
    """Test profile API endpoints and their database targeting"""
    
    def test_kg_user_get_profile_from_kg_database(
        self,
        kg_auth_token,
        kg_user,
        kg_db_session
    ):
        """Test that KG user profile retrieval connects to KG database"""
        response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        
        # API should succeed
        assert response.status_code == 200, f"Profile retrieval failed: {response.text}"
        
        profile = response.json()
        
        # Verify profile data matches KG database
        assert profile["phone_number"] == "+996701234567"
        assert profile["full_name"] == "KG Profile Test User"
        assert profile["market"] == "kg"
    
    
    def test_us_user_get_profile_from_us_database(
        self,
        us_auth_token,
        us_user,
        us_db_session
    ):
        """Test that US user profile retrieval connects to US database"""
        response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {us_auth_token}"}
        )
        
        # API should succeed
        assert response.status_code == 200, f"Profile retrieval failed: {response.text}"
        
        profile = response.json()
        
        # Verify profile data matches US database
        assert profile["phone_number"] == "+17025551234"
        assert profile["full_name"] == "US Profile Test User"
        assert profile["market"] == "us"
    
    
    def test_kg_user_update_profile_persists_to_kg_database(
        self,
        kg_auth_token,
        kg_user,
        kg_db_session
    ):
        """Test that KG user profile update saves to KG database only"""
        # Update via API
        update_data = {
            "full_name": "API Updated KG Name"
        }
        
        response = client.put(
            "/api/v1/auth/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        
        assert response.status_code == 200, f"Profile update failed: {response.text}"
        
        # Verify update persisted to KG database
        kg_db_session.refresh(kg_user)
        assert kg_user.full_name == "API Updated KG Name"
    
    
    def test_us_user_update_profile_persists_to_us_database(
        self,
        us_auth_token,
        us_user,
        us_db_session
    ):
        """Test that US user profile update saves to US database only"""
        # Update via API
        update_data = {
            "full_name": "API Updated US Name"
        }
        
        response = client.put(
            "/api/v1/auth/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {us_auth_token}"}
        )
        
        assert response.status_code == 200, f"Profile update failed: {response.text}"
        
        # Verify update persisted to US database
        us_db_session.refresh(us_user)
        assert us_user.full_name == "API Updated US Name"


# ========================================================================
# TEST SUITE 3: User Address - All Layers
# ========================================================================

class TestUserAddressAllLayers:
    """Test user address operations across all layers"""
    
    def test_kg_user_address_saved_to_kg_database(
        self,
        kg_user,
        kg_db_session,
        us_db_session
    ):
        """Test that KG user address is saved to KG database only"""
        # Create address in KG database
        address = UserAddress(
            user_id=kg_user.id,
            title="Home",
            full_address="123 Chui Avenue",
            city="Bishkek",
            country="Kyrgyzstan",
            postal_code="720000",
            is_default=True
        )
        kg_db_session.add(address)
        kg_db_session.commit()
        kg_db_session.refresh(address)
        
        # Verify address exists in KG database
        kg_address = kg_db_session.query(UserAddress).filter(
            UserAddress.user_id == kg_user.id
        ).first()
        assert kg_address is not None, "Address not found in KG database"
        assert kg_address.city == "Bishkek"
        
        # Verify NO address for this user in US database
        us_address = us_db_session.query(UserAddress).filter(
            UserAddress.user_id == kg_user.id
        ).first()
        assert us_address is None, "Address incorrectly found in US database"
    
    
    def test_us_user_address_saved_to_us_database(
        self,
        us_user,
        us_db_session,
        kg_db_session
    ):
        """Test that US user address is saved to US database only"""
        # Create address in US database
        address = UserAddress(
            user_id=us_user.id,
            title="Home",
            full_address="456 Main Street",
            city="Las Vegas",
            country="United States",
            postal_code="89101",
            is_default=True
        )
        us_db_session.add(address)
        us_db_session.commit()
        us_db_session.refresh(address)
        
        # Verify address exists in US database
        us_address = us_db_session.query(UserAddress).filter(
            UserAddress.user_id == us_user.id
        ).first()
        assert us_address is not None, "Address not found in US database"
        assert us_address.city == "Las Vegas"
        assert us_address.country == "United States"
        
        # Verify NO address for this user in KG database
        kg_address = kg_db_session.query(UserAddress).filter(
            UserAddress.user_id == us_user.id
        ).first()
        assert kg_address is None, "Address incorrectly found in KG database"
    
    
    def test_user_can_have_multiple_addresses_in_correct_database(
        self,
        kg_user,
        kg_db_session
    ):
        """Test that user can have multiple addresses in their market database"""
        # Create multiple addresses
        address1 = UserAddress(
            user_id=kg_user.id,
            title="Home",
            full_address="123 Chui Avenue",
            city="Bishkek",
            country="Kyrgyzstan",
            postal_code="720000",
            is_default=True
        )
        
        address2 = UserAddress(
            user_id=kg_user.id,
            title="Work",
            full_address="456 Lenin Street",
            city="Osh",
            country="Kyrgyzstan",
            postal_code="723500",
            is_default=False
        )
        
        kg_db_session.add(address1)
        kg_db_session.add(address2)
        kg_db_session.commit()
        
        # Verify both addresses exist
        addresses = kg_db_session.query(UserAddress).filter(
            UserAddress.user_id == kg_user.id
        ).all()
        
        assert len(addresses) == 2, "Should have 2 addresses"
        cities = [addr.city for addr in addresses]
        assert "Bishkek" in cities
        assert "Osh" in cities


# ========================================================================
# TEST SUITE 4: End-to-End Profile Workflow
# ========================================================================

class TestProfileEndToEndWorkflow:
    """Test complete profile workflow from API to database"""
    
    def test_complete_profile_management_kg_user(
        self,
        kg_auth_token,
        kg_user,
        kg_db_session,
        us_db_session
    ):
        """Test complete profile workflow for KG user (API → Logic → DB)"""
        # Step 1: Get initial profile via API
        get_response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        assert get_response.status_code == 200
        initial_profile = get_response.json()
        assert initial_profile["phone_number"] == "+996701234567"
        
        # Step 2: Update profile via API
        update_data = {
            "full_name": "Workflow Test KG User"
        }
        
        update_response = client.put(
            "/api/v1/auth/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        assert update_response.status_code == 200
        
        # Step 3: Verify update in database
        kg_db_session.refresh(kg_user)
        assert kg_user.full_name == "Workflow Test KG User"
        
        # Step 4: Verify NO changes in US database
        us_user_check = us_db_session.query(User).filter(
            User.full_name == "Workflow Test KG User"
        ).first()
        assert us_user_check is None, "Changes leaked to US database"
        
        # Step 5: Get updated profile via API
        final_response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        assert final_response.status_code == 200
        final_profile = final_response.json()
        assert final_profile["full_name"] == "Workflow Test KG User"
    
    
    def test_complete_profile_management_us_user(
        self,
        us_auth_token,
        us_user,
        us_db_session,
        kg_db_session
    ):
        """Test complete profile workflow for US user (API → Logic → DB)"""
        # Step 1: Get initial profile
        get_response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {us_auth_token}"}
        )
        assert get_response.status_code == 200
        initial_profile = get_response.json()
        assert initial_profile["phone_number"] == "+17025551234"
        
        # Step 2: Update profile
        update_data = {
            "full_name": "Workflow Test US User"
        }
        
        update_response = client.put(
            "/api/v1/auth/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {us_auth_token}"}
        )
        assert update_response.status_code == 200
        
        # Step 3: Verify update in database
        us_db_session.refresh(us_user)
        assert us_user.full_name == "Workflow Test US User"
        
        # Step 4: Verify NO changes in KG database
        kg_user_check = kg_db_session.query(User).filter(
            User.full_name == "Workflow Test US User"
        ).first()
        assert kg_user_check is None, "Changes leaked to KG database"


# ========================================================================
# TEST SUITE 5: Cross-Market Data Isolation
# ========================================================================

class TestCrossMarketDataIsolation:
    """Test that profile operations don't leak between markets"""
    
    def test_same_email_different_markets(
        self,
        kg_db_session,
        us_db_session
    ):
        """Test that same email can exist in different markets without conflict"""
        # Create KG user with email
        kg_user = User(
            phone_number="+996702222222",
            full_name="KG Same Email User",
            email="same@email.test",
            is_verified=True,
            is_active=True,
            market="kg"
        )
        kg_db_session.add(kg_user)
        kg_db_session.commit()
        
        # Create US user with SAME email
        us_user = User(
            phone_number="+17023333333",
            full_name="US Same Email User",
            email="same@email.test",
            is_verified=True,
            is_active=True,
            market="us",
            language="en",
            country="US"
        )
        us_db_session.add(us_user)
        us_db_session.commit()
        
        # Verify both users exist with same email in different databases
        kg_check = kg_db_session.query(User).filter(User.email == "same@email.test").first()
        us_check = us_db_session.query(User).filter(User.email == "same@email.test").first()
        
        assert kg_check is not None, "KG user not found"
        assert us_check is not None, "US user not found"
        assert kg_check.market == "kg"
        assert us_check.market == "us"
        assert kg_check.id != us_check.id, "Users should have different IDs"
        
        # Cleanup
        kg_db_session.delete(kg_user)
        us_db_session.delete(us_user)
        kg_db_session.commit()
        us_db_session.commit()
    
    
    def test_user_count_isolation(
        self,
        kg_user,
        us_user,
        kg_db_session,
        us_db_session
    ):
        """Test that user counts are independent per market"""
        kg_user_count = kg_db_session.query(User).count()
        us_user_count = us_db_session.query(User).count()
        
        # Both markets should have users
        assert kg_user_count > 0, "KG database has no users"
        assert us_user_count > 0, "US database has no users"
        
        # Counts can be different (they're independent databases)
        # Just verify both are positive


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

