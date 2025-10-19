"""
Tests for Admin Product Form with Enhanced Fields
Tests the complete product creation flow with all dropdowns
"""

import pytest
from sqlalchemy.orm import Session
from src.app_01.models.products.product import Product
from src.app_01.models.products.category import Category, Subcategory
from src.app_01.models.products.brand import Brand
from src.app_01.models.products.product_filter import ProductSeason, ProductMaterial, ProductStyle
from src.app_01.admin.multi_market_admin_views import ProductAdmin
from src.app_01.db.market_db import db_manager, Market


class TestAdminProductForm:
    """Test the enhanced product form with all fields"""
    
    @pytest.fixture(scope="function")
    def db(self):
        """Get database session for KG market"""
        SessionLocal = db_manager.get_session_factory(Market.KG)
        session = SessionLocal()
        yield session
        session.close()
    
    @pytest.fixture
    def test_brand(self, db: Session):
        """Create a test brand"""
        brand = db.query(Brand).filter(Brand.slug == "test-brand").first()
        if not brand:
            brand = Brand(
                name="Test Brand",
                slug="test-brand",
                description="Test brand for admin tests"
            )
            db.add(brand)
            db.commit()
            db.refresh(brand)
        return brand
    
    @pytest.fixture
    def test_category(self, db: Session):
        """Create a test category"""
        category = db.query(Category).filter(Category.slug == "test-category").first()
        if not category:
            category = Category(
                name="Test Category",
                slug="test-category",
                description="Test category for admin tests",
                is_active=True
            )
            db.add(category)
            db.commit()
            db.refresh(category)
        return category
    
    @pytest.fixture
    def test_subcategory(self, db: Session, test_category):
        """Create a test subcategory"""
        subcategory = db.query(Subcategory).filter(Subcategory.slug == "test-subcategory").first()
        if not subcategory:
            subcategory = Subcategory(
                name="Test Subcategory",
                slug="test-subcategory",
                description="Test subcategory for admin tests",
                category_id=test_category.id,
                is_active=True
            )
            db.add(subcategory)
            db.commit()
            db.refresh(subcategory)
        return subcategory
    
    @pytest.fixture
    def test_season(self, db: Session):
        """Create a test season"""
        season = db.query(ProductSeason).filter(ProductSeason.slug == "test-season").first()
        if not season:
            season = ProductSeason(
                name="Test Season",
                slug="test-season",
                description="Test season for admin tests"
            )
            db.add(season)
            db.commit()
            db.refresh(season)
        return season
    
    @pytest.fixture
    def test_material(self, db: Session):
        """Create a test material"""
        material = db.query(ProductMaterial).filter(ProductMaterial.slug == "test-material").first()
        if not material:
            material = ProductMaterial(
                name="Test Material",
                slug="test-material",
                description="Test material for admin tests"
            )
            db.add(material)
            db.commit()
            db.refresh(material)
        return material
    
    @pytest.fixture
    def test_style(self, db: Session):
        """Create a test style"""
        style = db.query(ProductStyle).filter(ProductStyle.slug == "test-style").first()
        if not style:
            style = ProductStyle(
                name="Test Style",
                slug="test-style",
                description="Test style for admin tests"
            )
            db.add(style)
            db.commit()
            db.refresh(style)
        return style
    
    def test_product_admin_form_columns(self):
        """Test that ProductAdmin has all required form columns"""
        expected_columns = [
            "title", "slug", "description",
            "brand", "category", "subcategory",
            "season", "material", "style",
            # NOTE: price and stock_quantity are NOT included - they're SKU properties, not Product columns
            "is_active", "is_featured", "attributes",
            "main_image", "additional_images"  # Added image fields
        ]
        
        assert hasattr(ProductAdmin, 'form_columns'), "ProductAdmin should have form_columns"
        assert ProductAdmin.form_columns == expected_columns, \
            f"Form columns mismatch. Expected: {expected_columns}, Got: {ProductAdmin.form_columns}"
    
    def test_product_admin_column_list(self):
        """Test that ProductAdmin column_list includes season, material, style, and image preview"""
        expected_in_list = ["main_image_preview", "season", "material", "style", "is_featured"]
        
        assert hasattr(ProductAdmin, 'column_list'), "ProductAdmin should have column_list"
        
        for field in expected_in_list:
            assert field in ProductAdmin.column_list, \
                f"Field '{field}' should be in column_list. Current list: {ProductAdmin.column_list}"
    
    def test_product_admin_column_details_list(self):
        """Test that ProductAdmin column_details_list includes all important fields"""
        expected_in_details = [
            "season", "material", "style", "is_featured", "attributes",
            "created_at", "updated_at"
        ]
        
        assert hasattr(ProductAdmin, 'column_details_list'), "ProductAdmin should have column_details_list"
        
        for field in expected_in_details:
            assert field in ProductAdmin.column_details_list, \
                f"Field '{field}' should be in column_details_list. Current list: {ProductAdmin.column_details_list}"
    
    def test_product_admin_column_formatters(self):
        """Test that ProductAdmin has formatters for season, material, style, and images"""
        expected_formatters = ["main_image_preview", "assets", "season", "material", "style", "is_featured"]
        
        assert hasattr(ProductAdmin, 'column_formatters'), "ProductAdmin should have column_formatters"
        
        for field in expected_formatters:
            assert field in ProductAdmin.column_formatters, \
                f"Formatter for '{field}' should be in column_formatters"
    
    def test_product_admin_form_args(self):
        """Test that ProductAdmin has form_args for all fields"""
        required_form_args = [
            "title", "slug", "description",
            "brand", "category", "subcategory",
            "season", "material", "style",
            "is_active", "is_featured", "attributes"
        ]
        
        assert hasattr(ProductAdmin, 'form_args'), "ProductAdmin should have form_args"
        
        for field in required_form_args:
            assert field in ProductAdmin.form_args, \
                f"Missing form_args for field: {field}"
            assert "label" in ProductAdmin.form_args[field], \
                f"Missing label in form_args for field: {field}"
    
    def test_create_product_with_all_fields(
        self, db: Session, test_brand, test_category, 
        test_subcategory, test_season, test_material, test_style
    ):
        """Test creating a product with all enhanced fields"""
        
        # Create product with all fields
        product = Product(
            title="Test Product Complete",
            slug="test-product-complete",
            description="Complete product with all fields",
            brand_id=test_brand.id,
            category_id=test_category.id,
            subcategory_id=test_subcategory.id,
            season_id=test_season.id,
            material_id=test_material.id,
            style_id=test_style.id,
            is_active=True,
            is_featured=True,
            attributes={"test": "value"}
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Verify all fields
        assert product.id is not None
        assert product.title == "Test Product Complete"
        assert product.slug == "test-product-complete"
        assert product.description == "Complete product with all fields"
        assert product.brand_id == test_brand.id
        assert product.category_id == test_category.id
        assert product.subcategory_id == test_subcategory.id
        assert product.season_id == test_season.id
        assert product.material_id == test_material.id
        assert product.style_id == test_style.id
        assert product.is_active is True
        assert product.is_featured is True
        assert product.attributes == {"test": "value"}
        
        # Verify relationships work
        assert product.brand.name == "Test Brand"
        assert product.category.name == "Test Category"
        assert product.subcategory.name == "Test Subcategory"
        assert product.season.name == "Test Season"
        assert product.material.name == "Test Material"
        assert product.style.name == "Test Style"
        
        # Cleanup
        db.delete(product)
        db.commit()
    
    def test_create_product_with_optional_fields_null(
        self, db: Session, test_brand, test_category, test_subcategory
    ):
        """Test creating a product with optional fields set to None"""
        
        product = Product(
            title="Test Product Minimal",
            slug="test-product-minimal",
            description="Product with minimal fields",
            brand_id=test_brand.id,
            category_id=test_category.id,
            subcategory_id=test_subcategory.id,
            season_id=None,  # Optional
            material_id=None,  # Optional
            style_id=None,  # Optional
            is_active=True,
            is_featured=False
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Verify product was created
        assert product.id is not None
        assert product.season_id is None
        assert product.material_id is None
        assert product.style_id is None
        
        # Cleanup
        db.delete(product)
        db.commit()
    
    def test_product_admin_column_descriptions(self):
        """Test that ProductAdmin has descriptions for new fields"""
        required_descriptions = [
            "title", "slug", "description",
            "brand", "category", "subcategory",
            "season", "material", "style",
            "is_active", "is_featured", "attributes"
        ]
        
        assert hasattr(ProductAdmin, 'column_descriptions'), \
            "ProductAdmin should have column_descriptions"
        
        for field in required_descriptions:
            assert field in ProductAdmin.column_descriptions, \
                f"Missing description for field: {field}"
    
    def test_lookup_tables_exist(self, db: Session):
        """Test that all lookup tables exist and are accessible"""
        
        # Test ProductSeason table
        seasons = db.query(ProductSeason).all()
        assert isinstance(seasons, list), "ProductSeason table should be accessible"
        
        # Test ProductMaterial table
        materials = db.query(ProductMaterial).all()
        assert isinstance(materials, list), "ProductMaterial table should be accessible"
        
        # Test ProductStyle table
        styles = db.query(ProductStyle).all()
        assert isinstance(styles, list), "ProductStyle table should be accessible"
    
    def test_product_relationships_defined(self):
        """Test that Product model has all required relationships"""
        product = Product(
            title="Test",
            slug="test",
            brand_id=1,
            category_id=1,
            subcategory_id=1
        )
        
        # Check relationships exist
        assert hasattr(product, 'brand'), "Product should have brand relationship"
        assert hasattr(product, 'category'), "Product should have category relationship"
        assert hasattr(product, 'subcategory'), "Product should have subcategory relationship"
        assert hasattr(product, 'season'), "Product should have season relationship"
        assert hasattr(product, 'material'), "Product should have material relationship"
        assert hasattr(product, 'style'), "Product should have style relationship"
    
    def test_form_include_pk_false(self):
        """Test that form_include_pk is set to False"""
        assert hasattr(ProductAdmin, 'form_include_pk'), \
            "ProductAdmin should have form_include_pk"
        assert ProductAdmin.form_include_pk is False, \
            "form_include_pk should be False to exclude primary key from form"


class TestAdminProductFormIntegration:
    """Integration tests for the complete product creation flow"""
    
    @pytest.fixture(scope="function")
    def db(self):
        """Get database session for KG market"""
        SessionLocal = db_manager.get_session_factory(Market.KG)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_complete_product_creation_flow(self, db: Session):
        """Test the complete flow of creating a product through admin"""
        
        # Step 1: Verify we have brands
        brands = db.query(Brand).limit(1).all()
        if not brands:
            pytest.skip("No brands in database. Add brands first.")
        
        # Step 2: Verify we have categories
        categories = db.query(Category).filter(Category.is_active == True).limit(1).all()
        if not categories:
            pytest.skip("No active categories in database. Add categories first.")
        
        # Step 3: Verify we have subcategories
        subcategories = db.query(Subcategory).filter(Subcategory.is_active == True).limit(1).all()
        if not subcategories:
            pytest.skip("No active subcategories in database. Add subcategories first.")
        
        brand = brands[0]
        category = categories[0]
        subcategory = subcategories[0]
        
        # Step 4: Create product
        product = Product(
            title=f"Admin Test Product {db.query(Product).count() + 1}",
            slug=f"admin-test-product-{db.query(Product).count() + 1}",
            description="Product created via admin panel test",
            brand_id=brand.id,
            category_id=category.id,
            subcategory_id=subcategory.id,
            is_active=True,
            is_featured=False
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Step 5: Verify product was created successfully
        assert product.id is not None
        assert product.brand.name == brand.name
        assert product.category.name == category.name
        assert product.subcategory.name == subcategory.name
        
        # Step 6: Verify product can be queried
        queried_product = db.query(Product).filter(Product.id == product.id).first()
        assert queried_product is not None
        assert queried_product.title == product.title
        
        # Cleanup
        db.delete(product)
        db.commit()
        
        print(f"✅ Successfully created and tested product: {product.title}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

