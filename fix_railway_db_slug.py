#!/usr/bin/env python3
"""
Fix product #42 slug in Railway database
"""

import psycopg2

# Railway database URL (production)
database_url = "postgresql://postgres:YgyDmMbYyzPKvSsNyDRShLJqehXtTdJx@metro.proxy.rlwy.net:45504/railway"

try:
    # Connect to Railway database
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Update product #42 slug
    cursor.execute("""
        UPDATE products
        SET slug = 'test-product1'
        WHERE id = 42
    """)
    
    conn.commit()
    
    print("✅ Railway database updated!")
    print("   Product #42 slug: test-product1")
    
    # Verify
    cursor.execute("SELECT id, title, slug FROM products WHERE id = 42")
    result = cursor.fetchone()
    print(f"\n   Verified: {result}")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

