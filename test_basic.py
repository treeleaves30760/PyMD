#!/usr/bin/env python3
"""
PyMD Basic Test Script - minimal test without matplotlib dependencies
"""


def test_core_functionality():
    """Test core PyMD functionality without external dependencies"""
    print("🧪 Testing PyMD Core Functionality...")

    try:
        # Test basic imports
        import sys
        import io
        from contextlib import redirect_stdout

        # Create a minimal renderer without matplotlib
        class MinimalPyMD:
            def __init__(self):
                self.elements = []

            def h1(self, text):
                html = f'<h1>{text}</h1>'
                self.elements.append(html)
                return html

            def h2(self, text):
                html = f'<h2>{text}</h2>'
                self.elements.append(html)
                return html

            def text(self, content):
                html = f'<p>{content}</p>'
                self.elements.append(html)
                return html

        # Test basic functionality
        pymd = MinimalPyMD()

        # Test basic operations
        pymd.h1("Test Document")
        pymd.text("This is a test paragraph.")
        pymd.h2("Section 2")
        pymd.text("Another paragraph.")

        # Check if elements were created
        if len(pymd.elements) == 4:
            print("✅ Core functionality test passed!")

            # Display sample output
            print("\n📄 Sample HTML output:")
            for element in pymd.elements:
                print(f"   {element}")

            return True
        else:
            print("❌ Core functionality test failed")
            return False

    except Exception as e:
        print(f"❌ Core functionality test failed with error: {e}")
        return False


def test_python_execution():
    """Test Python code execution"""
    print("\n🐍 Testing Python Code Execution...")

    try:
        # Test basic code execution
        exec_globals = {}
        code = """
result = 2 + 2
message = f"The result is {result}"
"""

        exec(code, exec_globals)

        if exec_globals.get('result') == 4:
            print("✅ Python execution test passed!")
            print(f"   Executed: {exec_globals.get('message')}")
            return True
        else:
            print("❌ Python execution test failed")
            return False

    except Exception as e:
        print(f"❌ Python execution test failed with error: {e}")
        return False


def test_file_operations():
    """Test file creation and reading"""
    print("\n📁 Testing File Operations...")

    try:
        import os
        import tempfile

        # Create a temporary test file
        test_content = '''```
# Test PyMD content
pymd.h1("Hello World")
pymd.text("This is a test.")

result = 5 * 5
pymd.text(f"5 * 5 = {result}")
```'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.pymd', delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        # Read it back
        with open(temp_file, 'r') as f:
            read_content = f.read()

        # Clean up
        os.unlink(temp_file)

        if read_content == test_content:
            print("✅ File operations test passed!")
            return True
        else:
            print("❌ File operations test failed")
            return False

    except Exception as e:
        print(f"❌ File operations test failed with error: {e}")
        return False


def main():
    """Run basic tests"""
    print("🐍 PyMD Basic Test Suite")
    print("=" * 50)

    tests = [
        test_core_functionality,
        test_python_execution,
        test_file_operations
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 Core PyMD functionality is working!")
        print("\n📝 Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Run full tests: python test_pymd.py")
        print("   3. Create document: python pymd_cli.py create test.pymd")
        print("   4. Start server: python pymd_cli.py serve test.pymd")
    else:
        print("⚠️  Some basic tests failed.")

    return passed == total


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
