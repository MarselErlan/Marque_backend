#!/usr/bin/env python3
"""Apply SKU code migration to production database"""

import os
import sys
from sqlalchemy import create_engine, text

# Get production database URL from Railway environment
database_url_kg = os.environ.get("DATABASE_URL_MARQUE_KG")
database_url_us = os.environ.get("DATABASE_URL_MARQUE_US")

if not database_url_kg and not database_url_us:
    print("❌ No DATABASE_URL found!")
    print("Available env vars:", [k for k in os.environ.keys() if "DATA" in k])
    sys.exit(1)

# Apply to both databases
databases = []
if database_url_kg:
    databases.append(("KG", database_url_kg))
if database_url_us:
    databases.append(("US", database_url_us))

sql = """
-- Add sku_code column to products table
ALTER TABLE products ADD COLUMN IF NOT EXISTS sku_code VARCHAR(50);

-- Set default values for existing products
UPDATE products 
SET sku_code = 'SKU-' || id
WHERE sku_code IS NULL;

-- Make column non-nullable
ALTER TABLE products ALTER COLUMN sku_code SET NOT NULL;

-- Create unique index
CREATE UNIQUE INDEX IF NOT EXISTS ix_products_sku_code ON products (sku_code);
"""

for market, database_url in databases:
    print(f"\n🚀 Applying migration to {market} database...")
    print(f"   URL: {database_url[:50]}...")
    
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            print(f"📝 Executing SQL for {market}...")
            conn.execute(text(sql))
            conn.commit()
            print(f"✅ Migration applied successfully to {market}!")
            
            # Verify
            result = conn.execute(text("SELECT COUNT(*) FROM products WHERE sku_code IS NOT NULL"))
            count = result.scalar()
            print(f"✅ {count} products in {market} have sku_code")
            
    except Exception as e:
        print(f"❌ Error for {market}: {e}")
        sys.exit(1)

print("\n🎉 All migrations completed successfully!")

