#!/usr/bin/env python3
"""
Test the new ``` syntax for separating markdown and code content
"""

import unittest
from conftest import test_utils


class TestNewSyntax(unittest.TestCase):
    """Test the new ``` syntax features"""

    def setUp(self):
        """Set up test environment"""
        self.renderer = test_utils.create_renderer()

    def test_mixed_content_structure(self):
        """Test mixing markdown content with code blocks"""
        content = """
# Hello

1. Good world
2. Split

- This is the first

```
A = 10
B = 20

for i in range(3):
    print(B)
```

# Good

```
print(A)
```

More text here.
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_mixed_content")

        # Check markdown elements
        test_utils.assert_contains(html, '<h1>Hello</h1>')
        test_utils.assert_contains(html, '<h1>Good</h1>')
        test_utils.assert_contains(html, '<ol><li>Good world</li>')
        test_utils.assert_contains(html, '<ul><li>This is the first</li>')
        test_utils.assert_contains(html, '<p>More text here.</p>')

        # Check code execution
        test_utils.assert_contains(html, '20\n20\n20')  # Loop output
        test_utils.assert_contains(html, '10')  # Variable A from second block

        print(
            f"✅ Mixed content structure test passed - output saved to {output_file}")

    def test_code_block_boundaries(self):
        """Test proper parsing of ``` boundaries"""
        content = """
Text before code.

```
x = "inside code block"
print(x)
```

Text between code blocks.

```
y = "second code block"
print(y)
```

Text after code.
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_code_boundaries")

        test_utils.assert_contains(html, '<p>Text before code.</p>')
        test_utils.assert_contains(html, '<p>Text between code blocks.</p>')
        test_utils.assert_contains(html, '<p>Text after code.</p>')
        test_utils.assert_contains(html, 'inside code block')
        test_utils.assert_contains(html, 'second code block')

        print(
            f"✅ Code block boundaries test passed - output saved to {output_file}")

    def test_empty_code_blocks(self):
        """Test handling of empty code blocks"""
        content = """
# Test Empty Blocks

```
```

Text after empty block.

```
print("Not empty")
```
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_empty_blocks")

        test_utils.assert_contains(html, '<h1>Test Empty Blocks</h1>')
        test_utils.assert_contains(html, '<p>Text after empty block.</p>')
        test_utils.assert_contains(html, 'Not empty')

        print(
            f"✅ Empty code blocks test passed - output saved to {output_file}")

    def test_nested_strings_in_code(self):
        """Test code blocks with complex nested strings"""
        content = """
# Nested Strings Test

```
code_sample = '''
def example():
    "This is a docstring"
    return "Hello World"
'''

print("Code sample defined")
pymd.code(code_sample, "python")
```
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_nested_strings")

        test_utils.assert_contains(html, 'Code sample defined')
        test_utils.assert_contains(html, '<pre><code class="language-python">')
        test_utils.assert_contains(html, 'def example():')

        print(f"✅ Nested strings test passed - output saved to {output_file}")

    def test_syntax_compatibility(self):
        """Test backward compatibility and new syntax together"""
        content = """
# Compatibility Test

Regular text paragraph.

- List item 1
- List item 2

```
# This is Python code, not a header
x = 42
print(f"Value: {x}")
```

1. Ordered item 1
2. Ordered item 2

```
pymd.h3("Generated Header from Code")
```

Final text paragraph.
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_compatibility")

        # Check that markdown elements work
        test_utils.assert_contains(html, '<h1>Compatibility Test</h1>')
        test_utils.assert_contains(html, '<ul><li>List item 1</li>')
        test_utils.assert_contains(html, '<ol><li>Ordered item 1</li>')
        test_utils.assert_contains(html, '<p>Regular text paragraph.</p>')
        test_utils.assert_contains(html, '<p>Final text paragraph.</p>')

        # Check code execution
        test_utils.assert_contains(html, 'Value: 42')
        test_utils.assert_contains(html, '<h3>Generated Header from Code</h3>')

        # Ensure Python comment doesn't become header
        test_utils.assert_not_contains(
            html, '<h1>This is Python code, not a header</h1>')

        print(
            f"✅ Syntax compatibility test passed - output saved to {output_file}")


def run_new_syntax_tests():
    """Run all new syntax tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNewSyntax)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_new_syntax_tests()
    if success:
        print("\n🎉 All new syntax tests passed!")
    else:
        print("\n❌ Some new syntax tests failed!")
