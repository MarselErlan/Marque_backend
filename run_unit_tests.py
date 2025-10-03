#!/usr/bin/env python3
"""
Unit Test Runner for Marque
Runs all unit tests with coverage reporting
"""

import sys
import subprocess
from pathlib import Path


def run_unit_tests():
    """Run unit tests with pytest"""
    print("🧪 Running Unit Tests...")
    print("=" * 70)
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/unit",
        "-v",
        "--tb=short",
        "--cov=src/app_01",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "-m", "not slow"
    ])
    
    return result.returncode == 0


def run_all_tests_with_coverage():
    """Run all tests including integration"""
    print("\n🧪 Running All Tests with Coverage...")
    print("=" * 70)
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=src/app_01",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "--cov-branch"
    ])
    
    return result.returncode == 0


def run_specific_test_module(module_name):
    """Run a specific test module"""
    print(f"\n🧪 Running {module_name}...")
    print("=" * 70)
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        f"tests/unit/test_{module_name}.py",
        "-v",
        "--tb=short"
    ])
    
    return result.returncode == 0


def run_fast_tests():
    """Run only fast unit tests"""
    print("\n🧪 Running Fast Tests...")
    print("=" * 70)
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/unit",
        "-v",
        "--tb=short",
        "-m", "unit"
    ])
    
    return result.returncode == 0


def main():
    """Main test runner"""
    print("🌍 Marque - Unit Test Suite")
    print("=" * 70)
    print()
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest not installed!")
        print("Run: pip install pytest pytest-cov")
        return 1
    
    # Run tests
    results = []
    
    # 1. Run unit tests
    if run_unit_tests():
        print("\n✅ Unit tests passed!")
        results.append(True)
    else:
        print("\n❌ Unit tests failed!")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("\n📋 Coverage report generated in htmlcov/index.html")
        print("   Open it in your browser to see detailed coverage")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed")
        print("   Please review the failed tests above")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

