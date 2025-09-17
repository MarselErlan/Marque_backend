#!/usr/bin/env python3
"""
Demo script for Marque Multi-Market Authentication System
Shows the complete authentication flow for both KG and US markets
"""

import asyncio
import json
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🌍 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n{step}. {description}")
    print("-" * 40)

def demo_kg_market():
    """Demo KG market authentication flow"""
    print_header("KG MARKET AUTHENTICATION DEMO")
    
    print_step(1, "Send Verification Code")
    print("📱 Phone: +996505325311")
    print("🌍 Market: KG (Kyrgyzstan)")
    print("💰 Currency: сом (KGS)")
    print("🌐 Language: Russian")
    
    # Simulate API call
    print("\n📤 API Request:")
    print("POST /api/v1/auth/send-code")
    print(json.dumps({
        "phone_number": "+996505325311"
    }, indent=2))
    
    print("\n📥 API Response:")
    print(json.dumps({
        "success": True,
        "message": "Verification code sent successfully",
        "phone_number": "+996 505 325 311",
        "market": "kg",
        "language": "ru",
        "expires_in_minutes": 10,
        "demo_code": "123456"
    }, indent=2))
    
    print_step(2, "Verify Phone Code")
    print("🔢 Code: 123456")
    
    print("\n📤 API Request:")
    print("POST /api/v1/auth/verify-code")
    print(json.dumps({
        "phone_number": "+996505325311",
        "verification_code": "123456"
    }, indent=2))
    
    print("\n📥 API Response:")
    print(json.dumps({
        "success": True,
        "message": "Phone number verified successfully",
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "expires_in": 1800,
        "user_id": 1,
        "market": "kg",
        "is_new_user": True
    }, indent=2))
    
    print_step(3, "Get User Profile")
    print("🔐 Using JWT token")
    
    print("\n📤 API Request:")
    print("GET /api/v1/auth/profile")
    print("Authorization: Bearer <token>")
    
    print("\n📥 API Response:")
    print(json.dumps({
        "id": 1,
        "phone_number": "+996505325311",
        "formatted_phone": "+996 505 325 311",
        "full_name": None,
        "profile_image_url": None,
        "is_verified": True,
        "market": "kg",
        "language": "ru",
        "country": "Kyrgyzstan",
        "currency": "сом",
        "currency_code": "KGS",
        "last_login": datetime.now().isoformat() + "Z",
        "created_at": datetime.now().isoformat() + "Z"
    }, indent=2))

def demo_us_market():
    """Demo US market authentication flow"""
    print_header("US MARKET AUTHENTICATION DEMO")
    
    print_step(1, "Send Verification Code")
    print("📱 Phone: +15551234567")
    print("🌍 Market: US (United States)")
    print("💰 Currency: $ (USD)")
    print("🌐 Language: English")
    
    # Simulate API call
    print("\n📤 API Request:")
    print("POST /api/v1/auth/send-code")
    print(json.dumps({
        "phone_number": "+15551234567"
    }, indent=2))
    
    print("\n📥 API Response:")
    print(json.dumps({
        "success": True,
        "message": "Verification code sent successfully",
        "phone_number": "+1 (555) 123-4567",
        "market": "us",
        "language": "en",
        "expires_in_minutes": 15,
        "demo_code": "789012"
    }, indent=2))
    
    print_step(2, "Verify Phone Code")
    print("🔢 Code: 789012")
    
    print("\n📤 API Request:")
    print("POST /api/v1/auth/verify-code")
    print(json.dumps({
        "phone_number": "+15551234567",
        "verification_code": "789012"
    }, indent=2))
    
    print("\n📥 API Response:")
    print(json.dumps({
        "success": True,
        "message": "Phone number verified successfully",
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "expires_in": 1800,
        "user_id": 2,
        "market": "us",
        "is_new_user": False
    }, indent=2))
    
    print_step(3, "Get User Profile")
    print("🔐 Using JWT token")
    
    print("\n📤 API Request:")
    print("GET /api/v1/auth/profile")
    print("Authorization: Bearer <token>")
    
    print("\n📥 API Response:")
    print(json.dumps({
        "id": 2,
        "phone_number": "+15551234567",
        "formatted_phone": "+1 (555) 123-4567",
        "full_name": "John Smith",
        "profile_image_url": "https://example.com/profile.jpg",
        "is_verified": True,
        "market": "us",
        "language": "en",
        "country": "United States",
        "currency": "$",
        "currency_code": "USD",
        "last_login": datetime.now().isoformat() + "Z",
        "created_at": datetime.now().isoformat() + "Z"
    }, indent=2))

