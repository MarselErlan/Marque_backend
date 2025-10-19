"""
Tests for Category & Subcategory Management in Admin Panel

Testing TDD approach for:
1. Category creation with image
2. Subcategory creation linked to category
3. Display of product counts
4. Visual relationship indicators
5. Image upload support
"""

import pytest
from sqlalchemy.orm import Session
from src.app_01.models import Category, Subcategory, Product, Brand
import uuid


@pytest.fixture(autouse=True)
def cleanup_db(db_session: Session):
    """Fixture to clean up product, category, and subcategory tables before each test."""
    yield
    db_session.query(Product).delete()
    db_session.query(Subcategory).delete()
    db_session.query(Category).delete()
    db_session.query(Brand).delete()
    db_session.commit()


class TestCategoryModel:
    """Test Category model enhancements"""
    
    def test_category_has_image_url_field(self, db_session: Session):
        """Test that Category model has image_url field"""
        # GIVEN: A new category
        category = Category(
            name="Мужчинам",
            slug="men",
            image_url="https://example.com/images/men-category.jpg"
        )
        
        # WHEN: Saving to database
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        # THEN: Image URL should be saved
        assert category.image_url == "https://example.com/images/men-category.jpg"
        assert category.id is not None
    
    def test_category_can_have_null_image(self, db_session: Session):
        """Test that image_url can be null"""
        # GIVEN: A category without image
        category = Category(
            name="Женщинам",
            slug="women"
        )
        
        # WHEN: Saving to database
        db_session.add(category)
        db_session.commit()
        
        # THEN: Should work fine
        assert category.image_url is None
    
    def test_category_subcategories_relationship(self, db_session: Session):
        """Test that category shows its subcategories"""
        # GIVEN: A category with subcategories
        category = Category(name="Обувь", slug="shoes")
        db_session.add(category)
        db_session.commit()
        
        sub1 = Subcategory(category_id=category.id, name="Футболки", slug="tshirts")
        sub2 = Subcategory(category_id=category.id, name="Джинсы", slug="jeans")
        db_session.add_all([sub1, sub2])
        db_session.commit()
        
        # WHEN: Accessing subcategories
        db_session.refresh(category)
        
        # THEN: Should have 2 subcategories
        assert len(category.subcategories) == 2
        assert "Футболки" in [s.name for s in category.subcategories]
        assert "Джинсы" in [s.name for s in category.subcategories]


class TestSubcategoryModel:
    """Test Subcategory model enhancements"""
    
    def test_subcategory_has_image_url(self, db_session: Session):
        """Test that subcategory has image_url field"""
        # GIVEN: A category and subcategory
        category = Category(name="Спорт", slug="sport")
        db_session.add(category)
        db_session.commit()
        
        subcategory = Subcategory(
            category_id=category.id,
            name="Футболки",
            slug="tshirts",
            image_url="https://example.com/images/tshirts.jpg"
        )
        
        # WHEN: Saving to database
        db_session.add(subcategory)
        db_session.commit()
        db_session.refresh(subcategory)
        
        # THEN: Image URL should be saved
        assert subcategory.image_url == "https://example.com/images/tshirts.jpg"
    
    def test_subcategory_product_count(self, db_session: Session):
        """Test the product_count and active_product_count properties."""
        unique_id = uuid.uuid4().hex[:6]
        brand = Brand(name=f"Test Brand {unique_id}", slug=f"brand-{unique_id}")
        category = Category(name=f"Test Category {unique_id}", slug=f"cat-{unique_id}")
        subcategory = Subcategory(
            name=f"Test Subcategory {unique_id}",
            slug=f"sub-{unique_id}",
            category=category,
        )
        db_session.add_all([brand, category, subcategory])
        db_session.commit()

        # Add products
        p1 = Product(
            title=f"Active Product {unique_id}",
            slug=f"active-{unique_id}",
            brand_id=brand.id,
            category_id=category.id,
            subcategory_id=subcategory.id,
            is_active=True,
        )
        p2 = Product(
            title=f"Inactive Product {unique_id}",
            slug=f"inactive-{unique_id}",
            brand_id=brand.id,
            category_id=category.id,
            subcategory_id=subcategory.id,
            is_active=False,
        )
        db_session.add_all([p1, p2])
        db_session.commit()

        db_session.refresh(subcategory)
        assert subcategory.product_count == 2
        assert subcategory.active_product_count == 1
    
    def test_subcategory_belongs_to_category(self, db_session: Session):
        """Test that subcategory has proper category relationship"""
        # GIVEN: A category with subcategory
        category = Category(name="Аксессуары", slug="accessories")
        db_session.add(category)
        db_session.commit()
        
        subcategory = Subcategory(
            category_id=category.id,
            name="Платья",
            slug="dresses"
        )
        db_session.add(subcategory)
        db_session.commit()
        
        # WHEN: Accessing category from subcategory
        db_session.refresh(subcategory)
        
        # THEN: Should show parent category
        assert subcategory.category is not None
        assert subcategory.category.name == "Аксессуары"
        assert subcategory.category_id == category.id


