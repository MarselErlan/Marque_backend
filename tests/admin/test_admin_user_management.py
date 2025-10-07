"""
Tests for Admin User Management
Testing AdminUserAdmin view
"""

import pytest
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from src.app_01.models.admins.admin import Admin


class TestAdminUserManagementModel:
    """Test Admin model access via admin panel"""
    
    def test_admin_model_exists(self, admin_test_db):
        """Test that Admin model can be accessed"""
        admins = admin_test_db.query(Admin).all()
        assert isinstance(admins, list)
    
    def test_create_admin_user(self, admin_test_db):
        """Test creating an admin user"""
        new_admin = Admin(
            username="testadmin",
            email="testadmin@example.com",
            hashed_password=bcrypt.hash("testpassword123"),
            full_name="Test Admin",
            admin_role="website_content",
            is_active=True,
            is_super_admin=False
        )
        admin_test_db.add(new_admin)
        admin_test_db.commit()
        admin_test_db.refresh(new_admin)
        
        assert new_admin.id is not None
        assert new_admin.username == "testadmin"
        assert new_admin.admin_role == "website_content"
        assert new_admin.is_active is True
    
    def test_update_admin_role(self, admin_test_db):
        """Test updating admin role"""
        admin_user = Admin(
            username="roletest",
            email="roletest@example.com",
            hashed_password=bcrypt.hash("password123"),
            admin_role="order_management",
            is_active=True
        )
        admin_test_db.add(admin_user)
        admin_test_db.commit()
        admin_test_db.refresh(admin_user)
        
        # Update role
        admin_user.admin_role = "super_admin"
        admin_user.is_super_admin = True
        admin_test_db.commit()
        
        updated = admin_test_db.query(Admin).filter(Admin.id == admin_user.id).first()
        assert updated.admin_role == "super_admin"
        assert updated.is_super_admin is True
    
    def test_deactivate_admin(self, admin_test_db):
        """Test deactivating admin account"""
        admin_user = Admin(
            username="deactivate_test",
            email="deactivate@example.com",
            hashed_password=bcrypt.hash("password123"),
            admin_role="website_content",
            is_active=True
        )
        admin_test_db.add(admin_user)
        admin_test_db.commit()
        admin_test_db.refresh(admin_user)
        
        # Deactivate
        admin_user.is_active = False
        admin_test_db.commit()
        
        deactivated = admin_test_db.query(Admin).filter(Admin.id == admin_user.id).first()
        assert deactivated.is_active is False
    
    def test_admin_permissions(self, admin_test_db):
        """Test setting admin permissions"""
        admin_user = Admin(
            username="permissions_test",
            email="permissions@example.com",
            hashed_password=bcrypt.hash("password123"),
            admin_role="website_content",
            permissions='{"products": ["create", "update", "delete"]}',
            is_active=True
        )
        admin_test_db.add(admin_user)
        admin_test_db.commit()
        admin_test_db.refresh(admin_user)
        
        assert admin_user.permissions is not None
        assert "products" in admin_user.permissions
    
    def test_search_admin_by_username(self, admin_test_db):
        """Test searching admins by username"""
        admin_user = Admin(
            username="searchme",
            email="search@example.com",
            hashed_password=bcrypt.hash("password123"),
            admin_role="website_content",
            is_active=True
        )
        admin_test_db.add(admin_user)
        admin_test_db.commit()
        
        found = admin_test_db.query(Admin).filter(
            Admin.username.like("%searchme%")
        ).first()
        
        assert found is not None
        assert found.username == "searchme"
    
    def test_filter_admins_by_role(self, admin_test_db):
        """Test filtering admins by role"""
        # Create admins with different roles
        admin1 = Admin(
            username="admin1",
            email="admin1@example.com",
            hashed_password=bcrypt.hash("password123"),
            admin_role="order_management",
            is_active=True
        )
        admin2 = Admin(
            username="admin2",
            email="admin2@example.com",
            hashed_password=bcrypt.hash("password123"),
            admin_role="order_management",
            is_active=True
        )
        admin_test_db.add_all([admin1, admin2])
        admin_test_db.commit()
        
        # Filter
        order_admins = admin_test_db.query(Admin).filter(
            Admin.admin_role == "order_management"
        ).all()
        
        assert len(order_admins) >= 2
        assert all(a.admin_role == "order_management" for a in order_admins)
    
    def test_password_is_hashed(self, admin_test_db):
        """Test that passwords are stored hashed"""
        plain_password = "mySecurePassword123"
        admin_user = Admin(
            username="hashtest",
            email="hashtest@example.com",
            hashed_password=bcrypt.hash(plain_password),
            admin_role="website_content",
            is_active=True
        )
        admin_test_db.add(admin_user)
        admin_test_db.commit()
        admin_test_db.refresh(admin_user)
        
        # Password should be hashed (not plain text)
        assert admin_user.hashed_password != plain_password
        assert admin_user.hashed_password.startswith("$2b$")
        
        # Verify password
        assert bcrypt.verify(plain_password, admin_user.hashed_password)
    
    def test_admin_properties(self, admin_test_db):
        """Test admin model properties"""
        # Test order management admin
        order_admin = Admin(
            username="orderadmin",
            email="order@example.com",
            hashed_password=bcrypt.hash("password123"),
            admin_role="order_management",
            is_super_admin=False,
            is_active=True
        )
        admin_test_db.add(order_admin)
        admin_test_db.commit()
        admin_test_db.refresh(order_admin)
        
        assert order_admin.is_order_management_admin is True
        assert order_admin.is_website_content_admin is False
        
        # Test super admin
        super_admin = Admin(
            username="superadmin",
            email="super@example.com",
            hashed_password=bcrypt.hash("password123"),
            admin_role="super_admin",
            is_super_admin=True,
            is_active=True
        )
        admin_test_db.add(super_admin)
        admin_test_db.commit()
        admin_test_db.refresh(super_admin)
        
        # Super admin should have all permissions
        assert super_admin.is_order_management_admin is True
        assert super_admin.is_website_content_admin is True


# Mark all tests as admin tests
pytestmark = pytest.mark.admin

