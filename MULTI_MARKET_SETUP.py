"""
Multi-Market Setup Example
This demonstrates how to set up the complete multi-market system
for both KG (Kyrgyzstan) and US markets with different logic.
"""

from src.app_01.db.market_db import (
    db_manager, Market, MarketConfig, detect_market_from_phone, 
    format_phone_for_market, format_price_for_market
)
from src.app_01.models.users.market_user import UserKG, UserUS, get_user_model
from src.app_01.models.users.market_phone_verification import (
    PhoneVerificationKG, PhoneVerificationUS, create_verification_for_market
)
from src.app_01.models.users.market_user_address import (
    UserAddressKG, UserAddressUS, create_address_for_market
)
from src.app_01.models.users.market_user_payment_method import (
    UserPaymentMethodKG, UserPaymentMethodUS, create_payment_method_for_market
)
from datetime import datetime

def create_multi_market_system():
    """Create the complete multi-market system"""
    print("🌍 Creating Multi-Market System...")
    
    # Get database sessions for both markets
    kg_session_factory = db_manager.get_session_factory(Market.KG)
    us_session_factory = db_manager.get_session_factory(Market.US)
    
    try:
        # Create KG market data
        print("\n🇰🇬 Creating KG (Kyrgyzstan) Market Data...")
        create_kg_market_data(kg_session_factory())
        
        # Create US market data
        print("\n🇺🇸 Creating US (United States) Market Data...")
        create_us_market_data(us_session_factory())
        
        print("\n🎉 Multi-Market System created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating multi-market system: {e}")
        return False