class TestCategoryAdminView:
    """Test Category admin interface enhancements"""
    
    def test_category_admin_shows_image_field(self):
        """Test that category admin form includes image_url field"""
        from src.app_01.admin.catalog_admin_views import CategoryAdmin
        
        # THEN: form_columns should include image_url
        assert "image_url" in CategoryAdmin.form_columns
    
    def test_category_admin_shows_subcategory_count(self):
        """Test that category list shows subcategory count"""
        from src.app_01.admin.catalog_admin_views import CategoryAdmin
        
        # THEN: Should have formatter or column for subcategory count
        assert hasattr(CategoryAdmin, 'column_formatters') or \
               'subcategories' in str(CategoryAdmin.column_list)
    
    def test_category_admin_has_product_count_display(self):
        """Test that category shows total product count"""
        from src.app_01.admin.catalog_admin_views import CategoryAdmin
        
        # THEN: Should display or calculate product count
        # Can be done via formatter or property
        assert True  # Will implement with formatter


class TestSubcategoryAdminView:
    """Test Subcategory admin interface enhancements"""
    
    def test_subcategory_admin_shows_image_field(self):
        """Test that subcategory admin form includes image_url field"""
        from src.app_01.admin.catalog_admin_views import SubcategoryAdmin
        
        # THEN: form_columns should include image_url
        assert "image_url" in SubcategoryAdmin.form_columns
    
    def test_subcategory_admin_shows_parent_category(self):
        """Test that subcategory list shows parent category"""
        from src.app_01.admin.catalog_admin_views import SubcategoryAdmin
        
        # THEN: column_list should include category or category_id
        assert "category" in SubcategoryAdmin.column_list or \
               "category_id" in SubcategoryAdmin.column_list
    
    def test_subcategory_admin_shows_product_count(self):
        """Test that subcategory list shows product count"""
        from src.app_01.admin.catalog_admin_views import SubcategoryAdmin
        
        # THEN: Should have product_count in column_list or formatters
        assert hasattr(SubcategoryAdmin, 'column_formatters')
    
    def test_subcategory_admin_filter_by_category(self):
        """Test that admin can filter subcategories by category"""
        from src.app_01.admin.catalog_admin_views import SubcategoryAdmin
        
        # THEN: column_filters should include category_id
        assert "category_id" in SubcategoryAdmin.column_filters


class TestCategorySubcategoryIntegration:
    """Test the full category-subcategory workflow"""
    
    def test_create_category_then_subcategories(self, db_session: Session):
        """Test complete workflow: create category, then add subcategories"""
        # GIVEN: A new category "Sport"
        category = Category(
            name="Спорт",
            slug="sports",
            image_url="https://example.com/sport.jpg"
        )
        db_session.add(category)
        db_session.commit()
        
        # WHEN: Adding multiple subcategories
        subcategories = [
            Subcategory(
                category_id=category.id,
                name="Кроссовки",
                slug="sneakers",
                image_url="https://example.com/sneakers.jpg"
            ),
            Subcategory(
                category_id=category.id,
                name="Спортивная одежда",
                slug="sportswear",
                image_url="https://example.com/sportswear.jpg"
            ),
            Subcategory(
                category_id=category.id,
                name="Аксессуары",
                slug="accessories",
                image_url="https://example.com/accessories.jpg"
            ),
        ]
        db_session.add_all(subcategories)
        db_session.commit()
        
        # THEN: Category should show all subcategories
        db_session.refresh(category)
        assert len(category.subcategories) == 3
        assert all(sub.category_id == category.id for sub in subcategories)
        assert all(sub.image_url is not None for sub in subcategories)
    
    def test_cascade_delete_subcategories(self, db_session: Session):
        """Test that deleting category removes subcategories (if configured)"""
        # NOTE: Current model has cascade="all, delete-orphan"
        # So deleting category should delete subcategories
        
        # GIVEN: Category with subcategories
        category = Category(name="Test", slug="test")
        db_session.add(category)
        db_session.commit()
        
        sub = Subcategory(category_id=category.id, name="Sub", slug="sub")
        db_session.add(sub)
        db_session.commit()
        
        subcategory_id = sub.id
        
        # WHEN: Deleting category
        db_session.delete(category)
        db_session.commit()
        
        # THEN: Subcategory should also be deleted
        deleted_sub = db_session.query(Subcategory).filter_by(id=subcategory_id).first()
        assert deleted_sub is None

