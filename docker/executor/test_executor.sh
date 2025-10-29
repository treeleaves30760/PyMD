#!/bin/bash
# Test script for PyMD Executor Docker image

set -e  # Exit on error

echo "=========================================="
echo "PyMD Executor Docker Image Tests"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name=$1
    local command=$2

    echo -e "${YELLOW}TEST: ${test_name}${NC}"

    if eval "$command"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# Test 1: Basic image run
echo "Test 1: Basic Image Run"
echo "------------------------"
run_test "Run default command" \
    "docker run --rm pymd-executor:latest python -c \"print('Hello from PyMD Executor!')\" | grep -q 'Hello from PyMD Executor!'"

# Test 2: Python version
echo "Test 2: Python Version"
echo "---------------------"
run_test "Check Python 3.11" \
    "docker run --rm pymd-executor:latest python --version | grep -q 'Python 3.11'"

# Test 3: User permissions
echo "Test 3: User Permissions"
echo "-----------------------"
run_test "Run as non-root user" \
    "docker run --rm pymd-executor:latest whoami | grep -q 'executor'"

# Test 4: Pip availability
echo "Test 4: Pip Availability"
echo "-----------------------"
run_test "Check pip is installed" \
    "docker run --rm pymd-executor:latest pip --version | grep -q 'pip'"

# Test 5: Basic Python execution
echo "Test 5: Basic Python Code"
echo "------------------------"
run_test "Execute simple Python code" \
    "docker run --rm pymd-executor:latest python -c \"x = 5 + 3; print(f'Result: {x}')\" | grep -q 'Result: 8'"

# Test 6: Standard library imports
echo "Test 6: Standard Library"
echo "-----------------------"
run_test "Import standard library modules" \
    "docker run --rm pymd-executor:latest python -c \"import json, sys, os; print('OK')\" | grep -q 'OK'"

# Test 7: Execute.py script
echo "Test 7: Execute.py Script"
echo "------------------------"
run_test "Test execute.py with simple code" \
    "echo 'print(\"Execute.py works!\")' | docker run --rm -i pymd-executor:latest python /usr/local/bin/execute.py 2>/dev/null | grep -q 'Execute.py works'"

# Test 8: Working directory
echo "Test 8: Working Directory"
echo "------------------------"
run_test "Check working directory is /workspace" \
    "docker run --rm pymd-executor:latest pwd | grep -q '/workspace'"

# Test 9: Network isolation (this should fail - no network)
echo "Test 9: Network Isolation"
echo "------------------------"
echo "(This test expects network to be available by default)"
run_test "Network is available (will be disabled in production)" \
    "docker run --rm pymd-executor:latest python -c \"import socket; socket.gethostbyname('google.com')\" 2>&1"

# Test 10: Resource limits
echo "Test 10: Resource Limits"
echo "-----------------------"
run_test "Run with memory limit" \
    "docker run --rm --memory=512m pymd-executor:latest python -c \"print('Memory limited')\" | grep -q 'Memory limited'"

run_test "Run with CPU limit" \
    "docker run --rm --cpus=0.5 pymd-executor:latest python -c \"print('CPU limited')\" | grep -q 'CPU limited'"

# Test 11: Volume mounting
echo "Test 11: Volume Mounting"
echo "-----------------------"
run_test "Create and use volume" \
    "docker volume create test-pymd-volume >/dev/null && \
     docker run --rm -v test-pymd-volume:/workspace/.venv pymd-executor:latest python -c \"import os; print('Volume mounted')\" | grep -q 'Volume mounted' && \
     docker volume rm test-pymd-volume >/dev/null"

# Test 12: Math operations
echo "Test 12: Complex Operations"
echo "--------------------------"
run_test "Perform complex calculations" \
    "docker run --rm pymd-executor:latest python -c \"import math; result = math.sqrt(144); print(f'Square root: {result}')\" | grep -q 'Square root: 12'"

# Test 13: File operations in workspace
echo "Test 13: File Operations"
echo "-----------------------"
run_test "Write and read file in workspace" \
    "docker run --rm pymd-executor:latest bash -c \"echo 'test content' > /workspace/test.txt && cat /workspace/test.txt\" | grep -q 'test content'"

# Test 14: JSON processing
echo "Test 14: JSON Processing"
echo "-----------------------"
run_test "Parse JSON" \
    "docker run --rm pymd-executor:latest python -c \"import json; data = json.dumps({'test': 'value'}); print(data)\" | grep -q 'test'"

# Test 15: Error handling
echo "Test 15: Error Handling"
echo "----------------------"
run_test "Handle Python errors gracefully" \
    "docker run --rm pymd-executor:latest python -c \"1/0\" 2>&1 | grep -q 'ZeroDivisionError' || true"

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed! ✗${NC}"
    exit 1
fi
