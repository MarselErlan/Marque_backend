"""
ETL Script: Populate US Database with Test Data
Copies products, SKUs, brands, and categories from KG to US database for testing
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.products.product import Product
from src.app_01.models.products.sku import SKU
from src.app_01.models.products.brand import Brand
from src.app_01.models.products.category import Category, Subcategory


def copy_brands(kg_db, us_db):
    """Copy brands from KG to US database"""
    kg_brands = kg_db.query(Brand).all()
    brand_map = {}
    copied = 0
    
    for kg_brand in kg_brands:
        # Check if brand already exists
        us_brand = us_db.query(Brand).filter(Brand.slug == kg_brand.slug).first()
        if not us_brand:
            us_brand = Brand(
                name=kg_brand.name,
                slug=kg_brand.slug,
                description=kg_brand.description,
                logo_url=kg_brand.logo_url,
                is_active=kg_brand.is_active
            )
            us_db.add(us_brand)
            us_db.flush()
            copied += 1
        brand_map[kg_brand.id] = us_brand.id
    
    us_db.commit()
    return brand_map, copied


def copy_categories(kg_db, us_db):
    """Copy categories from KG to US database"""
    kg_categories = kg_db.query(Category).all()
    category_map = {}
    copied = 0
    
    for kg_cat in kg_categories:
        # Check if category already exists
        us_cat = us_db.query(Category).filter(Category.slug == kg_cat.slug).first()
        if not us_cat:
            us_cat = Category(
                name=kg_cat.name,
                slug=kg_cat.slug,
                description=kg_cat.description,
                is_active=kg_cat.is_active
            )
            us_db.add(us_cat)
            us_db.flush()
            copied += 1
        category_map[kg_cat.id] = us_cat.id
    
    us_db.commit()
    return category_map, copied


def copy_subcategories(kg_db, us_db, category_map):
    """Copy subcategories from KG to US database"""
    kg_subcats = kg_db.query(Subcategory).all()
    subcat_map = {}
    copied = 0
    
    for kg_subcat in kg_subcats:
        # Check if subcategory already exists
        us_subcat = us_db.query(Subcategory).filter(Subcategory.slug == kg_subcat.slug).first()
        if not us_subcat:
            us_subcat = Subcategory(
                name=kg_subcat.name,
                slug=kg_subcat.slug,
                description=kg_subcat.description,
                category_id=category_map.get(kg_subcat.category_id),
                is_active=kg_subcat.is_active
            )
            us_db.add(us_subcat)
            us_db.flush()
            copied += 1
        subcat_map[kg_subcat.id] = us_subcat.id
    
    us_db.commit()
    return subcat_map, copied


def copy_products_and_skus(kg_db, us_db, brand_map, category_map, subcat_map, limit=10):
    """Copy products and their SKUs from KG to US database"""
    kg_products = kg_db.query(Product).filter(Product.is_active == True).limit(limit).all()
    product_count = 0
    sku_count = 0
    
    for kg_product in kg_products:
        # Check if product already exists
        us_product = us_db.query(Product).filter(Product.slug == kg_product.slug).first()
        if us_product:
            print(f"  ⏭️  Product '{kg_product.title}' already exists (ID: {us_product.id})")
            # Still copy SKUs for existing product if needed
            existing_skus = us_db.query(SKU).filter(SKU.product_id == us_product.id).count()
            if existing_skus == 0:
                # Copy SKUs for this existing product
                kg_skus = kg_db.query(SKU).filter(SKU.product_id == kg_product.id).all()
                for kg_sku in kg_skus:
                    us_sku = SKU(
                        product_id=us_product.id,
                        sku_code=kg_sku.sku_code,
                        size=kg_sku.size,
                        color=kg_sku.color,
                        price=kg_sku.price,
                        original_price=kg_sku.original_price,
                        stock=kg_sku.stock,
                        is_active=kg_sku.is_active,
                        variant_image=kg_sku.variant_image
                    )
                    us_db.add(us_sku)
                    sku_count += 1
                us_db.commit()
            continue
        
        # Create new product
        us_product = Product(
            title=kg_product.title,
            slug=kg_product.slug,
            sku_code=kg_product.sku_code,
            description=kg_product.description,
            brand_id=brand_map.get(kg_product.brand_id),
            category_id=category_map.get(kg_product.category_id),
            subcategory_id=subcat_map.get(kg_product.subcategory_id) if kg_product.subcategory_id else None,
            main_image=kg_product.main_image,
            additional_images=kg_product.additional_images,
            meta_title=kg_product.meta_title,
            meta_description=kg_product.meta_description,
            meta_keywords=kg_product.meta_keywords,
            tags=kg_product.tags,
            view_count=0,
            is_new=kg_product.is_new,
            is_trending=kg_product.is_trending,
            is_active=kg_product.is_active,
            low_stock_threshold=kg_product.low_stock_threshold or 5
        )
        us_db.add(us_product)
        us_db.flush()
        product_count += 1
        
        print(f"  ✅ Copied product: {us_product.title} (ID: {us_product.id})")
        
        # Copy SKUs for this product
        kg_skus = kg_db.query(SKU).filter(SKU.product_id == kg_product.id).all()
        for kg_sku in kg_skus:
            us_sku = SKU(
                product_id=us_product.id,
                sku_code=kg_sku.sku_code,
                size=kg_sku.size,
                color=kg_sku.color,
                price=kg_sku.price,
                original_price=kg_sku.original_price,
                stock=kg_sku.stock,
                is_active=kg_sku.is_active,
                variant_image=kg_sku.variant_image
            )
            us_db.add(us_sku)
            sku_count += 1
            print(f"    • SKU: {us_sku.sku_code} (Size: {us_sku.size}, Color: {us_sku.color}, Stock: {us_sku.stock})")
    
    us_db.commit()
    return product_count, sku_count


def verify_data_integrity(us_db):
    """Verify data integrity after ETL"""
    print("\n🔍 Verifying data integrity...")
    
    issues = []
    
    # Check for orphaned products (no SKUs)
    products_without_skus = us_db.query(Product).outerjoin(SKU).filter(SKU.id == None).count()
    if products_without_skus > 0:
        issues.append(f"Found {products_without_skus} products without SKUs")
    
    # Check for SKUs without products
    skus_without_products = us_db.query(SKU).outerjoin(Product).filter(Product.id == None).count()
    if skus_without_products > 0:
        issues.append(f"Found {skus_without_products} SKUs without products")
    
    # Check for products without brands
    products_without_brands = us_db.query(Product).filter(Product.brand_id == None).count()
    if products_without_brands > 0:
        issues.append(f"Found {products_without_brands} products without brands")
    
    # Check for products without categories
    products_without_categories = us_db.query(Product).filter(Product.category_id == None).count()
    if products_without_categories > 0:
        issues.append(f"Found {products_without_categories} products without categories")
    
    if issues:
        print("  ⚠️  Data integrity issues found:")
        for issue in issues:
            print(f"     - {issue}")
        return False
    else:
        print("  ✅ All data integrity checks passed!")
        return True


def get_database_stats(db, market_name):
    """Get statistics about database contents"""
    brand_count = db.query(Brand).count()
    category_count = db.query(Category).count()
    subcategory_count = db.query(Subcategory).count()
    product_count = db.query(Product).count()
    sku_count = db.query(SKU).count()
    active_products = db.query(Product).filter(Product.is_active == True).count()
    
    return {
        "market": market_name,
        "brands": brand_count,
        "categories": category_count,
        "subcategories": subcategory_count,
        "products": product_count,
        "skus": sku_count,
        "active_products": active_products
    }


def main():
    print("\n" + "="*70)
    print("  ETL: Populate US Database with Test Data")
    print("="*70 + "\n")
    
    # Get database sessions
    KGSessionLocal = db_manager.get_session_factory(Market.KG)
    USSessionLocal = db_manager.get_session_factory(Market.US)
    
    kg_db = KGSessionLocal()
    us_db = USSessionLocal()
    
    try:
        # Get initial stats
        print("📊 Initial Database State:")
        kg_stats = get_database_stats(kg_db, "KG")
        us_stats_before = get_database_stats(us_db, "US")
        
        print(f"\n  KG Database:")
        print(f"    • Brands: {kg_stats['brands']}")
        print(f"    • Categories: {kg_stats['categories']}")
        print(f"    • Subcategories: {kg_stats['subcategories']}")
        print(f"    • Products: {kg_stats['products']} ({kg_stats['active_products']} active)")
        print(f"    • SKUs: {kg_stats['skus']}")
        
        print(f"\n  US Database (BEFORE):")
        print(f"    • Brands: {us_stats_before['brands']}")
        print(f"    • Categories: {us_stats_before['categories']}")
        print(f"    • Subcategories: {us_stats_before['subcategories']}")
        print(f"    • Products: {us_stats_before['products']} ({us_stats_before['active_products']} active)")
        print(f"    • SKUs: {us_stats_before['skus']}")
        
        print("\n" + "-"*70)
        print("\n🚀 Starting ETL Process...\n")
        
        # Step 1: Copy brands
        print("📋 Step 1: Copying brands...")
        brand_map, brands_copied = copy_brands(kg_db, us_db)
        print(f"   ✅ Processed {len(brand_map)} brands ({brands_copied} new)\n")
        
        # Step 2: Copy categories
        print("📂 Step 2: Copying categories...")
        category_map, categories_copied = copy_categories(kg_db, us_db)
        print(f"   ✅ Processed {len(category_map)} categories ({categories_copied} new)\n")
        
        # Step 3: Copy subcategories
        print("📁 Step 3: Copying subcategories...")
        subcat_map, subcats_copied = copy_subcategories(kg_db, us_db, category_map)
        print(f"   ✅ Processed {len(subcat_map)} subcategories ({subcats_copied} new)\n")
        
        # Step 4: Copy products and SKUs (limit to 10 products for testing)
        print("📦 Step 4: Copying products and SKUs (limit: 10)...")
        product_count, sku_count = copy_products_and_skus(
            kg_db, us_db, brand_map, category_map, subcat_map, limit=10
        )
        print(f"\n   ✅ Copied {product_count} new products and {sku_count} SKUs\n")
        
        # Step 5: Verify data integrity
        integrity_ok = verify_data_integrity(us_db)
        
        # Get final stats
        print("\n📊 Final Database State:")
        us_stats_after = get_database_stats(us_db, "US")
        
        print(f"\n  US Database (AFTER):")
        print(f"    • Brands: {us_stats_after['brands']} (+{us_stats_after['brands'] - us_stats_before['brands']})")
        print(f"    • Categories: {us_stats_after['categories']} (+{us_stats_after['categories'] - us_stats_before['categories']})")
        print(f"    • Subcategories: {us_stats_after['subcategories']} (+{us_stats_after['subcategories'] - us_stats_before['subcategories']})")
        print(f"    • Products: {us_stats_after['products']} (+{us_stats_after['products'] - us_stats_before['products']})")
        print(f"    • SKUs: {us_stats_after['skus']} (+{us_stats_after['skus'] - us_stats_before['skus']})")
        
        print("\n" + "="*70)
        if integrity_ok and us_stats_after['skus'] > 0:
            print("  ✅ ETL COMPLETE - US Database Ready for Testing!")
        else:
            print("  ⚠️  ETL COMPLETE - But some issues detected")
        print("="*70 + "\n")
        
        return 0 if integrity_ok else 1
        
    except Exception as e:
        print(f"\n❌ ETL Failed: {e}")
        import traceback
        traceback.print_exc()
        us_db.rollback()
        return 1
    finally:
        kg_db.close()
        us_db.close()


if __name__ == "__main__":
    exit(main())

