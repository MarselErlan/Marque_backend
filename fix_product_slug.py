#!/usr/bin/env python3
"""
Fix product #42 slug - generate from product name
"""

import psycopg2
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Get DATABASE_URL from environment
database_url = os.getenv("DATABASE_URL_MARQUE_KG")

if not database_url:
    print("ERROR: DATABASE_URL not found")
    exit(1)

def slugify(text):
    """Convert text to URL-friendly slug"""
    # Convert to lowercase and replace spaces with hyphens
    text = text.lower().strip()
    # Remove special characters
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'[-\s]+', '-', text)
    return text

try:
    # Connect to database
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Get product name
    cursor.execute("SELECT id, title FROM products WHERE id = 42")
    result = cursor.fetchone()
    
    if not result:
        print("❌ Product #42 not found")
        exit(1)
    
    product_id, product_name = result
    
    # Generate slug from name
    slug = slugify(product_name)
    
    print(f"Product: {product_name}")
    print(f"Generated slug: {slug}")
    
    # Update product with slug
    cursor.execute("""
        UPDATE products
        SET slug = %s
        WHERE id = %s
    """, (slug, product_id))
    
    conn.commit()
    
    print(f"\n✅ Product #{product_id} updated!")
    print(f"   Slug: {slug}")
    print(f"\n🔗 Product detail URL:")
    print(f"   http://localhost:3000/product/{slug}")
    print(f"   https://marque.website/product/{slug}")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

