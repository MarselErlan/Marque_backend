#!/usr/bin/env python3
"""
Focused Coverage Tests
Targeted tests to increase coverage from 88% to 95%+
"""

import pytest
import os
from unittest.mock import patch, MagicMock

# Import the modules we need to test
from src.app_01.db.market_db import Market, MarketConfig, MarketDatabaseManager
from src.app_01.schemas.auth import PhoneLoginRequest, VerifyCodeRequest


class TestMarketConfigErrorHandling:
    """Test MarketConfig error handling and edge cases"""
    
    def test_market_config_unsupported_market(self):
        """Test MarketConfig.get_config with unsupported market"""
        with pytest.raises(ValueError, match="Unsupported market"):
            MarketConfig.get_config("INVALID_MARKET")
    
    def test_market_config_kg_config(self):
        """Test MarketConfig KG configuration"""
        kg_config = MarketConfig.get_config(Market.KG)
        assert kg_config["currency_code"] == "KGS"
        assert kg_config["country_code"] == "KG"
        assert kg_config["country"] == "Kyrgyzstan"
    
    def test_market_config_us_config(self):
        """Test MarketConfig US configuration"""
        us_config = MarketConfig.get_config(Market.US)
        assert us_config["currency_code"] == "USD"
        assert us_config["country_code"] == "US"
        assert us_config["country"] == "United States"


class TestMarketDatabaseManagerEdgeCases:
    """Test MarketDatabaseManager edge cases"""
    
    def test_get_db_session_generator(self):
        """Test get_db_session generator function"""
        # Mock the manager and session factory
        with patch('src.app_01.db.market_db.MarketDatabaseManager._setup_market_database'):
            manager = MarketDatabaseManager()
            
            # Create a mock session
            mock_session = MagicMock()
            mock_session_factory = MagicMock(return_value=mock_session)
            manager.session_factories[Market.KG] = mock_session_factory
            
            # Test the generator
            session_gen = manager.get_db_session(Market.KG)
            session = next(session_gen)
            
            assert session == mock_session
            
            # Test that session is closed when generator exits
            try:
                next(session_gen)
            except StopIteration:
                pass
            
            # Verify session.close was called
            mock_session.close.assert_called_once()
    
    def test_market_database_manager_invalid_market(self):
        """Test MarketDatabaseManager with invalid market"""
        with patch('src.app_01.db.market_db.MarketDatabaseManager._setup_market_database'):
            manager = MarketDatabaseManager()
            
            # Test with invalid market (should raise KeyError)
            with pytest.raises(KeyError):
                manager.get_engine("INVALID_MARKET")


