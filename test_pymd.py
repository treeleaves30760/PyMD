#!/usr/bin/env python3
"""
PyMD Test Script
Quick test to verify PyMD installation and basic functionality
"""

import sys
import os
from pymd_renderer import PyMDRenderer


def test_basic_rendering():
    """Test basic PyMD rendering functionality"""
    print("🧪 Testing PyMD Basic Rendering...")

    # Simple test content
    test_content = '''
```
pymd.h1("Test Document")
pymd.text("This is a test of PyMD rendering.")

pymd.h2("Math Test")
result = 2 + 2
pymd.text(f"2 + 2 = {result}")

pymd.h2("List Test")
data = [1, 2, 3, 4, 5]
pymd.text(f"Sample data: {data}")
```
'''

    try:
        renderer = PyMDRenderer()
        html = renderer.parse_and_render(test_content)

        # Check if HTML was generated
        if len(html) > 100 and '<h1>' in html and '<p>' in html:
            print("✅ Basic rendering test passed!")
            return True
        else:
            print("❌ Basic rendering test failed - HTML output incomplete")
            return False

    except Exception as e:
        print(f"❌ Basic rendering test failed with error: {e}")
        return False


def test_matplotlib_rendering():
    """Test matplotlib image rendering"""
    print("📊 Testing Matplotlib Rendering...")

    test_content = '''
```
import matplotlib.pyplot as plt
import numpy as np

pymd.h1("Plot Test")

x = np.linspace(0, 2*np.pi, 50)
y = np.sin(x)

plt.figure(figsize=(8, 4))
plt.plot(x, y)
plt.title("Test Plot")

pymd.image(plt.gcf(), "Test sine wave")
pymd.text("Plot rendering complete!")
```
'''

    try:
        renderer = PyMDRenderer()
        html = renderer.parse_and_render(test_content)

        # Check if image was embedded
        if 'data:image/png;base64,' in html:
            print("✅ Matplotlib rendering test passed!")
            return True
        else:
            print("❌ Matplotlib rendering test failed - no image found")
            return False

    except Exception as e:
        print(f"❌ Matplotlib rendering test failed with error: {e}")
        return False


def test_pandas_rendering():
    """Test pandas DataFrame rendering"""
    print("📋 Testing Pandas DataFrame Rendering...")

    test_content = '''
```
import pandas as pd

pymd.h1("DataFrame Test")

df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': ['x', 'y', 'z']
})

pymd.table(df)
pymd.text("DataFrame rendering complete!")
```
'''

    try:
        renderer = PyMDRenderer()
        html = renderer.parse_and_render(test_content)

        # Check if table was rendered
        if '<table' in html and 'pymd-table' in html:
            print("✅ Pandas DataFrame rendering test passed!")
            return True
        else:
            print("❌ Pandas DataFrame rendering test failed - no table found")
            return False

    except Exception as e:
        print(f"❌ Pandas DataFrame rendering test failed with error: {e}")
        return False


def test_cli_availability():
    """Test if CLI script is available and executable"""
    print("🖥️  Testing CLI Availability...")

    cli_path = os.path.join(os.path.dirname(__file__), 'pymd_cli.py')

    if os.path.exists(cli_path) and os.access(cli_path, os.X_OK):
        print("✅ CLI script is available and executable!")
        return True
    else:
        print("❌ CLI script is not available or not executable")
        return False


def run_all_tests():
    """Run all PyMD tests"""
    print("🐍 PyMD Test Suite")
    print("=" * 50)

    tests = [
        test_basic_rendering,
        test_matplotlib_rendering,
        test_pandas_rendering,
        test_cli_availability
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! PyMD is ready to use!")
        print("\n🚀 Quick start:")
        print("   python pymd_cli.py create my_document.pymd")
        print("   python pymd_cli.py serve my_document.pymd")
        return True
    else:
        print("⚠️  Some tests failed. Please check your installation.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
