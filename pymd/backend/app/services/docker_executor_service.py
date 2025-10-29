"""Docker Executor Service

This service manages Docker containers for executing user code in isolated environments.
"""
import docker
import json
import logging
import os
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import uuid

from pymd.backend.app.config import settings

logger = logging.getLogger(__name__)


class DockerExecutorService:
    """Service for managing Docker container execution"""

    def __init__(self):
        """Initialize Docker client"""
        self.client: Optional[docker.DockerClient] = None
        self.available: bool = False

        if not getattr(settings, "DOCKER_ENABLED", True):
            logger.warning("Docker integration disabled via configuration")
            return

        base_url = self._resolve_base_url()

        try:
            self.client = docker.DockerClient(base_url=base_url)
            # Test connection
            self.client.ping()
            self.available = True
            logger.info(f"Docker client initialized successfully using {base_url}")
        except docker.errors.DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None
            self.available = False
        except Exception as e:
            logger.exception(f"Unexpected error while initializing Docker client: {e}")
            self.client = None
            self.available = False

    def _resolve_base_url(self) -> str:
        """
        Determine the Docker base URL from settings or environment variables.

        Returns:
            Docker connection string
        """
        # Preference order: settings override -> env var -> default socket
        configured_host = getattr(settings, "DOCKER_HOST_OVERRIDE", None)
        if configured_host:
            candidate = configured_host
        else:
            candidate = os.environ.get("DOCKER_HOST", "unix:///var/run/docker.sock")

        # Some environments expose Docker contexts as http+docker without the unix adapter.
        # Fallback to the standard Unix socket when that happens.
        if candidate.startswith("http+docker://"):
            context_key = candidate[len("http+docker://"):].strip("/")
            if context_key in ("localunixsocket", "localhost"):
                return "unix:///var/run/docker.sock"

        return candidate

    def _ensure_available(self) -> bool:
        """
        Check whether the Docker client is available.

        Returns:
            True if Docker operations can be performed, False otherwise.
        """
        if self.client and self.available:
            return True

        logger.error("Docker client is not available")
        return False

    def _get_resource_limits(self, tier: str = "free") -> Dict[str, Any]:
        """
        Get resource limits based on user tier.

        Args:
            tier: User tier ("free" or "pro")

        Returns:
            Dictionary of resource limits
        """
        if tier == "pro":
            return {
                "timeout": settings.EXECUTION_TIMEOUT_PRO,
                "cpu_limit": settings.EXECUTION_CPU_LIMIT_PRO,
                "memory_limit": settings.EXECUTION_MEMORY_LIMIT_PRO,
            }
        else:
            return {
                "timeout": settings.EXECUTION_TIMEOUT_FREE,
                "cpu_limit": settings.EXECUTION_CPU_LIMIT_FREE,
                "memory_limit": settings.EXECUTION_MEMORY_LIMIT_FREE,
            }

    def create_volume(self, volume_name: str) -> bool:
        """
        Create a Docker volume for an environment.

        Args:
            volume_name: Name of the volume to create

        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_available():
            return False

        try:
            self.client.volumes.create(
                name=volume_name,
                driver=settings.DOCKER_VOLUME_DRIVER,
                labels={
                    "app": "pymd",
                    "created_at": datetime.utcnow().isoformat(),
                }
            )
            logger.info(f"Created Docker volume: {volume_name}")
            return True
        except docker.errors.APIError as e:
            if "already exists" in str(e).lower():
                logger.warning(f"Volume {volume_name} already exists")
                return True
            logger.error(f"Failed to create volume {volume_name}: {e}")
            return False

    def delete_volume(self, volume_name: str) -> bool:
        """
        Delete a Docker volume.

        Args:
            volume_name: Name of the volume to delete

        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_available():
            return False

        try:
            volume = self.client.volumes.get(volume_name)
            volume.remove()
            logger.info(f"Deleted Docker volume: {volume_name}")
            return True
        except docker.errors.NotFound:
            logger.warning(f"Volume {volume_name} not found")
            return True  # Already gone
        except docker.errors.APIError as e:
            logger.error(f"Failed to delete volume {volume_name}: {e}")
            return False

    def volume_exists(self, volume_name: str) -> bool:
        """
        Check if a Docker volume exists.

        Args:
            volume_name: Name of the volume

        Returns:
            True if volume exists, False otherwise
        """
        if not self._ensure_available():
            return False

        try:
            self.client.volumes.get(volume_name)
            return True
        except docker.errors.NotFound:
            return False

    def execute_code(
        self,
        code: str,
        volume_name: str,
        tier: str = "free",
        environment_vars: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, str, str, Optional[str]]:
        """
        Execute Python code in an isolated Docker container.

        Args:
            code: Python code to execute
            volume_name: Name of the Docker volume to mount
            tier: User tier for resource limits
            environment_vars: Optional environment variables

        Returns:
            Tuple of (success, stdout, stderr, error_message)
        """
        if not self._ensure_available():
            error_message = "Docker is not available; cannot execute code"
            logger.error(error_message)
            return False, "", "", error_message

        container = None
        try:
            limits = self._get_resource_limits(tier)

            # Calculate CPU quota (cpu_limit * 100000 microseconds per second)
            cpu_quota = int(float(limits["cpu_limit"]) * 100000)

            # Container configuration
            container_config = {
                "image": settings.DOCKER_EXECUTOR_IMAGE,
                "command": ["python", "-u", "/workspace/execute.py"],
                "stdin_open": True,
                "detach": True,
                "remove": False,  # Manual cleanup to capture logs
                "volumes": {
                    volume_name: {"bind": "/workspace/.venv", "mode": "rw"}
                },
                "mem_limit": limits["memory_limit"],
                "memswap_limit": limits["memory_limit"],  # No swap
                "cpu_quota": cpu_quota,
                "cpu_period": 100000,
                "network_mode": settings.DOCKER_NETWORK_MODE,
                "security_opt": ["no-new-privileges"],
                "cap_drop": ["ALL"],
                "pids_limit": settings.DOCKER_PIDS_LIMIT,
                "read_only": False,  # Need write access to /workspace
                "labels": {
                    "app": "pymd",
                    "execution_id": str(uuid.uuid4()),
                    "created_at": datetime.utcnow().isoformat(),
                }
            }

            if environment_vars:
                container_config["environment"] = environment_vars

            # Create and start container
            container = self.client.containers.run(**container_config)

            # Send code to container via stdin
            socket = container.attach_socket(params={"stdin": 1, "stream": 1})
            try:
                socket._sock.sendall(code.encode("utf-8"))
            finally:
                socket.close()

            # Wait for execution with timeout
            result = container.wait(timeout=limits["timeout"])
            exit_code = result.get("StatusCode", 1)

            # Get logs
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")

            # Try to parse JSON output from execute.py
            try:
                execution_result = json.loads(logs)
                success = execution_result.get("success", False)
                stdout = execution_result.get("stdout", "")
                stderr = execution_result.get("stderr", "")
                error = execution_result.get("error")
                error_message = None
                if error:
                    error_message = f"{error['type']}: {error['message']}"

                return success, stdout, stderr, error_message

            except json.JSONDecodeError:
                # If not JSON, treat as raw output
                if exit_code == 0:
                    return True, logs, "", None
                else:
                    return False, "", logs, "Execution failed"

        except docker.errors.ContainerError as e:
            logger.error(f"Container error: {e}")
            return False, "", str(e), f"Container error: {e}"

        except docker.errors.ImageNotFound:
            error_msg = f"Docker image {settings.DOCKER_EXECUTOR_IMAGE} not found"
            logger.error(error_msg)
            return False, "", error_msg, error_msg

        except docker.errors.APIError as e:
            logger.error(f"Docker API error: {e}")
            return False, "", str(e), f"Docker error: {e}"

        except Exception as e:
            logger.error(f"Unexpected error during execution: {e}")
            return False, "", str(e), f"Unexpected error: {e}"

        finally:
            # Cleanup container
            if container:
                try:
                    container.stop(timeout=1)
                    container.remove()
                except Exception as e:
                    logger.warning(f"Failed to cleanup container: {e}")

    def install_package(
        self,
        package_name: str,
        volume_name: str,
        tier: str = "free"
    ) -> Tuple[bool, str, str]:
        """
        Install a Python package in an environment.

        Args:
            package_name: Name of the package to install (e.g., "numpy==1.24.0")
            volume_name: Name of the Docker volume
            tier: User tier for resource limits

        Returns:
            Tuple of (success, output, error_message)
        """
        if not self._ensure_available():
            error_message = "Docker is not available; cannot install packages"
            logger.error(error_message)
            return False, "", error_message

        container = None
        try:
            limits = self._get_resource_limits(tier)
            cpu_quota = int(float(limits["cpu_limit"]) * 100000)

            # Prepare pip install command
            install_cmd = [
                "pip", "install", "--user", "--no-cache-dir", package_name
            ]

            # Container configuration
            container = self.client.containers.run(
                image=settings.DOCKER_EXECUTOR_IMAGE,
                command=install_cmd,
                detach=True,
                remove=False,
                volumes={
                    volume_name: {"bind": "/workspace/.venv", "mode": "rw"}
                },
                mem_limit=limits["memory_limit"],
                cpu_quota=cpu_quota,
                cpu_period=100000,
                network_mode="bridge",  # Need network for pip install
                labels={"app": "pymd", "type": "package_install"}
            )

            # Wait for installation with timeout
            # Timeout configurable via settings
            result = container.wait(timeout=getattr(
                settings, "PACKAGE_INSTALL_TIMEOUT", 300))
            exit_code = result.get("StatusCode", 1)

            # Get logs
            output = container.logs(stdout=True, stderr=True).decode("utf-8")

            success = exit_code == 0
            error_message = None if success else f"Installation failed with exit code {exit_code}"

            return success, output, error_message

        except docker.errors.APIError as e:
            logger.error(f"Docker API error during package installation: {e}")
            return False, "", f"Docker error: {e}"

        except Exception as e:
            logger.error(f"Unexpected error during package installation: {e}")
            return False, "", f"Unexpected error: {e}"

        finally:
            if container:
                try:
                    container.stop(timeout=1)
                    container.remove()
                except Exception as e:
                    logger.warning(f"Failed to cleanup install container: {e}")

    def list_installed_packages(self, volume_name: str) -> Optional[list]:
        """
        List installed packages in an environment.

        Args:
            volume_name: Name of the Docker volume

        Returns:
            List of package names with versions, or None on error
        """
        if not self._ensure_available():
            logger.error("Docker is not available; cannot list packages")
            return None

        container = None
        try:
            container = self.client.containers.run(
                image=settings.DOCKER_EXECUTOR_IMAGE,
                command=["pip", "list", "--format=json", "--user"],
                detach=True,
                remove=False,
                volumes={
                    volume_name: {"bind": "/workspace/.venv", "mode": "ro"}
                },
                network_mode="none"
            )

            result = container.wait(timeout=30)
            if result.get("StatusCode", 1) != 0:
                return None

            output = container.logs(stdout=True, stderr=False).decode("utf-8")
            packages = json.loads(output)
            return packages

        except Exception as e:
            logger.error(f"Failed to list packages: {e}")
            return None

        finally:
            if container:
                try:
                    container.stop(timeout=1)
                    container.remove()
                except Exception as e:
                    logger.warning(f"Failed to cleanup list container: {e}")

    def cleanup_stopped_containers(self) -> int:
        """
        Clean up stopped PyMD containers.

        Returns:
            Number of containers removed
        """
        if not self._ensure_available():
            return 0

        try:
            containers = self.client.containers.list(
                all=True,
                filters={
                    "status": "exited",
                    "label": "app=pymd"
                }
            )

            count = 0
            for container in containers:
                try:
                    container.remove()
                    count += 1
                except Exception as e:
                    logger.warning(
                        f"Failed to remove container {container.id}: {e}")

            logger.info(f"Cleaned up {count} stopped containers")
            return count

        except Exception as e:
            logger.error(f"Failed to cleanup containers: {e}")
            return 0

    def get_volume_size(self, volume_name: str) -> Optional[int]:
        """
        Get the size of a Docker volume in bytes.

        Note: This is an approximation using Docker inspect.

        Args:
            volume_name: Name of the volume

        Returns:
            Size in bytes, or None if not available
        """
        if not self._ensure_available():
            return None

        try:
            volume = self.client.volumes.get(volume_name)
            # Docker doesn't directly provide volume size
            # This would need to be calculated differently depending on driver
            # For now, return None - size tracking will be done via database
            return None
        except Exception as e:
            logger.error(f"Failed to get volume size: {e}")
            return None


# Global instance
docker_executor_service = DockerExecutorService()