class TestAuthSchemaValidation:
    """Test auth schema validation edge cases"""
    
    def test_phone_login_request_kg_validation(self):
        """Test PhoneLoginRequest validation for KG phone numbers"""
        # Valid KG phone number
        valid_kg_phone = "+996555123456"
        request = PhoneLoginRequest(phone_number=valid_kg_phone)
        assert request.phone_number == valid_kg_phone
        
        # Invalid KG phone number (wrong length)
        with pytest.raises(ValueError, match="Phone number must be in format"):
            PhoneLoginRequest(phone_number="+9965512345")  # Too short
    
    def test_phone_login_request_us_validation(self):
        """Test PhoneLoginRequest validation for US phone numbers"""
        # Valid US phone number
        valid_us_phone = "+15551234567"
        request = PhoneLoginRequest(phone_number=valid_us_phone)
        assert request.phone_number == valid_us_phone
        
        # Invalid US phone number (wrong length)
        with pytest.raises(ValueError, match="Phone number must be in format"):
            PhoneLoginRequest(phone_number="+155512345")  # Too short
    
    def test_phone_login_request_invalid_format(self):
        """Test PhoneLoginRequest with completely invalid phone number"""
        with pytest.raises(ValueError, match="Phone number must be in format"):
            PhoneLoginRequest(phone_number="+123456789")  # Wrong country code
    
    def test_verify_code_request_invalid_code(self):
        """Test VerifyCodeRequest with invalid verification code"""
        # Valid code
        valid_request = VerifyCodeRequest(
            phone_number="+996555123456",
            verification_code="123456"
        )
        assert valid_request.verification_code == "123456"
        
        # Invalid code (contains letters)
        with pytest.raises(ValueError, match="Verification code must contain only digits"):
            VerifyCodeRequest(
                phone_number="+996555123456",
                verification_code="12345a"
            )
        
        # Invalid code (contains special characters)
        with pytest.raises(ValueError, match="Verification code must contain only digits"):
            VerifyCodeRequest(
                phone_number="+996555123456",
                verification_code="123-45"
            )
    
    def test_phone_number_with_spaces_and_dashes(self):
        """Test phone number validation with various formatting"""
        # Phone number with spaces and dashes
        formatted_phone = "+996 555-123-456"
        request = PhoneLoginRequest(phone_number=formatted_phone)
        assert request.phone_number == "+996555123456"  # Should be cleaned
        
        # Phone number with parentheses
        formatted_phone = "+1 (555) 123-4567"
        request = PhoneLoginRequest(phone_number=formatted_phone)
        assert request.phone_number == "+15551234567"  # Should be cleaned
    
    def test_phone_number_edge_cases(self):
        """Test phone number edge cases"""
        # Empty phone number
        with pytest.raises(ValueError):
            PhoneLoginRequest(phone_number="")
        
        # Phone number with only country code
        with pytest.raises(ValueError):
            PhoneLoginRequest(phone_number="+996")
        
        # Phone number with extra digits
        with pytest.raises(ValueError):
            PhoneLoginRequest(phone_number="+9965551234567890")


class TestMarketDatabaseManagerMethods:
    """Test MarketDatabaseManager getter methods"""
    
    def test_market_database_manager_methods(self):
        """Test MarketDatabaseManager getter methods"""
        # Mock the manager to avoid actual database connections
        with patch('src.app_01.db.market_db.MarketDatabaseManager._setup_market_database'):
            manager = MarketDatabaseManager()
            
            # Mock the internal dictionaries
            mock_engine = MagicMock()
            mock_session_factory = MagicMock()
            mock_base = MagicMock()
            
            manager.engines[Market.KG] = mock_engine
            manager.session_factories[Market.KG] = mock_session_factory
            manager.bases[Market.KG] = mock_base
            
            # Test get_engine
            result_engine = manager.get_engine(Market.KG)
            assert result_engine == mock_engine
            
            # Test get_session_factory
            result_session_factory = manager.get_session_factory(Market.KG)
            assert result_session_factory == mock_session_factory
            
            # Test get_base
            result_base = manager.get_base(Market.KG)
            assert result_base == mock_base


class TestMarketDatabaseInitialization:
    """Test market database initialization edge cases"""
    
    def test_market_database_manager_initialization_error(self):
        """Test MarketDatabaseManager initialization with missing environment variables"""
        # Mock os.getenv to return None for database URLs
        with patch('os.getenv', return_value=None):
            with patch('src.app_01.db.market_db.create_engine') as mock_create_engine:
                mock_engine = MagicMock()
                mock_create_engine.return_value = mock_engine
                
                # This should not raise an error but use fallback URLs
                manager = MarketDatabaseManager()
                
                # Verify that create_engine was called with fallback URLs
                assert mock_create_engine.call_count == 2  # Called for both KG and US


def test_market_enum_values():
    """Test Market enum values"""
    assert Market.KG.value == "kg"
    assert Market.US.value == "us"
    
    # Test enum iteration
    markets = list(Market)
    assert len(markets) == 2
    assert Market.KG in markets
    assert Market.US in markets


def test_market_config_properties():
    """Test MarketConfig properties"""
    kg_config = MarketConfig.get_config(Market.KG)
    
    # Test all properties are accessible
    assert "currency_code" in kg_config
    assert "country_code" in kg_config
    assert "country" in kg_config
    assert "currency" in kg_config
    assert "language" in kg_config
    assert "timezone" in kg_config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
