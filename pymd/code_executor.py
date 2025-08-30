"""
Code execution and caching utilities for PyMD renderer
"""

import sys
import io
import traceback
import hashlib
import time
from typing import Dict, Any, Optional


class CodeExecutor:
    """Handles Python code execution with caching and variable management"""
    
    def __init__(self):
        self.variables = {}
        self.code_cache = {}
        self.max_cache_size = 100  # Maximum number of cached results
        self.execution_stats = {
            'total_executions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0
        }
    
    def _get_code_hash(self, code: str, variables_snapshot: Dict[str, Any]) -> str:
        """Generate a hash for code block and variable state"""
        # Create a combined hash of code content and relevant variables
        content = code + str(sorted(variables_snapshot.items()))
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _get_variable_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of current variables for caching"""
        # Only include serializable variables for hashing
        snapshot = {}
        for key, value in self.variables.items():
            try:
                # Try to serialize the value to check if it's cacheable
                str(value)
                snapshot[key] = value
            except:
                # Skip non-serializable values
                pass
        return snapshot

    def clear_cache(self):
        """Clear all cached results"""
        self.code_cache.clear()
        self.execution_stats = {
            'total_executions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0
        }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return self.execution_stats.copy()
    
    def _detect_heavy_imports(self, code: str) -> list[str]:
        """Detect imports that might take time to load"""
        heavy_imports = []
        lines = code.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                # Check for known heavy imports
                if any(lib in line for lib in ['matplotlib', 'pandas', 'numpy', 'scipy', 'sklearn', 'tensorflow', 'torch', 'plotly']):
                    heavy_imports.append(line)
        
        return heavy_imports

    def _manage_cache_size(self):
        """Remove oldest cache entries if cache is too large"""
        if len(self.code_cache) > self.max_cache_size:
            # Remove oldest half of cache entries
            items_to_remove = len(self.code_cache) - (self.max_cache_size // 2)
            keys_to_remove = list(self.code_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self.code_cache[key]
    
    def _parse_input_mocks(self, code: str) -> Dict[str, str]:
        """Parse input mock values from comments in the format: # input: value"""
        input_mocks = {}
        lines = code.split('\n')

        for line in lines:
            # Look for input() calls with mock values in comments
            if 'input(' in line and '# input:' in line:
                # Extract the mock value after "# input:"
                comment_part = line.split('# input:')[1].strip()
                # Find the input() call to get a unique identifier
                # For simplicity, we'll use line position, but this could be improved
                input_mocks[len(input_mocks)] = comment_part
            elif 'input(' in line and '# input:' not in line:
                input_mocks[len(input_mocks)] = ''

        return input_mocks

    def _create_mock_input(self, input_mocks: Dict[str, str]):
        """Create a mock input function that returns predefined values"""
        mock_values = list(input_mocks.values())
        call_count = [0]  # Use list to make it mutable in closure

        def mock_input(_prompt=''):
            value = mock_values[call_count[0]]
            call_count[0] += 1
            # Don't print anything - just return the mock value silently
            return value

        return mock_input
    
    def execute_code(self, code: str, cache_key: str = None, 
                    custom_globals: Dict[str, Any] = None, 
                    status_callback: Optional[callable] = None) -> Dict[str, Any]:
        """Execute Python code and capture output with caching"""
        start_time = time.time()
        
        # Generate cache key if not provided
        if cache_key is None:
            variables_snapshot = self._get_variable_snapshot()
            cache_key = self._get_code_hash(code, variables_snapshot)

        # Check cache first
        if cache_key in self.code_cache:
            cached_result = self.code_cache[cache_key].copy()
            # Restore variables from cache
            self.variables.update(cached_result['variables'])
            
            # Update stats
            self.execution_stats['cache_hits'] += 1
            self.execution_stats['total_executions'] += 1
            
            if status_callback:
                status_callback("Using cached result")
            
            return cached_result

        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # Check for heavy imports and notify
        heavy_imports = self._detect_heavy_imports(code)
        if heavy_imports and status_callback:
            status_callback(f"Loading libraries: {', '.join(heavy_imports)}")
        
        result = {
            'success': True,
            'output': '',
            'error': '',
            'variables': {},
            'cache_key': cache_key,
            'execution_time': 0.0,
            'was_cached': False,
            'heavy_imports': heavy_imports
        }

        try:
            # Parse input mock values
            input_mocks = self._parse_input_mocks(code)

            # Create execution environment
            exec_globals = {
                '__builtins__': __builtins__,
                **self.variables
            }
            
            # Add custom globals if provided
            if custom_globals:
                exec_globals.update(custom_globals)

            # Override input function if there are input() calls in the code
            if 'input(' in code:
                if input_mocks:
                    exec_globals['input'] = self._create_mock_input(input_mocks)
                else:
                    # Check if there are any input() calls without mock values
                    lines = code.split('\n')
                    input_line_found = False
                    for line in lines:
                        if 'input(' in line and '# input:' not in line:
                            input_line_found = True
                            break

                    if input_line_found:
                        raise RuntimeError("input() function found without mock value. "
                                         "Please add '# input: <value>' comment after each input() call.")

            # Redirect output
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Execute the code
            exec(code, exec_globals)

            # Update variables but preserve certain keys
            updated_vars = {k: v for k, v in exec_globals.items()
                           if not k.startswith('__') and k not in ['input']}
            self.variables.update(updated_vars)

            result['output'] = stdout_capture.getvalue()
            result['variables'] = self.variables.copy()
            
            # Record execution time
            execution_time = time.time() - start_time
            result['execution_time'] = execution_time
            
            # Update stats
            self.execution_stats['cache_misses'] += 1
            self.execution_stats['total_executions'] += 1
            self.execution_stats['total_execution_time'] += execution_time
            self.execution_stats['average_execution_time'] = (
                self.execution_stats['total_execution_time'] / self.execution_stats['total_executions']
            )

            # Cache the successful result
            self.code_cache[cache_key] = result.copy()
            self._manage_cache_size()

        except Exception:
            result['success'] = False
            result['error'] = traceback.format_exc()
            result['output'] = stdout_capture.getvalue()
            result['variables'] = self.variables.copy()
            
            # Record execution time even for errors
            execution_time = time.time() - start_time
            result['execution_time'] = execution_time
            
            # Update stats
            self.execution_stats['cache_misses'] += 1
            self.execution_stats['total_executions'] += 1
            self.execution_stats['total_execution_time'] += execution_time
            self.execution_stats['average_execution_time'] = (
                self.execution_stats['total_execution_time'] / self.execution_stats['total_executions']
            )

            # Cache the error result too to avoid re-executing failing code
            self.code_cache[cache_key] = result.copy()
            self._manage_cache_size()

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return result