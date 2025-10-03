"""
Unit tests for database utilities
Tests for market detection, phone formatting, and database operations
"""

import pytest
from src.app_01.db.market_db import (
    Market,
    detect_market_from_phone,
    format_phone_for_market,
    get_market_config,
    db_manager
)


class TestMarketDetection:
    """Test market detection from phone numbers"""
    
    def test_detect_kg_market_with_996(self):
        """Test KG market detection with +996 prefix"""
        assert detect_market_from_phone("+996555123456") == Market.KG
        assert detect_market_from_phone("+996700987654") == Market.KG
        assert detect_market_from_phone("+996312445566") == Market.KG
    
    def test_detect_us_market_with_1(self):
        """Test US market detection with +1 prefix"""
        assert detect_market_from_phone("+12125551234") == Market.US
        assert detect_market_from_phone("+14155551234") == Market.US
        assert detect_market_from_phone("+13105551234") == Market.US
    
    def test_detect_kg_market_without_plus_raises_error(self):
        """Test that phone without + raises ValueError"""
        with pytest.raises(ValueError):
            detect_market_from_phone("996555123456")
    
    def test_detect_us_market_without_plus_raises_error(self):
        """Test that phone without + raises ValueError"""
        with pytest.raises(ValueError):
            detect_market_from_phone("12125551234")
    
    def test_invalid_phone_raises_error(self):
        """Test that invalid phone raises ValueError"""
        with pytest.raises(ValueError):
            detect_market_from_phone("+999999999")
        with pytest.raises(ValueError):
            detect_market_from_phone("invalid")
        with pytest.raises(ValueError):
            detect_market_from_phone("")


class TestPhoneFormatting:
    """Test phone number formatting for markets"""
    
    def test_format_kg_phone(self):
        """Test KG phone formatting with proper prefix"""
        formatted = format_phone_for_market("+996555123456", Market.KG)
        # Should format with spaces: +996 555 123 456
        assert formatted.startswith("+996")
        assert " " in formatted
    
    def test_format_us_phone(self):
        """Test US phone formatting with proper prefix"""
        formatted = format_phone_for_market("+12125551234", Market.US)
        # Should format as: +1 (212) 555-1234
        assert formatted.startswith("+1")
        assert "(" in formatted and ")" in formatted
    
    def test_format_returns_as_is_for_invalid(self):
        """Test formatting returns phone as-is if invalid format"""
        phone = "996555123456"  # No +
        formatted = format_phone_for_market(phone, Market.KG)
        assert formatted == phone  # Should return unchanged
    
    def test_format_with_proper_format(self):
        """Test formatting with proper format"""
        formatted = format_phone_for_market("+996555123456", Market.KG)
        assert formatted == "+996 555 123 456"


class TestMarketConfig:
    """Test market configuration retrieval"""
    
    def test_kg_config(self):
        """Test KG market configuration"""
        config = get_market_config(Market.KG)
        assert isinstance(config, dict)
        assert config["country"] == "Kyrgyzstan"
        assert config["country_code"] == "KG"
        assert config["currency_code"] == "KGS"
        assert config["language"] == "ru"
        assert config["phone_prefix"] == "+996"
    
    def test_us_config(self):
        """Test US market configuration"""
        config = get_market_config(Market.US)
        assert isinstance(config, dict)
        assert config["country"] == "United States"
        assert config["country_code"] == "US"
        assert config["currency_code"] == "USD"
        assert config["language"] == "en"
        assert config["phone_prefix"] == "+1"


class TestDatabaseManager:
    """Test database manager operations"""
    
    def test_get_session_factory_kg(self):
        """Test getting session factory for KG"""
        factory = db_manager.get_session_factory(Market.KG)
        assert factory is not None
        assert callable(factory)
    
    def test_get_session_factory_us(self):
        """Test getting session factory for US"""
        factory = db_manager.get_session_factory(Market.US)
        assert factory is not None
        assert callable(factory)
    
    def test_get_engine_kg(self):
        """Test getting engine for KG"""
        engine = db_manager.get_engine(Market.KG)
        assert engine is not None
    
    def test_get_engine_us(self):
        """Test getting engine for US"""
        engine = db_manager.get_engine(Market.US)
        assert engine is not None
    
    def test_markets_have_separate_engines(self):
        """Test that markets have separate engines"""
        kg_engine = db_manager.get_engine(Market.KG)
        us_engine = db_manager.get_engine(Market.US)
        assert kg_engine != us_engine


@pytest.mark.parametrize("phone,expected_market", [
    ("+996555123456", Market.KG),
    ("+996700111222", Market.KG),
    ("+12125551234", Market.US),
    ("+14155559999", Market.US),
])
def test_market_detection_parametrized(phone, expected_market):
    """Parametrized test for market detection with valid phones"""
    assert detect_market_from_phone(phone) == expected_market


@pytest.mark.parametrize("phone,market,should_contain", [
    ("+996555123456", Market.KG, "+996"),
    ("+12125551234", Market.US, "+1"),
])
def test_phone_formatting_parametrized(phone, market, should_contain):
    """Parametrized test for phone formatting with valid phones"""
    formatted = format_phone_for_market(phone, market)
    assert should_contain in formatted