def demo_market_features():
    """Demo market-specific features"""
    print_header("MARKET-SPECIFIC FEATURES")
    
    print_step(1, "Supported Markets")
    print("\n📤 API Request:")
    print("GET /api/v1/auth/markets")
    
    print("\n📥 API Response:")
    print(json.dumps({
        "supported_markets": [
            {
                "market": "kg",
                "country": "Kyrgyzstan",
                "currency": "сом",
                "currency_code": "KGS",
                "language": "ru",
                "phone_prefix": "+996",
                "phone_format": "+996 XXX XXX XXX"
            },
            {
                "market": "us",
                "country": "United States",
                "currency": "$",
                "currency_code": "USD",
                "language": "en",
                "phone_prefix": "+1",
                "phone_format": "+1 (XXX) XXX-XXXX"
            }
        ],
        "default_market": "kg"
    }, indent=2))
    
    print_step(2, "Market Detection")
    print("🔍 Automatic market detection from phone numbers:")
    print("   +996505325311 → KG Market")
    print("   +15551234567  → US Market")
    
    print_step(3, "Phone Formatting")
    print("📱 Market-specific phone formatting:")
    print("   KG: +996505325311 → +996 505 325 311")
    print("   US: +15551234567  → +1 (555) 123-4567")
    
    print_step(4, "Currency Formatting")
    print("💰 Market-specific currency formatting:")
    print("   KG: 2999.0 → 2999 сом")
    print("   US: 29.99  → $29.99")

def demo_error_handling():
    """Demo error handling scenarios"""
    print_header("ERROR HANDLING DEMOS")
    
    print_step(1, "Invalid Phone Format")
    print("📱 Phone: +44123456789 (UK - not supported)")
    
    print("\n📤 API Request:")
    print("POST /api/v1/auth/send-code")
    print(json.dumps({
        "phone_number": "+44123456789"
    }, indent=2))
    
    print("\n📥 API Response (422 Validation Error):")
    print(json.dumps({
        "success": False,
        "error": "validation_error",
        "message": "Phone number must be in format +996XXXXXXXXX (KG) or +1XXXXXXXXXX (US)",
        "details": [
            {
                "loc": ["body", "phone_number"],
                "msg": "Phone number must be in format +996XXXXXXXXX (KG) or +1XXXXXXXXXX (US)",
                "type": "value_error"
            }
        ]
    }, indent=2))
    
    print_step(2, "Invalid Verification Code")
    print("🔢 Code: 999999 (invalid)")
    
    print("\n📤 API Request:")
    print("POST /api/v1/auth/verify-code")
    print(json.dumps({
        "phone_number": "+996505325311",
        "verification_code": "999999"
    }, indent=2))
    
    print("\n📥 API Response (400 Bad Request):")
    print(json.dumps({
        "success": False,
        "error": "validation_error",
        "message": "Invalid or expired verification code",
        "status_code": 400
    }, indent=2))
    
    print_step(3, "Unauthorized Access")
    print("🔐 Missing or invalid JWT token")
    
    print("\n📤 API Request:")
    print("GET /api/v1/auth/profile")
    print("Authorization: Bearer invalid_token")
    
    print("\n📥 API Response (401 Unauthorized):")
    print(json.dumps({
        "success": False,
        "error": "http_error",
        "message": "Invalid token",
        "status_code": 401
    }, indent=2))

def main():
    """Main demo function"""
    print("🌍 MARQUE MULTI-MARKET AUTHENTICATION SYSTEM")
    print("Complete End-to-End Demo")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run demos
    demo_kg_market()
    demo_us_market()
    demo_market_features()
    demo_error_handling()
    
    print_header("SYSTEM SUMMARY")
    print("✅ Multi-market support (KG & US)")
    print("✅ Phone number authentication")
    print("✅ SMS verification codes")
    print("✅ JWT token-based security")
    print("✅ Market-specific formatting")
    print("✅ Comprehensive error handling")
    print("✅ Test-driven development")
    print("✅ Separate databases per market")
    print("✅ Production-ready architecture")
    
    print("\n🚀 Ready for production deployment!")
    print("📚 Full documentation available in AUTH_SYSTEM_README.md")

if __name__ == "__main__":
    main()
