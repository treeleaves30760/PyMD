#!/usr/bin/env python3
"""
Test basic PyMD functionality
"""

import unittest
from conftest import test_utils


class TestBasicFunctionality(unittest.TestCase):
    """Test basic PyMD rendering functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.renderer = test_utils.create_renderer()
    
    def test_headers(self):
        """Test header rendering"""
        content = """
# Main Header
## Sub Header
### Third Level
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_headers")
        
        test_utils.assert_contains(html, '<h1>Main Header</h1>')
        test_utils.assert_contains(html, '<h2>Sub Header</h2>')
        test_utils.assert_contains(html, '<h3>Third Level</h3>')
        
        print(f"✅ Headers test passed - output saved to {output_file}")
    
    def test_lists(self):
        """Test list rendering"""
        content = """
- Unordered item 1
- Unordered item 2
- Unordered item 3

1. Ordered item 1
2. Ordered item 2
3. Ordered item 3
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_lists")
        
        test_utils.assert_contains(html, '<ul>')
        test_utils.assert_contains(html, '<li>Unordered item 1</li>')
        test_utils.assert_contains(html, '<ol>')
        test_utils.assert_contains(html, '<li>Ordered item 1</li>')
        
        print(f"✅ Lists test passed - output saved to {output_file}")
    
    def test_plain_text(self):
        """Test plain text rendering"""
        content = """
This is a paragraph of text.
This is another paragraph.
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_plain_text")
        
        test_utils.assert_contains(html, '<p>This is a paragraph of text.</p>')
        test_utils.assert_contains(html, '<p>This is another paragraph.</p>')
        
        print(f"✅ Plain text test passed - output saved to {output_file}")
    
    def test_comments(self):
        """Test comment filtering"""
        content = """
# Header
// This is a comment and should be ignored
This is text.
// Another comment
"""
        html = self.renderer.parse_and_render(content)
        output_file = test_utils.save_test_output(html, "test_comments")
        
        test_utils.assert_contains(html, '<h1>Header</h1>')
        test_utils.assert_contains(html, '<p>This is text.</p>')
        test_utils.assert_not_contains(html, '// This is a comment')
        test_utils.assert_not_contains(html, '// Another comment')
        
        print(f"✅ Comments test passed - output saved to {output_file}")


def run_basic_tests():
    """Run all basic functionality tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicFunctionality)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_basic_tests()
    if success:
        print("\n🎉 All basic functionality tests passed!")
    else:
        print("\n❌ Some basic functionality tests failed!")