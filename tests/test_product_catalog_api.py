"""
Unit tests for Product Catalog API

Tests all 18 endpoints for catalog management:
- Attributes (sizes, colors, brands)
- Filters
- Seasons
- Materials
- Styles
- Catalog overview
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app_01.main import app
from src.app_01.db import Base, get_db
# Import all models to ensure they're registered with Base
from src.app_01.models import (
    Product, ProductAsset, Category, Subcategory, Brand, SKU, Review,
    ProductAttribute, ProductFilter, ProductSeason, ProductMaterial,
    ProductStyle, ProductDiscount, ProductSearch
)

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_product_catalog.db"
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
def sample_attributes():
    """Create sample product attributes"""
    db = TestingSessionLocal()
    
    # Sizes
    sizes = [
        ProductAttribute(attribute_type="size", attribute_value="S", display_name="Small", usage_count=10, is_featured=True),
        ProductAttribute(attribute_type="size", attribute_value="M", display_name="Medium", usage_count=20),
        ProductAttribute(attribute_type="size", attribute_value="L", display_name="Large", usage_count=15),
    ]
    
    # Colors
    colors = [
        ProductAttribute(attribute_type="color", attribute_value="red", display_name="Red", usage_count=25, is_featured=True),
        ProductAttribute(attribute_type="color", attribute_value="blue", display_name="Blue", usage_count=18),
        ProductAttribute(attribute_type="color", attribute_value="black", display_name="Black", usage_count=30),
    ]
    
    # Brands
    brands = [
        ProductAttribute(attribute_type="brand", attribute_value="nike", display_name="Nike", usage_count=50, is_featured=True),
        ProductAttribute(attribute_type="brand", attribute_value="adidas", display_name="Adidas", usage_count=40),
    ]
    
    for attr in sizes + colors + brands:
        db.add(attr)
    
    db.commit()
    db.close()
    
    return {"sizes": len(sizes), "colors": len(colors), "brands": len(brands)}


@pytest.fixture
def sample_seasons():
    """Create sample seasons"""
    db = TestingSessionLocal()
    
    seasons = [
        ProductSeason(name="Лето", slug="summer", product_count=50, is_featured=True, is_active=True),
        ProductSeason(name="Зима", slug="winter", product_count=30, is_featured=False, is_active=True),
        ProductSeason(name="Мульти", slug="multi", product_count=40, is_featured=True, is_active=True),
    ]
    
    for season in seasons:
        db.add(season)
    
    db.commit()
    db.close()
    
    return len(seasons)


@pytest.fixture
def sample_materials():
    """Create sample materials"""
    db = TestingSessionLocal()
    
    materials = [
        ProductMaterial(name="Хлопок", slug="cotton", product_count=60, is_featured=True, is_active=True),
        ProductMaterial(name="Полиэстер", slug="polyester", product_count=45, is_featured=False, is_active=True),
        ProductMaterial(name="Шерсть", slug="wool", product_count=20, is_featured=True, is_active=True),
    ]
    
    for material in materials:
        db.add(material)
    
    db.commit()
    db.close()
    
    return len(materials)


@pytest.fixture
def sample_styles():
    """Create sample styles"""
    db = TestingSessionLocal()
    
    styles = [
        ProductStyle(name="Спортивный", slug="sport", product_count=70, is_featured=True, is_active=True),
        ProductStyle(name="Классический", slug="classic", product_count=50, is_featured=False, is_active=True),
        ProductStyle(name="Повседневный", slug="casual", product_count=65, is_featured=True, is_active=True),
    ]
    
    for style in styles:
        db.add(style)
    
    db.commit()
    db.close()
    
    return len(styles)


@pytest.fixture
def sample_filters():
    """Create sample filters"""
    db = TestingSessionLocal()
    
    filters = [
        ProductFilter(filter_type="size", filter_value="XL", display_name="Extra Large", usage_count=15),
        ProductFilter(filter_type="color", filter_value="green", display_name="Green", usage_count=12),
        ProductFilter(filter_type="price_range", filter_value="0-1000", display_name="Under 1000", usage_count=50),
    ]
    
    for f in filters:
        db.add(f)
    
    db.commit()
    db.close()
    
    return len(filters)


class TestAttributesAPI:
    """Test product attributes endpoints"""
    
    def test_get_all_sizes(self, sample_attributes):
        """Test getting all sizes"""
        response = client.get("/api/v1/catalog/attributes/sizes")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == sample_attributes["sizes"]
        assert all(attr["attribute_type"] == "size" for attr in data)
    
    def test_get_featured_sizes_only(self, sample_attributes):
        """Test getting only featured sizes"""
        response = client.get("/api/v1/catalog/attributes/sizes?featured_only=true")
        
        assert response.status_code == 200
        data = response.json()
        assert all(attr["is_featured"] is True for attr in data)
        assert len(data) >= 1
    
    def test_get_all_colors(self, sample_attributes):
        """Test getting all colors"""
        response = client.get("/api/v1/catalog/attributes/colors")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == sample_attributes["colors"]
        assert all(attr["attribute_type"] == "color" for attr in data)
    
    def test_get_featured_colors_only(self, sample_attributes):
        """Test getting only featured colors"""
        response = client.get("/api/v1/catalog/attributes/colors?featured_only=true")
        
        assert response.status_code == 200
        data = response.json()
        assert all(attr["is_featured"] is True for attr in data)
    
    def test_get_all_brands(self, sample_attributes):
        """Test getting all brand attributes"""
        response = client.get("/api/v1/catalog/attributes/brands")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == sample_attributes["brands"]
        assert all(attr["attribute_type"] == "brand" for attr in data)
    
    def test_get_most_used_attributes(self, sample_attributes):
        """Test getting most used attributes"""
        response = client.get("/api/v1/catalog/attributes/most-used/color?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
        # Should be sorted by usage_count descending
        if len(data) >= 2:
            assert data[0]["usage_count"] >= data[1]["usage_count"]


class TestFiltersAPI:
    """Test product filters endpoints"""
    
    def test_get_filters_by_type(self, sample_filters):
        """Test getting filters by type"""
        response = client.get("/api/v1/catalog/filters/size")
        
        assert response.status_code == 200
        data = response.json()
        assert all(f["filter_type"] == "size" for f in data)
    
    def test_get_popular_filters(self, sample_filters):
        """Test getting popular filters"""
        response = client.get("/api/v1/catalog/filters/popular/price_range?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        # Should be sorted by usage_count descending
        if len(data) >= 2:
            assert data[0]["usage_count"] >= data[1]["usage_count"]
    
    def test_get_all_filter_types(self, sample_filters):
        """Test getting all filter types"""
        response = client.get("/api/v1/catalog/filters")
        
        assert response.status_code == 200
        data = response.json()
        assert "filter_types" in data
        assert "count" in data
        assert isinstance(data["filter_types"], list)


class TestSeasonsAPI:
    """Test seasons endpoints"""
    
    def test_get_all_seasons(self, sample_seasons):
        """Test getting all seasons"""
        response = client.get("/api/v1/catalog/seasons")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == sample_seasons
        assert all(s["is_active"] is True for s in data)
    
    def test_get_featured_seasons_only(self, sample_seasons):
        """Test getting only featured seasons"""
        response = client.get("/api/v1/catalog/seasons?featured_only=true")
        
        assert response.status_code == 200
        data = response.json()
        assert all(s["is_featured"] is True for s in data)
        assert len(data) >= 1
    
    def test_get_popular_seasons(self, sample_seasons):
        """Test getting seasons by popularity"""
        response = client.get("/api/v1/catalog/seasons/popular?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
        # Should be sorted by product_count descending
        if len(data) >= 2:
            assert data[0]["product_count"] >= data[1]["product_count"]
    
    def test_get_season_by_slug(self, sample_seasons):
        """Test getting season by slug"""
        response = client.get("/api/v1/catalog/seasons/summer")
        
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "summer"
        assert data["name"] == "Лето"
    
    def test_get_season_by_invalid_slug(self):
        """Test getting season with invalid slug"""
        response = client.get("/api/v1/catalog/seasons/invalid-season")
        
        assert response.status_code == 404


class TestMaterialsAPI:
    """Test materials endpoints"""
    
    def test_get_all_materials(self, sample_materials):
        """Test getting all materials"""
        response = client.get("/api/v1/catalog/materials")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == sample_materials
    
    def test_get_featured_materials_only(self, sample_materials):
        """Test getting only featured materials"""
        response = client.get("/api/v1/catalog/materials?featured_only=true")
        
        assert response.status_code == 200
        data = response.json()
        assert all(m["is_featured"] is True for m in data)
    
    def test_get_popular_materials(self, sample_materials):
        """Test getting materials by popularity"""
        response = client.get("/api/v1/catalog/materials/popular?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
        # Should be sorted by product_count descending
        if len(data) >= 2:
            assert data[0]["product_count"] >= data[1]["product_count"]
    
    def test_get_material_by_slug(self, sample_materials):
        """Test getting material by slug"""
        response = client.get("/api/v1/catalog/materials/cotton")
        
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "cotton"
        assert data["name"] == "Хлопок"
    
    def test_get_material_by_invalid_slug(self):
        """Test getting material with invalid slug"""
        response = client.get("/api/v1/catalog/materials/invalid-material")
        
        assert response.status_code == 404


class TestStylesAPI:
    """Test styles endpoints"""
    
    def test_get_all_styles(self, sample_styles):
        """Test getting all styles"""
        response = client.get("/api/v1/catalog/styles")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == sample_styles
    
    def test_get_featured_styles_only(self, sample_styles):
        """Test getting only featured styles"""
        response = client.get("/api/v1/catalog/styles?featured_only=true")
        
        assert response.status_code == 200
        data = response.json()
        assert all(s["is_featured"] is True for s in data)
    
    def test_get_popular_styles(self, sample_styles):
        """Test getting styles by popularity"""
        response = client.get("/api/v1/catalog/styles/popular?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
        # Should be sorted by product_count descending
        if len(data) >= 2:
            assert data[0]["product_count"] >= data[1]["product_count"]
    
    def test_get_style_by_slug(self, sample_styles):
        """Test getting style by slug"""
        response = client.get("/api/v1/catalog/styles/sport")
        
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "sport"
        assert data["name"] == "Спортивный"
    
    def test_get_style_by_invalid_slug(self):
        """Test getting style with invalid slug"""
        response = client.get("/api/v1/catalog/styles/invalid-style")
        
        assert response.status_code == 404


class TestCatalogOverview:
    """Test catalog overview endpoint"""
    
    def test_get_catalog_overview(self, sample_attributes, sample_seasons, sample_materials, sample_styles):
        """Test getting complete catalog overview"""
        response = client.get("/api/v1/catalog/overview")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "attributes" in data
        assert "seasons" in data
        assert "materials" in data
        assert "styles" in data
        
        # Check attributes
        assert "total_sizes" in data["attributes"]
        assert "total_colors" in data["attributes"]
        assert "total_brands" in data["attributes"]
        assert data["attributes"]["total_sizes"] == sample_attributes["sizes"]
        
        # Check seasons
        assert "total" in data["seasons"]
        assert "featured" in data["seasons"]
        assert data["seasons"]["total"] == sample_seasons
        
        # Check materials
        assert data["materials"]["total"] == sample_materials
        
        # Check styles
        assert data["styles"]["total"] == sample_styles
    
    def test_catalog_overview_empty_database(self):
        """Test catalog overview with empty database"""
        response = client.get("/api/v1/catalog/overview")
        
        assert response.status_code == 200
        data = response.json()
        assert data["attributes"]["total_sizes"] == 0
        assert data["seasons"]["total"] == 0


class TestAttributeTracking:
    """Test attribute usage tracking"""
    
    def test_increment_attribute_usage(self):
        """Test incrementing attribute usage count"""
        db = TestingSessionLocal()
        
        attr = ProductAttribute(
            attribute_type="size",
            attribute_value="M",
            display_name="Medium",
            usage_count=5
        )
        db.add(attr)
        db.commit()
        db.refresh(attr)
        
        # Increment usage
        attr.increment_usage()
        db.commit()
        db.refresh(attr)
        
        assert attr.usage_count == 6
        db.close()
    
    def test_decrement_attribute_usage(self):
        """Test decrementing attribute usage count"""
        db = TestingSessionLocal()
        
        attr = ProductAttribute(
            attribute_type="size",
            attribute_value="L",
            display_name="Large",
            usage_count=10
        )
        db.add(attr)
        db.commit()
        db.refresh(attr)
        
        # Decrement usage
        attr.decrement_usage()
        db.commit()
        db.refresh(attr)
        
        assert attr.usage_count == 9
        db.close()
    
    def test_decrement_usage_at_zero(self):
        """Test that usage count doesn't go below zero"""
        db = TestingSessionLocal()
        
        attr = ProductAttribute(
            attribute_type="size",
            attribute_value="S",
            display_name="Small",
            usage_count=0
        )
        db.add(attr)
        db.commit()
        db.refresh(attr)
        
        # Try to decrement
        attr.decrement_usage()
        db.commit()
        db.refresh(attr)
        
        assert attr.usage_count == 0  # Should stay at 0
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

