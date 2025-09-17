"""
Phone Number Authentication Setup Example
This demonstrates how to set up the complete phone number authentication system
and user profile management matching the Marque user interface design.
"""

from src.app_01.db import SessionLocal
from src.app_01.models import (
    User, PhoneVerification, UserAddress, UserPaymentMethod, UserNotification
)
from datetime import datetime, timedelta
import random

def create_phone_auth_system():
    """Create the complete phone number authentication system"""
    db = SessionLocal()
    
    try:
        print("📱 Creating Phone Number Authentication System...")
        
        # 1. Create Sample Users with Phone Numbers
        print("\n👥 Creating Sample Users...")
        
        users = [
            User(
                phone_number="+996 505 32 53 11",
                full_name="Анна Ахматова",
                is_verified=True,
                profile_image_url="https://example.com/profiles/anna.jpg"
            ),
            User(
                phone_number="+996 505 23 12 55",
                full_name="Иван Иванов",
                is_verified=True,
                profile_image_url="https://example.com/profiles/ivan.jpg"
            ),
            User(
                phone_number="+996 777 88 99 00",
                full_name="Мария Петрова",
                is_verified=True,
                profile_image_url="https://example.com/profiles/maria.jpg"
            ),
            User(
                phone_number="+996 555 66 77 88",
                full_name="Алексей Смирнов",
                is_verified=False,  # Not verified yet
                profile_image_url="https://example.com/profiles/alex.jpg"
            )
        ]
        
        db.add_all(users)
        db.commit()
        for user in users:
            db.refresh(user)
        
        print(f"✅ Created {len(users)} sample users")
        
        # 2. Create Sample Phone Verifications
        print("\n📱 Creating Sample Phone Verifications...")
        
        verifications = [
            PhoneVerification(
                user_id=users[0].id,
                phone_number=users[0].phone_number,
                verification_code="123456",
                is_used=True,
                expires_at=datetime.utcnow() + timedelta(minutes=10),
                verified_at=datetime.utcnow() - timedelta(minutes=5)
            ),
            PhoneVerification(
                user_id=users[1].id,
                phone_number=users[1].phone_number,
                verification_code="654321",
                is_used=True,
                expires_at=datetime.utcnow() + timedelta(minutes=10),
                verified_at=datetime.utcnow() - timedelta(hours=2)
            ),
            PhoneVerification(
                user_id=None,  # New user registration
                phone_number="+996 999 88 77 66",
                verification_code="789012",
                is_used=False,
                expires_at=datetime.utcnow() + timedelta(minutes=10)
            )
        ]
        
        db.add_all(verifications)
        db.commit()
        
        print(f"✅ Created {len(verifications)} phone verifications")
        
        # 3. Create Sample User Addresses
        print("\n🏠 Creating Sample User Addresses...")
        
        addresses = [
            UserAddress(
                user_id=users[0].id,
                address_type="home",
                title="Адрес ул. Юнусалиева, 34",
                full_address="ул. Юнусалиева, 34, Бишкек, Кыргызстан",
                street="ул. Юнусалиева",
                building="34",
                apartment="12",
                city="Бишкек",
                postal_code="720000",
                country="Кыргызстан",
                is_default=True,
                is_active=True
            ),
            UserAddress(
                user_id=users[0].id,
                address_type="work",
                title="Адрес ул. Уметалиева, 11а",
                full_address="ул. Уметалиева, 11а, Бишкек, Кыргызстан",
                street="ул. Уметалиева",
                building="11а",
                apartment="5",
                city="Бишкек",
                postal_code="720000",
                country="Кыргызстан",
                is_default=False,
                is_active=True
            ),
            UserAddress(
                user_id=users[1].id,
                address_type="home",
                title="Адрес пр. Чуй, 123",
                full_address="пр. Чуй, 123, Бишкек, Кыргызстан",
                street="пр. Чуй",
                building="123",
                apartment="45",
                city="Бишкек",
                postal_code="720000",
                country="Кыргызстан",
                is_default=True,
                is_active=True
            )
        ]
        
        db.add_all(addresses)
        db.commit()
        
        print(f"✅ Created {len(addresses)} user addresses")
        
        # 4. Create Sample Payment Methods
        print("\n💳 Creating Sample Payment Methods...")
        
        payment_methods = [
            UserPaymentMethod(
                user_id=users[0].id,
                payment_type="card",
                card_type="visa",
                card_number_masked="2352",
                card_holder_name="ANNA AKHMATOVA",
                expiry_month="12",
                expiry_year="2025",
                is_default=True,
                is_active=True
            ),
            UserPaymentMethod(
                user_id=users[0].id,
                payment_type="card",
                card_type="mastercard",
                card_number_masked="5256",
                card_holder_name="ANNA AKHMATOVA",
                expiry_month="08",
                expiry_year="2026",
                is_default=False,
                is_active=True
            ),
            UserPaymentMethod(
                user_id=users[1].id,
                payment_type="card",
                card_type="visa",
                card_number_masked="9876",
                card_holder_name="IVAN IVANOV",
                expiry_month="03",
                expiry_year="2027",
                is_default=True,
                is_active=True
            )
        ]
        
        db.add_all(payment_methods)
        db.commit()
        
        print(f"✅ Created {len(payment_methods)} payment methods")
        
        # 5. Create Sample Notifications
        print("\n🔔 Creating Sample Notifications...")
        
        notifications = [
            UserNotification(
                user_id=users[0].id,
                notification_type="order",
                title="Заказ №123 подтверждён",
                message="Ваш заказ №123 успешно подтверждён и передан в обработку.",
                order_id=123,
                is_read=False,
                is_active=True,
                metadata={"order_id": 123, "products": ["Футболка H&M", "Джинсы Nike"]}
            ),
            UserNotification(
                user_id=users[0].id,
                notification_type="order",
                title="Заказ №123 передан курьеру",
                message="Ваш заказ №123 передан курьеру. Ожидаемая доставка: 21.07.2025",
                order_id=123,
                is_read=False,
                is_active=True,
                metadata={"order_id": 123, "delivery_date": "21.07.2025"}
            ),
            UserNotification(
                user_id=users[0].id,
                notification_type="order",
                title="Заказ №123 доставлен",
                message="Ваш заказ №123 успешно доставлен. Спасибо за покупку!",
                order_id=123,
                is_read=False,
                is_active=True,
                metadata={"order_id": 123, "delivered_at": "15.07.2025"}
            ),
            UserNotification(
                user_id=users[1].id,
                notification_type="promotion",
                title="Скидка 20% на все товары H&M",
                message="Специальное предложение! Получите скидку 20% на все товары бренда H&M до конца месяца.",
                is_read=False,
                is_active=True,
                metadata={"brand": "H&M", "discount": "20%", "expires": "31.07.2025"}
            ),
            UserNotification(
                user_id=users[2].id,
                notification_type="system",
                title="Добро пожаловать в MARQUE!",
                message="Спасибо за регистрацию! Теперь вы можете делать покупки в нашем интернет-магазине.",
                is_read=True,
                is_active=True,
                metadata={"welcome": True}
            )
        ]
        
        db.add_all(notifications)
        db.commit()
        
        print(f"✅ Created {len(notifications)} notifications")
        
        print("\n🎉 Phone Authentication System created successfully!")
        print("\n📊 Summary:")
        print(f"   - {len(users)} users with phone numbers")
        print(f"   - {len(verifications)} phone verifications")
        print(f"   - {len(addresses)} user addresses")
        print(f"   - {len(payment_methods)} payment methods")
        print(f"   - {len(notifications)} notifications")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating phone auth system: {e}")
        return False
    finally:
        db.close()

