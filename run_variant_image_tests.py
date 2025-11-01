#!/usr/bin/env python3
"""
Test runner for variant image feature.

Runs:
1. Unit tests for database model and schema
2. API integration tests
3. Regression tests
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all variant image tests"""
    
    print("=" * 80)
    print("🧪 VARIANT IMAGE FEATURE - TEST SUITE")
    print("=" * 80)
    print()
    
    # Test files
    test_files = [
        "tests/test_variant_image_feature.py",
        "tests/test_variant_image_api_integration.py"
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        print(f"\n📋 Running: {test_file}")
        print("-" * 80)
        
        # Run pytest with verbose output
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                test_file,
                "-v",
                "--tb=short",
                "--color=yes",
                "-x"  # Stop on first failure
            ],
            capture_output=False
        )
        
        if result.returncode == 0:
            print(f"✅ {test_file} - ALL TESTS PASSED")
        else:
            print(f"❌ {test_file} - SOME TESTS FAILED")
            total_failed += 1
        
        print("-" * 80)
    
    # Summary
    print()
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    if total_failed == 0:
        print("✅ ALL TEST SUITES PASSED!")
        print()
        print("✓ Database model tests")
        print("✓ Schema serialization tests")
        print("✓ API integration tests")
        print("✓ Regression tests")
        print()
        print("🎉 Variant image feature is ready for deployment!")
        return 0
    else:
        print(f"❌ {total_failed} test suite(s) failed")
        print()
        print("Please review the failures above and fix them.")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)

