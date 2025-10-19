"""
Unit tests for Pydantic schemas
Tests for request/response validation
"""

import pytest
from pydantic import ValidationError
from src.app_01.schemas.auth import (
    PhoneLoginRequest,
    VerifyCodeRequest,
    UserProfile,
    MarketInfo
)
from src.app_01.schemas.banner import (
    BannerCreate,
    BannerResponse
)
from src.app_01.schemas.product import (
    ProductSchema,
    ProductSearchResponse
)


class TestAuthSchemas:
    """Test authentication schemas"""
    
    def test_phone_login_request_valid(self):
        """Test valid phone login request"""
        request = PhoneLoginRequest(phone="+996555123456")
        assert request.phone == "+996555123456"
    
    def test_phone_login_request_invalid(self):
        """Test invalid phone login request"""
        with pytest.raises(ValidationError):
            PhoneLoginRequest()
    
    def test_verify_code_request_valid(self):
        """Test valid verify code request"""
        request = VerifyCodeRequest(
            phone="+996555123456",
            verification_code="123456"
        )
        assert request.phone == "+996555123456"
        assert request.verification_code == "123456"
    
    def test_verify_code_request_missing_fields(self):
        """Test verify code request with missing fields"""
        with pytest.raises(ValidationError):
            VerifyCodeRequest(phone="+996555123456")


class TestBannerSchemas:
    """Test banner schemas"""
    
    def test_banner_create_valid(self):
        """Test valid banner creation"""
        banner = BannerCreate(
            title="Test Banner",
            description="Test description",
            image_url="https://example.com/banner.jpg",
            banner_type="promo"
        )
        assert banner.title == "Test Banner"
        assert banner.banner_type == "promo"
    
    def test_banner_create_missing_required(self):
        """Test banner creation with missing required fields"""
        with pytest.raises(ValidationError):
            BannerCreate()


class TestProductSchemas:
    """Test product schemas"""
    
    def test_product_schema_valid(self):
        """Test valid product schema"""
        product = ProductSchema(
            id="1",
            name="Test Product",
            brand="Test Brand",
            price=99.99,
            image="https://example.com/image.jpg",
            category="Test Category"
        )
        assert product.id == "1"
        assert product.name == "Test Product"
        assert product.price == 99.99
    
    def test_product_schema_with_defaults(self):
        """Test product schema with default values"""
        product = ProductSchema(
            id="1",
            name="Test",
            brand="Brand",
            price=10.0,
            image="url",
            category="Cat"
        )
        assert product.rating == 0
        assert product.reviews == 0
        assert product.salesCount == 0
        assert product.inStock == True
    
    def test_product_search_response_valid(self):
        """Test valid product search response"""
        response = ProductSearchResponse(
            query="test",
            results=[],
            total=0,
            page=1,
            limit=20,
            total_pages=0,
            has_more=False
        )
        assert response.query == "test"
        assert response.total == 0


@pytest.mark.parametrize("phone", [
    "+996555123456",
    "+996700987654",
    "+12125551234",
])
def test_phone_validation_parametrized(phone):
    """Parametrized test for phone validation"""
    request = PhoneLoginRequest(phone=phone)
    assert request.phone == phone