def show_phone_auth_usage():
    """Show how to use the phone authentication system"""
    print("\n📱 PHONE AUTHENTICATION SYSTEM USAGE")
    print("=" * 50)
    print()
    print("🔐 Authentication Flow:")
    print("   1. User enters phone number: +996 505 23 12 55")
    print("   2. System sends SMS with 6-digit code")
    print("   3. User enters verification code")
    print("   4. System verifies code and logs user in")
    print("   5. User profile is loaded with all data")
    print()
    print("👤 User Profile Features:")
    print("   ✅ Phone number as primary identifier")
    print("   ✅ Full name (Анна Ахматова)")
    print("   ✅ Profile photo")
    print("   ✅ Phone number verification status")
    print("   ✅ Last login tracking")
    print()
    print("🏠 Address Management:")
    print("   ✅ Multiple delivery addresses")
    print("   ✅ Address types: home, work, other")
    print("   ✅ Default address selection")
    print("   ✅ Full address details")
    print()
    print("💳 Payment Methods:")
    print("   ✅ Bank cards (Visa, Mastercard)")
    print("   ✅ Masked card numbers for security")
    print("   ✅ Default payment method")
    print("   ✅ Card holder information")
    print()
    print("🔔 Notifications:")
    print("   ✅ Order status notifications")
    print("   ✅ Promotion notifications")
    print("   ✅ System notifications")
    print("   ✅ Read/unread status")
    print()
    print("📱 Phone Verification:")
    print("   ✅ 6-digit SMS codes")
    print("   ✅ 10-minute expiration")
    print("   ✅ One-time use codes")
    print("   ✅ Automatic cleanup")
    print()
    print("🚀 How to Access SQLAdmin:")
    print("   1. Run: python main_admin.py")
    print("   2. Visit: http://localhost:8001/admin")
    print("   3. Login: content_admin / admin123")
    print("   4. Manage: Пользователи, Верификация телефонов, Адреса, Способы оплаты, Уведомления")

