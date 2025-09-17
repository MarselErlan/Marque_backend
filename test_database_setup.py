#!/usr/bin/env python3
"""
Test script to verify database setup for both KG and US markets
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection(database_name, database_url):
    """Test database connection and verify tables"""
    print(f"\n🔍 Testing {database_name} Database...")
    print("=" * 50)
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            # Get database version
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to {database_name}")
            print(f"📊 Database: {version[:50]}...")
            
            # Get all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            print(f"\n📋 Tables found: {len(tables)}")
            for table in tables:
                print(f"   ✅ {table}")
            
            # Test each table structure
            expected_tables = [
                'alembic_version',
                'phone_verifications', 
                'user_addresses',
                'user_notifications',
                'user_payment_methods',
                'users'
            ]
            
            print(f"\n🔍 Verifying table structure...")
            missing_tables = []
            for expected_table in expected_tables:
                if expected_table in tables:
                    # Get column info
                    result = conn.execute(text(f"""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_name = '{expected_table}'
                        ORDER BY ordinal_position
                    """))
                    columns = result.fetchall()
                    print(f"   ✅ {expected_table}: {len(columns)} columns")
                else:
                    missing_tables.append(expected_table)
                    print(f"   ❌ {expected_table}: MISSING")
            
            if missing_tables:
                print(f"\n⚠️  Missing tables: {missing_tables}")
                return False
            
            # Test inserting and querying data
            print(f"\n🧪 Testing data operations...")
            
            # Test users table
            test_user_data = {
                'phone_number': '+996700123456' if 'KG' in database_name else '+1234567890',
                'full_name': 'Test User',
                'market': 'KG' if 'KG' in database_name else 'US',
                'language': 'ru' if 'KG' in database_name else 'en',
                'country': 'Kyrgyzstan' if 'KG' in database_name else 'United States',
                'is_active': True,
                'is_verified': False
            }
            
            # Insert test user
            insert_query = text("""
                INSERT INTO users (phone_number, full_name, market, language, country, is_active, is_verified)
                VALUES (:phone_number, :full_name, :market, :language, :country, :is_active, :is_verified)
                RETURNING id
            """)
            
            result = conn.execute(insert_query, test_user_data)
            user_id = result.fetchone()[0]
            print(f"   ✅ Inserted test user with ID: {user_id}")
            
            # Query test user
            select_query = text("SELECT * FROM users WHERE id = :user_id")
            result = conn.execute(select_query, {'user_id': user_id})
            user = result.fetchone()
            
            if user:
                print(f"   ✅ Retrieved user: {user.full_name} ({user.phone_number})")
            else:
                print(f"   ❌ Failed to retrieve user")
                return False
            
            # Test phone verification table
            verification_data = {
                'user_id': user_id,
                'phone_number': test_user_data['phone_number'],
                'verification_code': '123456',
                'is_used': False,
                'expires_at': '2024-12-31 23:59:59',
                'market': test_user_data['market']
            }
            
            insert_verification = text("""
                INSERT INTO phone_verifications (user_id, phone_number, verification_code, is_used, expires_at, market)
                VALUES (:user_id, :phone_number, :verification_code, :is_used, :expires_at, :market)
                RETURNING id
            """)
            
            result = conn.execute(insert_verification, verification_data)
            verification_id = result.fetchone()[0]
            print(f"   ✅ Inserted phone verification with ID: {verification_id}")
            
            # Clean up test data
            conn.execute(text("DELETE FROM phone_verifications WHERE id = :id"), {'id': verification_id})
            conn.execute(text("DELETE FROM users WHERE id = :id"), {'id': user_id})
            conn.commit()
            print(f"   ✅ Cleaned up test data")
            
            print(f"\n🎉 {database_name} database test PASSED!")
            return True
            
    except Exception as e:
        print(f"❌ Error testing {database_name}: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 DATABASE SETUP VERIFICATION TEST")
    print("=" * 60)
    
    # Get database URLs
    kg_url = os.getenv("DATABASE_URL_MARQUE_KG")
    us_url = os.getenv("DATABASE_URL_MARQUE_US")
    
    if not kg_url:
        print("❌ DATABASE_URL_MARQUE_KG not found in .env file")
        return 1
    
    if not us_url:
        print("❌ DATABASE_URL_MARQUE_US not found in .env file")
        return 1
    
    print(f"📋 Found database URLs:")
    print(f"   🇰🇬 KG: {kg_url[:50]}...")
    print(f"   🇺🇸 US: {us_url[:50]}...")
    
    # Test both databases
    kg_success = test_database_connection("KG Market", kg_url)
    us_success = test_database_connection("US Market", us_url)
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY:")
    print(f"   🇰🇬 KG Market Database: {'✅ PASSED' if kg_success else '❌ FAILED'}")
    print(f"   🇺🇸 US Market Database: {'✅ PASSED' if us_success else '❌ FAILED'}")
    
    if kg_success and us_success:
        print("\n🎉 ALL TESTS PASSED! Both databases are set up correctly.")
        print("🚀 Ready for multi-market authentication system!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
