#!/usr/bin/env python3
"""
Fix product #42 to use an existing image file
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DATABASE_URL from environment
database_url = os.getenv("DATABASE_URL_MARQUE_KG")

if not database_url:
    print("ERROR: DATABASE_URL not found")
    exit(1)

try:
    # Connect to database
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Use one of the existing images
    main_image = "/uploads/product/deb31057-8c00-4ebe-b2ea-76ad15e9e730.png"
    additional_images_json = '["/uploads/product/e1a44ed6-090a-49e3-ac58-77470e1d93d6.png"]'
    
    # Update product #42
    cursor.execute("""
        UPDATE products
        SET main_image = %s,
            additional_images = %s::json
        WHERE id = 42
    """, (main_image, additional_images_json))
    
    conn.commit()
    
    print("✅ Product #42 updated successfully!")
    print(f"   main_image: {main_image}")
    print(f"   additional_images: {additional_images_json}")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

