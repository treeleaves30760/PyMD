#!/usr/bin/env python3
"""
Integration tests for PyMD Docker Executor Service

This script tests the DockerExecutorService directly to ensure
it works correctly with the executor image.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../pymd/backend'))

import docker
import json
from datetime import datetime


class Colors:
    """ANSI color codes"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_test(name):
    """Print test name"""
    print(f"{Colors.YELLOW}TEST: {name}{Colors.NC}")


def print_pass():
    """Print pass message"""
    print(f"{Colors.GREEN}✓ PASSED{Colors.NC}\n")


def print_fail(message=""):
    """Print fail message"""
    print(f"{Colors.RED}✗ FAILED{Colors.NC}")
    if message:
        print(f"  Error: {message}")
    print()


def test_docker_connection():
    """Test Docker daemon connection"""
    print_test("Docker Connection")
    try:
        # Try Docker Desktop socket on Mac first
        socket_paths = [
            "unix:///Users/hsupohsiang/.docker/run/docker.sock",
            "unix:///var/run/docker.sock"
        ]

        client = None
        for socket_path in socket_paths:
            try:
                client = docker.DockerClient(base_url=socket_path)
                client.ping()
                break
            except:
                continue

        if not client:
            # Fallback to environment
            client = docker.from_env()
            client.ping()

        print_pass()
        return True, client
    except Exception as e:
        print_fail(str(e))
        return False, None


def test_image_exists(client):
    """Test that pymd-executor image exists"""
    print_test("Image Exists")
    try:
        client.images.get("pymd-executor:latest")
        print_pass()
        return True
    except docker.errors.ImageNotFound:
        print_fail("pymd-executor:latest image not found")
        return False
    except Exception as e:
        print_fail(str(e))
        return False


def test_simple_execution(client):
    """Test simple code execution"""
    print_test("Simple Code Execution")
    try:
        container = client.containers.run(
            image="pymd-executor:latest",
            command=["python", "-c", "print('Hello, World!')"],
            remove=True,
            detach=False
        )
        output = container.decode('utf-8').strip()

        if "Hello, World!" in output:
            print_pass()
            return True
        else:
            print_fail(f"Unexpected output: {output}")
            return False
    except Exception as e:
        print_fail(str(e))
        return False


def test_execute_py_json_output(client):
    """Test execute.py JSON output format"""
    print_test("Execute.py JSON Output")
    try:
        code = "print('Test output')"

        # Create container
        container = client.containers.create(
            image="pymd-executor:latest",
            command=["python", "/usr/local/bin/execute.py"],
            stdin_open=True,
            tty=False
        )

        # Start and attach
        container.start()
        sock = container.attach_socket(params={'stdin': 1, 'stream': 1})
        sock._sock.sendall(code.encode('utf-8'))
        sock.close()

        # Wait for completion
        result_dict = container.wait()
        logs = container.logs().decode('utf-8').strip()

        # Cleanup
        container.remove()

        # Parse JSON output
        result = json.loads(logs)

        # Check JSON structure
        if not isinstance(result, dict):
            print_fail("Output is not a JSON object")
            return False

        required_keys = ['success', 'stdout', 'stderr', 'error']
        for key in required_keys:
            if key not in result:
                print_fail(f"Missing key: {key}")
                return False

        # Check success
        if not result['success']:
            print_fail(f"Execution failed: {result.get('error')}")
            return False

        # Check stdout
        if "Test output" not in result['stdout']:
            print_fail(f"Expected output not found: {result['stdout']}")
            return False

        print(f"  Result: {result}")
        print_pass()
        return True

    except json.JSONDecodeError as e:
        print_fail(f"Invalid JSON output: {e}")
        return False
    except Exception as e:
        print_fail(str(e))
        return False


def test_execute_py_error_handling(client):
    """Test execute.py error handling"""
    print_test("Execute.py Error Handling")
    try:
        code = "1 / 0"  # Intentional error

        # Create container
        container = client.containers.create(
            image="pymd-executor:latest",
            command=["python", "/usr/local/bin/execute.py"],
            stdin_open=True,
            tty=False
        )

        # Start and attach
        container.start()
        sock = container.attach_socket(params={'stdin': 1, 'stream': 1})
        sock._sock.sendall(code.encode('utf-8'))
        sock.close()

        # Wait for completion
        result_dict = container.wait()
        logs = container.logs().decode('utf-8').strip()

        # Cleanup
        container.remove()

        # Parse JSON output
        result = json.loads(logs)

        # Should fail
        if result['success']:
            print_fail("Should have failed but succeeded")
            return False

        # Check error info
        if not result.get('error'):
            print_fail("Missing error information")
            return False

        error = result['error']
        if error['type'] != 'ZeroDivisionError':
            print_fail(f"Wrong error type: {error['type']}")
            return False

        print(f"  Error captured correctly: {error['type']}")
        print_pass()
        return True

    except Exception as e:
        print_fail(str(e))
        return False


