#!/usr/bin/env python3
"""
Activate categories in PRODUCTION Railway database
Run this to fix the catalog showing empty categories
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# IMPORTANT: Use your Railway PRODUCTION database URL
PRODUCTION_DATABASE_URL = os.getenv("RAILWAY_PROD_DATABASE_URL", "postgresql://...")

print("\n" + "="*70)
print("🚀 ACTIVATING CATEGORIES IN PRODUCTION DATABASE")
print("="*70)

# Create engine for production
engine = create_engine(PRODUCTION_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

try:
    # Activate all categories that have products
    result = session.execute("""
        UPDATE categories 
        SET is_active = TRUE 
        WHERE id IN (
            SELECT DISTINCT category_id 
            FROM products 
            WHERE is_active = TRUE
        )
        AND (is_active IS NULL OR is_active = FALSE)
        RETURNING id, name, slug;
    """)
    
    activated_categories = result.fetchall()
    
    if activated_categories:
        print("\n✅ ACTIVATED CATEGORIES:")
        for cat in activated_categories:
            print(f"  - ID: {cat[0]} | Name: {cat[1]} | Slug: {cat[2]}")
    else:
        print("\n✅ All categories already active!")
    
    # Activate all subcategories that have products
    result = session.execute("""
        UPDATE subcategories 
        SET is_active = TRUE 
        WHERE id IN (
            SELECT DISTINCT subcategory_id 
            FROM products 
            WHERE is_active = TRUE
        )
        AND (is_active IS NULL OR is_active = FALSE)
        RETURNING id, name, slug;
    """)
    
    activated_subcategories = result.fetchall()
    
    if activated_subcategories:
        print("\n✅ ACTIVATED SUBCATEGORIES:")
        for subcat in activated_subcategories:
            print(f"  - ID: {subcat[0]} | Name: {subcat[1]} | Slug: {subcat[2]}")
    else:
        print("\n✅ All subcategories already active!")
    
    session.commit()
    
    # Verify activation
    result = session.execute("""
        SELECT c.id, c.name, c.slug, c.is_active,
               (SELECT COUNT(*) FROM products WHERE category_id = c.id AND is_active = TRUE) as product_count
        FROM categories c
        ORDER BY c.id;
    """)
    
    categories = result.fetchall()
    
    print("\n" + "="*70)
    print("📊 CURRENT CATEGORY STATUS:")
    print("="*70)
    for cat in categories:
        status = "✅" if cat[3] else "❌"
        print(f"{status} ID: {cat[0]:2d} | {cat[1]:30s} | Products: {cat[4]:2d} | Active: {cat[3]}")
    
    print("\n" + "="*70)
    print("✅ PRODUCTION DATABASE UPDATED SUCCESSFULLY!")
    print("="*70)
    print("\n🎯 Next steps:")
    print("1. Wait 30 seconds for Railway backend to restart")
    print("2. Refresh your frontend: https://marque.website")
    print("3. Click 'Каталог' - categories should now show!\n")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    session.rollback()
    print("\n⚠️  Make sure you set the RAILWAY_PROD_DATABASE_URL environment variable!")
    print("    Get it from: Railway Dashboard → Your Service → Variables → DATABASE_URL")
finally:
    session.close()

