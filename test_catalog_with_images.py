"""
Test Catalog System with Images

Creates a complete catalog structure:
- Category (Men) with image
- Subcategory (T-shirts) with image  
- Product (Cotton T-shirt) with image

Tests the full catalog flow from the design.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.app_01.db import db_manager, Market
from src.app_01.models import Category, Subcategory, Brand, Product, SKU, ProductAsset
from datetime import datetime


def test_catalog_creation():
    """Test creating category → subcategory → product with images"""
    
    print("\n" + "="*80)
    print("🧪 TESTING CATALOG SYSTEM WITH IMAGES")
    print("="*80 + "\n")
    
    # Get database session
    db = next(db_manager.get_db_session(Market.KG))
    
    try:
        # Step 1: Create Category with image
        print("📁 Step 1: Creating Category...")
        print("-" * 80)
        
        # Check if category exists
        existing_category = db.query(Category).filter(Category.slug == "men-test").first()
        if existing_category:
            print(f"   ⚠️  Category already exists (ID: {existing_category.id})")
            category = existing_category
        else:
            category = Category(
                name="Мужчинам (Test)",
                slug="men-test",
                description="Мужская одежда и аксессуары - тестовая категория",
                icon="fa-male",
                image_url="/uploads/categories/test-men-category.jpg",  # Will be replaced with real upload
                sort_order=1,
                is_active=True
            )
            db.add(category)
            db.flush()
            print(f"   ✅ Category created: {category.name} (ID: {category.id})")
            print(f"      Slug: {category.slug}")
            print(f"      Image: {category.image_url}")
        
        # Step 2: Create Subcategory with image
        print("\n📂 Step 2: Creating Subcategory...")
        print("-" * 80)
        
        existing_subcategory = db.query(Subcategory).filter(
            Subcategory.slug == "tshirts-test"
        ).first()
        
        if existing_subcategory:
            print(f"   ⚠️  Subcategory already exists (ID: {existing_subcategory.id})")
            subcategory = existing_subcategory
        else:
            subcategory = Subcategory(
                category_id=category.id,
                name="Футболки и поло (Test)",
                slug="tshirts-test",
                description="Мужские футболки, поло и базовые майки",
                image_url="/uploads/subcategories/test-tshirts.jpg",  # Will be replaced with real upload
                sort_order=1,
                is_active=True
            )
            db.add(subcategory)
            db.flush()
            print(f"   ✅ Subcategory created: {subcategory.name} (ID: {subcategory.id})")
            print(f"      Parent: {category.name}")
            print(f"      Slug: {subcategory.slug}")
            print(f"      Image: {subcategory.image_url}")
        
        # Step 3: Create Brand (if not exists)
        print("\n🏷️  Step 3: Creating Brand...")
        print("-" * 80)
        
        existing_brand = db.query(Brand).filter(Brand.slug == "test-brand").first()
        if existing_brand:
            print(f"   ⚠️  Brand already exists (ID: {existing_brand.id})")
            brand = existing_brand
        else:
            brand = Brand(
                name="Test Brand",
                slug="test-brand",
                description="Test brand for catalog testing",
                logo_url="/uploads/brands/test-brand-logo.jpg",
                country="KG",
                sort_order=1,
                is_active=True
            )
            db.add(brand)
            db.flush()
            print(f"   ✅ Brand created: {brand.name} (ID: {brand.id})")
        
        # Step 4: Create Product with image
        print("\n👕 Step 4: Creating Product...")
        print("-" * 80)
        
        existing_product = db.query(Product).filter(
            Product.slug == "cotton-tshirt-test"
        ).first()
        
        if existing_product:
            print(f"   ⚠️  Product already exists (ID: {existing_product.id})")
            product = existing_product
        else:
            product = Product(
                title="Футболка из хлопка (Test)",
                slug="cotton-tshirt-test",
                description="Базовая футболка из 100% хлопка. Комфортная посадка, дышащий материал.",
                brand_id=brand.id,
                category_id=category.id,
                subcategory_id=subcategory.id,
                rating_avg=4.5,
                rating_count=25,
                sold_count=150,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(product)
            db.flush()
            print(f"   ✅ Product created: {product.title} (ID: {product.id})")
            print(f"      Brand: {brand.name}")
            print(f"      Category: {category.name}")
            print(f"      Subcategory: {subcategory.name}")
        
        # Step 5: Add Product Image (Asset)
        print("\n🖼️  Step 5: Adding Product Image...")
        print("-" * 80)
        
        existing_asset = db.query(ProductAsset).filter(
            ProductAsset.product_id == product.id
        ).first()
        
        if existing_asset:
            print(f"   ⚠️  Product image already exists")
        else:
            asset = ProductAsset(
                product_id=product.id,
                url="/uploads/products/test-cotton-tshirt.jpg",  # Will be replaced with real upload
                type="image"
            )
            db.add(asset)
            db.flush()
            print(f"   ✅ Product image added: {asset.url}")
        
        # Step 6: Add SKUs (sizes and colors)
        print("\n📦 Step 6: Adding SKUs (sizes & colors)...")
        print("-" * 80)
        
        sku_data = [
            {"size": "S", "color": "Black", "price": 2999, "original_price": 3699, "stock": 20},
            {"size": "M", "color": "Black", "price": 2999, "original_price": 3699, "stock": 35},
            {"size": "L", "color": "Black", "price": 2999, "original_price": 3699, "stock": 28},
            {"size": "M", "color": "White", "price": 2999, "original_price": 3699, "stock": 25},
            {"size": "L", "color": "White", "price": 2999, "original_price": 3699, "stock": 15},
        ]
        
        for sku_info in sku_data:
            existing_sku = db.query(SKU).filter(
                SKU.product_id == product.id,
                SKU.size == sku_info["size"],
                SKU.color == sku_info["color"]
            ).first()
            
            if existing_sku:
                print(f"   ⚠️  SKU already exists: {sku_info['size']} - {sku_info['color']}")
            else:
                sku = SKU(
                    product_id=product.id,
                    size=sku_info["size"],
                    color=sku_info["color"],
                    sku_code=f"TEST-{product.id}-{sku_info['size']}-{sku_info['color']}",
                    price=sku_info["price"],
                    original_price=sku_info["original_price"],
                    stock=sku_info["stock"]
                )
                db.add(sku)
                print(f"   ✅ SKU added: {sku_info['size']} - {sku_info['color']} ({sku_info['stock']} in stock)")
        
        # Commit all changes
        db.commit()
        
        # Step 7: Test API endpoints
        print("\n" + "="*80)
        print("🌐 TEST API ENDPOINTS")
        print("="*80 + "\n")
        
        print("curl http://localhost:8000/api/v1/categories")
        print("curl http://localhost:8000/api/v1/categories/men-test")
        print("curl http://localhost:8000/api/v1/subcategories/tshirts-test/products")
        print("curl http://localhost:8000/api/v1/products/cotton-tshirt-test")
        
        # Summary
        print("\n" + "="*80)
        print("✅ TEST DATA CREATED!")
        print("="*80)
        print(f"\n📁 Category: {category.name} (ID: {category.id})")
        print(f"📂 Subcategory: {subcategory.name} (ID: {subcategory.id})")
        print(f"👕 Product: {product.title} (ID: {product.id})")
        print(f"📦 SKUs: 5 variants")
        
        print("\n" + "="*80)
        print("📝 NEXT: Upload real images via /admin!")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    result = test_catalog_creation()
    
    if result:
        print("🎉 Success! Test data created!\n")
        sys.exit(0)
    else:
        print("❌ Failed! Check errors above.\n")
        sys.exit(1)
