#!/usr/bin/env python3
"""
Setup US market database tables in Railway PostgreSQL
"""

import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_us_database():
    """Setup US market database tables"""
    print("🇺🇸 Setting up US Market Database...")
    
    # Get US DATABASE_URL
    us_database_url = os.getenv("DATABASE_URL_MARQUE_US")
    if not us_database_url:
        print("❌ DATABASE_URL_MARQUE_US not found in environment variables")
        print("Please add your US database URL to .env file:")
        print("DATABASE_URL_MARQUE_US=postgresql://user:password@host:port/database")
        return False
    
    print(f"🔗 Connecting to US database: {us_database_url[:50]}...")
    
    try:
        # Create engine
        engine = create_engine(us_database_url)
        Base = declarative_base()
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to US PostgreSQL: {version[:50]}...")
        
        # Define US User model
        class UserUS(Base):
            __tablename__ = "users"
            
            id = Column(Integer, primary_key=True, index=True)
            phone_number = Column(String(20), unique=True, nullable=False, index=True)
            full_name = Column(String(255), nullable=True)
            profile_image_url = Column(String(500), nullable=True)
            is_active = Column(Boolean, default=True)
            is_verified = Column(Boolean, default=False)
            last_login = Column(DateTime, nullable=True)
            market = Column(String(10), default="us", nullable=False, index=True)
            language = Column(String(10), default="en", nullable=False)
            country = Column(String(100), default="United States", nullable=False)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, onupdate=datetime.utcnow)
            
            # Legacy fields for compatibility
            email = Column(String(255), unique=True, nullable=True, index=True)
            username = Column(String(100), unique=True, nullable=True, index=True)
            hashed_password = Column(String(255), nullable=True)
        
        # Define US PhoneVerification model
        class PhoneVerificationUS(Base):
            __tablename__ = "phone_verifications"
            
            id = Column(Integer, primary_key=True, index=True)
            user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
            phone_number = Column(String(20), nullable=False, index=True)
            verification_code = Column(String(10), nullable=False)
            is_used = Column(Boolean, default=False)
            expires_at = Column(DateTime, nullable=False)
            created_at = Column(DateTime, default=datetime.utcnow)
            verified_at = Column(DateTime, nullable=True)
            market = Column(String(10), default="us", nullable=False, index=True)
        
        # Define US UserAddress model
        class UserAddressUS(Base):
            __tablename__ = "user_addresses"
            
            id = Column(Integer, primary_key=True, index=True)
            user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
            address_type = Column(String(20), nullable=False, default="home")
            title = Column(String(100), nullable=False)
            full_address = Column(Text, nullable=False)
            
            # US-specific address fields
            street_address = Column(String(200), nullable=True)
            street_number = Column(String(20), nullable=True)
            street_name = Column(String(200), nullable=True)
            apartment_unit = Column(String(20), nullable=True)
            city = Column(String(100), nullable=True)
            state = Column(String(50), nullable=True)
            postal_code = Column(String(20), nullable=True)
            country = Column(String(100), default="United States", nullable=True)
            
            is_default = Column(Boolean, default=False)
            is_active = Column(Boolean, default=True)
            market = Column(String(10), default="us", nullable=False, index=True)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, onupdate=datetime.utcnow)
        
        # Define US UserPaymentMethod model
        class UserPaymentMethodUS(Base):
            __tablename__ = "user_payment_methods"
            
            id = Column(Integer, primary_key=True, index=True)
            user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
            payment_type = Column(String(20), nullable=False, default="card")
            card_type = Column(String(20), nullable=True)
            card_number_masked = Column(String(20), nullable=True)
            card_holder_name = Column(String(100), nullable=True)
            expiry_month = Column(String(2), nullable=True)
            expiry_year = Column(String(4), nullable=True)
            paypal_email = Column(String(255), nullable=True)
            is_default = Column(Boolean, default=False)
            is_active = Column(Boolean, default=True)
            market = Column(String(10), default="us", nullable=False, index=True)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, onupdate=datetime.utcnow)
        
        # Define US UserNotification model
        class UserNotificationUS(Base):
            __tablename__ = "user_notifications"
            
            id = Column(Integer, primary_key=True, index=True)
            user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
            notification_type = Column(String(20), nullable=False)
            title = Column(String(200), nullable=False)
            message = Column(Text, nullable=True)
            order_id = Column(Integer, nullable=True)
            is_read = Column(Boolean, default=False)
            is_active = Column(Boolean, default=True)
            created_at = Column(DateTime, default=datetime.utcnow)
            read_at = Column(DateTime, nullable=True)
        
        # Create all US tables
        print("📋 Creating US market tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            print(f"✅ US market tables created successfully:")
            for table in tables:
                print(f"   🇺🇸 {table}")
        
        # Insert US test data
        print("\n🧪 Inserting US test data...")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Create US test user
            test_user = UserUS(
                phone_number="+15551234567",
                full_name="John Smith",
                market="us",
                language="en",
                country="United States",
                is_verified=True
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print(f"✅ US test user created: {test_user.full_name} ({test_user.phone_number})")
            
            # Create US test verification
            test_verification = PhoneVerificationUS(
                user_id=test_user.id,
                phone_number=test_user.phone_number,
                verification_code="789012",
                expires_at=datetime.utcnow(),
                market="us"
            )
            
            db.add(test_verification)
            db.commit()
            
            print(f"✅ US test verification created: {test_verification.verification_code}")
            
        except Exception as e:
            print(f"⚠️  US test data insertion failed: {e}")
        finally:
            db.close()
        
        print("\n🎉 US market database setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up US database: {e}")
        return False

def main():
    """Main function"""
    print("🇺🇸 RAILWAY US MARKET DATABASE SETUP")
    print("=" * 50)
    
    if setup_us_database():
        print("\n✅ US Market Features:")
        print("   🇺🇸 United States market support")
        print("   📱 Phone number authentication (+1)")
        print("   🔐 SMS verification system")
        print("   🏠 US-specific address fields")
        print("   💳 US payment methods (Visa, Mastercard, Amex, PayPal, Apple Pay, Google Pay)")
        print("   🔔 Notification system")
        print("   🌐 English language support")
        print("\n🚀 US market database is ready!")
        return 0
    else:
        print("\n❌ Failed to setup US database")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
