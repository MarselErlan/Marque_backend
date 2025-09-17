#!/usr/bin/env python3
"""
Setup KG market database tables in Railway PostgreSQL
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

def setup_kg_database():
    """Setup KG market database tables"""
    print("🇰🇬 Setting up KG Market Database...")
    
    # Get KG DATABASE_URL
    kg_database_url = os.getenv("DATABASE_URL_MARQUE_KG")
    if not kg_database_url:
        print("❌ DATABASE_URL_MARQUE_KG not found in environment variables")
        print("Please add your KG database URL to .env file:")
        print("DATABASE_URL_MARQUE_KG=postgresql://user:password@host:port/database")
        return False
    
    print(f"🔗 Connecting to KG database: {kg_database_url[:50]}...")
    
    try:
        # Create engine
        engine = create_engine(kg_database_url)
        Base = declarative_base()
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to KG PostgreSQL: {version[:50]}...")
        
        # Define KG User model
        class UserKG(Base):
            __tablename__ = "users"
            
            id = Column(Integer, primary_key=True, index=True)
            phone_number = Column(String(20), unique=True, nullable=False, index=True)
            full_name = Column(String(255), nullable=True)
            profile_image_url = Column(String(500), nullable=True)
            is_active = Column(Boolean, default=True)
            is_verified = Column(Boolean, default=False)
            last_login = Column(DateTime, nullable=True)
            market = Column(String(10), default="kg", nullable=False, index=True)
            language = Column(String(10), default="ru", nullable=False)
            country = Column(String(100), default="Kyrgyzstan", nullable=False)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, onupdate=datetime.utcnow)
            
            # Legacy fields for compatibility
            email = Column(String(255), unique=True, nullable=True, index=True)
            username = Column(String(100), unique=True, nullable=True, index=True)
            hashed_password = Column(String(255), nullable=True)
        
        # Define KG PhoneVerification model
        class PhoneVerificationKG(Base):
            __tablename__ = "phone_verifications"
            
            id = Column(Integer, primary_key=True, index=True)
            user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
            phone_number = Column(String(20), nullable=False, index=True)
            verification_code = Column(String(10), nullable=False)
            is_used = Column(Boolean, default=False)
            expires_at = Column(DateTime, nullable=False)
            created_at = Column(DateTime, default=datetime.utcnow)
            verified_at = Column(DateTime, nullable=True)
            market = Column(String(10), default="kg", nullable=False, index=True)
        
        # Define KG UserAddress model
        class UserAddressKG(Base):
            __tablename__ = "user_addresses"
            
            id = Column(Integer, primary_key=True, index=True)
            user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
            address_type = Column(String(20), nullable=False, default="home")
            title = Column(String(100), nullable=False)
            full_address = Column(Text, nullable=False)
            
            # KG-specific address fields
            street = Column(String(200), nullable=True)
            building = Column(String(50), nullable=True)
            apartment = Column(String(20), nullable=True)
            city = Column(String(100), nullable=True)
            postal_code = Column(String(20), nullable=True)
            country = Column(String(100), default="Kyrgyzstan", nullable=True)
            region = Column(String(100), nullable=True)
            district = Column(String(100), nullable=True)
            
            is_default = Column(Boolean, default=False)
            is_active = Column(Boolean, default=True)
            market = Column(String(10), default="kg", nullable=False, index=True)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, onupdate=datetime.utcnow)
        
        # Define KG UserPaymentMethod model
        class UserPaymentMethodKG(Base):
            __tablename__ = "user_payment_methods"
            
            id = Column(Integer, primary_key=True, index=True)
            user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
            payment_type = Column(String(20), nullable=False, default="card")
            card_type = Column(String(20), nullable=True)
            card_number_masked = Column(String(20), nullable=True)
            card_holder_name = Column(String(100), nullable=True)
            expiry_month = Column(String(2), nullable=True)
            expiry_year = Column(String(4), nullable=True)
            bank_name = Column(String(100), nullable=True)
            is_default = Column(Boolean, default=False)
            is_active = Column(Boolean, default=True)
            market = Column(String(10), default="kg", nullable=False, index=True)
            created_at = Column(DateTime, default=datetime.utcnow)
            updated_at = Column(DateTime, onupdate=datetime.utcnow)
        
        # Define KG UserNotification model
        class UserNotificationKG(Base):
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
        
        # Create all KG tables
        print("📋 Creating KG market tables...")
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
            
            print(f"✅ KG market tables created successfully:")
            for table in tables:
                print(f"   🇰🇬 {table}")
        
        # Insert KG test data
        print("\n🧪 Inserting KG test data...")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Create KG test user
            test_user = UserKG(
                phone_number="+996505325311",
                full_name="Анна Ахматова",
                market="kg",
                language="ru",
                country="Kyrgyzstan",
                is_verified=True
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print(f"✅ KG test user created: {test_user.full_name} ({test_user.phone_number})")
            
            # Create KG test verification
            test_verification = PhoneVerificationKG(
                user_id=test_user.id,
                phone_number=test_user.phone_number,
                verification_code="123456",
                expires_at=datetime.utcnow(),
                market="kg"
            )
            
            db.add(test_verification)
            db.commit()
            
            print(f"✅ KG test verification created: {test_verification.verification_code}")
            
        except Exception as e:
            print(f"⚠️  KG test data insertion failed: {e}")
        finally:
            db.close()
        
        print("\n🎉 KG market database setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up KG database: {e}")
        return False

def main():
    """Main function"""
    print("🇰🇬 RAILWAY KG MARKET DATABASE SETUP")
    print("=" * 50)
    
    if setup_kg_database():
        print("\n✅ KG Market Features:")
        print("   🇰🇬 Kyrgyzstan market support")
        print("   📱 Phone number authentication (+996)")
        print("   🔐 SMS verification system")
        print("   🏠 KG-specific address fields")
        print("   💳 KG payment methods (Visa, Mastercard, Элкарт)")
        print("   🔔 Notification system")
        print("   🌐 Russian language support")
        print("\n🚀 KG market database is ready!")
        return 0
    else:
        print("\n❌ Failed to setup KG database")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
