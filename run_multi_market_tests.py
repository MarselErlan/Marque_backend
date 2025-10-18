#!/usr/bin/env python3
"""
Multi-Market Admin Test Runner

This script runs all tests for the multi-market admin system and provides
a comprehensive report of the test results.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Exit Code: {result.returncode}")
        print(f"Duration: {duration:.2f}s")
        
        if result.stdout:
            print(f"\n📤 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print(f"\n📥 STDERR:")
            print(result.stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False, "", str(e)

def main():
    """Run all multi-market admin tests"""
    print("🌍 Multi-Market Admin System - Test Suite")
    print("=" * 60)
    
    # Check if pytest is available
    print("🔍 Checking test environment...")
    
    # Install required packages if needed
    success, stdout, stderr = run_command(
        "pip install pytest pytest-asyncio",
        "Installing test dependencies"
    )
    
    if not success:
        print("❌ Failed to install test dependencies")
        return False
    
    # Run multi-market admin unit tests
    success1, stdout1, stderr1 = run_command(
        "python -m pytest tests/test_multi_market_admin.py -v --tb=short",
        "Running Multi-Market Admin Unit Tests"
    )
    
    # Run multi-market integration tests
    success2, stdout2, stderr2 = run_command(
        "python -m pytest tests/test_multi_market_integration.py -v --tb=short",
        "Running Multi-Market Integration Tests"
    )
    
    # Run all multi-market tests together
    success3, stdout3, stderr3 = run_command(
        "python -m pytest tests/test_multi_market*.py -v --tb=short --maxfail=5",
        "Running All Multi-Market Tests"
    )
    
    # Generate test report
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    
    tests = [
        ("Multi-Market Admin Unit Tests", success1),
        ("Multi-Market Integration Tests", success2),
        ("All Multi-Market Tests", success3)
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<35} {status}")
    
    print(f"\n📈 Overall Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! Multi-market admin system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above for details.")
        return False

def run_specific_test():
    """Run a specific test for debugging"""
    print("🔧 Running specific multi-market admin test...")
    
    # Test the authentication backend directly
    try:
        from tests.test_multi_market_admin import TestMultiMarketAuthenticationBackend
        from src.app_01.admin.multi_market_admin_views import MultiMarketAuthenticationBackend
        
        print("✅ Successfully imported multi-market admin classes")
        
        # Test market configuration
        from src.app_01.db.market_db import Market, MarketConfig
        
        kg_config = MarketConfig.get_config(Market.KG)
        us_config = MarketConfig.get_config(Market.US)
        
        print(f"✅ KG Market Config: {kg_config['currency']} ({kg_config['country']})")
        print(f"✅ US Market Config: {us_config['currency']} ({us_config['country']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in specific test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--specific":
        success = run_specific_test()
    else:
        success = main()
    
    sys.exit(0 if success else 1)
