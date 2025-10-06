#!/usr/bin/env python3
"""
Verify Production Database Schema
Checks if all required columns exist in the production database
"""

import os
import sys
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

load_dotenv()

def verify_database_schema(db_url, market_name):
    """Verify that database has all required columns"""
    print(f"\n🔍 Checking {market_name} Database Schema...")
    print("=" * 50)
    
    try:
        engine = create_engine(db_url)
        inspector = inspect(engine)
        
        # Check if users table exists
        if 'users' not in inspector.get_table_names():
            print(f"❌ CRITICAL: 'users' table does not exist!")
            return False
        
        print(f"✅ 'users' table exists")
        
        # Get columns
        columns = {col['name']: col['type'] for col in inspector.get_columns('users')}
        
        # Required columns for multi-market architecture
        required_columns = {
            'id': 'INTEGER',
            'phone_number': 'VARCHAR',
            'full_name': 'VARCHAR',
            'market': 'VARCHAR',  # CRITICAL
            'language': 'VARCHAR',  # CRITICAL
            'country': 'VARCHAR',  # CRITICAL
            'is_active': 'BOOLEAN',
            'is_verified': 'BOOLEAN',
            'created_at': 'TIMESTAMP',
            'updated_at': 'TIMESTAMP'
        }
        
        missing_columns = []
        existing_columns = []
        
        for col_name, expected_type in required_columns.items():
            if col_name in columns:
                existing_columns.append(col_name)
                print(f"  ✅ {col_name} ({columns[col_name]})")
            else:
                missing_columns.append(col_name)
                print(f"  ❌ {col_name} - MISSING!")
        
        # Check other tables
        other_required_tables = [
            'products',
            'skus',
            'categories',
            'banners',
            'carts',
            'cart_items',
            'wishlists',
            'wishlist_items',
            'phone_verifications'
        ]
        
        print(f"\n📊 Checking other tables...")
        for table in other_required_tables:
            if table in inspector.get_table_names():
                print(f"  ✅ {table}")
            else:
                print(f"  ⚠️  {table} - not found")
        
        # Summary
        print(f"\n" + "=" * 50)
        if missing_columns:
            print(f"❌ SCHEMA INCOMPLETE - Missing {len(missing_columns)} columns:")
            for col in missing_columns:
                print(f"   - {col}")
            print(f"\n🔧 FIX: Run migrations with:")
            print(f"   alembic upgrade head")
            return False
        else:
            print(f"✅ ALL REQUIRED COLUMNS PRESENT ({len(existing_columns)}/{len(required_columns)})")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    """Main verification function"""
    print("\n🚀 Marque Production Database Verification")
    print("=" * 50)
    
    # Get database URLs from environment
    kg_db_url = os.getenv('DATABASE_URL_MARQUE_KG') or os.getenv('DATABASE_URL_KG')
    us_db_url = os.getenv('DATABASE_URL_MARQUE_US') or os.getenv('DATABASE_URL_US')
    
    if not kg_db_url and not us_db_url:
        print("❌ ERROR: No database URLs found!")
        print("Set DATABASE_URL_MARQUE_KG and DATABASE_URL_MARQUE_US")
        sys.exit(1)
    
    results = {}
    
    # Verify KG database
    if kg_db_url:
        results['KG'] = verify_database_schema(kg_db_url, 'KG (Kyrgyzstan)')
    else:
        print("\n⚠️  KG database URL not configured")
        results['KG'] = None
    
    # Verify US database
    if us_db_url:
        results['US'] = verify_database_schema(us_db_url, 'US (United States)')
    else:
        print("\n⚠️  US database URL not configured")
        results['US'] = None
    
    # Final summary
    print("\n" + "=" * 50)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 50)
    
    all_good = True
    for market, result in results.items():
        if result is None:
            print(f"⚠️  {market}: Not configured")
        elif result:
            print(f"✅ {market}: Schema OK")
        else:
            print(f"❌ {market}: Schema INCOMPLETE - NEEDS MIGRATION")
            all_good = False
    
    print("=" * 50)
    
    if all_good and any(results.values()):
        print("\n✅ ALL DATABASES READY FOR PRODUCTION! 🎉")
        sys.exit(0)
    else:
        print("\n❌ ACTION REQUIRED: Run migrations to fix database schema")
        print("\nQuick Fix:")
        print("  1. Install Railway CLI: npm i -g @railway/cli")
        print("  2. Login: railway login")
        print("  3. Link project: railway link")
        print("  4. Run migrations: ./railway_migrate.sh")
        print("\nOr check: PRODUCTION_DATABASE_FIX.md")
        sys.exit(1)

if __name__ == '__main__':
    main()

