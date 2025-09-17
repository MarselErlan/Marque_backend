#!/usr/bin/env python3
"""
Test database functionality with sample data
"""

import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_kg_database():
    """Test KG database functionality"""
    print("🇰🇬 Testing KG Market Database...")
    
    # Create engine and session
    engine = create_engine("sqlite:///databases/marque_kg.db")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    # Define KG models
    class UserKG(Base):
        __tablename__ = "users"
        
        id = Column(Integer, primary_key=True, index=True)
        phone_number = Column(String(20), unique=True, nullable=False, index=True)
        full_name = Column(String(255), nullable=True)
        profile_image_url = Column(String(500), nullable=True)
        is_active = Column(Boolean, default=True)
        is_verified = Column(Boolean, default=False)
        last_login = Column(DateTime, nullable=True)
        market = Column(String(10), default="kg", nullable=False)
        language = Column(String(10), default="ru", nullable=False)
        country = Column(String(100), default="Kyrgyzstan", nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
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
        market = Column(String(10), default="kg", nullable=False)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Test 1: Create a KG user
        print("📱 Creating KG user...")
        kg_user = UserKG(
            phone_number="+996505325311",
            full_name="Анна Ахматова",
            is_verified=True,
            market="kg",
            language="ru",
            country="Kyrgyzstan"
        )
        
        db.add(kg_user)
        db.commit()
        db.refresh(kg_user)
        
        print(f"✅ Created KG user: {kg_user.full_name} ({kg_user.phone_number})")
        
        # Test 2: Create phone verification
        print("🔐 Creating phone verification...")
        verification = PhoneVerificationKG(
            user_id=kg_user.id,
            phone_number=kg_user.phone_number,
            verification_code="123456",
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            market="kg"
        )
        
        db.add(verification)
        db.commit()
        db.refresh(verification)
        
        print(f"✅ Created verification code: {verification.verification_code}")
        
        # Test 3: Query user
        print("🔍 Querying user...")
        found_user = db.query(UserKG).filter(UserKG.phone_number == "+996505325311").first()
        
        if found_user:
            print(f"✅ Found user: {found_user.full_name}")
            print(f"   Market: {found_user.market}")
            print(f"   Language: {found_user.language}")
            print(f"   Country: {found_user.country}")
            print(f"   Verified: {found_user.is_verified}")
        else:
            print("❌ User not found")
            return False
        
        # Test 4: Query verification
        print("🔍 Querying verification...")
        found_verification = db.query(PhoneVerificationKG).filter(
            PhoneVerificationKG.phone_number == "+996505325311"
        ).first()
        
        if found_verification:
            print(f"✅ Found verification: {found_verification.verification_code}")
            print(f"   Expires: {found_verification.expires_at}")
            print(f"   Used: {found_verification.is_used}")
        else:
            print("❌ Verification not found")
            return False
        
        print("✅ KG database functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ KG database test failed: {e}")
        return False
    finally:
        db.close()

def test_us_database():
    """Test US database functionality"""
    print("\n🇺🇸 Testing US Market Database...")
    
    # Create engine and session
    engine = create_engine("sqlite:///databases/marque_us.db")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    # Define US models
    class UserUS(Base):
        __tablename__ = "users"
        
        id = Column(Integer, primary_key=True, index=True)
        phone_number = Column(String(20), unique=True, nullable=False, index=True)
        full_name = Column(String(255), nullable=True)
        profile_image_url = Column(String(500), nullable=True)
        is_active = Column(Boolean, default=True)
        is_verified = Column(Boolean, default=False)
        last_login = Column(DateTime, nullable=True)
        market = Column(String(10), default="us", nullable=False)
        language = Column(String(10), default="en", nullable=False)
        country = Column(String(100), default="United States", nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
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
        market = Column(String(10), default="us", nullable=False)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Test 1: Create a US user
        print("📱 Creating US user...")
        us_user = UserUS(
            phone_number="+15551234567",
            full_name="John Smith",
            is_verified=True,
            market="us",
            language="en",
            country="United States"
        )
        
        db.add(us_user)
        db.commit()
        db.refresh(us_user)
        
        print(f"✅ Created US user: {us_user.full_name} ({us_user.phone_number})")
        
        # Test 2: Create phone verification
        print("🔐 Creating phone verification...")
        verification = PhoneVerificationUS(
            user_id=us_user.id,
            phone_number=us_user.phone_number,
            verification_code="789012",
            expires_at=datetime.utcnow() + timedelta(minutes=15),
            market="us"
        )
        
        db.add(verification)
        db.commit()
        db.refresh(verification)
        
        print(f"✅ Created verification code: {verification.verification_code}")
        
        # Test 3: Query user
        print("🔍 Querying user...")
        found_user = db.query(UserUS).filter(UserUS.phone_number == "+15551234567").first()
        
        if found_user:
            print(f"✅ Found user: {found_user.full_name}")
            print(f"   Market: {found_user.market}")
            print(f"   Language: {found_user.language}")
            print(f"   Country: {found_user.country}")
            print(f"   Verified: {found_user.is_verified}")
        else:
            print("❌ User not found")
            return False
        
        # Test 4: Query verification
        print("🔍 Querying verification...")
        found_verification = db.query(PhoneVerificationUS).filter(
            PhoneVerificationUS.phone_number == "+15551234567"
        ).first()
        
        if found_verification:
            print(f"✅ Found verification: {found_verification.verification_code}")
            print(f"   Expires: {found_verification.expires_at}")
            print(f"   Used: {found_verification.is_used}")
        else:
            print("❌ Verification not found")
            return False
        
        print("✅ US database functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ US database test failed: {e}")
        return False
    finally:
        db.close()

def main():
    """Main test function"""
    print("🌍 MARQUE MULTI-MARKET DATABASE FUNCTIONALITY TEST")
    print("=" * 60)
    
    success_count = 0
    total_markets = 2
    
    # Test KG database
    if test_kg_database():
        success_count += 1
    
    # Test US database
    if test_us_database():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {success_count}/{total_markets} markets tested successfully")
    
    if success_count == total_markets:
        print("🎉 All database functionality tests passed!")
        print("\n✅ Database Features Verified:")
        print("   📱 User creation and storage")
        print("   🔐 Phone verification code storage")
        print("   🔍 User and verification queries")
        print("   🌍 Market-specific data handling")
        print("   💾 Data persistence and retrieval")
        print("\n🚀 Database is fully functional and ready for authentication system!")
        return 0
    else:
        print("⚠️  Some database tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
