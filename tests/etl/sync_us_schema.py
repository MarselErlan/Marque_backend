"""
Schema Sync Script: Ensure US database schema matches KG database
Adds missing columns to US database tables
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app_01.db.market_db import db_manager, Market
from sqlalchemy import text


def sync_brands_table(us_conn):
    """Add missing columns to brands table"""
    print("📋 Syncing brands table...")
    
    columns_to_add = [
        ("is_featured", "BOOLEAN DEFAULT FALSE"),
        ("sort_order", "INTEGER DEFAULT 0"),
        ("website_url", "VARCHAR(500)"),
        ("country", "VARCHAR(50)"),
        ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
        ("updated_at", "TIMESTAMP WITH TIME ZONE"),
    ]
    
    added = 0
    for col_name, col_def in columns_to_add:
        try:
            us_conn.execute(text(f"ALTER TABLE brands ADD COLUMN IF NOT EXISTS {col_name} {col_def}"))
            print(f"  ✅ Added column: {col_name}")
            added += 1
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"  ⏭️  Column {col_name} already exists")
            else:
                print(f"  ❌ Failed to add {col_name}: {e}")
    
    # Add indexes
    try:
        us_conn.execute(text("CREATE INDEX IF NOT EXISTS idx_brand_active_sort ON brands (is_active, sort_order)"))
        us_conn.execute(text("CREATE INDEX IF NOT EXISTS idx_brand_country ON brands (country)"))
        print(f"  ✅ Added indexes")
    except Exception as e:
        print(f"  ⚠️  Index creation: {e}")
    
    us_conn.commit()
    return added


def sync_categories_table(us_conn):
    """Add missing columns to categories table"""
    print("📂 Syncing categories table...")
    
    columns_to_add = [
        ("sort_order", "INTEGER DEFAULT 0"),
        ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
        ("updated_at", "TIMESTAMP WITH TIME ZONE"),
    ]
    
    added = 0
    for col_name, col_def in columns_to_add:
        try:
            us_conn.execute(text(f"ALTER TABLE categories ADD COLUMN IF NOT EXISTS {col_name} {col_def}"))
            print(f"  ✅ Added column: {col_name}")
            added += 1
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"  ⏭️  Column {col_name} already exists")
            else:
                print(f"  ❌ Failed to add {col_name}: {e}")
    
    us_conn.commit()
    return added


def sync_subcategories_table(us_conn):
    """Add missing columns to subcategories table"""
    print("📁 Syncing subcategories table...")
    
    columns_to_add = [
        ("sort_order", "INTEGER DEFAULT 0"),
        ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
        ("updated_at", "TIMESTAMP WITH TIME ZONE"),
    ]
    
    added = 0
    for col_name, col_def in columns_to_add:
        try:
            us_conn.execute(text(f"ALTER TABLE subcategories ADD COLUMN IF NOT EXISTS {col_name} {col_def}"))
            print(f"  ✅ Added column: {col_name}")
            added += 1
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"  ⏭️  Column {col_name} already exists")
            else:
                print(f"  ❌ Failed to add {col_name}: {e}")
    
    us_conn.commit()
    return added


def check_schema_match(kg_conn, us_conn, table_name):
    """Check if schemas match between KG and US databases"""
    kg_columns = kg_conn.execute(text(f"""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
    """)).fetchall()
    
    us_columns = us_conn.execute(text(f"""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
    """)).fetchall()
    
    kg_col_names = {col[0] for col in kg_columns}
    us_col_names = {col[0] for col in us_columns}
    
    missing_in_us = kg_col_names - us_col_names
    extra_in_us = us_col_names - kg_col_names
    
    return kg_columns, us_columns, missing_in_us, extra_in_us


def main():
    print("\n" + "="*70)
    print("  Schema Sync: US Database")
    print("="*70 + "\n")
    
    # Get database connections
    KGSessionLocal = db_manager.get_session_factory(Market.KG)
    USSessionLocal = db_manager.get_session_factory(Market.US)
    
    kg_session = KGSessionLocal()
    us_session = USSessionLocal()
    
    kg_conn = kg_session.connection()
    us_conn = us_session.connection()
    
    try:
        # Sync brands table
        sync_brands_table(us_conn)
        
        # Sync categories table
        sync_categories_table(us_conn)
        
        # Sync subcategories table
        sync_subcategories_table(us_conn)
        
        # Check critical tables
        print("\n🔍 Verifying schema sync for critical tables...")
        tables_to_check = ['brands', 'categories', 'subcategories', 'products', 'skus']
        
        all_synced = True
        for table in tables_to_check:
            try:
                kg_cols, us_cols, missing, extra = check_schema_match(kg_conn, us_conn, table)
                
                if missing:
                    print(f"\n  ⚠️  Table '{table}' - Missing in US: {missing}")
                    all_synced = False
                elif extra:
                    print(f"\n  ℹ️  Table '{table}' - Extra in US: {extra}")
                else:
                    print(f"  ✅ Table '{table}' - Schema matches ({len(kg_cols)} columns)")
            except Exception as e:
                print(f"  ⚠️  Could not check table '{table}': {e}")
        
        print("\n" + "="*70)
        if all_synced:
            print("  ✅ SCHEMA SYNC COMPLETE - All tables synced!")
        else:
            print("  ⚠️  SCHEMA SYNC PARTIAL - Some mismatches remain")
        print("="*70 + "\n")
        
        return 0 if all_synced else 1
        
    except Exception as e:
        print(f"\n❌ Schema sync failed: {e}")
        import traceback
        traceback.print_exc()
        us_session.rollback()
        return 1
    finally:
        kg_session.close()
        us_session.close()


if __name__ == "__main__":
    exit(main())

