"""
Update Products with New Business Fields
=========================================

This script updates all existing products with the new business-ready fields:
- Auto-generates SEO meta fields from existing data
- Updates new product status based on creation date
- Sets default values for new columns
- Validates products

Run this after applying the database migration.

Usage:
    python update_products_with_new_fields.py [--dry-run]
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app_01.db import db_manager, Market
from src.app_01.models.products.product import Product


def update_product_seo_fields(product):
    """Auto-generate SEO fields from existing product data"""
    updated = False
    
    # Generate meta_title from title + brand + category
    if not product.meta_title and product.title:
        parts = [product.title]
        if product.brand:
            parts.append(product.brand.name)
        if product.category:
            parts.append(product.category.name)
        product.meta_title = " - ".join(parts)[:255]
        updated = True
        print(f"  ✓ Generated meta_title: {product.meta_title}")
    
    # Generate meta_description from description
    if not product.meta_description and product.description:
        # Take first 160 characters and clean it
        desc = product.description.replace('\n', ' ').strip()[:157]
        product.meta_description = desc + "..." if len(product.description) > 157 else desc
        updated = True
        print(f"  ✓ Generated meta_description: {product.meta_description[:50]}...")
    
    # Generate keywords from title, brand, category, subcategory
    if not product.meta_keywords:
        keywords = []
        if product.title:
            keywords.extend(product.title.lower().split())
        if product.brand:
            keywords.append(product.brand.name.lower())
        if product.category:
            keywords.append(product.category.name.lower())
        if product.subcategory:
            keywords.append(product.subcategory.name.lower())
        
        # Remove duplicates and join
        unique_keywords = list(set(keywords))[:10]  # Limit to 10 keywords
        product.meta_keywords = ", ".join(unique_keywords)
        updated = True
        print(f"  ✓ Generated meta_keywords: {product.meta_keywords}")
    
    return updated


def update_product_status(product, new_product_threshold_days=30):
    """Update product status flags"""
    updated = False
    
    # Update is_new based on creation date
    if product.created_at:
        age_days = (datetime.now(product.created_at.tzinfo) - product.created_at).days
        old_is_new = product.is_new
        product.is_new = age_days <= new_product_threshold_days
        
        if old_is_new != product.is_new:
            updated = True
            status = "NEW" if product.is_new else "NOT NEW"
            print(f"  ✓ Updated is_new: {status} (age: {age_days} days)")
    
    return updated


def validate_and_report(product):
    """Validate product and report issues"""
    is_valid, errors = product.validate_for_activation()
    
    if not is_valid:
        print(f"  ⚠️  Validation issues:")
        for error in errors:
            print(f"      - {error}")
        return False
    
    return True


def main(dry_run=False):
    """Main function to update all products"""
    print("=" * 70)
    print("Product Update Script - Business Fields")
    print("=" * 70)
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be saved\n")
    
    # Get session for KG market (default)
    SessionFactory = db_manager.get_session_factory(Market.KG)
    db = SessionFactory()
    
    try:
        # Get all products
        products = db.query(Product).all()
        total_products = len(products)
        
        print(f"📦 Found {total_products} products to update\n")
        
        updated_count = 0
        validation_issues_count = 0
        
        for i, product in enumerate(products, 1):
            print(f"[{i}/{total_products}] Processing: {product.title} (ID: {product.id})")
            
            product_updated = False
            
            # Update SEO fields
            if update_product_seo_fields(product):
                product_updated = True
            
            # Update status flags
            if update_product_status(product, new_product_threshold_days=30):
                product_updated = True
            
            # Set default values if missing
            if product.view_count is None:
                product.view_count = 0
                product_updated = True
                print(f"  ✓ Set view_count to 0")
            
            if product.low_stock_threshold is None:
                product.low_stock_threshold = 5
                product_updated = True
                print(f"  ✓ Set low_stock_threshold to 5")
            
            # Validate product
            is_valid = validate_and_report(product)
            if not is_valid:
                validation_issues_count += 1
            
            # Show product stats
            print(f"  📊 Stats:")
            print(f"      - Stock: {product.total_stock} ({product.stock_status})")
            print(f"      - Price: {product.display_price} сом")
            if product.discount_percentage > 0:
                print(f"      - Discount: {product.discount_percentage}%")
            print(f"      - SKUs: {len(product.skus)}")
            print(f"      - Images: {len(product.get_all_images())}")
            print(f"      - Rating: {product.rating_avg} ⭐ ({product.rating_count} reviews)")
            print(f"      - Sold: {product.sold_count}, Views: {product.view_count}")
            print(f"      - Active: {product.is_active}, Featured: {product.is_featured}")
            print(f"      - New: {product.is_new}, Trending: {product.is_trending}")
            
            if product_updated:
                updated_count += 1
            
            print()
        
        # Summary
        print("=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"Total products: {total_products}")
        print(f"Updated: {updated_count}")
        print(f"Already up-to-date: {total_products - updated_count}")
        print(f"Validation issues: {validation_issues_count}")
        print()
        
        # Commit or rollback
        if not dry_run:
            if updated_count > 0:
                db.commit()
                print("✅ Changes committed to database")
            else:
                print("ℹ️  No changes needed")
        else:
            db.rollback()
            print("🔍 DRY RUN - No changes saved")
        
        # Recommendations
        if validation_issues_count > 0:
            print()
            print("⚠️  RECOMMENDATIONS:")
            print(f"   - {validation_issues_count} products have validation issues")
            print("   - Review the issues above and fix them before activating")
        
        # Stock warnings
        low_stock_products = [p for p in products if p.is_low_stock]
        if low_stock_products:
            print()
            print("📦 LOW STOCK WARNINGS:")
            for p in low_stock_products[:10]:  # Show first 10
                print(f"   - {p.title}: {p.total_stock} left")
            if len(low_stock_products) > 10:
                print(f"   ... and {len(low_stock_products) - 10} more")
        
        # Missing SEO
        missing_seo = [p for p in products if not p.meta_description]
        if missing_seo:
            print()
            print("🔍 SEO OPPORTUNITIES:")
            print(f"   - {len(missing_seo)} products still need manual SEO optimization")
            print("   - Consider writing custom meta descriptions for better Google ranking")
        
        print()
        print("✨ Done! Your products are now business-ready!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    
    if dry_run:
        print("\n💡 TIP: Remove --dry-run flag to apply changes\n")
    
    try:
        main(dry_run=dry_run)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

