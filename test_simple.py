#!/usr/bin/env python3
"""
Simple test to verify the authentication system works
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_market_detection():
    """Test market detection functionality"""
    print("🧪 Testing Market Detection...")
    
    try:
        from src.app_01.db.market_db import Market, detect_market_from_phone
        
        # Test KG phone detection
        kg_phone = "+996505325311"
        market = detect_market_from_phone(kg_phone)
        assert market == Market.KG
        print(f"✅ KG phone detection: {kg_phone} → {market.value}")
        
        # Test US phone detection
        us_phone = "+15551234567"
        market = detect_market_from_phone(us_phone)
        assert market == Market.US
        print(f"✅ US phone detection: {us_phone} → {market.value}")
        
        print("✅ Market detection tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Market detection test failed: {e}")
        return False

def test_market_config():
    """Test market configuration"""
    print("\n🧪 Testing Market Configuration...")
    
    try:
        from src.app_01.db.market_db import Market, MarketConfig
        
        # Test KG config
        kg_config = MarketConfig.get_config(Market.KG)
        assert kg_config["currency"] == "сом"
        assert kg_config["currency_code"] == "KGS"
        assert kg_config["language"] == "ru"
        print(f"✅ KG config: {kg_config['currency']} ({kg_config['currency_code']})")
        
        # Test US config
        us_config = MarketConfig.get_config(Market.US)
        assert us_config["currency"] == "$"
        assert us_config["currency_code"] == "USD"
        assert us_config["language"] == "en"
        print(f"✅ US config: {us_config['currency']} ({us_config['currency_code']})")
        
        print("✅ Market configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Market configuration test failed: {e}")
        return False

def test_phone_formatting():
    """Test phone number formatting"""
    print("\n🧪 Testing Phone Formatting...")
    
    try:
        from src.app_01.db.market_db import Market, format_phone_for_market
        
        # Test KG formatting
        kg_phone = "+996505325311"
        formatted_kg = format_phone_for_market(kg_phone, Market.KG)
        expected_kg = "+996 505 325 311"
        assert formatted_kg == expected_kg
        print(f"✅ KG formatting: {kg_phone} → {formatted_kg}")
        
        # Test US formatting
        us_phone = "+15551234567"
        formatted_us = format_phone_for_market(us_phone, Market.US)
        expected_us = "+1 (555) 123-4567"
        assert formatted_us == expected_us
        print(f"✅ US formatting: {us_phone} → {formatted_us}")
        
        print("✅ Phone formatting tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Phone formatting test failed: {e}")
        return False

def test_price_formatting():
    """Test price formatting"""
    print("\n🧪 Testing Price Formatting...")
    
    try:
        from src.app_01.db.market_db import Market, format_price_for_market
        
        # Test KG price formatting
        kg_price = format_price_for_market(2999.0, Market.KG)
        expected_kg = "2999.0 сом"
        assert kg_price == expected_kg
        print(f"✅ KG price: 2999.0 → {kg_price}")
        
        # Test US price formatting
        us_price = format_price_for_market(29.99, Market.US)
        expected_us = "$29.99"
        assert us_price == expected_us
        print(f"✅ US price: 29.99 → {us_price}")
        
        print("✅ Price formatting tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Price formatting test failed: {e}")
        return False

def test_schemas():
    """Test Pydantic schemas"""
    print("\n🧪 Testing Pydantic Schemas...")
    
    try:
        from src.app_01.schemas.auth import PhoneLoginRequest, VerifyCodeRequest, MarketEnum
        
        # Test valid KG phone request
        kg_request = PhoneLoginRequest(phone_number="+996505325311")
        assert kg_request.phone_number == "+996505325311"
        print(f"✅ KG phone request: {kg_request.phone_number}")
        
        # Test valid US phone request
        us_request = PhoneLoginRequest(phone_number="+15551234567")
        assert us_request.phone_number == "+15551234567"
        print(f"✅ US phone request: {us_request.phone_number}")
        
        # Test verification request
        verify_request = VerifyCodeRequest(
            phone_number="+996505325311",
            verification_code="123456"
        )
        assert verify_request.phone_number == "+996505325311"
        assert verify_request.verification_code == "123456"
        print(f"✅ Verification request: {verify_request.phone_number} with code {verify_request.verification_code}")
        
        print("✅ Schema validation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Schema validation test failed: {e}")
        return False

def test_invalid_inputs():
    """Test invalid input handling"""
    print("\n🧪 Testing Invalid Input Handling...")
    
    try:
        from src.app_01.schemas.auth import PhoneLoginRequest
        from pydantic import ValidationError
        
        # Test invalid phone number
        try:
            invalid_request = PhoneLoginRequest(phone_number="+44123456789")
            print("❌ Should have failed for invalid phone")
            return False
        except ValidationError:
            print("✅ Correctly rejected invalid phone number")
        
        print("✅ Invalid input handling tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Invalid input handling test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🌍 MARQUE MULTI-MARKET AUTHENTICATION - SIMPLE TESTS")
    print("=" * 60)
    
    tests = [
        test_market_detection,
        test_market_config,
        test_phone_formatting,
        test_price_formatting,
        test_schemas,
        test_invalid_inputs
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
