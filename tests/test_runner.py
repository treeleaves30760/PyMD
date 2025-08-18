#!/usr/bin/env python3
"""
Main test runner for PyMD test suite
"""

import sys
import os
import unittest
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import test modules
from test_basic_functionality import run_basic_tests
from test_code_execution import run_code_execution_tests
from test_new_syntax import run_new_syntax_tests
from test_styling import run_styling_tests


def run_all_tests():
    """Run all PyMD tests"""
    print("🐍 PyMD Comprehensive Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Run basic functionality tests
    print("\n📝 Running Basic Functionality Tests...")
    test_results.append(("Basic Functionality", run_basic_tests()))
    
    # Run code execution tests
    print("\n🔧 Running Code Execution Tests...")
    test_results.append(("Code Execution", run_code_execution_tests()))
    
    # Run new syntax tests
    print("\n✨ Running New Syntax Tests...")
    test_results.append(("New Syntax", run_new_syntax_tests()))
    
    # Run styling tests
    print("\n🎨 Running Styling Tests...")
    test_results.append(("Styling", run_styling_tests()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! PyMD is working correctly!")
        print("\n🚀 Ready for use:")
        print("   • All basic functionality works")
        print("   • Code execution is stable")
        print("   • New ``` syntax is functional")
        print("   • Styling is consistent")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False


def run_specific_test(test_name):
    """Run a specific test suite"""
    test_functions = {
        'basic': run_basic_tests,
        'code': run_code_execution_tests,
        'syntax': run_new_syntax_tests,
        'styling': run_styling_tests
    }
    
    if test_name in test_functions:
        print(f"Running {test_name} tests...")
        return test_functions[test_name]()
    else:
        print(f"Unknown test: {test_name}")
        print(f"Available tests: {', '.join(test_functions.keys())}")
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Run all tests
        success = run_all_tests()
    
    sys.exit(0 if success else 1)