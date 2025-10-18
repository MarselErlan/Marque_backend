"""
Unit tests for Product Asset API

Tests all 11 endpoints for image/video management:
- Upload images/videos
- Set primary image
- Get product gallery
- Update assets
- Delete/restore assets
- Asset statistics
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from io import BytesIO

from src.app_01.main import app
from src.app_01.db import Base, get_db
from src.app_01.models.products.product import Product
from src.app_01.models.products.product_asset import ProductAsset
from src.app_01.models.products.category import Category
from src.app_01.models.products.brand import Brand

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_product_assets.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create tables before each test, drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_product(setup_database):
    """Create a test product"""
    db = TestingSessionLocal()
    
    # Create category and brand first
    category = Category(name="Test Category", slug="test-category", is_active=True)
    brand = Brand(name="Test Brand", slug="test-brand", is_active=True)
    db.add(category)
    db.add(brand)
    db.commit()
    
    product = Product(
        name="Test Product",
        slug="test-product",
        description="Test description",
        category_id=category.id,
        brand_id=brand.id,
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    yield product
    db.close()


@pytest.fixture
def test_asset(test_product):
    """Create a test product asset"""
    db = TestingSessionLocal()
    
    asset = ProductAsset(
        product_id=test_product.id,
        url="/uploads/products/test-image.jpg",
        type="image",
        alt_text="Test image",
        order=0,
        is_primary=True,
        is_active=True,
        width=1200,
        height=800,
        file_size=250000
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    
    yield asset
    db.close()


class TestProductAssetUpload:
    """Test image/video upload endpoints"""
    
    def test_upload_image_success(self, test_product):
        """Test successful image upload"""
        # Create fake image file
        image_data = BytesIO(b"fake image data")
        
        response = client.post(
            "/api/v1/product-assets/upload",
            data={
                "product_id": test_product.id,
                "asset_type": "image",
                "alt_text": "New product image",
                "order": 0,
                "is_primary": True
            },
            files={"file": ("test.jpg", image_data, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == test_product.id
        assert data["type"] == "image"
        assert data["alt_text"] == "New product image"
        assert data["is_primary"] is True
    
    def test_upload_image_invalid_product(self):
        """Test upload with non-existent product"""
        image_data = BytesIO(b"fake image data")
        
        response = client.post(
            "/api/v1/product-assets/upload",
            data={
                "product_id": 99999,
                "asset_type": "image"
            },
            files={"file": ("test.jpg", image_data, "image/jpeg")}
        )
        
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]
    
    def test_upload_video_success(self, test_product):
        """Test successful video upload"""
        video_data = BytesIO(b"fake video data")
        
        response = client.post(
            "/api/v1/product-assets/upload",
            data={
                "product_id": test_product.id,
                "asset_type": "video",
                "alt_text": "Product video",
                "order": 1
            },
            files={"file": ("test.mp4", video_data, "video/mp4")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "video"


class TestProductGallery:
    """Test product gallery endpoints"""
    
    def test_get_product_gallery(self, test_product, test_asset):
        """Test getting complete product gallery"""
        response = client.get(f"/api/v1/product-assets/product/{test_product.id}/gallery")
        
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == test_product.id
        assert data["product_name"] == test_product.name
        assert data["primary_image"] is not None
        assert data["primary_image"]["id"] == test_asset.id
        assert len(data["all_images"]) >= 1
        assert data["total_assets"] >= 1
    
    def test_get_gallery_invalid_product(self):
        """Test gallery for non-existent product"""
        response = client.get("/api/v1/product-assets/product/99999/gallery")
        
        assert response.status_code == 404
    
    def test_get_gallery_with_inactive_assets(self, test_product):
        """Test gallery with include_inactive parameter"""
        db = TestingSessionLocal()
        
        # Create inactive asset
        inactive_asset = ProductAsset(
            product_id=test_product.id,
            url="/test-inactive.jpg",
            type="image",
            is_active=False
        )
        db.add(inactive_asset)
        db.commit()
        
        # Without inactive
        response = client.get(f"/api/v1/product-assets/product/{test_product.id}/gallery")
        data = response.json()
        inactive_count_default = len([img for img in data["all_images"] if not img["is_active"]])
        assert inactive_count_default == 0
        
        # With inactive
        response = client.get(
            f"/api/v1/product-assets/product/{test_product.id}/gallery?include_inactive=true"
        )
        data = response.json()
        total_count = len(data["all_images"])
        assert total_count >= 1


class TestPrimaryImage:
    """Test primary image management"""
    
    def test_set_primary_image(self, test_product, test_asset):
        """Test setting an asset as primary"""
        db = TestingSessionLocal()
        
        # Create another asset
        new_asset = ProductAsset(
            product_id=test_product.id,
            url="/test-new.jpg",
            type="image",
            is_primary=False
        )
        db.add(new_asset)
        db.commit()
        db.refresh(new_asset)
        
        # Set new asset as primary
        response = client.patch(f"/api/v1/product-assets/{new_asset.id}/set-primary")
        
        assert response.status_code == 200
        assert "primary" in response.json()["message"].lower()
        
        # Verify old primary is no longer primary
        db.refresh(test_asset)
        assert test_asset.is_primary is False
        
        # Verify new asset is primary
        db.refresh(new_asset)
        assert new_asset.is_primary is True
    
    def test_set_primary_invalid_asset(self):
        """Test setting non-existent asset as primary"""
        response = client.patch("/api/v1/product-assets/99999/set-primary")
        
        assert response.status_code == 404
    
    def test_set_primary_video_fails(self, test_product):
        """Test that videos cannot be set as primary"""
        db = TestingSessionLocal()
        
        video = ProductAsset(
            product_id=test_product.id,
            url="/test-video.mp4",
            type="video"
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        
        response = client.patch(f"/api/v1/product-assets/{video.id}/set-primary")
        
        assert response.status_code == 400
        assert "Only images" in response.json()["detail"]


class TestAssetUpdate:
    """Test asset update operations"""
    
    def test_update_asset_alt_text(self, test_asset):
        """Test updating asset alt text"""
        response = client.patch(
            f"/api/v1/product-assets/{test_asset.id}",
            json={"alt_text": "Updated alt text"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["alt_text"] == "Updated alt text"
    
    def test_update_asset_order(self, test_asset):
        """Test updating asset display order"""
        response = client.patch(
            f"/api/v1/product-assets/{test_asset.id}",
            json={"order": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["order"] == 5
    
    def test_update_asset_active_status(self, test_asset):
        """Test deactivating asset"""
        response = client.patch(
            f"/api/v1/product-assets/{test_asset.id}",
            json={"is_active": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
    
    def test_update_multiple_fields(self, test_asset):
        """Test updating multiple fields at once"""
        response = client.patch(
            f"/api/v1/product-assets/{test_asset.id}",
            json={
                "alt_text": "New alt text",
                "order": 10,
                "is_active": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["alt_text"] == "New alt text"
        assert data["order"] == 10
        assert data["is_active"] is False


class TestAssetDelete:
    """Test asset deletion"""
    
    def test_soft_delete_asset(self, test_asset):
        """Test soft delete (deactivate)"""
        response = client.delete(f"/api/v1/product-assets/{test_asset.id}")
        
        assert response.status_code == 200
        assert "deactivated" in response.json()["message"]
        
        # Verify asset still exists but is inactive
        db = TestingSessionLocal()
        db_asset = db.query(ProductAsset).filter(ProductAsset.id == test_asset.id).first()
        assert db_asset is not None
        assert db_asset.is_active is False
    
    def test_hard_delete_asset(self, test_asset):
        """Test permanent deletion"""
        response = client.delete(
            f"/api/v1/product-assets/{test_asset.id}?hard_delete=true"
        )
        
        assert response.status_code == 200
        assert "permanently deleted" in response.json()["message"]
        
        # Verify asset no longer exists
        db = TestingSessionLocal()
        db_asset = db.query(ProductAsset).filter(ProductAsset.id == test_asset.id).first()
        assert db_asset is None
    
    def test_delete_invalid_asset(self):
        """Test deleting non-existent asset"""
        response = client.delete("/api/v1/product-assets/99999")
        
        assert response.status_code == 404


class TestAssetRestore:
    """Test asset restoration"""
    
    def test_restore_deactivated_asset(self, test_asset):
        """Test restoring a soft-deleted asset"""
        # First deactivate
        client.delete(f"/api/v1/product-assets/{test_asset.id}")
        
        # Then restore
        response = client.post(f"/api/v1/product-assets/{test_asset.id}/restore")
        
        assert response.status_code == 200
        assert "restored" in response.json()["message"]
        
        # Verify asset is active again
        db = TestingSessionLocal()
        db_asset = db.query(ProductAsset).filter(ProductAsset.id == test_asset.id).first()
        assert db_asset.is_active is True
    
    def test_restore_invalid_asset(self):
        """Test restoring non-existent asset"""
        response = client.post("/api/v1/product-assets/99999/restore")
        
        assert response.status_code == 404


class TestAssetStatistics:
    """Test asset statistics"""
    
    def test_get_asset_stats(self, test_product, test_asset):
        """Test getting asset statistics"""
        db = TestingSessionLocal()
        
        # Create more assets
        for i in range(3):
            asset = ProductAsset(
                product_id=test_product.id,
                url=f"/test-{i}.jpg",
                type="image",
                file_size=100000 * (i + 1)
            )
            db.add(asset)
        
        video = ProductAsset(
            product_id=test_product.id,
            url="/test-video.mp4",
            type="video",
            file_size=500000
        )
        db.add(video)
        db.commit()
        
        response = client.get("/api/v1/product-assets/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_images"] >= 4
        assert data["total_videos"] >= 1
        assert data["total_assets"] >= 5
        assert data["total_file_size_bytes"] > 0
        assert data["total_file_size_mb"] > 0
        assert data["average_file_size_bytes"] > 0


class TestAssetProperties:
    """Test ProductAsset model properties"""
    
    def test_aspect_ratio_property(self, test_asset):
        """Test aspect ratio calculation"""
        db = TestingSessionLocal()
        db_asset = db.query(ProductAsset).filter(ProductAsset.id == test_asset.id).first()
        
        # test_asset has width=1200, height=800
        expected_ratio = 1200 / 800
        assert db_asset.aspect_ratio == round(expected_ratio, 2)
    
    def test_is_landscape_property(self, test_asset):
        """Test landscape detection"""
        db = TestingSessionLocal()
        db_asset = db.query(ProductAsset).filter(ProductAsset.id == test_asset.id).first()
        
        # test_asset has width=1200, height=800 (landscape)
        assert db_asset.is_landscape is True
        assert db_asset.is_portrait is False
    
    def test_is_portrait_property(self, test_product):
        """Test portrait detection"""
        db = TestingSessionLocal()
        
        portrait_asset = ProductAsset(
            product_id=test_product.id,
            url="/portrait.jpg",
            type="image",
            width=800,
            height=1200
        )
        db.add(portrait_asset)
        db.commit()
        db.refresh(portrait_asset)
        
        assert portrait_asset.is_portrait is True
        assert portrait_asset.is_landscape is False
    
    def test_file_size_mb_property(self, test_asset):
        """Test file size in MB"""
        db = TestingSessionLocal()
        db_asset = db.query(ProductAsset).filter(ProductAsset.id == test_asset.id).first()
        
        # test_asset has file_size=250000 bytes
        expected_mb = 250000 / (1024 * 1024)
        assert db_asset.file_size_mb == round(expected_mb, 2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

