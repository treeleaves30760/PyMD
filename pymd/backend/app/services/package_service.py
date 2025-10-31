"""Package Service

This service manages package installation, uninstallation, and tracking for user environments.
"""
import logging
import re
import asyncio
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
import uuid

from pymd.backend.app.models import (
    UserEnvironment,
    EnvironmentStatus,
    EnvironmentPackage,
    User,
    UserRole,
)
from pymd.backend.app.config import settings
from pymd.backend.app.services.docker_executor_service import docker_executor_service
from pymd.backend.app.services.environment_service import (
    EnvironmentService,
    EnvironmentServiceError,
    EnvironmentNotFoundError,
)

logger = logging.getLogger(__name__)


class PackageServiceError(Exception):
    """Base exception for package service errors"""
    pass


class PackageQuotaExceededError(PackageServiceError):
    """Raised when package quota is exceeded"""
    pass


class PackageNotFoundError(PackageServiceError):
    """Raised when package is not found"""
    pass


class PackageInstallationError(PackageServiceError):
    """Raised when package installation fails"""
    pass


class PackageService:
    """Service for managing packages in user environments"""

    def __init__(self):
        self.docker_service = docker_executor_service
        self.environment_service = EnvironmentService()

    def _get_tier_limits(self, user_role: UserRole) -> Dict[str, int]:
        """
        Get package limits based on user role.

        Args:
            user_role: User's role

        Returns:
            Dictionary with limits
        """
        if user_role == UserRole.ADMIN or user_role == UserRole.USER:
            return {
                "max_packages": settings.MAX_PACKAGES_PRO,
                "max_environments": settings.MAX_ENVIRONMENTS_PRO,
                "max_size_bytes": settings.MAX_ENVIRONMENT_SIZE_PRO,
            }
        else:
            return {
                "max_packages": settings.MAX_PACKAGES_FREE,
                "max_environments": settings.MAX_ENVIRONMENTS_FREE,
                "max_size_bytes": settings.MAX_ENVIRONMENT_SIZE_FREE,
            }

    def _parse_package_spec(self, package_spec: str) -> Tuple[str, Optional[str]]:
        """
        Parse package specification into name and version.

        Args:
            package_spec: Package specification (e.g., "numpy", "pandas==2.0.0", "flask>=2.0")

        Returns:
            Tuple of (package_name, version_spec)
        """
        # Match patterns like: numpy, numpy==1.24.0, numpy>=1.24, numpy~=1.24
        match = re.match(r'^([a-zA-Z0-9_\-\.]+)(.*)?$', package_spec.strip())
        if not match:
            raise PackageServiceError(f"Invalid package specification: {package_spec}")

        package_name = match.group(1)
        version_spec = match.group(2).strip() if match.group(2) else None

        return package_name, version_spec

    async def check_package_quota(
        self,
        environment_id: uuid.UUID,
        packages_to_add: int,
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> bool:
        """
        Check if user can install more packages.

        Args:
            environment_id: Environment UUID
            packages_to_add: Number of packages to add
            user_id: User UUID
            db: Database session

        Returns:
            True if quota allows, False otherwise

        Raises:
            PackageQuotaExceededError: If quota would be exceeded
        """
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise PackageServiceError("User not found")

        # Get limits
        limits = self._get_tier_limits(user.role)

        # Get environment
        environment = await self.environment_service.get_environment(
            environment_id, user_id, db
        )

        # Check current package count
        current_count = environment.package_count
        new_count = current_count + packages_to_add

        if new_count > limits["max_packages"]:
            raise PackageQuotaExceededError(
                f"Package limit exceeded. Maximum {limits['max_packages']} packages allowed. "
                f"Current: {current_count}, Attempting to add: {packages_to_add}"
            )

        return True

    async def install_packages(
        self,
        environment_id: uuid.UUID,
        packages: List[str],
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Install one or more packages in an environment.

        Args:
            environment_id: Environment UUID
            packages: List of package specifications (e.g., ["numpy", "pandas==2.0.0"])
            user_id: User UUID
            db: Database session

        Returns:
            Tuple of (successful_installs, failed_installs)
            Each item is a dict with {package, version, message}

        Raises:
            PackageQuotaExceededError: If quota would be exceeded
            EnvironmentNotFoundError: If environment not found
        """
        # Get environment
        environment = await self.environment_service.get_environment(
            environment_id, user_id, db
        )

        if environment.status != EnvironmentStatus.ACTIVE:
            raise PackageServiceError(
                f"Environment is not active (status: {environment.status})"
            )

        # Check quota
        await self.check_package_quota(environment_id, len(packages), user_id, db)

        successful = []
        failed = []

        # Get user role for tier
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        tier = "pro" if user.role in [UserRole.ADMIN, UserRole.USER] else "free"

        for package_spec in packages:
            try:
                # Parse package specification
                package_name, version_spec = self._parse_package_spec(package_spec)
                full_spec = f"{package_name}{version_spec}" if version_spec else package_name

                # Check if already installed
                existing = await db.execute(
                    select(EnvironmentPackage).where(
                        and_(
                            EnvironmentPackage.environment_id == environment_id,
                            EnvironmentPackage.package_name == package_name
                        )
                    )
                )
                existing_package = existing.scalar_one_or_none()

                if existing_package:
                    logger.warning(f"Package {package_name} already installed in environment {environment_id}")
                    failed.append({
                        "package": package_name,
                        "version": version_spec,
                        "message": f"Package {package_name} is already installed"
                    })
                    continue

                # Install package via Docker
                logger.info(f"Installing package {full_spec} in environment {environment_id}")

                success, output, error_message = await asyncio.to_thread(
                    self.docker_service.install_package,
                    full_spec,
                    environment.volume_name,
                    tier
                )

                if not success:
                    logger.error(f"Failed to install {full_spec}: {error_message}")
                    failed.append({
                        "package": package_name,
                        "version": version_spec,
                        "message": error_message or "Installation failed"
                    })
                    continue

                # Extract installed version from pip output
                installed_version = version_spec.lstrip("=<>~!") if version_spec else None

                # Create package record in database
                package_record = EnvironmentPackage(
                    id=uuid.uuid4(),
                    environment_id=environment_id,
                    package_name=package_name,
                    version=installed_version,
                    size_bytes=None,  # TODO: Calculate actual size in Phase 4
                    installed_at=datetime.utcnow()
                )

                db.add(package_record)

                successful.append({
                    "package": package_name,
                    "version": installed_version,
                    "message": "Successfully installed"
                })

                logger.info(f"Successfully installed {package_name} in environment {environment_id}")

            except Exception as e:
                logger.error(f"Error installing package {package_spec}: {e}")
                failed.append({
                    "package": package_spec,
                    "version": None,
                    "message": str(e)
                })

        # Update environment statistics
        if successful:
            await self.update_environment_stats(environment_id, db)

        await db.commit()

        return successful, failed

    async def uninstall_package(
        self,
        environment_id: uuid.UUID,
        package_name: str,
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> bool:
        """
        Uninstall a package from an environment.

        Args:
            environment_id: Environment UUID
            package_name: Name of package to uninstall
            user_id: User UUID
            db: Database session

        Returns:
            True if successful

        Raises:
            PackageNotFoundError: If package not found
            EnvironmentNotFoundError: If environment not found
        """
        # Get environment
        environment = await self.environment_service.get_environment(
            environment_id, user_id, db
        )

        # Find package record
        result = await db.execute(
            select(EnvironmentPackage).where(
                and_(
                    EnvironmentPackage.environment_id == environment_id,
                    EnvironmentPackage.package_name == package_name
                )
            )
        )
        package = result.scalar_one_or_none()

        if not package:
            raise PackageNotFoundError(
                f"Package {package_name} not found in environment"
            )

        try:
            # Uninstall via Docker (pip uninstall)
            # Note: DockerExecutorService doesn't have uninstall_package yet
            # We'll run a container with pip uninstall command
            from pymd.backend.app.services.docker_executor_service import docker_executor_service

            container = docker_executor_service.client.containers.run(
                image=settings.DOCKER_EXECUTOR_IMAGE,
                command=["pip", "uninstall", "-y", "--user", package_name],
                detach=True,
                remove=False,
                volumes={
                    environment.volume_name: {"bind": "/workspace/.venv", "mode": "rw"}
                },
                network_mode="none"
            )

            result = container.wait(timeout=60)
            exit_code = result.get("StatusCode", 1)

            # Cleanup container
            try:
                container.stop(timeout=1)
                container.remove()
            except Exception as e:
                logger.warning(f"Failed to cleanup uninstall container: {e}")

            if exit_code != 0:
                output = container.logs().decode("utf-8")
                logger.error(f"Failed to uninstall {package_name}: {output}")
                raise PackageServiceError(f"Failed to uninstall package: {output}")

            # Delete package record from database
            await db.delete(package)

            # Update environment statistics
            await self.update_environment_stats(environment_id, db)

            await db.commit()

            logger.info(f"Successfully uninstalled {package_name} from environment {environment_id}")
            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to uninstall package {package_name}: {e}")
            raise PackageServiceError(f"Failed to uninstall package: {e}")

    async def list_packages(
        self,
        environment_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> List[EnvironmentPackage]:
        """
        List all packages installed in an environment.

        Args:
            environment_id: Environment UUID
            user_id: User UUID
            db: Database session

        Returns:
            List of EnvironmentPackage records
        """
        # Verify environment access
        await self.environment_service.get_environment(environment_id, user_id, db)

        # Get packages from database
        result = await db.execute(
            select(EnvironmentPackage).where(
                EnvironmentPackage.environment_id == environment_id
            ).order_by(EnvironmentPackage.installed_at.desc())
        )

        return list(result.scalars().all())

    async def get_package_info(
        self,
        environment_id: uuid.UUID,
        package_name: str,
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> Optional[EnvironmentPackage]:
        """
        Get information about a specific package.

        Args:
            environment_id: Environment UUID
            package_name: Package name
            user_id: User UUID
            db: Database session

        Returns:
            EnvironmentPackage or None
        """
        # Verify environment access
        await self.environment_service.get_environment(environment_id, user_id, db)

        result = await db.execute(
            select(EnvironmentPackage).where(
                and_(
                    EnvironmentPackage.environment_id == environment_id,
                    EnvironmentPackage.package_name == package_name
                )
            )
        )

        return result.scalar_one_or_none()

    async def import_requirements(
        self,
        environment_id: uuid.UUID,
        requirements_txt: str,
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> Tuple[int, int, List[Dict[str, Any]]]:
        """
        Import packages from requirements.txt format.

        Args:
            environment_id: Environment UUID
            requirements_txt: Contents of requirements.txt file
            user_id: User UUID
            db: Database session

        Returns:
            Tuple of (success_count, fail_count, details)
        """
        # Parse requirements.txt
        lines = requirements_txt.strip().split('\n')
        packages = []

        for line in lines:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            # Skip -e and -r flags (editable installs and recursive requirements)
            if line.startswith('-'):
                logger.warning(f"Skipping unsupported requirement: {line}")
                continue
            packages.append(line)

        if not packages:
            raise PackageServiceError("No valid packages found in requirements.txt")

        # Install packages
        successful, failed = await self.install_packages(
            environment_id, packages, user_id, db
        )

        return len(successful), len(failed), {
            "successful": successful,
            "failed": failed
        }

    async def update_environment_stats(
        self,
        environment_id: uuid.UUID,
        db: AsyncSession
    ) -> None:
        """
        Update environment statistics (package count and total size).

        Args:
            environment_id: Environment UUID
            db: Database session
        """
        # Count packages
        count_result = await db.execute(
            select(func.count(EnvironmentPackage.id)).where(
                EnvironmentPackage.environment_id == environment_id
            )
        )
        package_count = count_result.scalar()

        # Sum package sizes
        size_result = await db.execute(
            select(func.sum(EnvironmentPackage.size_bytes)).where(
                EnvironmentPackage.environment_id == environment_id
            )
        )
        total_size = size_result.scalar() or 0

        # Update environment
        env_result = await db.execute(
            select(UserEnvironment).where(UserEnvironment.id == environment_id)
        )
        environment = env_result.scalar_one_or_none()

        if environment:
            environment.package_count = package_count
            environment.total_size_bytes = total_size
            environment.updated_at = datetime.utcnow()
            await db.commit()

    async def sync_packages_from_docker(
        self,
        environment_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> int:
        """
        Sync package list from Docker container to database.
        Useful for recovering from database inconsistencies.

        Args:
            environment_id: Environment UUID
            user_id: User UUID
            db: Database session

        Returns:
            Number of packages synced
        """
        # Get environment
        environment = await self.environment_service.get_environment(
            environment_id, user_id, db
        )

        # Get packages from Docker
        packages = await asyncio.to_thread(
            self.docker_service.list_installed_packages,
            environment.volume_name
        )

        if packages is None:
            raise PackageServiceError("Failed to list packages from Docker")

        # Delete all existing package records
        await db.execute(
            delete(EnvironmentPackage).where(
                EnvironmentPackage.environment_id == environment_id
            )
        )

        # Create new records
        for pkg in packages:
            package_name = pkg.get("name")
            version = pkg.get("version")

            if not package_name:
                continue

            package_record = EnvironmentPackage(
                id=uuid.uuid4(),
                environment_id=environment_id,
                package_name=package_name,
                version=version,
                size_bytes=None,
                installed_at=datetime.utcnow()
            )
            db.add(package_record)

        # Update environment stats
        await self.update_environment_stats(environment_id, db)

        await db.commit()

        logger.info(f"Synced {len(packages)} packages for environment {environment_id}")
        return len(packages)


# Global instance
package_service = PackageService()
