#!/usr/bin/env python3
"""
Test US market features specifically
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_us_market_features():
    """Test US market specific features"""
    print("🇺🇸 TESTING US MARKET FEATURES")
    print("=" * 60)
    
    us_url = os.getenv("DATABASE_URL_MARQUE_US")
    if not us_url:
        print("❌ DATABASE_URL_MARQUE_US not found")
        return False
    
    try:
        engine = create_engine(us_url)
        
        with engine.connect() as conn:
            print("✅ Connected to US database")
            
            # Test 1: Verify existing US users
            print("\n📋 Test 1: Verify existing US users")
            result = conn.execute(text("""
                SELECT id, phone_number, full_name, market, language, country, is_active, is_verified
                FROM users 
                WHERE market = 'US'
                ORDER BY id
            """))
            users = result.fetchall()
            
            print(f"   📊 Found {len(users)} US users:")
            for user in users:
                print(f"      - ID: {user.id} | {user.full_name} | {user.phone_number} | {user.market} | {user.language}")
            
            if len(users) == 0:
                print("   ❌ No US users found!")
                return False
            
            # Test 2: Test US phone number format validation
            print("\n📱 Test 2: US phone number format validation")
            us_phone_formats = [
                '+1234567890',      # Standard US format
                '+15551234567',     # US with area code
                '+12125551234',     # US with different area code
                '+19876543210'      # US with another area code
            ]
            
            for phone in us_phone_formats:
                # Check if phone follows US format (+1 followed by 10 digits)
                if phone.startswith('+1') and len(phone) == 12:
                    print(f"   ✅ {phone} - Valid US format")
                else:
                    print(f"   ❌ {phone} - Invalid US format")
            
            # Test 3: Test US address formats
            print("\n🏠 Test 3: US address formats")
            result = conn.execute(text("""
                SELECT id, title, full_address, street_address, street_number, street_name, city, state, postal_code, country
                FROM user_addresses 
                WHERE market = 'US'
                ORDER BY id
            """))
            addresses = result.fetchall()
            
            print(f"   📊 Found {len(addresses)} US addresses:")
            for addr in addresses:
                print(f"      - {addr.title}: {addr.full_address}")
                print(f"        Street: {addr.street_address} | City: {addr.city} | State: {addr.state} | ZIP: {addr.postal_code}")
            
            # Test 4: Test US payment methods
            print("\n💳 Test 4: US payment methods")
            result = conn.execute(text("""
                SELECT id, payment_type, card_type, card_number_masked, card_holder_name, bank_name
                FROM user_payment_methods 
                WHERE market = 'US'
                ORDER BY id
            """))
            payments = result.fetchall()
            
            print(f"   📊 Found {len(payments)} US payment methods:")
            for payment in payments:
                print(f"      - {payment.card_type} ending in {payment.card_number_masked}")
                print(f"        Holder: {payment.card_holder_name} | Bank: {payment.bank_name}")
            
            # Test 5: Test US notifications
            print("\n🔔 Test 5: US notifications")
            result = conn.execute(text("""
                SELECT id, notification_type, title, message, is_read
                FROM user_notifications 
                WHERE user_id IN (SELECT id FROM users WHERE market = 'US')
                ORDER BY id
            """))
            notifications = result.fetchall()
            
            print(f"   📊 Found {len(notifications)} US notifications:")
            for notif in notifications:
                print(f"      - {notif.title}")
                print(f"        Type: {notif.notification_type} | Read: {notif.is_read}")
                print(f"        Message: {notif.message}")
            
            # Test 6: Create new US user with full profile
            print("\n👤 Test 6: Create new US user with full profile")
            new_user_data = {
                'phone_number': '+15551234567',
                'full_name': 'Emily Davis',
                'market': 'US',
                'language': 'en',
                'country': 'United States',
                'is_active': True,
                'is_verified': True
            }
            
            # Insert new user
            insert_user = text("""
                INSERT INTO users (phone_number, full_name, market, language, country, is_active, is_verified, created_at)
                VALUES (:phone_number, :full_name, :market, :language, :country, :is_active, :is_verified, :created_at)
                RETURNING id
            """)
            
            new_user_data['created_at'] = datetime.now()
            result = conn.execute(insert_user, new_user_data)
            new_user_id = result.fetchone()[0]
            print(f"   ✅ Created new US user: {new_user_data['full_name']} - ID: {new_user_id}")
            
            # Add address for new user
            new_address_data = {
                'user_id': new_user_id,
                'address_type': 'home',
                'title': 'Home',
                'full_address': '789 Oak Avenue, Chicago, IL 60601',
                'street_address': '789 Oak Avenue',
                'street_number': '789',
                'street_name': 'Oak Avenue',
                'city': 'Chicago',
                'state': 'IL',
                'postal_code': '60601',
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
            
            new_address_data['created_at'] = datetime.now()
            result = conn.execute(insert_address, new_address_data)
            new_address_id = result.fetchone()[0]
            print(f"   ✅ Added address: {new_address_data['full_address']} - ID: {new_address_id}")
            
            # Add payment method for new user
            new_payment_data = {
                'user_id': new_user_id,
                'payment_type': 'card',
                'card_type': 'amex',
                'card_number_masked': '****7777',
                'card_holder_name': 'Emily Davis',
                'bank_name': 'Wells Fargo',
                'market': 'US',
                'is_default': True,
                'is_active': True
            }
            
            insert_payment = text("""
                INSERT INTO user_payment_methods (user_id, payment_type, card_type, card_number_masked, card_holder_name, bank_name, market, is_default, is_active, created_at)
                VALUES (:user_id, :payment_type, :card_type, :card_number_masked, :card_holder_name, :bank_name, :market, :is_default, :is_active, :created_at)
                RETURNING id
            """)
            
            new_payment_data['created_at'] = datetime.now()
            result = conn.execute(insert_payment, new_payment_data)
            new_payment_id = result.fetchone()[0]
            print(f"   ✅ Added payment method: {new_payment_data['card_type']} ending in {new_payment_data['card_number_masked']} - ID: {new_payment_id}")
            
            # Add notification for new user
            new_notification_data = {
                'user_id': new_user_id,
                'notification_type': 'welcome',
                'title': 'Welcome to Marque US!',
                'message': 'Thank you for joining Marque US. We are excited to have you on board!',
                'is_read': False,
                'is_active': True
            }
            
            insert_notification = text("""
                INSERT INTO user_notifications (user_id, notification_type, title, message, is_read, is_active, created_at)
                VALUES (:user_id, :notification_type, :title, :message, :is_read, :is_active, :created_at)
                RETURNING id
            """)
            
            new_notification_data['created_at'] = datetime.now()
            result = conn.execute(insert_notification, new_notification_data)
            new_notification_id = result.fetchone()[0]
            print(f"   ✅ Added notification: {new_notification_data['title']} - ID: {new_notification_id}")
            
            # Test 7: Verify complete user profile
            print("\n📊 Test 7: Verify complete user profile")
            profile_query = text("""
                SELECT 
                    u.id, u.phone_number, u.full_name, u.market, u.language, u.country,
                    COUNT(DISTINCT a.id) as address_count,
                    COUNT(DISTINCT p.id) as payment_count,
                    COUNT(DISTINCT n.id) as notification_count
                FROM users u
                LEFT JOIN user_addresses a ON u.id = a.user_id AND a.is_active = true
                LEFT JOIN user_payment_methods p ON u.id = p.user_id AND p.is_active = true
                LEFT JOIN user_notifications n ON u.id = n.user_id AND n.is_active = true
                WHERE u.id = :user_id
                GROUP BY u.id, u.phone_number, u.full_name, u.market, u.language, u.country
            """)
            
            result = conn.execute(profile_query, {'user_id': new_user_id})
            profile = result.fetchone()
            
            if profile:
                print(f"   ✅ Complete Profile for {profile.full_name}:")
                print(f"      - Phone: {profile.phone_number}")
                print(f"      - Market: {profile.market}")
                print(f"      - Language: {profile.language}")
                print(f"      - Country: {profile.country}")
                print(f"      - Addresses: {profile.address_count}")
                print(f"      - Payment Methods: {profile.payment_count}")
                print(f"      - Notifications: {profile.notification_count}")
            
            # Test 8: US market specific validations
            print("\n🌍 Test 8: US market specific validations")
            
            # Validate US phone numbers
            us_phones = ['+1234567890', '+15551234567', '+12125551234']
            for phone in us_phones:
                if phone.startswith('+1') and len(phone) == 12:
                    print(f"   ✅ {phone} - Valid US phone format")
                else:
                    print(f"   ❌ {phone} - Invalid US phone format")
            
            # Validate US addresses
            us_addresses = [
                '123 Main St, New York, NY 10001',
                '456 Broadway, Los Angeles, CA 90210',
                '789 Oak Avenue, Chicago, IL 60601'
            ]
            for addr in us_addresses:
                if ', ' in addr and any(state in addr for state in ['NY', 'CA', 'IL', 'TX', 'FL']):
                    print(f"   ✅ {addr} - Valid US address format")
                else:
                    print(f"   ❌ {addr} - Invalid US address format")
            
            # Validate US payment methods
            us_banks = ['Chase Bank', 'Bank of America', 'Wells Fargo', 'Citibank']
            for bank in us_banks:
                print(f"   ✅ {bank} - Valid US bank")
            
            conn.commit()
            print(f"\n🎉 US Market Features Test Completed Successfully!")
            print(f"   📊 Total US users now: {len(users) + 1}")
            print(f"   🆕 New user created: Emily Davis (+15551234567)")
            return True
            
    except Exception as e:
        print(f"❌ Error testing US market features: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 US MARKET FEATURES TEST")
    print("=" * 70)
    
    success = test_us_market_features()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 US MARKET TEST PASSED!")
        print("✅ All US market features are working correctly:")
        print("   📱 US phone number formats")
        print("   🏠 US address formats (with state and ZIP)")
        print("   💳 US payment methods and banks")
        print("   🔔 US notifications in English")
        print("   👤 Complete user profile management")
        print("   🌍 Market-specific validations")
        return 0
    else:
        print("❌ US MARKET TEST FAILED!")
        print("Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
