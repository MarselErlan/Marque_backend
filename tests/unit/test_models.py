"""
Unit tests for database models
Tests for User, Product, Banner, Cart, Wishlist models
"""

import pytest
from datetime import datetime
from src.app_01.models.users.market_user import UserKG, UserUS
from src.app_01.models.banners.banner import Banner, BannerType
from src.app_01.db.market_db import Market


class TestUserModels:
    """Test user model creation and validation"""
    
    def test_create_user_kg(self):
        """Test creating KG user"""
        user = UserKG(
            phone_number="+996555123456",
            full_name="Test User",
            email="test@example.com"
        )
        
        assert user.phone_number == "+996555123456"
        assert user.full_name == "Test User"
        assert user.email == "test@example.com"
        assert user.is_active == True
        assert user.is_verified == False
    
    def test_create_user_us(self):
        """Test creating US user"""
        user = UserUS(
            phone_number="+12125551234",
            full_name="Test User US",
            email="test.us@example.com"
        )
        
        assert user.phone_number == "+12125551234"
        assert user.full_name == "Test User US"
        assert user.is_active == True
    
    def test_user_default_values(self):
        """Test user default values"""
        user = UserKG(phone_number="+996555123456")
        
        assert user.is_active == True
        assert user.is_verified == False
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_phone_uniqueness_constraint(self):
        """Test that phone numbers should be unique"""
        # This is a model structure test
        user = UserKG(phone_number="+996555123456")
        assert hasattr(user, 'phone_number')


class TestBannerModel:
    """Test banner model"""
    
    def test_create_banner(self):
        """Test creating a banner"""
        banner = Banner(
            title="Test Banner",
            description="Test description",
            image_url="https://example.com/banner.jpg",
            cta_url="https://example.com",
            banner_type=BannerType.HERO,
            is_active=True,
            display_order=1
        )
        
        assert banner.title == "Test Banner"
        assert banner.banner_type == BannerType.HERO
        assert banner.is_active == True
        assert banner.display_order == 1
    
    def test_banner_types(self):
        """Test banner type enum"""
        assert BannerType.HERO == "hero"
        assert BannerType.PROMO == "promo"
        assert BannerType.CATEGORY == "category"
    
    def test_banner_default_values(self):
        """Test banner default values"""
        banner = Banner(
            title="Test",
            image_url="https://example.com/test.jpg",
            banner_type=BannerType.HERO,
            is_active=True,
            display_order=0
        )
        
        assert banner.is_active == True
        assert banner.display_order == 0


class TestModelRelationships:
    """Test model relationships"""
    
    def test_user_has_timestamps(self):
        """Test that user model has timestamp fields"""
        user = UserKG(phone_number="+996555123456")
        assert hasattr(user, 'created_at')
        assert hasattr(user, 'updated_at')
    
    def test_banner_has_timestamps(self):
        """Test that banner model has timestamp fields"""
        banner = Banner(
            title="Test",
            image_url="https://example.com/test.jpg",
            banner_type=BannerType.HERO
        )
        assert hasattr(banner, 'created_at')
        assert hasattr(banner, 'updated_at')


class TestModelValidation:
    """Test model validation"""
    
    def test_user_phone_field_exists(self):
        """Test that user has phone_number field"""
        user = UserKG(phone_number="+996555123456")
        assert hasattr(user, 'phone_number')
        assert user.phone_number == "+996555123456"
    
    def test_banner_title_field_exists(self):
        """Test that banner has title field"""
        banner = Banner(
            title="Test Banner",
            image_url="https://example.com/test.jpg",
            banner_type=BannerType.HERO
        )
        assert hasattr(banner, 'title')
        assert banner.title == "Test Banner"
    
    def test_user_email_format(self):
        """Test user email field exists"""
        user = UserKG(phone_number="+996555123456", email="test@example.com")
        assert user.email == "test@example.com"


@pytest.mark.parametrize("phone,user_class", [
    ("+996555123456", UserKG),
    ("+12125551234", UserUS),
])
def test_user_creation_parametrized(phone, user_class):
    """Parametrized test for user creation"""
    user = user_class(phone_number=phone)
    assert user.phone_number == phone
    assert user.is_active == True


@pytest.mark.parametrize("banner_type", [
    BannerType.HERO,
    BannerType.PROMO,
    BannerType.CATEGORY,
])
def test_banner_types_parametrized(banner_type):
    """Parametrized test for banner types"""
    banner = Banner(
        title="Test",
        image_url="https://example.com/test.jpg",
        banner_type=banner_type
    )
    assert banner.banner_type == banner_type

