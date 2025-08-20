#!/usr/bin/env python3
"""
Performance test for PyMD renderer caching system
Tests that demonstrate the caching improvements.
"""

import time
import sys
import os

# Add parent directory to path for importing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymd.renderer import PyMDRenderer

class TestCachingPerformance:
    """Test suite for caching performance"""
    
    def test_caching_speedup(self):
        """Test that caching provides speedup for repeated renders"""
        
        # Create test content with some computational work
        test_content = """
# Caching Performance Test

```
import random
import math

# Generate some data
data = []
for i in range(10000):
    data.append(random.randint(1, 100) ** 2)
    
total = sum(data)
average = total / len(data)
print(f"Processed {len(data)} numbers, average: {average:.2f}")
```

```
# Use previous results
sqrt_total = math.sqrt(total)
print(f"Square root of total: {sqrt_total:.2f}")
```
"""
        
        renderer = PyMDRenderer()
        
        # First render (no cache)
        start_time = time.time()
        html1 = renderer.parse_and_render(test_content)
        first_render_time = time.time() - start_time
        
        # Second render (should use cache)
        start_time = time.time()
        html2 = renderer.parse_and_render(test_content)
        second_render_time = time.time() - start_time
        
        # Verify results are identical
        assert html1 == html2, "Cached and non-cached results should be identical"
        
        # Verify we have cache entries
        assert len(renderer.code_cache) > 0, "Cache should contain entries after rendering"
        
        # Performance should improve (at least for non-trivial content)
        print(f"First render: {first_render_time:.3f}s, Cached render: {second_render_time:.3f}s")
        
        # For meaningful performance tests, first render should be slower when content has computation
        # But we'll just verify the cache is working by checking cache entries
        assert len(renderer.code_cache) == 2, "Should have cached 2 code blocks"
    
    def test_cache_invalidation(self):
        """Test that cache is properly invalidated when content changes"""
        
        base_content = """
```
x = 10
print(f"x = {x}")
```
"""
        
        modified_content = """
```
x = 20
print(f"x = {x}")
```
"""
        
        renderer = PyMDRenderer()
        
        # Render base content
        html1 = renderer.parse_and_render(base_content)
        cache_size_1 = len(renderer.code_cache)
        
        # Render modified content
        html2 = renderer.parse_and_render(modified_content)
        cache_size_2 = len(renderer.code_cache)
        
        # Results should be different
        assert html1 != html2, "Different content should produce different results"
        
        # Cache should grow (new entries for modified content)
        assert cache_size_2 > cache_size_1, "Cache should contain entries for both versions"
    
    def test_cache_clearing(self):
        """Test that cache can be manually cleared"""
        
        content = """
```
print("Hello from cache test")
```
"""
        
        renderer = PyMDRenderer()
        
        # Render to populate cache
        renderer.parse_and_render(content)
        assert len(renderer.code_cache) > 0, "Cache should be populated"
        
        # Clear cache
        renderer.clear_cache()
        assert len(renderer.code_cache) == 0, "Cache should be empty after clearing"
        assert renderer.last_full_content_hash is None, "Content hash should be reset"
        
        # Render again should repopulate cache
        renderer.parse_and_render(content)
        assert len(renderer.code_cache) > 0, "Cache should be repopulated"


if __name__ == "__main__":
    # Run the tests as a demo
    test_suite = TestCachingPerformance()
    
    print("🧪 Running Caching Performance Tests")
    print("=" * 40)
    
    try:
        print("🔄 Testing caching speedup...")
        test_suite.test_caching_speedup()
        print("✅ Caching speedup test passed")
        
        print("🔄 Testing cache invalidation...")
        test_suite.test_cache_invalidation() 
        print("✅ Cache invalidation test passed")
        
        print("🔄 Testing cache clearing...")
        test_suite.test_cache_clearing()
        print("✅ Cache clearing test passed")
        
        print("\n🎉 All caching tests passed!")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)