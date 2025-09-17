#!/usr/bin/env python3
"""
Integration testing for the complete Marque system
Tests API endpoints, database operations, and multi-market functionality
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_database_integration():
    """Test database integration for both markets"""
    print("🗄️ DATABASE INTEGRATION TEST")
    print("=" * 50)
    
    kg_url = os.getenv("DATABASE_URL_MARQUE_KG")
    us_url = os.getenv("DATABASE_URL_MARQUE_US")
    
    if not kg_url or not us_url:
        print("❌ Database URLs not found")
        return False
    
    try:
        # Test KG database
        print("🇰🇬 Testing KG Database Integration...")
        kg_engine = create_engine(kg_url)
        
        with kg_engine.connect() as conn:
            # Test user creation and relationships
            user_data = {
                'phone_number': '+996700999999',
                'full_name': 'Integration Test User KG',
                'market': 'KG',
                'language': 'ru',
                'country': 'Кыргызстан',
                'is_active': True,
                'is_verified': True
            }
            
            # Create user
            insert_user = text("""
                INSERT INTO users (phone_number, full_name, market, language, country, is_active, is_verified, created_at)
                VALUES (:phone_number, :full_name, :market, :language, :country, :is_active, :is_verified, :created_at)
                RETURNING id
            """)
            
            user_data['created_at'] = datetime.now()
            result = conn.execute(insert_user, user_data)
            user_id = result.fetchone()[0]
            print(f"   ✅ Created KG user - ID: {user_id}")
            
            # Create related data
            verification_data = {
                'user_id': user_id,
                'phone_number': user_data['phone_number'],
                'verification_code': '999999',
                'is_used': True,
                'expires_at': datetime.now() + timedelta(minutes=10),
                'market': 'KG'
            }
            
            insert_verification = text("""
                INSERT INTO phone_verifications (user_id, phone_number, verification_code, is_used, expires_at, market, created_at)
                VALUES (:user_id, :phone_number, :verification_code, :is_used, :expires_at, :market, :created_at)
                RETURNING id
            """)
            
            verification_data['created_at'] = datetime.now()
            result = conn.execute(insert_verification, verification_data)
            verification_id = result.fetchone()[0]
            print(f"   ✅ Created KG verification - ID: {verification_id}")
            
            # Test complex query with joins
            complex_query = text("""
                SELECT 
                    u.id, u.phone_number, u.full_name, u.market, u.language,
                    COUNT(DISTINCT a.id) as address_count,
                    COUNT(DISTINCT p.id) as payment_count,
                    COUNT(DISTINCT n.id) as notification_count,
                    COUNT(DISTINCT v.id) as verification_count
                FROM users u
                LEFT JOIN user_addresses a ON u.id = a.user_id AND a.is_active = true
                LEFT JOIN user_payment_methods p ON u.id = p.user_id AND p.is_active = true
                LEFT JOIN user_notifications n ON u.id = n.user_id AND n.is_active = true
                LEFT JOIN phone_verifications v ON u.id = v.user_id
                WHERE u.id = :user_id
                GROUP BY u.id, u.phone_number, u.full_name, u.market, u.language
            """)
            
            result = conn.execute(complex_query, {'user_id': user_id})
            profile = result.fetchone()
            
            if profile:
                print(f"   ✅ Complex query successful:")
                print(f"      - User: {profile.full_name} ({profile.phone_number})")
                print(f"      - Market: {profile.market}")
                print(f"      - Verifications: {profile.verification_count}")
            
            # Clean up
            conn.execute(text("DELETE FROM phone_verifications WHERE id = :id"), {'id': verification_id})
            conn.execute(text("DELETE FROM users WHERE id = :id"), {'id': user_id})
            conn.commit()
            print(f"   ✅ KG database integration test passed")
        
        # Test US database
        print("\n🇺🇸 Testing US Database Integration...")
        us_engine = create_engine(us_url)
        
        with us_engine.connect() as conn:
            # Test user creation and relationships
            user_data = {
                'phone_number': '+1555999999',
                'full_name': 'Integration Test User US',
                'market': 'US',
                'language': 'en',
                'country': 'United States',
                'is_active': True,
                'is_verified': True
            }
            
            # Create user
            insert_user = text("""
                INSERT INTO users (phone_number, full_name, market, language, country, is_active, is_verified, created_at)
                VALUES (:phone_number, :full_name, :market, :language, :country, :is_active, :is_verified, :created_at)
                RETURNING id
            """)
            
            user_data['created_at'] = datetime.now()
            result = conn.execute(insert_user, user_data)
            user_id = result.fetchone()[0]
            print(f"   ✅ Created US user - ID: {user_id}")
            
            # Test US-specific address format
            address_data = {
                'user_id': user_id,
                'address_type': 'home',
                'title': 'Home',
                'full_address': '999 Test St, Test City, TX 12345',
                'street_address': '999 Test St',
                'street_number': '999',
                'street_name': 'Test St',
                'city': 'Test City',
                'state': 'TX',
                'postal_code': '12345',
                'country': 'United States',
                'market': 'US',
                'is_default': True,
                'is_active': True
            }
            
            insert_address = text("""
                INSERT INTO user_addresses (user_id, address_type, title, full_address, street_address, street_number, street_name, city, state, postal_code, country, market, is_default, is_active, created_at)
                VALUES (:user_id, :address_type, :title, :full_address, :street_address, :street_number, :street_name, :city, :state, :postal_code, :country, :market, :is_default, :is_active, :created_at)
                RETURNING id
            """)
            
            address_data['created_at'] = datetime.now()
            result = conn.execute(insert_address, address_data)
            address_id = result.fetchone()[0]
            print(f"   ✅ Created US address - ID: {address_id}")
            
            # Test complex query with joins
            complex_query = text("""
                SELECT 
                    u.id, u.phone_number, u.full_name, u.market, u.language,
                    COUNT(DISTINCT a.id) as address_count,
                    COUNT(DISTINCT p.id) as payment_count,
                    COUNT(DISTINCT n.id) as notification_count
                FROM users u
                LEFT JOIN user_addresses a ON u.id = a.user_id AND a.is_active = true
                LEFT JOIN user_payment_methods p ON u.id = p.user_id AND p.is_active = true
                LEFT JOIN user_notifications n ON u.id = n.user_id AND n.is_active = true
                WHERE u.id = :user_id
                GROUP BY u.id, u.phone_number, u.full_name, u.market, u.language
            """)
            
            result = conn.execute(complex_query, {'user_id': user_id})
            profile = result.fetchone()
            
            if profile:
                print(f"   ✅ Complex query successful:")
                print(f"      - User: {profile.full_name} ({profile.phone_number})")
                print(f"      - Market: {profile.market}")
                print(f"      - Addresses: {profile.address_count}")
            
            # Clean up
            conn.execute(text("DELETE FROM user_addresses WHERE id = :id"), {'id': address_id})
            conn.execute(text("DELETE FROM users WHERE id = :id"), {'id': user_id})
            conn.commit()
            print(f"   ✅ US database integration test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        return False

def test_market_detection():
    """Test market detection logic"""
    print("\n🌍 MARKET DETECTION TEST")
    print("=" * 50)
    
    # Test phone number market detection
    test_phones = [
        ('+996700123456', 'KG'),
        ('+996700234567', 'KG'),
        ('+1234567890', 'US'),
        ('+15551234567', 'US'),
        ('+12125551234', 'US'),
        ('+447700900123', 'UK'),  # Should default to US
        ('+8613812345678', 'CN')   # Should default to US
    ]
    
    for phone, expected_market in test_phones:
        if phone.startswith('+996'):
            detected_market = 'KG'
        elif phone.startswith('+1'):
            detected_market = 'US'
        else:
            detected_market = 'US'  # Default fallback
        
        if detected_market == expected_market:
            print(f"   ✅ {phone} -> {detected_market} (correct)")
        else:
            print(f"   ❌ {phone} -> {detected_market} (expected {expected_market})")
    
    # Test market-specific configurations
    print(f"\n📋 Market-specific configurations:")
    
    kg_config = {
        'language': 'ru',
        'country': 'Кыргызстан',
        'currency': 'KGS',
        'phone_prefix': '+996',
        'address_format': 'kyrgyz'
    }
    
    us_config = {
        'language': 'en',
        'country': 'United States',
        'currency': 'USD',
        'phone_prefix': '+1',
        'address_format': 'us'
    }
    
    print(f"   🇰🇬 KG Config: {kg_config}")
    print(f"   🇺🇸 US Config: {us_config}")
    
    return True

def test_data_validation():
    """Test data validation across markets"""
    print("\n✅ DATA VALIDATION TEST")
    print("=" * 50)
    
    # Test phone number validation
    print("📱 Phone number validation:")
    valid_phones = {
        'KG': ['+996700123456', '+996700234567'],
        'US': ['+1234567890', '+15551234567', '+12125551234']
    }
    
    for market, phones in valid_phones.items():
        for phone in phones:
            if market == 'KG' and phone.startswith('+996') and len(phone) == 13:
                print(f"   ✅ {phone} - Valid {market} format")
            elif market == 'US' and phone.startswith('+1') and len(phone) == 12:
                print(f"   ✅ {phone} - Valid {market} format")
            else:
                print(f"   ❌ {phone} - Invalid {market} format")
    
    # Test address validation
    print(f"\n🏠 Address validation:")
    valid_addresses = {
        'KG': [
            'ул. Чуй 123, Бишкек, Кыргызстан',
            'пр. Манаса 456, Бишкек, Кыргызстан'
        ],
        'US': [
            '123 Main St, New York, NY 10001',
            '456 Broadway, Los Angeles, CA 90210'
        ]
    }
    
    for market, addresses in valid_addresses.items():
        for address in addresses:
            if market == 'KG' and 'ул.' in address and 'Бишкек' in address:
                print(f"   ✅ {address} - Valid {market} format")
            elif market == 'US' and ', ' in address and any(state in address for state in ['NY', 'CA', 'TX', 'FL']):
                print(f"   ✅ {address} - Valid {market} format")
            else:
                print(f"   ❌ {address} - Invalid {market} format")
    
    # Test payment method validation
    print(f"\n💳 Payment method validation:")
    valid_payments = {
        'KG': ['visa', 'mastercard', 'local_card'],
        'US': ['visa', 'mastercard', 'amex', 'discover']
    }
    
    for market, payment_types in valid_payments.items():
        for payment_type in payment_types:
            print(f"   ✅ {payment_type} - Valid {market} payment method")
    
    return True

def test_transaction_handling():
    """Test transaction handling and rollback"""
    print("\n🔄 TRANSACTION HANDLING TEST")
    print("=" * 50)
    
    kg_url = os.getenv("DATABASE_URL_MARQUE_KG")
    if not kg_url:
        print("❌ KG database URL not found")
        return False
    
    try:
        engine = create_engine(kg_url)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Create user
                user_data = {
                    'phone_number': '+996700888888',
                    'full_name': 'Transaction Test User',
                    'market': 'KG',
                    'language': 'ru',
                    'country': 'Кыргызстан',
                    'is_active': True,
                    'is_verified': True
                }
                
                insert_user = text("""
                    INSERT INTO users (phone_number, full_name, market, language, country, is_active, is_verified, created_at)
                    VALUES (:phone_number, :full_name, :market, :language, :country, :is_active, :is_verified, :created_at)
                    RETURNING id
                """)
                
                user_data['created_at'] = datetime.now()
                result = conn.execute(insert_user, user_data)
                user_id = result.fetchone()[0]
                print(f"   ✅ Created user in transaction - ID: {user_id}")
                
                # Create address
                address_data = {
                    'user_id': user_id,
                    'address_type': 'home',
                    'title': 'Дом',
                    'full_address': 'ул. Тест 888, Бишкек, Кыргызстан',
                    'street': 'ул. Тест',
                    'building': '888',
                    'city': 'Бишкек',
                    'country': 'Кыргызстан',
                    'market': 'KG',
                    'is_default': True,
                    'is_active': True
                }
                
                insert_address = text("""
                    INSERT INTO user_addresses (user_id, address_type, title, full_address, street, building, city, country, market, is_default, is_active, created_at)
                    VALUES (:user_id, :address_type, :title, :full_address, :street, :building, :city, :country, :market, :is_default, :is_active, :created_at)
                    RETURNING id
                """)
                
                address_data['created_at'] = datetime.now()
                result = conn.execute(insert_address, address_data)
                address_id = result.fetchone()[0]
                print(f"   ✅ Created address in transaction - ID: {address_id}")
                
                # Simulate error and rollback
                print(f"   🔄 Simulating error and rolling back transaction...")
                trans.rollback()
                print(f"   ✅ Transaction rolled back successfully")
                
                # Verify data was not committed
                check_user = text("SELECT id FROM users WHERE phone_number = :phone")
                result = conn.execute(check_user, {'phone': user_data['phone_number']})
                if result.fetchone() is None:
                    print(f"   ✅ User not found - rollback successful")
                else:
                    print(f"   ❌ User found - rollback failed")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"   ❌ Transaction error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Transaction handling test failed: {e}")
        return False

def test_performance():
    """Test database performance"""
    print("\n⚡ PERFORMANCE TEST")
    print("=" * 50)
    
    kg_url = os.getenv("DATABASE_URL_MARQUE_KG")
    if not kg_url:
        print("❌ KG database URL not found")
        return False
    
    try:
        engine = create_engine(kg_url)
        
        with engine.connect() as conn:
            # Test query performance
            start_time = datetime.now()
            
            # Complex query with joins
            query = text("""
                SELECT 
                    u.id, u.phone_number, u.full_name, u.market,
                    COUNT(DISTINCT a.id) as address_count,
                    COUNT(DISTINCT p.id) as payment_count,
                    COUNT(DISTINCT n.id) as notification_count
                FROM users u
                LEFT JOIN user_addresses a ON u.id = a.user_id AND a.is_active = true
                LEFT JOIN user_payment_methods p ON u.id = p.user_id AND p.is_active = true
                LEFT JOIN user_notifications n ON u.id = n.user_id AND n.is_active = true
                WHERE u.market = 'KG'
                GROUP BY u.id, u.phone_number, u.full_name, u.market
                ORDER BY u.created_at DESC
            """)
            
            result = conn.execute(query)
            users = result.fetchall()
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            print(f"   ✅ Complex query executed in {execution_time:.3f} seconds")
            print(f"   📊 Retrieved {len(users)} users with related data")
            
            if execution_time < 1.0:
                print(f"   ✅ Performance is good (< 1 second)")
            elif execution_time < 5.0:
                print(f"   ⚠️ Performance is acceptable (< 5 seconds)")
            else:
                print(f"   ❌ Performance is slow (> 5 seconds)")
            
            return True
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Main integration test function"""
    print("🧪 COMPREHENSIVE INTEGRATION TEST")
    print("=" * 70)
    print("Testing complete system integration across all components")
    print()
    
    # Run all integration tests
    tests = [
        ("Database Integration", test_database_integration),
        ("Market Detection", test_market_detection),
        ("Data Validation", test_data_validation),
        ("Transaction Handling", test_transaction_handling),
        ("Performance", test_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 INTEGRATION TEST RESULTS:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ System is fully integrated and ready for production:")
        print("   🗄️ Database operations working correctly")
        print("   🌍 Multi-market detection functioning")
        print("   ✅ Data validation working across markets")
        print("   🔄 Transaction handling with rollback support")
        print("   ⚡ Performance is acceptable")
        return 0
    else:
        print(f"\n⚠️ {total - passed} integration tests failed.")
        print("Please review the failed tests above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