def create_kg_market_data(db):
    """Create sample data for KG market"""
    try:
        # 1. Create KG Users
        print("   👥 Creating KG Users...")
        
        kg_users = [
            UserKG(
                phone_number="+996505325311",
                full_name="Анна Ахматова",
                is_verified=True,
                profile_image_url="https://example.com/profiles/anna_kg.jpg",
                market="kg",
                language="ru",
                country="Kyrgyzstan"
            ),
            UserKG(
                phone_number="+996555123456",
                full_name="Иван Иванов",
                is_verified=True,
                profile_image_url="https://example.com/profiles/ivan_kg.jpg",
                market="kg",
                language="ru",
                country="Kyrgyzstan"
            ),
            UserKG(
                phone_number="+996777888999",
                full_name="Мария Петрова",
                is_verified=False,
                profile_image_url="https://example.com/profiles/maria_kg.jpg",
                market="kg",
                language="ru",
                country="Kyrgyzstan"
            )
        ]
        
        db.add_all(kg_users)
        db.commit()
        for user in kg_users:
            db.refresh(user)
        
        print(f"     ✅ Created {len(kg_users)} KG users")
        
        # 2. Create KG Phone Verifications
        print("   📱 Creating KG Phone Verifications...")
        
        kg_verifications = [
            PhoneVerificationKG(
                user_id=kg_users[0].id,
                phone_number=kg_users[0].phone_number,
                verification_code="123456",
                is_used=True,
                expires_at=datetime.utcnow(),
                verified_at=datetime.utcnow(),
                market="kg"
            ),
            PhoneVerificationKG(
                user_id=kg_users[1].id,
                phone_number=kg_users[1].phone_number,
                verification_code="654321",
                is_used=True,
                expires_at=datetime.utcnow(),
                verified_at=datetime.utcnow(),
                market="kg"
            )
        ]
        
        db.add_all(kg_verifications)
        db.commit()
        
        print(f"     ✅ Created {len(kg_verifications)} KG verifications")
        
        # 3. Create KG Addresses
        print("   🏠 Creating KG Addresses...")
        
        kg_addresses = [
            UserAddressKG(
                user_id=kg_users[0].id,
                address_type="home",
                title="Адрес ул. Юнусалиева, 34",
                full_address="ул. Юнусалиева, 34, кв. 12, Бишкек, Чуйская область, Кыргызстан",
                street="ул. Юнусалиева",
                building="34",
                apartment="12",
                city="Бишкек",
                region="Чуйская область",
                country="Kyrgyzstan",
                is_default=True,
                market="kg"
            ),
            UserAddressKG(
                user_id=kg_users[0].id,
                address_type="work",
                title="Адрес пр. Чуй, 123",
                full_address="пр. Чуй, 123, офис 45, Бишкек, Чуйская область, Кыргызстан",
                street="пр. Чуй",
                building="123",
                apartment="45",
                city="Бишкек",
                region="Чуйская область",
                country="Kyrgyzstan",
                is_default=False,
                market="kg"
            )
        ]
        
        db.add_all(kg_addresses)
        db.commit()
        
        print(f"     ✅ Created {len(kg_addresses)} KG addresses")
        
        # 4. Create KG Payment Methods
        print("   💳 Creating KG Payment Methods...")
        
        kg_payment_methods = [
            UserPaymentMethodKG(
                user_id=kg_users[0].id,
                payment_type="card",
                card_type="visa",
                card_number_masked="2352",
                card_holder_name="ANNA AKHMATOVA",
                expiry_month="12",
                expiry_year="2025",
                bank_name="ОАО 'Демир Банк'",
                is_default=True,
                market="kg"
            ),
            UserPaymentMethodKG(
                user_id=kg_users[0].id,
                payment_type="cash_on_delivery",
                is_default=False,
                market="kg"
            ),
            UserPaymentMethodKG(
                user_id=kg_users[1].id,
                payment_type="card",
                card_type="elcard",
                card_number_masked="9876",
                card_holder_name="IVAN IVANOV",
                expiry_month="08",
                expiry_year="2026",
                bank_name="ОАО 'Айыл Банк'",
                is_default=True,
                market="kg"
            )
        ]
        
        db.add_all(kg_payment_methods)
        db.commit()
        
        print(f"     ✅ Created {len(kg_payment_methods)} KG payment methods")
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def create_us_market_data(db):
    """Create sample data for US market"""
    try:
        # 1. Create US Users
        print("   👥 Creating US Users...")
        
        us_users = [
            UserUS(
                phone_number="+15551234567",
                full_name="John Smith",
                is_verified=True,
                profile_image_url="https://example.com/profiles/john_us.jpg",
                market="us",
                language="en",
                country="United States"
            ),
            UserUS(
                phone_number="+15559876543",
                full_name="Sarah Johnson",
                is_verified=True,
                profile_image_url="https://example.com/profiles/sarah_us.jpg",
                market="us",
                language="en",
                country="United States"
            ),
            UserUS(
                phone_number="+15555678901",
                full_name="Michael Brown",
                is_verified=False,
                profile_image_url="https://example.com/profiles/michael_us.jpg",
                market="us",
                language="en",
                country="United States"
            )
        ]
        
        db.add_all(us_users)
        db.commit()
        for user in us_users:
            db.refresh(user)
        
        print(f"     ✅ Created {len(us_users)} US users")
        
        # 2. Create US Phone Verifications
        print("   📱 Creating US Phone Verifications...")
        
        us_verifications = [
            PhoneVerificationUS(
                user_id=us_users[0].id,
                phone_number=us_users[0].phone_number,
                verification_code="789012",
                is_used=True,
                expires_at=datetime.utcnow(),
                verified_at=datetime.utcnow(),
                market="us"
            ),
            PhoneVerificationUS(
                user_id=us_users[1].id,
                phone_number=us_users[1].phone_number,
                verification_code="345678",
                is_used=True,
                expires_at=datetime.utcnow(),
                verified_at=datetime.utcnow(),
                market="us"
            )
        ]
        
        db.add_all(us_verifications)
        db.commit()
        
        print(f"     ✅ Created {len(us_verifications)} US verifications")
        
        # 3. Create US Addresses
        print("   🏠 Creating US Addresses...")
        
        us_addresses = [
            UserAddressUS(
                user_id=us_users[0].id,
                address_type="home",
                title="123 Main St, New York, NY 10001",
                full_address="123 Main Street, Apartment 4B, New York, NY 10001, United States",
                street_address="123 Main Street",
                street_number="123",
                street_name="Main Street",
                apartment_unit="4B",
                city="New York",
                state="NY",
                postal_code="10001",
                country="United States",
                is_default=True,
                market="us"
            ),
            UserAddressUS(
                user_id=us_users[0].id,
                address_type="work",
                title="456 Business Ave, New York, NY 10002",
                full_address="456 Business Avenue, Suite 200, New York, NY 10002, United States",
                street_address="456 Business Avenue",
                street_number="456",
                street_name="Business Avenue",
                apartment_unit="Suite 200",
                city="New York",
                state="NY",
                postal_code="10002",
                country="United States",
                is_default=False,
                market="us"
            )
        ]
        
        db.add_all(us_addresses)
        db.commit()
        
        print(f"     ✅ Created {len(us_addresses)} US addresses")
        
        # 4. Create US Payment Methods
        print("   💳 Creating US Payment Methods...")
        
        us_payment_methods = [
            UserPaymentMethodUS(
                user_id=us_users[0].id,
                payment_type="card",
                card_type="visa",
                card_number_masked="4532",
                card_holder_name="JOHN SMITH",
                expiry_month="12",
                expiry_year="2025",
                is_default=True,
                market="us"
            ),
            UserPaymentMethodUS(
                user_id=us_users[0].id,
                payment_type="paypal",
                paypal_email="john.smith@example.com",
                is_default=False,
                market="us"
            ),
            UserPaymentMethodUS(
                user_id=us_users[1].id,
                payment_type="card",
                card_type="mastercard",
                card_number_masked="5555",
                card_holder_name="SARAH JOHNSON",
                expiry_month="06",
                expiry_year="2026",
                is_default=True,
                market="us"
            ),
            UserPaymentMethodUS(
                user_id=us_users[1].id,
                payment_type="apple_pay",
                is_default=False,
                market="us"
            )
        ]
        
        db.add_all(us_payment_methods)
        db.commit()
        
        print(f"     ✅ Created {len(us_payment_methods)} US payment methods")
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def demonstrate_multi_market_features():
    """Demonstrate multi-market features"""
    print("\n🌍 MULTI-MARKET FEATURES DEMONSTRATION")
    print("=" * 50)
    
    # Get database sessions
    kg_session_factory = db_manager.get_session_factory(Market.KG)
    us_session_factory = db_manager.get_session_factory(Market.US)
    
    try:
        # Example 1: Market Detection
        print("\n1. Market Detection from Phone Numbers:")
        kg_phone = "+996505325311"
        us_phone = "+15551234567"
        
        kg_market = detect_market_from_phone(kg_phone)
        us_market = detect_market_from_phone(us_phone)
        
        print(f"   KG Phone {kg_phone} → Market: {kg_market.value}")
        print(f"   US Phone {us_phone} → Market: {us_market.value}")
        
        # Example 2: Phone Formatting
        print("\n2. Phone Number Formatting:")
        kg_formatted = format_phone_for_market(kg_phone, Market.KG)
        us_formatted = format_phone_for_market(us_phone, Market.US)
        
        print(f"   KG: {kg_phone} → {kg_formatted}")
        print(f"   US: {us_phone} → {us_formatted}")
        
        # Example 3: Price Formatting
        print("\n3. Price Formatting:")
        kg_price = format_price_for_market(2999.0, Market.KG)
        us_price = format_price_for_market(29.99, Market.US)
        
        print(f"   KG: 2999.0 → {kg_price}")
        print(f"   US: 29.99 → {us_price}")
        
        # Example 4: Market Configurations
        print("\n4. Market Configurations:")
        kg_config = MarketConfig.get_config(Market.KG)
        us_config = MarketConfig.get_config(Market.US)
        
        print(f"   KG Currency: {kg_config['currency']} ({kg_config['currency_code']})")
        print(f"   US Currency: {us_config['currency']} ({us_config['currency_code']})")
        print(f"   KG Language: {kg_config['default_language']}")
        print(f"   US Language: {us_config['default_language']}")
        print(f"   KG Tax Rate: {kg_config['tax_rate']*100}%")
        print(f"   US Tax Rate: {us_config['tax_rate']*100}%")
        
        # Example 5: User Data by Market
        print("\n5. User Data by Market:")
        
        # KG Users
        kg_db = kg_session_factory()
        kg_users = kg_db.query(UserKG).limit(2).all()
        print("   KG Users:")
        for user in kg_users:
            print(f"     - {user.display_name} ({user.formatted_phone}) - {user.currency}")
        kg_db.close()
        
        # US Users
        us_db = us_session_factory()
        us_users = us_db.query(UserUS).limit(2).all()
        print("   US Users:")
        for user in us_users:
            print(f"     - {user.display_name} ({user.formatted_phone}) - {user.currency}")
        us_db.close()
        
        # Example 6: Payment Methods by Market
        print("\n6. Payment Methods by Market:")
        
        # KG Payment Methods
        kg_db = kg_session_factory()
        kg_payments = kg_db.query(UserPaymentMethodKG).limit(3).all()
        print("   KG Payment Methods:")
        for payment in kg_payments:
            print(f"     - {payment.display_name}")
        kg_db.close()
        
        # US Payment Methods
        us_db = us_session_factory()
        us_payments = us_db.query(UserPaymentMethodUS).limit(3).all()
        print("   US Payment Methods:")
        for payment in us_payments:
            print(f"     - {payment.display_name}")
        us_db.close()
        
    except Exception as e:
        print(f"❌ Error demonstrating multi-market features: {e}")

