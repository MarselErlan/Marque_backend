"""
Check which database/market has user_id 19
"""
import os
from sqlalchemy import create_engine, text

# Railway database URLs
DATABASE_URL_US = os.getenv("DATABASE_URL_US", "")
DATABASE_URL_KG = os.getenv("DATABASE_URL_KG", "")

print("\n🔍 CHECKING USER 19 IN DATABASES\n")

# Check US database
if DATABASE_URL_US:
    print("Checking US database...")
    engine_us = create_engine(DATABASE_URL_US)
    with engine_us.connect() as conn:
        result = conn.execute(text("SELECT id, phone_number, market FROM users WHERE id = 19"))
        user = result.fetchone()
        if user:
            print(f"✅ User 19 found in US database!")
            print(f"   Phone: {user[1]}, Market: {user[2]}")
        else:
            print(f"❌ User 19 NOT found in US database")

# Check KG database  
if DATABASE_URL_KG:
    print("\nChecking KG database...")
    engine_kg = create_engine(DATABASE_URL_KG)
    with engine_kg.connect() as conn:
        result = conn.execute(text("SELECT id, phone_number, market FROM users WHERE id = 19"))
        user = result.fetchone()
        if user:
            print(f"✅ User 19 found in KG database!")
            print(f"   Phone: {user[1]}, Market: {user[2]}")
        else:
            print(f"❌ User 19 NOT found in KG database")

print("\n" + "="*60)
print("SOLUTION:")
print("="*60)
print("Use the market where user 19 exists when testing wishlist")
print("Update your test script to use the correct market (us or kg)")

