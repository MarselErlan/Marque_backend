"""
Test-driven development tests for authentication models
Tests for User, PhoneVerification, and related models for both KG and US markets
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from db.market_db import Market, MarketConfig
from models.users.market_user import UserKG, UserUS, get_user_model
from models.users.market_phone_verification import (
    PhoneVerificationKG, PhoneVerificationUS, create_verification_for_market, verify_code_for_market
)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestUserModels:
    """Test user models for both markets"""
    
    def setup_method(self):
        """Setup test database and session"""
        # Create tables for both markets
        from db.market_db import get_base
        kg_base = get_base(Market.KG)
        us_base = get_base(Market.US)
        
        # For testing, we'll use the same engine but different table names
        kg_base.metadata.create_all(bind=engine)
        us_base.metadata.create_all(bind=engine)
        
        self.db = TestingSessionLocal()
    
    def teardown_method(self):
        """Clean up test database"""
        self.db.close()
    
    def test_kg_user_creation(self):
        """Test KG user creation with phone number"""
        # Given
        phone_number = "+996505325311"
        full_name = "Анна Ахматова"
        
        # When
        user = UserKG(
            phone_number=phone_number,
            full_name=full_name,
            market="kg",
            language="ru",
            country="Kyrgyzstan"
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Then
        assert user.id is not None
        assert user.phone_number == phone_number
        assert user.full_name == full_name
        assert user.market == "kg"
        assert user.language == "ru"
        assert user.country == "Kyrgyzstan"
        assert user.currency == "сом"
        assert user.currency_code == "KGS"
        assert user.is_verified == False
        assert user.is_active == True
    
    def test_us_user_creation(self):
        """Test US user creation with phone number"""
        # Given
        phone_number = "+15551234567"
        full_name = "John Smith"
        
        # When
        user = UserUS(
            phone_number=phone_number,
            full_name=full_name,
            market="us",
            language="en",
            country="United States"
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Then
        assert user.id is not None
        assert user.phone_number == phone_number
        assert user.full_name == full_name
        assert user.market == "us"
        assert user.language == "en"
        assert user.country == "United States"
        assert user.currency == "$"
        assert user.currency_code == "USD"
        assert user.is_verified == False
        assert user.is_active == True
    
    def test_kg_user_phone_formatting(self):
        """Test KG phone number formatting"""
        # Given
        phone_number = "+996505325311"
        user = UserKG(phone_number=phone_number, market="kg")
        
        # When
        formatted_phone = user.formatted_phone
        
        # Then
        assert formatted_phone == "+996 505 325 311"
    
    def test_us_user_phone_formatting(self):
        """Test US phone number formatting"""
        # Given
        phone_number = "+15551234567"
        user = UserUS(phone_number=phone_number, market="us")
        
        # When
        formatted_phone = user.formatted_phone
        
        # Then
        assert formatted_phone == "+1 (555) 123-4567"
    
    def test_user_display_name(self):
        """Test user display name property"""
        # Given
        user_with_name = UserKG(phone_number="+996505325311", full_name="Анна Ахматова")
        user_without_name = UserKG(phone_number="+996505325312")
        
        # When & Then
        assert user_with_name.display_name == "Анна Ахматова"
        assert user_without_name.display_name == "User +996505325312"
    
    def test_get_user_model_by_market(self):
        """Test getting correct user model by market"""
        # When & Then
        assert get_user_model(Market.KG) == UserKG
        assert get_user_model(Market.US) == UserUS
    
    def test_user_get_by_phone(self):
        """Test finding user by phone number"""
        # Given
        phone_number = "+996505325311"
        user = UserKG(phone_number=phone_number, full_name="Test User")
        self.db.add(user)
        self.db.commit()
        
        # When
        found_user = UserKG.get_by_phone(self.db, phone_number)
        
        # Then
        assert found_user is not None
        assert found_user.phone_number == phone_number
        assert found_user.full_name == "Test User"

class TestPhoneVerification:
    """Test phone verification models for both markets"""
    
    def setup_method(self):
        """Setup test database and session"""
        from db.market_db import get_base
        kg_base = get_base(Market.KG)
        us_base = get_base(Market.US)
        
        kg_base.metadata.create_all(bind=engine)
        us_base.metadata.create_all(bind=engine)
        
        self.db = TestingSessionLocal()
    
    def teardown_method(self):
        """Clean up test database"""
        self.db.close()
    
    def test_kg_phone_verification_creation(self):
        """Test KG phone verification creation"""
        # Given
        phone_number = "+996505325311"
        verification_code = "123456"
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # When
        verification = PhoneVerificationKG(
            phone_number=phone_number,
            verification_code=verification_code,
            expires_at=expires_at,
            market="kg"
        )
        
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        
        # Then
        assert verification.id is not None
        assert verification.phone_number == phone_number
        assert verification.verification_code == verification_code
        assert verification.is_used == False
        assert verification.market == "kg"
        assert verification.is_valid == True
    
    def test_us_phone_verification_creation(self):
        """Test US phone verification creation"""
        # Given
        phone_number = "+15551234567"
        verification_code = "789012"
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        # When
        verification = PhoneVerificationUS(
            phone_number=phone_number,
            verification_code=verification_code,
            expires_at=expires_at,
            market="us"
        )
        
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        
        # Then
        assert verification.id is not None
        assert verification.phone_number == phone_number
        assert verification.verification_code == verification_code
        assert verification.is_used == False
        assert verification.market == "us"
        assert verification.is_valid == True
    
    def test_verification_code_expiration(self):
        """Test verification code expiration"""
        # Given
        expired_time = datetime.utcnow() - timedelta(minutes=5)
        verification = PhoneVerificationKG(
            phone_number="+996505325311",
            verification_code="123456",
            expires_at=expired_time,
            market="kg"
        )
        
        # When & Then
        assert verification.is_expired == True
        assert verification.is_valid == False
    
    def test_verification_code_mark_as_used(self):
        """Test marking verification code as used"""
        # Given
        verification = PhoneVerificationKG(
            phone_number="+996505325311",
            verification_code="123456",
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            market="kg"
        )
        
        self.db.add(verification)
        self.db.commit()
        
        # When
        verification.mark_as_used()
        self.db.commit()
        
        # Then
        assert verification.is_used == True
        assert verification.verified_at is not None
        assert verification.is_valid == False
    
    def test_verify_code_success(self):
        """Test successful code verification"""
        # Given
        phone_number = "+996505325311"
        verification_code = "123456"
        verification = PhoneVerificationKG(
            phone_number=phone_number,
            verification_code=verification_code,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            market="kg"
        )
        
        self.db.add(verification)
        self.db.commit()
        
        # When
        result = PhoneVerificationKG.verify_code(self.db, phone_number, verification_code)
        
        # Then
        assert result is not None
        assert result.verification_code == verification_code
        assert result.is_used == True
    
    def test_verify_code_invalid(self):
        """Test invalid code verification"""
        # Given
        phone_number = "+996505325311"
        invalid_code = "999999"
        
        # When
        result = PhoneVerificationKG.verify_code(self.db, phone_number, invalid_code)
        
        # Then
        assert result is None
    
    def test_verify_code_expired(self):
        """Test expired code verification"""
        # Given
        phone_number = "+996505325311"
        verification_code = "123456"
        verification = PhoneVerificationKG(
            phone_number=phone_number,
            verification_code=verification_code,
            expires_at=datetime.utcnow() - timedelta(minutes=5),
            market="kg"
        )
        
        self.db.add(verification)
        self.db.commit()
        
        # When
        result = PhoneVerificationKG.verify_code(self.db, phone_number, verification_code)
        
        # Then
        assert result is None

class TestMarketDetection:
    """Test market detection functionality"""
    
    def test_kg_phone_detection(self):
        """Test KG phone number market detection"""
        from db.market_db import detect_market_from_phone
        
        # Given
        kg_phone = "+996505325311"
        
        # When
        market = detect_market_from_phone(kg_phone)
        
        # Then
        assert market == Market.KG
    
    def test_us_phone_detection(self):
        """Test US phone number market detection"""
        from db.market_db import detect_market_from_phone
        
        # Given
        us_phone = "+15551234567"
        
        # When
        market = detect_market_from_phone(us_phone)
        
        # Then
        assert market == Market.US
    
    def test_invalid_phone_detection(self):
        """Test invalid phone number market detection"""
        from db.market_db import detect_market_from_phone
        
        # Given
        invalid_phone = "+44123456789"
        
        # When & Then
        with pytest.raises(ValueError):
            detect_market_from_phone(invalid_phone)

if __name__ == "__main__":
    pytest.main([__file__])