def show_multi_market_usage():
    """Show how to use the multi-market system"""
    print("\n🌍 MULTI-MARKET SYSTEM USAGE")
    print("=" * 50)
    print()
    print("🔧 Database Configuration:")
    print("   ✅ Separate databases for KG and US markets")
    print("   ✅ Market-specific table schemas")
    print("   ✅ Independent data isolation")
    print()
    print("📱 Phone Number Handling:")
    print("   ✅ KG Format: +996 XXX XXX XXX")
    print("   ✅ US Format: +1 (XXX) XXX-XXXX")
    print("   ✅ Automatic market detection")
    print("   ✅ Market-specific validation")
    print()
    print("💰 Currency & Pricing:")
    print("   ✅ KG: сом (KGS) - 2999 сом")
    print("   ✅ US: $ (USD) - $29.99")
    print("   ✅ Market-specific formatting")
    print("   ✅ Different tax rates")
    print()
    print("🏠 Address Management:")
    print("   ✅ KG: Street, Building, Apartment, City, Region")
    print("   ✅ US: Street Address, City, State, ZIP Code")
    print("   ✅ Market-specific required fields")
    print("   ✅ Different postal systems")
    print()
    print("💳 Payment Methods:")
    print("   ✅ KG: Visa, Mastercard, Элкарт, Cash on Delivery, Bank Transfer")
    print("   ✅ US: Visa, Mastercard, Amex, Discover, PayPal, Apple Pay, Google Pay")
    print("   ✅ Market-specific payment options")
    print("   ✅ Different banking systems")
    print()
    print("🌐 Language Support:")
    print("   ✅ KG: Russian (ru)")
    print("   ✅ US: English (en)")
    print("   ✅ Market-specific localization")
    print("   ✅ Different date formats")
    print()
    print("🚀 How to Access:")
    print("   1. Run: python MULTI_MARKET_SETUP.py")
    print("   2. Configure environment variables:")
    print("      - DATABASE_URL_MARQUE_KG")
    print("      - DATABASE_URL_MARQUE_US")
    print("   3. Use market detection in your API endpoints")

def main():
    """Main function"""
    print("🌍 MARQUE MULTI-MARKET SETUP")
    print("=" * 40)
    
    if create_multi_market_system():
        show_multi_market_usage()
        demonstrate_multi_market_features()
        print("\n✅ Multi-market setup completed successfully!")
        print("   Now you have separate systems for KG and US markets")
        print("   Each market has its own database, models, and business logic")
    else:
        print("\n❌ Multi-market setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
