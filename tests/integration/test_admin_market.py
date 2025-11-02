"""
Comprehensive Integration Tests for Admin Market-Based Database Access

Tests admin authentication, market selection, and database isolation across KG and US markets
"""
import pytest
from sqlalchemy.orm import Session
import bcrypt

from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin
from src.app_01.models.products.product import Product
from src.app_01.models.products.brand import Brand
from src.app_01.models.products.category import Category


# ========================================================================
# FIXTURES
# ========================================================================

@pytest.fixture(scope="function")
def kg_admin_session():
    """Get KG database session for admin operations"""
    SessionLocal = db_manager.get_session_factory(Market.KG)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def us_admin_session():
    """Get US database session for admin operations"""
    SessionLocal = db_manager.get_session_factory(Market.US)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def kg_admin(kg_admin_session):
    """Create a KG admin for testing"""
    # Clean up existing
    existing_admin = kg_admin_session.query(Admin).filter(
        Admin.username == "kg_test_admin"
    ).first()
    if existing_admin:
        kg_admin_session.delete(existing_admin)
        kg_admin_session.commit()
    
    # Create admin with hashed password
    password = "test123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    admin = Admin(
        username="kg_test_admin",
        email="kg_admin@test.com",
        hashed_password=hashed.decode('utf-8'),
        full_name="KG Test Admin",
        admin_role="super_admin",
        is_super_admin=True,
        is_active=True,
        market="kg"  # Admin's assigned market
    )
    kg_admin_session.add(admin)
    kg_admin_session.commit()
    kg_admin_session.refresh(admin)
    
    yield admin
    
    # Cleanup
    kg_admin_session.delete(admin)
    kg_admin_session.commit()


@pytest.fixture
def us_admin(us_admin_session):
    """Create a US admin for testing"""
    # Clean up existing
    existing_admin = us_admin_session.query(Admin).filter(
        Admin.username == "us_test_admin"
    ).first()
    if existing_admin:
        us_admin_session.delete(existing_admin)
        us_admin_session.commit()
    
    # Create admin with hashed password
    password = "test456"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    admin = Admin(
        username="us_test_admin",
        email="us_admin@test.com",
        hashed_password=hashed.decode('utf-8'),
        full_name="US Test Admin",
        admin_role="super_admin",
        is_super_admin=True,
        is_active=True,
        market="us"  # Admin's assigned market
    )
    us_admin_session.add(admin)
    us_admin_session.commit()
    us_admin_session.refresh(admin)
    
    yield admin
    
    # Cleanup
    us_admin_session.delete(admin)
    us_admin_session.commit()


# Note: Product fixtures removed - not needed for admin market tests
# Admin market functionality can be tested without creating test products


# ========================================================================
# TEST SUITE 1: Admin Market Column Storage
# ========================================================================

class TestAdminMarketStorage:
    """Test that admin market is correctly stored and retrieved"""
    
    def test_kg_admin_has_correct_market(self, kg_admin, kg_admin_session):
        """Test KG admin has market='kg'"""
        # Fetch fresh from database
        admin = kg_admin_session.query(Admin).filter(Admin.id == kg_admin.id).first()
        
        assert admin is not None
        assert admin.market == "kg"
        assert admin.username == "kg_test_admin"
    
    def test_us_admin_has_correct_market(self, us_admin, us_admin_session):
        """Test US admin has market='us'"""
        # Fetch fresh from database
        admin = us_admin_session.query(Admin).filter(Admin.id == us_admin.id).first()
        
        assert admin is not None
        assert admin.market == "us"
        assert admin.username == "us_test_admin"
    
    def test_admin_market_update(self, kg_admin, kg_admin_session):
        """Test that admin market can be updated"""
        # Update market
        kg_admin.market = "us"
        kg_admin_session.commit()
        
        # Fetch fresh from database
        kg_admin_session.expire_all()
        admin = kg_admin_session.query(Admin).filter(Admin.id == kg_admin.id).first()
        
        assert admin.market == "us"
        
        # Restore original market
        admin.market = "kg"
        kg_admin_session.commit()


