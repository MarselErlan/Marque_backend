"""
Test Runner for Multi-Market Authentication System
Run all tests with TDD approach
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_model_tests():
    """Run model tests"""
    print("🧪 Running Model Tests...")
    result = pytest.main([
        "src/app_01/tests/test_auth_models.py",
        "-v",
        "--tb=short"
    ])
    return result == 0

def run_integration_tests():
    """Run integration tests"""
    print("🔗 Running Integration Tests...")
    result = pytest.main([
        "src/app_01/tests/test_auth_integration.py",
        "-v",
        "--tb=short"
    ])
    return result == 0

def run_all_tests():
    """Run all tests"""
    print("🚀 Running All Tests...")
    result = pytest.main([
        "src/app_01/tests/",
        "-v",
        "--tb=short"
    ])
    return result == 0

def main():
    """Main test runner"""
    print("🌍 Marque Multi-Market Authentication - Test Suite")
    print("=" * 60)
    
    # Run tests in order (TDD approach)
    tests_passed = 0
    total_tests = 3
    
    # 1. Model tests
    if run_model_tests():
        print("✅ Model tests passed!")
        tests_passed += 1
    else:
        print("❌ Model tests failed!")
    
    print()
    
    # 2. Integration tests
    if run_integration_tests():
        print("✅ Integration tests passed!")
        tests_passed += 1
    else:
        print("❌ Integration tests failed!")
    
    print()
    
    # 3. All tests with coverage
    if run_all_tests():
        print("✅ All tests passed!")
        tests_passed += 1
    else:
        print("❌ Some tests failed!")
    
    print()
    print("=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} test suites passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Ready for production!")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix before deployment.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
