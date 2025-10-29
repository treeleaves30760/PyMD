#!/usr/bin/env python3
"""
PyMD Code Execution Script

This script runs inside the Docker container to execute user code.
It reads code from stdin, executes it, and writes output to stdout/stderr.
"""
import sys
import traceback
import json
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr


def execute_code(code: str) -> dict:
    """
    Execute Python code and capture output.

    Args:
        code: Python code to execute

    Returns:
        dict with 'success', 'stdout', 'stderr', and optionally 'error'
    """
    stdout_capture = StringIO()
    stderr_capture = StringIO()

    result = {
        'success': False,
        'stdout': '',
        'stderr': '',
        'error': None
    }

    try:
        # Prepare execution globals
        exec_globals = {
            '__name__': '__main__',
            '__file__': '<pymd>',
            '__builtins__': __builtins__,
        }

        # Execute code with output capture
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, exec_globals)

        result['success'] = True
        result['stdout'] = stdout_capture.getvalue()
        result['stderr'] = stderr_capture.getvalue()

    except Exception as e:
        result['success'] = False
        result['stdout'] = stdout_capture.getvalue()
        result['stderr'] = stderr_capture.getvalue()
        result['error'] = {
            'type': type(e).__name__,
            'message': str(e),
            'traceback': traceback.format_exc()
        }

    return result


def main():
    """Main execution function"""
    try:
        # Read code from stdin
        code = sys.stdin.read()

        if not code or not code.strip():
            print(json.dumps({
                'success': False,
                'error': {
                    'type': 'ValueError',
                    'message': 'No code provided',
                    'traceback': ''
                }
            }))
            sys.exit(1)

        # Execute code
        result = execute_code(code)

        # Write result as JSON to stdout
        print(json.dumps(result))

        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)

    except Exception as e:
        # Handle unexpected errors
        error_result = {
            'success': False,
            'stdout': '',
            'stderr': '',
            'error': {
                'type': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc()
            }
        }
        print(json.dumps(error_result))
        sys.exit(1)


if __name__ == '__main__':
    main()
