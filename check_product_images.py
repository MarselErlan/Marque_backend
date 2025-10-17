#!/usr/bin/env python3
"""
Check if product #42 has main_image and additional_images populated
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DATABASE_URL from environment
database_url = os.getenv("DATABASE_URL_MARQUE_KG") or os.getenv("MARQUE_KG_DATABASE_URL") or os.getenv("DATABASE_URL")

if not database_url:
    print("ERROR: DATABASE_URL not found in environment variables")
    exit(1)

try:
    # Connect to database
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Query product #42
    cursor.execute("""
        SELECT id, title, main_image, additional_images
        FROM products
        WHERE id = 42
    """)
    
    result = cursor.fetchone()
    
    if result:
        product_id, title, main_image, additional_images = result
        print(f"✅ Product Found: {title} (ID: {product_id})")
        print(f"\nmain_image: {main_image if main_image else '❌ NULL'}")
        print(f"additional_images: {additional_images if additional_images else '❌ NULL'}")
        
        if not main_image and not additional_images:
            print("\n⚠️  WARNING: Product has NO images in main_image or additional_images fields!")
            print("   The product might have images in the old 'product_assets' table instead.")
            
            # Check old assets table
            cursor.execute("""
                SELECT COUNT(*), STRING_AGG(url, ', ') 
                FROM product_assets
                WHERE product_id = 42 AND type = 'image'
            """)
            asset_count, asset_urls = cursor.fetchone()
            print(f"\n   Product has {asset_count} images in product_assets table:")
            if asset_urls:
                print(f"   URLs: {asset_urls}")
    else:
        print("❌ Product #42 not found in database!")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