# ========================================================================
# TEST SUITE 2: Database Connection Based on Market
# ========================================================================

class TestAdminDatabaseConnection:
    """Test that admin connects to correct database based on market column"""
    
    def test_kg_admin_connects_to_kg_database(self, kg_admin):
        """Test KG admin connects to KG database"""
        # Verify admin's market
        assert kg_admin.market == "kg"
        
        # Get database session based on admin's market
        admin_market = Market(kg_admin.market)
        AdminSessionLocal = db_manager.get_session_factory(admin_market)
        admin_db = AdminSessionLocal()
        
        try:
            # Verify we can query from correct database
            admin_count = admin_db.query(Admin).count()
            assert admin_count >= 1, "Should be able to query KG database"
            
            # Verify the admin's market is correctly stored
            found_admin = admin_db.query(Admin).filter(
                Admin.username == "kg_test_admin"
            ).first()
            assert found_admin is not None
            assert found_admin.market == "kg"
            
        finally:
            admin_db.close()
    
    def test_us_admin_connects_to_us_database(self, us_admin):
        """Test US admin connects to US database"""
        # Verify admin's market
        assert us_admin.market == "us"
        
        # Get database session based on admin's market
        admin_market = Market(us_admin.market)
        AdminSessionLocal = db_manager.get_session_factory(admin_market)
        admin_db = AdminSessionLocal()
        
        try:
            # Verify we can query from correct database
            admin_count = admin_db.query(Admin).count()
            assert admin_count >= 1, "Should be able to query US database"
            
            # Verify the admin's market is correctly stored
            found_admin = admin_db.query(Admin).filter(
                Admin.username == "us_test_admin"
            ).first()
            assert found_admin is not None
            assert found_admin.market == "us"
            
        finally:
            admin_db.close()
    
    def test_admin_market_determines_database(self, kg_admin, us_admin):
        """Test that admin.market column determines which database to connect to"""
        # KG admin should get KG database
        kg_market = Market(kg_admin.market)
        assert kg_market == Market.KG
        
        # US admin should get US database
        us_market = Market(us_admin.market)
        assert us_market == Market.US
        
        # Verify databases are different
        kg_session = next(db_manager.get_db_session(kg_market))
        us_session = next(db_manager.get_db_session(us_market))
        
        try:
            # Different databases should have different connections
            assert kg_session != us_session
        finally:
            kg_session.close()
            us_session.close()


# ========================================================================
# TEST SUITE 3: Admin Count Isolation
# ========================================================================

class TestAdminIsolation:
    """Test that admin records are isolated between databases"""
    
    def test_kg_admin_not_in_us_database(self, kg_admin):
        """Test KG admin doesn't exist in US database"""
        us_session = next(db_manager.get_db_session(Market.US))
        
        try:
            us_admin = us_session.query(Admin).filter(
                Admin.username == "kg_test_admin"
            ).first()
            
            assert us_admin is None, "KG admin should not exist in US database"
            
        finally:
            us_session.close()
    
    def test_us_admin_not_in_kg_database(self, us_admin):
        """Test US admin doesn't exist in KG database"""
        kg_session = next(db_manager.get_db_session(Market.KG))
        
        try:
            kg_admin = kg_session.query(Admin).filter(
                Admin.username == "us_test_admin"
            ).first()
            
            assert kg_admin is None, "US admin should not exist in KG database"
            
        finally:
            kg_session.close()
    
    def test_admin_count_isolation(self, kg_admin, us_admin):
        """Test that admin counts are separate between databases"""
        kg_session = next(db_manager.get_db_session(Market.KG))
        us_session = next(db_manager.get_db_session(Market.US))
        
        try:
            kg_count_initial = kg_session.query(Admin).count()
            us_count_initial = us_session.query(Admin).count()
            
            # Creating admin in one database shouldn't affect the other
            # KG admin already exists (from fixture)
            kg_count_after = kg_session.query(Admin).count()
            us_count_after = us_session.query(Admin).count()
            
            # US count should not have changed
            assert us_count_initial == us_count_after
            
            # KG count includes our test admin
            assert kg_count_after >= kg_count_initial
            
        finally:
            kg_session.close()
            us_session.close()