def demonstrate_phone_auth():
    """Demonstrate phone authentication functionality"""
    db = SessionLocal()
    
    try:
        print("\n📱 PHONE AUTHENTICATION EXAMPLES")
        print("=" * 40)
        
        # Example 1: Find user by phone
        print("\n1. Find User by Phone Number:")
        user = User.get_by_phone(db, "+996 505 32 53 11")
        if user:
            print(f"   Found user: {user.display_name}")
            print(f"   Phone: {user.formatted_phone}")
            print(f"   Verified: {user.is_verified}")
        else:
            print("   User not found")
        
        # Example 2: Create verification code
        print("\n2. Create Verification Code:")
        verification = PhoneVerification.create_verification(
            db, "+996 555 66 77 88", user_id=None
        )
        print(f"   Created verification code: {verification.verification_code}")
        print(f"   Expires at: {verification.expires_at}")
        
        # Example 3: Verify code
        print("\n3. Verify Code:")
        verified = PhoneVerification.verify_code(
            db, "+996 555 66 77 88", verification.verification_code
        )
        if verified:
            print("   ✅ Code verified successfully")
        else:
            print("   ❌ Invalid or expired code")
        
        # Example 4: Get user addresses
        print("\n4. Get User Addresses:")
        user = User.get_by_phone(db, "+996 505 32 53 11")
        if user:
            addresses = UserAddress.get_user_addresses(db, user.id)
            print(f"   Found {len(addresses)} addresses:")
            for addr in addresses:
                default_text = " (default)" if addr.is_default else ""
                print(f"   - {addr.title}{default_text}")
        
        # Example 5: Get user payment methods
        print("\n5. Get User Payment Methods:")
        if user:
            payment_methods = UserPaymentMethod.get_user_payment_methods(db, user.id)
            print(f"   Found {len(payment_methods)} payment methods:")
            for pm in payment_methods:
                default_text = " (default)" if pm.is_default else ""
                print(f"   - {pm.display_name}{default_text}")
        
        # Example 6: Get user notifications
        print("\n6. Get User Notifications:")
        if user:
            notifications = UserNotification.get_user_notifications(db, user.id)
            unread_count = UserNotification.get_unread_count(db, user.id)
            print(f"   Total notifications: {len(notifications)}")
            print(f"   Unread notifications: {unread_count}")
            for notif in notifications[:3]:  # Show first 3
                read_text = "✓" if notif.is_read else "○"
                print(f"   {read_text} {notif.title}")
        
    except Exception as e:
        print(f"❌ Error demonstrating phone auth: {e}")
    finally:
        db.close()

def main():
    """Main function"""
    print("📱 MARQUE PHONE AUTHENTICATION SETUP")
    print("=" * 45)
    
    if create_phone_auth_system():
        show_phone_auth_usage()
        demonstrate_phone_auth()
        print("\n✅ Phone authentication setup completed successfully!")
        print("   Now you can run: python main_admin.py")
        print("   Then visit: http://localhost:8001/admin")
        print("   Manage users in: Пользователи, Верификация телефонов, Адреса, Способы оплаты, Уведомления")
    else:
        print("\n❌ Phone authentication setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
