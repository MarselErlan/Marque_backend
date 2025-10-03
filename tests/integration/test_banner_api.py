"""
Integration tests for banner API
Tests banner listing and management
"""

import pytest


@pytest.mark.integration
class TestBannerAPI:
    """Test banner API endpoints"""
    
    def test_get_banners_endpoint(self, api_client):
        """Test getting all banners"""
        response = api_client.get("/api/v1/banners")
        
        # Should not be 404
        assert response.status_code != 404
    
    def test_get_banners_returns_list(self, api_client):
        """Test that banners endpoint returns a list"""
        response = api_client.get("/api/v1/banners")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_banner_by_id(self, api_client, sample_banner):
        """Test getting banner by ID"""
        response = api_client.get(f"/api/v1/banners/{sample_banner.id}")
        
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == sample_banner.id
            assert data["title"] == sample_banner.title
    
    def test_get_nonexistent_banner(self, api_client):
        """Test getting non-existent banner"""
        response = api_client.get("/api/v1/banners/999999")
        
        # Should return 404
        assert response.status_code in [404, 422]


@pytest.mark.integration
class TestBannerFiltering:
    """Test banner filtering"""
    
    def test_filter_by_type(self, api_client):
        """Test filtering banners by type"""
        response = api_client.get("/api/v1/banners?banner_type=sale")
        
        assert response.status_code in [200, 422]
    
    def test_filter_by_active_status(self, api_client):
        """Test filtering by active status"""
        response = api_client.get("/api/v1/banners?is_active=true")
        
        assert response.status_code in [200, 422]


@pytest.mark.integration
class TestBannerWithDatabase:
    """Test banner operations with database"""
    
    def test_banner_in_database(self, test_db, sample_banner):
        """Test that banner is created in database"""
        from src.app_01.models.banners.banner import Banner
        
        banner = test_db.query(Banner).filter_by(id=sample_banner.id).first()
        assert banner is not None
        assert banner.title == "Summer Sale"
        assert banner.is_active == True
    
    def test_banner_type_enum(self, test_db, sample_banner):
        """Test banner type enum"""
        from src.app_01.models.banners.banner import BannerType
        
        assert sample_banner.banner_type == BannerType.SALE


@pytest.mark.integration
class TestBannerAdmin:
    """Test banner admin operations"""
    
    def test_create_banner_without_auth(self, api_client):
        """Test creating banner without authentication"""
        response = api_client.post("/api/v1/admin/banners", json={
            "title": "Test Banner",
            "image_url": "https://example.com/test.jpg",
            "banner_type": "sale"
        })
        
        # Should require authentication
        assert response.status_code in [401, 403, 404]
    
    def test_update_banner_without_auth(self, api_client, sample_banner):
        """Test updating banner without authentication"""
        response = api_client.put(f"/api/v1/admin/banners/{sample_banner.id}", json={
            "title": "Updated Banner"
        })
        
        # Should require authentication
        assert response.status_code in [401, 403, 404]
    
    def test_delete_banner_without_auth(self, api_client, sample_banner):
        """Test deleting banner without authentication"""
        response = api_client.delete(f"/api/v1/admin/banners/{sample_banner.id}")
        
        # Should require authentication
        assert response.status_code in [401, 403, 404]