def test_volume_operations(client):
    """Test Docker volume creation and usage"""
    print_test("Volume Operations")
    volume_name = f"test-pymd-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    try:
        # Create volume
        volume = client.volumes.create(name=volume_name)

        # Run container with volume
        output = client.containers.run(
            image="pymd-executor:latest",
            command=["python", "-c", "print('Volume works!')"],
            volumes={volume_name: {'bind': '/workspace/.venv', 'mode': 'rw'}},
            remove=True
        ).decode('utf-8')

        # Cleanup
        volume.remove()

        if "Volume works!" in output:
            print_pass()
            return True
        else:
            print_fail(f"Unexpected output: {output}")
            return False

    except Exception as e:
        # Cleanup on error
        try:
            vol = client.volumes.get(volume_name)
            vol.remove()
        except:
            pass
        print_fail(str(e))
        return False


def test_resource_limits(client):
    """Test resource limit enforcement"""
    print_test("Resource Limits")
    try:
        # Test with memory limit
        output = client.containers.run(
            image="pymd-executor:latest",
            command=["python", "-c", "print('Limited')"],
            mem_limit="512m",
            memswap_limit="512m",
            cpu_quota=50000,  # 0.5 CPU
            cpu_period=100000,
            remove=True
        ).decode('utf-8')

        if "Limited" in output:
            print_pass()
            return True
        else:
            print_fail(f"Unexpected output: {output}")
            return False
    except Exception as e:
        print_fail(str(e))
        return False


def test_network_isolation(client):
    """Test network isolation"""
    print_test("Network Isolation (network=none)")
    try:
        # Run with no network
        result = client.containers.run(
            image="pymd-executor:latest",
            command=["python", "-c", "import socket; socket.gethostbyname('google.com')"],
            network_mode="none",
            remove=True,
            detach=False
        )

        # Should fail with network disabled
        print_fail("Should have failed with network disabled")
        return False

    except docker.errors.ContainerError as e:
        # Expected to fail
        if "socket.gaierror" in str(e) or "Name or service not known" in str(e):
            print(f"  Network correctly isolated")
            print_pass()
            return True
        else:
            print_fail(f"Unexpected error: {e}")
            return False
    except Exception as e:
        print_fail(f"Unexpected exception: {e}")
        return False


def test_security_features(client):
    """Test security features"""
    print_test("Security Features (non-root user)")
    try:
        # Check user is not root
        output = client.containers.run(
            image="pymd-executor:latest",
            command=["whoami"],
            remove=True
        ).decode('utf-8').strip()

        if output == "executor":
            print(f"  Running as: {output}")
            print_pass()
            return True
        else:
            print_fail(f"Running as: {output} (expected: executor)")
            return False
    except Exception as e:
        print_fail(str(e))
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("PyMD Docker Executor Integration Tests")
    print("=" * 50)
    print()

    tests_passed = 0
    tests_failed = 0

    # Test 1: Docker connection
    success, client = test_docker_connection()
    if not success:
        print(f"{Colors.RED}Cannot proceed without Docker connection{Colors.NC}")
        return 1
    tests_passed += 1

    # All other tests
    tests = [
        (test_image_exists, client),
        (test_simple_execution, client),
        (test_execute_py_json_output, client),
        (test_execute_py_error_handling, client),
        (test_volume_operations, client),
        (test_resource_limits, client),
        (test_network_isolation, client),
        (test_security_features, client),
    ]

    for test_func, arg in tests:
        if test_func(arg):
            tests_passed += 1
        else:
            tests_failed += 1

    # Summary
    print()
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"{Colors.GREEN}Passed: {tests_passed}{Colors.NC}")
    print(f"{Colors.RED}Failed: {tests_failed}{Colors.NC}")
    print()

    if tests_failed == 0:
        print(f"{Colors.GREEN}All tests passed! ✓{Colors.NC}")
        return 0
    else:
        print(f"{Colors.RED}Some tests failed! ✗{Colors.NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
