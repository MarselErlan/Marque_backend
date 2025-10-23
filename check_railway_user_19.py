"""
Quick script to find User ID 19 in Railway Production
"""

import os
from sqlalchemy import create_engine, text

# Use the same DATABASE_URL we used for fixing images
RAILWAY_DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:YgyDmMbYyzPKvSsNyDRShLJqehXtTdJx@metro.proxy.rlwy.net:45504/railway")

print("🔍 Searching for User ID 19 in Railway Production Database")
print("=" * 80)
print(f"Database: {RAILWAY_DB_URL[:50]}...")
print()

try:
    engine = create_engine(RAILWAY_DB_URL)
    
    with engine.connect() as conn:
        # Check if User ID 19 exists
        print("1️⃣ Looking for User ID 19...")
        user_19 = conn.execute(text('''
            SELECT id, phone_number, full_name, is_active, is_verified, 
                   last_login, created_at
            FROM users
            WHERE id = 19
        ''')).fetchone()
        
        if user_19:
            print("✅ FOUND User ID 19!")
            print(f"  Phone: {user_19[1]}")
            print(f"  Name: {user_19[2] or 'Not set'}")
            print(f"  is_active: {user_19[3]}")
            print(f"  is_verified: {user_19[4]}")
            print(f"  last_login: {user_19[5]}")
            print(f"  created_at: {user_19[6]}")
        else:
            print("❌ User ID 19 NOT FOUND in this database")
        
        print()
        print("2️⃣ All users in this database:")
        print("-" * 80)
        
        all_users = conn.execute(text('''
            SELECT id, phone_number, full_name, is_active, is_verified
            FROM users
            ORDER BY id DESC
            LIMIT 20
        ''')).fetchall()
        
        print(f"Total users (showing last 20): {len(all_users)}")
        print()
        
        for user in all_users:
            print(f"User ID {user[0]}: {user[1]} - {user[2] or 'No name'}")
            print(f"  Active: {user[3]}, Verified: {user[4]}")
        
        print()
        print("3️⃣ Database statistics:")
        print("-" * 80)
        
        stats = conn.execute(text('''
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN phone_number LIKE '+996%' THEN 1 END) as kg_users,
                COUNT(CASE WHEN phone_number LIKE '+1%' THEN 1 END) as us_users,
                COUNT(CASE WHEN is_active = true THEN 1 END) as active_users,
                COUNT(CASE WHEN is_verified = true THEN 1 END) as verified_users
            FROM users
        ''')).fetchone()
        
        print(f"  Total users: {stats[0]}")
        print(f"  KG users (+996): {stats[1]}")
        print(f"  US users (+1): {stats[2]}")
        print(f"  Active: {stats[3]}")
        print(f"  Verified: {stats[4]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("This might mean:")
    print("1. The DATABASE_URL is for KG market (doesn't have User 19)")
    print("2. User 19 is in DATABASE_URL_MARQUE_US (different database)")
    print()
    print("To check US database, run:")
    print("  export DATABASE_URL='your_DATABASE_URL_MARQUE_US_value'")
    print("  python3 check_railway_user_19.py")

print()
print("=" * 80)
print("💡 TIP: Check Railway Variables for DATABASE_URL_MARQUE_US")

