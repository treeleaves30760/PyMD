#!/usr/bin/env python3
"""
Test styling and CSS functionality
"""

import unittest
from conftest import test_utils


class TestStyling(unittest.TestCase):
    """Test styling and CSS features"""
    
    def setUp(self):
        """Set up test environment"""
        self.renderer = test_utils.create_renderer()
    
    def test_list_styling_elements(self):
        """Test that lists have proper CSS classes and structure"""
        content = """
# List Styling Test

- First unordered item
- Second unordered item  
- Third unordered item with longer text to test wrapping

1. First ordered item
2. Second ordered item
3. Third ordered item
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_list_styling")
        
        # Check basic list structure
        test_utils.assert_contains(html, '<ul>')
        test_utils.assert_contains(html, '<ol>')
        test_utils.assert_contains(html, '<li>')
        
        # Check CSS includes custom list styling
        test_utils.assert_contains(html, 'ul, ol {')
        test_utils.assert_contains(html, 'list-style: none;')
        test_utils.assert_contains(html, 'ul li::before {')
        test_utils.assert_contains(html, 'content: "•";')
        test_utils.assert_contains(html, 'ol li::before {')
        test_utils.assert_contains(html, 'counter(list-counter)')
        
        print(f"✅ List styling test passed - output saved to {output_file}")
    
    def test_code_output_styling(self):
        """Test code output styling"""
        content = """
# Code Output Styling

```
print("This is code output")
print("With multiple lines")
```
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_code_output_styling")
        
        # Check code output structure
        test_utils.assert_contains(html, '<pre class="code-output">')
        test_utils.assert_contains(html, 'This is code output')
        
        # Check CSS includes code output styling
        test_utils.assert_contains(html, '.code-output {')
        test_utils.assert_contains(html, 'font-family: \'SFMono-Regular\'')
        test_utils.assert_contains(html, 'white-space: pre-wrap;')
        
        print(f"✅ Code output styling test passed - output saved to {output_file}")
    
    def test_header_styling(self):
        """Test header styling"""
        content = """
# Main Header
## Secondary Header  
### Third Level Header
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_header_styling")
        
        # Check header structure
        test_utils.assert_contains(html, '<h1>Main Header</h1>')
        test_utils.assert_contains(html, '<h2>Secondary Header</h2>')
        test_utils.assert_contains(html, '<h3>Third Level Header</h3>')
        
        # Check CSS includes header styling
        test_utils.assert_contains(html, 'h1, h2, h3, h4, h5, h6 {')
        test_utils.assert_contains(html, 'h1 {')
        test_utils.assert_contains(html, 'border-bottom: 1px solid #eaecef;')
        
        print(f"✅ Header styling test passed - output saved to {output_file}")
    
    def test_comprehensive_styling(self):
        """Test comprehensive styling with multiple elements"""
        content = """
# Comprehensive Styling Test

This is a paragraph of text.

- Unordered list item
- Another unordered item

1. Ordered list item
2. Another ordered item

```
print("Code execution with output")
result = 42 * 2
print(f"Result: {result}")
```

```
code_sample = '''def example():
    return "hello"'''
pymd.code(code_sample, "python")
```

Final paragraph.
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_comprehensive_styling")
        
        # Check all major styling elements are present
        test_utils.assert_contains(html, '<h1>')
        test_utils.assert_contains(html, '<p>')
        test_utils.assert_contains(html, '<ul>')
        test_utils.assert_contains(html, '<ol>')
        test_utils.assert_contains(html, '<pre class="code-output">')
        test_utils.assert_contains(html, '<pre><code class="language-python">')
        
        # Check CSS completeness
        test_utils.assert_contains(html, 'body {')
        test_utils.assert_contains(html, 'ul, ol {')
        test_utils.assert_contains(html, '.code-output {')
        test_utils.assert_contains(html, 'pre {')
        
        print(f"✅ Comprehensive styling test passed - output saved to {output_file}")


def run_styling_tests():
    """Run all styling tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStyling)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_styling_tests()
    if success:
        print("\n🎉 All styling tests passed!")
    else:
        print("\n❌ Some styling tests failed!")