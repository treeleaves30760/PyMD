#!/usr/bin/env python3
"""
Simple PyMD CLI for testing
"""

import argparse
import os
import sys


def create_simple_test():
    """Create a simple test PyMD file"""
    content = '''```
pymd.h1("Hello PyMD!")
pymd.text("This is a simple test document.")

# Simple calculation
result = 2 + 2
pymd.text(f"2 + 2 = {result}")
```'''

    filename = "test_simple.pymd"
    with open(filename, 'w') as f:
        f.write(content)

    print(f"✅ Created test file: {filename}")
    return filename


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Simple PyMD CLI')
    parser.add_argument('--create-test', action='store_true',
                        help='Create a simple test file')

    args = parser.parse_args()

    if args.create_test:
        create_simple_test()
        print("Run: python simple_cli.py --help")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