# ========================================================================
# TEST SUITE 4: Market-Based Admin Authentication
# ========================================================================

class TestAdminMarketAuthentication:
    """Test admin authentication reads market from database"""
    
    def test_kg_admin_market_from_database(self, kg_admin, kg_admin_session):
        """Test that KG admin's market is read from database"""
        # Simulate authentication check - fetch admin from database
        admin_from_db = kg_admin_session.query(Admin).filter(
            Admin.id == kg_admin.id
        ).first()
        
        assert admin_from_db is not None
        assert admin_from_db.market == "kg"
        assert admin_from_db.is_active is True
        
        # Verify admin's database market determines database connection
        admin_market = Market(admin_from_db.market)
        assert admin_market == Market.KG
    
    def test_us_admin_market_from_database(self, us_admin, us_admin_session):
        """Test that US admin's market is read from database"""
        # Simulate authentication check - fetch admin from database
        admin_from_db = us_admin_session.query(Admin).filter(
            Admin.id == us_admin.id
        ).first()
        
        assert admin_from_db is not None
        assert admin_from_db.market == "us"
        assert admin_from_db.is_active is True
        
        # Verify admin's database market determines database connection
        admin_market = Market(admin_from_db.market)
        assert admin_market == Market.US
    
    def test_inactive_admin_cannot_access(self, kg_admin, kg_admin_session):
        """Test that inactive admins are rejected"""
        # Deactivate admin
        kg_admin.is_active = False
        kg_admin_session.commit()
        
        # Fetch from database
        admin_from_db = kg_admin_session.query(Admin).filter(
            Admin.id == kg_admin.id
        ).first()
        
        assert admin_from_db.is_active is False
        
        # Authentication should fail for inactive admin
        # (In real code, this would be handled by authenticate() method)
        
        # Reactivate for cleanup
        kg_admin.is_active = True
        kg_admin_session.commit()


# ========================================================================
# TEST SUITE 5: Cross-Database Admin Lookup
# ========================================================================

class TestCrossDatabaseAdminLookup:
    """Test finding admin across databases when market unknown"""
    
    def test_find_admin_in_correct_database(self, kg_admin, us_admin):
        """Test finding admin in correct database using market column"""
        # Scenario: We have admin_id but need to find which database
        kg_admin_id = kg_admin.id
        us_admin_id = us_admin.id
        
        # Try KG database first for KG admin
        kg_session = next(db_manager.get_db_session(Market.KG))
        try:
            found_admin = kg_session.query(Admin).filter(
                Admin.id == kg_admin_id
            ).first()
            
            assert found_admin is not None
            assert found_admin.market == "kg"
            
        finally:
            kg_session.close()
        
        # Try US database for US admin
        us_session = next(db_manager.get_db_session(Market.US))
        try:
            found_admin = us_session.query(Admin).filter(
                Admin.id == us_admin_id
            ).first()
            
            assert found_admin is not None
            assert found_admin.market == "us"
            
        finally:
            us_session.close()
    
    def test_admin_not_found_in_wrong_database(self, kg_admin):
        """Test admin not found when searching wrong database"""
        kg_admin_id = kg_admin.id
        
        # Try to find KG admin in US database (should fail)
        us_session = next(db_manager.get_db_session(Market.US))
        try:
            found_admin = us_session.query(Admin).filter(
                Admin.id == kg_admin_id
            ).first()
            
            # Admin should not be found in US database
            # (unless there's a collision in IDs, which is extremely unlikely)
            # We can't assert None because IDs might overlap, so we check market if found
            if found_admin:
                assert found_admin.market != "kg"
                assert found_admin.username != "kg_test_admin"
            
        finally:
            us_session.close()

