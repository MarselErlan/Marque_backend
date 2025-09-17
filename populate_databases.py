#!/usr/bin/env python3
"""
Populate databases with real user data for both KG and US markets
This will create persistent data visible in Railway dashboard
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def populate_kg_database():
    """Populate KG database with real user data"""
    print("🇰🇬 Populating KG Database with Real User Data...")
    print("=" * 50)
    
    kg_url = os.getenv("DATABASE_URL_MARQUE_KG")
    if not kg_url:
        print("❌ DATABASE_URL_MARQUE_KG not found")
        return False
    
    try:
        engine = create_engine(kg_url)
        
        with engine.connect() as conn:
            # Create real KG users
            kg_users = [
                {
                    'phone_number': '+996700123456',
                    'full_name': 'Айбек Токтогулов',
                    'market': 'KG',
                    'language': 'ru',
                    'country': 'Кыргызстан',
                    'is_active': True,
                    'is_verified': True
                },
                {
                    'phone_number': '+996700234567',
                    'full_name': 'Айнура Касымова',
                    'market': 'KG',
                    'language': 'ru',
                    'country': 'Кыргызстан',
                    'is_active': True,
                    'is_verified': True
                },
                {
                    'phone_number': '+996700345678',
                    'full_name': 'Эрлан Беков',
                    'market': 'KG',
                    'language': 'ru',
                    'country': 'Кыргызстан',
                    'is_active': True,
                    'is_verified': False
                }
            ]
            
            user_ids = []
            for user_data in kg_users:
                # Insert user
                insert_query = text("""
                    INSERT INTO users (phone_number, full_name, market, language, country, is_active, is_verified, created_at)
                    VALUES (:phone_number, :full_name, :market, :language, :country, :is_active, :is_verified, :created_at)
                    RETURNING id
                """)
                
                user_data['created_at'] = datetime.now()
                result = conn.execute(insert_query, user_data)
                user_id = result.fetchone()[0]
                user_ids.append(user_id)
                print(f"   ✅ Created user: {user_data['full_name']} ({user_data['phone_number']}) - ID: {user_id}")
            
            # Create addresses for users
            kg_addresses = [
                {
                    'user_id': user_ids[0],
                    'address_type': 'home',
                    'title': 'Дом',
                    'full_address': 'ул. Чуй 123, Бишкек, Кыргызстан',
                    'street': 'ул. Чуй',
                    'building': '123',
                    'city': 'Бишкек',
                    'country': 'Кыргызстан',
                    'market': 'KG',
                    'is_default': True,
                    'is_active': True
                },
                {
                    'user_id': user_ids[1],
                    'address_type': 'work',
                    'title': 'Работа',
                    'full_address': 'пр. Манаса 456, Бишкек, Кыргызстан',
                    'street': 'пр. Манаса',
                    'building': '456',
                    'city': 'Бишкек',
                    'country': 'Кыргызстан',
                    'market': 'KG',
                    'is_default': True,
                    'is_active': True
                }
            ]
            
            for address_data in kg_addresses:
                insert_address = text("""
                    INSERT INTO user_addresses (user_id, address_type, title, full_address, street, building, city, country, market, is_default, is_active, created_at)
                    VALUES (:user_id, :address_type, :title, :full_address, :street, :building, :city, :country, :market, :is_default, :is_active, :created_at)
                    RETURNING id
                """)
                
                address_data['created_at'] = datetime.now()
                result = conn.execute(insert_address, address_data)
                address_id = result.fetchone()[0]
                print(f"   ✅ Created address: {address_data['title']} - {address_data['full_address']} - ID: {address_id}")
            
            # Create payment methods
            kg_payments = [
                {
                    'user_id': user_ids[0],
                    'payment_type': 'card',
                    'card_type': 'visa',
                    'card_number_masked': '****1234',
                    'card_holder_name': 'Айбек Токтогулов',
                    'bank_name': 'Демир Банк',
                    'market': 'KG',
                    'is_default': True,
                    'is_active': True
                },
                {
                    'user_id': user_ids[1],
                    'payment_type': 'card',
                    'card_type': 'mastercard',
                    'card_number_masked': '****5678',
                    'card_holder_name': 'Айнура Касымова',
                    'bank_name': 'Айыл Банк',
                    'market': 'KG',
                    'is_default': True,
                    'is_active': True
                }
            ]
            
            for payment_data in kg_payments:
                insert_payment = text("""
                    INSERT INTO user_payment_methods (user_id, payment_type, card_type, card_number_masked, card_holder_name, bank_name, market, is_default, is_active, created_at)
                    VALUES (:user_id, :payment_type, :card_type, :card_number_masked, :card_holder_name, :bank_name, :market, :is_default, :is_active, :created_at)
                    RETURNING id
                """)
                
                payment_data['created_at'] = datetime.now()
                result = conn.execute(insert_payment, payment_data)
                payment_id = result.fetchone()[0]
                print(f"   ✅ Created payment method: {payment_data['card_type']} ending in {payment_data['card_number_masked']} - ID: {payment_id}")
            
            # Create notifications
            kg_notifications = [
                {
                    'user_id': user_ids[0],
                    'notification_type': 'welcome',
                    'title': 'Добро пожаловать в Marque!',
                    'message': 'Спасибо за регистрацию в Marque KG. Наслаждайтесь покупками!',
                    'is_read': False,
                    'is_active': True
                },
                {
                    'user_id': user_ids[1],
                    'notification_type': 'order',
                    'title': 'Заказ подтвержден',
                    'message': 'Ваш заказ #12345 был подтвержден и отправлен на обработку.',
                    'is_read': True,
                    'is_active': True
                }
            ]
            
            for notification_data in kg_notifications:
                insert_notification = text("""
                    INSERT INTO user_notifications (user_id, notification_type, title, message, is_read, is_active, created_at)
                    VALUES (:user_id, :notification_type, :title, :message, :is_read, :is_active, :created_at)
                    RETURNING id
                """)
                
                notification_data['created_at'] = datetime.now()
                result = conn.execute(insert_notification, notification_data)
                notification_id = result.fetchone()[0]
                print(f"   ✅ Created notification: {notification_data['title']} - ID: {notification_id}")
            
            conn.commit()
            print(f"\n🎉 KG Database populated successfully!")
            print(f"   📊 Created: {len(kg_users)} users, {len(kg_addresses)} addresses, {len(kg_payments)} payments, {len(kg_notifications)} notifications")
            return True
            
    except Exception as e:
        print(f"❌ Error populating KG database: {e}")
        return False

def populate_us_database():
    """Populate US database with real user data"""
    print("\n🇺🇸 Populating US Database with Real User Data...")
    print("=" * 50)
    
    us_url = os.getenv("DATABASE_URL_MARQUE_US")
    if not us_url:
        print("❌ DATABASE_URL_MARQUE_US not found")
        return False
    
    try:
        engine = create_engine(us_url)
        
        with engine.connect() as conn:
            # Create real US users
            us_users = [
                {
                    'phone_number': '+1234567890',
                    'full_name': 'John Smith',
                    'market': 'US',
                    'language': 'en',
                    'country': 'United States',
                    'is_active': True,
                    'is_verified': True
                },
                {
                    'phone_number': '+1234567891',
                    'full_name': 'Sarah Johnson',
                    'market': 'US',
                    'language': 'en',
                    'country': 'United States',
                    'is_active': True,
                    'is_verified': True
                },
                {
                    'phone_number': '+1234567892',
                    'full_name': 'Michael Brown',
                    'market': 'US',
                    'language': 'en',
                    'country': 'United States',
                    'is_active': True,
                    'is_verified': False
                }
            ]
            
            user_ids = []
            for user_data in us_users:
                # Insert user
                insert_query = text("""
                    INSERT INTO users (phone_number, full_name, market, language, country, is_active, is_verified, created_at)
                    VALUES (:phone_number, :full_name, :market, :language, :country, :is_active, :is_verified, :created_at)
                    RETURNING id
                """)
                
                user_data['created_at'] = datetime.now()
                result = conn.execute(insert_query, user_data)
                user_id = result.fetchone()[0]
                user_ids.append(user_id)
                print(f"   ✅ Created user: {user_data['full_name']} ({user_data['phone_number']}) - ID: {user_id}")
            
            # Create addresses for users (US format)
            us_addresses = [
                {
                    'user_id': user_ids[0],
                    'address_type': 'home',
                    'title': 'Home',
                    'full_address': '123 Main St, New York, NY 10001',
                    'street_address': '123 Main St',
                    'street_number': '123',
                    'street_name': 'Main St',
                    'city': 'New York',
                    'state': 'NY',
                    'postal_code': '10001',
                    'country': 'United States',
                    'market': 'US',
                    'is_default': True,
                    'is_active': True
                },
                {
                    'user_id': user_ids[1],
                    'address_type': 'work',
                    'title': 'Office',
                    'full_address': '456 Broadway, Los Angeles, CA 90210',
                    'street_address': '456 Broadway',
                    'street_number': '456',
                    'street_name': 'Broadway',
                    'city': 'Los Angeles',
                    'state': 'CA',
                    'postal_code': '90210',
                    'country': 'United States',
                    'market': 'US',
                    'is_default': True,
                    'is_active': True
                }
            ]
            
            for address_data in us_addresses:
                insert_address = text("""
                    INSERT INTO user_addresses (user_id, address_type, title, full_address, street_address, street_number, street_name, city, state, postal_code, country, market, is_default, is_active, created_at)
                    VALUES (:user_id, :address_type, :title, :full_address, :street_address, :street_number, :street_name, :city, :state, :postal_code, :country, :market, :is_default, :is_active, :created_at)
                    RETURNING id
                """)
                
                address_data['created_at'] = datetime.now()
                result = conn.execute(insert_address, address_data)
                address_id = result.fetchone()[0]
                print(f"   ✅ Created address: {address_data['title']} - {address_data['full_address']} - ID: {address_id}")
            
            # Create payment methods
            us_payments = [
                {
                    'user_id': user_ids[0],
                    'payment_type': 'card',
                    'card_type': 'visa',
                    'card_number_masked': '****9999',
                    'card_holder_name': 'John Smith',
                    'bank_name': 'Chase Bank',
                    'market': 'US',
                    'is_default': True,
                    'is_active': True
                },
                {
                    'user_id': user_ids[1],
                    'payment_type': 'card',
                    'card_type': 'mastercard',
                    'card_number_masked': '****8888',
                    'card_holder_name': 'Sarah Johnson',
                    'bank_name': 'Bank of America',
                    'market': 'US',
                    'is_default': True,
                    'is_active': True
                }
            ]
            
            for payment_data in us_payments:
                insert_payment = text("""
                    INSERT INTO user_payment_methods (user_id, payment_type, card_type, card_number_masked, card_holder_name, bank_name, market, is_default, is_active, created_at)
                    VALUES (:user_id, :payment_type, :card_type, :card_number_masked, :card_holder_name, :bank_name, :market, :is_default, :is_active, :created_at)
                    RETURNING id
                """)
                
                payment_data['created_at'] = datetime.now()
                result = conn.execute(insert_payment, payment_data)
                payment_id = result.fetchone()[0]
                print(f"   ✅ Created payment method: {payment_data['card_type']} ending in {payment_data['card_number_masked']} - ID: {payment_id}")
            
            # Create notifications
            us_notifications = [
                {
                    'user_id': user_ids[0],
                    'notification_type': 'welcome',
                    'title': 'Welcome to Marque!',
                    'message': 'Thank you for joining Marque US. Enjoy your shopping experience!',
                    'is_read': False,
                    'is_active': True
                },
                {
                    'user_id': user_ids[1],
                    'notification_type': 'order',
                    'title': 'Order Confirmed',
                    'message': 'Your order #67890 has been confirmed and is being processed.',
                    'is_read': True,
                    'is_active': True
                }
            ]
            
            for notification_data in us_notifications:
                insert_notification = text("""
                    INSERT INTO user_notifications (user_id, notification_type, title, message, is_read, is_active, created_at)
                    VALUES (:user_id, :notification_type, :title, :message, :is_read, :is_active, :created_at)
                    RETURNING id
                """)
                
                notification_data['created_at'] = datetime.now()
                result = conn.execute(insert_notification, notification_data)
                notification_id = result.fetchone()[0]
                print(f"   ✅ Created notification: {notification_data['title']} - ID: {notification_id}")
            
            conn.commit()
            print(f"\n🎉 US Database populated successfully!")
            print(f"   📊 Created: {len(us_users)} users, {len(us_addresses)} addresses, {len(us_payments)} payments, {len(us_notifications)} notifications")
            return True
            
    except Exception as e:
        print(f"❌ Error populating US database: {e}")
        return False

def main():
    """Main function to populate both databases"""
    print("🚀 POPULATING DATABASES WITH REAL USER DATA")
    print("=" * 60)
    print("This will create persistent data visible in Railway dashboard")
    print()
    
    # Populate KG database
    kg_success = populate_kg_database()
    
    # Populate US database
    us_success = populate_us_database()
    
    print("\n" + "=" * 60)
    print("📊 POPULATION RESULTS:")
    print(f"   🇰🇬 KG Database: {'✅ POPULATED' if kg_success else '❌ FAILED'}")
    print(f"   🇺🇸 US Database: {'✅ POPULATED' if us_success else '❌ FAILED'}")
    
    if kg_success and us_success:
        print("\n🎉 BOTH DATABASES POPULATED SUCCESSFULLY!")
        print("📱 You can now see real user data in your Railway dashboard:")
        print("   - KG Market: 3 users with addresses, payments, and notifications")
        print("   - US Market: 3 users with addresses, payments, and notifications")
        print("\n🔄 Refresh your Railway dashboard to see the data!")
        return 0
    else:
        print("\n⚠️  Some databases failed to populate. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
