"""
Code execution and caching utilities for PyMD renderer
"""

import sys
import io
import traceback
import hashlib
from typing import Dict, Any


class CodeExecutor:
    """Handles Python code execution with caching and variable management"""
    
    def __init__(self):
        self.variables = {}
        self.code_cache = {}
        self.max_cache_size = 100  # Maximum number of cached results
    
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
                    custom_globals: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute Python code and capture output with caching"""
        # Generate cache key if not provided
        if cache_key is None:
            variables_snapshot = self._get_variable_snapshot()
            cache_key = self._get_code_hash(code, variables_snapshot)

        # Check cache first
        if cache_key in self.code_cache:
            cached_result = self.code_cache[cache_key]
            # Restore variables from cache
            self.variables.update(cached_result['variables'])
            return cached_result.copy()

        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        result = {
            'success': True,
            'output': '',
            'error': '',
            'variables': {},
            'cache_key': cache_key
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

            # Cache the successful result
            self.code_cache[cache_key] = result.copy()
            self._manage_cache_size()

        except Exception:
            result['success'] = False
            result['error'] = traceback.format_exc()
            result['output'] = stdout_capture.getvalue()
            result['variables'] = self.variables.copy()

            # Cache the error result too to avoid re-executing failing code
            self.code_cache[cache_key] = result.copy()
            self._manage_cache_size()

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return result