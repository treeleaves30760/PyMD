"""Environment Service

This service manages user Python environments, including creation, deletion,
and quota enforcement.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
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

logger = logging.getLogger(__name__)


class EnvironmentServiceError(Exception):
    """Base exception for environment service errors"""
    pass


class QuotaExceededError(EnvironmentServiceError):
    """Raised when user quota is exceeded"""
    pass


class EnvironmentNotFoundError(EnvironmentServiceError):
    """Raised when environment is not found"""
    pass


class EnvironmentService:
    """Service for managing user environments"""

    def __init__(self):
        self.docker_service = docker_executor_service

    def _get_volume_name(self, user_id: uuid.UUID, env_name: str) -> str:
        """
        Generate Docker volume name for an environment.

        Args:
            user_id: User UUID
            env_name: Environment name

        Returns:
            Volume name string
        """
        return f"pymd-env-{user_id}-{env_name}"

    def _get_tier_limits(self, user_role: UserRole) -> Dict[str, int]:
        """
        Get resource limits based on user role.

        Args:
            user_role: User's role

        Returns:
            Dictionary with limits
        """
        if user_role == UserRole.ADMIN or user_role == UserRole.USER:
            # Treat USER as PRO tier for now (adjust based on actual tier system)
            return {
                "max_environments": settings.MAX_ENVIRONMENTS_PRO,
                "max_packages": settings.MAX_PACKAGES_PRO,
                "max_size_bytes": settings.MAX_ENVIRONMENT_SIZE_PRO,
            }
        else:
            return {
                "max_environments": settings.MAX_ENVIRONMENTS_FREE,
                "max_packages": settings.MAX_PACKAGES_FREE,
                "max_size_bytes": settings.MAX_ENVIRONMENT_SIZE_FREE,
            }

    async def check_environment_quota(
        self,
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> bool:
        """
        Check if user can create another environment.

        Args:
            user_id: User UUID
            db: Database session

        Returns:
            True if user can create environment, False otherwise

        Raises:
            QuotaExceededError: If quota exceeded
        """
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise EnvironmentServiceError("User not found")

        # Get limits
        limits = self._get_tier_limits(user.role)

        # Count existing environments
        count_result = await db.execute(
            select(func.count(UserEnvironment.id)).where(
                and_(
                    UserEnvironment.user_id == user_id,
                    UserEnvironment.status != EnvironmentStatus.DELETED
                )
            )
        )
        current_count = count_result.scalar()

        if current_count >= limits["max_environments"]:
            raise QuotaExceededError(
                f"Environment limit reached. Maximum {limits['max_environments']} environments allowed."
            )

        return True

    async def create_environment(
        self,
        user_id: uuid.UUID,
        name: str,
        db: AsyncSession,
        python_version: str = "3.11"
    ) -> UserEnvironment:
        """
        Create a new environment for a user.

        Args:
            user_id: User UUID
            name: Environment name
            python_version: Python version (default: 3.11)
            db: Database session

        Returns:
            Created UserEnvironment

        Raises:
            QuotaExceededError: If user quota exceeded
            EnvironmentServiceError: If creation fails
        """
        try:
            # Check quota
            await self.check_environment_quota(user_id, db)

            # Generate volume name
            volume_name = self._get_volume_name(user_id, name)

            # Create environment record
            environment = UserEnvironment(
                id=uuid.uuid4(),
                user_id=user_id,
                name=name,
                python_version=python_version,
                volume_name=volume_name,
                status=EnvironmentStatus.CREATING,
                total_size_bytes=0,
                package_count=0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            db.add(environment)
            await db.commit()
            await db.refresh(environment)

            # Create Docker volume
            import asyncio
            volume_created = await asyncio.to_thread(self.docker_service.create_volume, volume_name)

            if not volume_created:
                # Rollback database record
                environment.status = EnvironmentStatus.ERROR
                await db.commit()
                raise EnvironmentServiceError(
                    f"Failed to create Docker volume: {volume_name}")

            # Update status to active
            environment.status = EnvironmentStatus.ACTIVE
            environment.last_used_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(environment)

            logger.info(
                f"Created environment {environment.id} for user {user_id}")
            return environment

        except IntegrityError as e:
            await db.rollback()
            if "idx_env_user_name" in str(e):
                raise EnvironmentServiceError(
                    f"Environment '{name}' already exists for this user")
            raise EnvironmentServiceError(f"Database error: {e}")

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create environment: {e}")
            raise EnvironmentServiceError(f"Failed to create environment: {e}")

    async def get_environment(
        self,
        environment_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> Optional[UserEnvironment]:
        """
        Get an environment by ID.

        Args:
            environment_id: Environment UUID
            user_id: User UUID (for access control)
            db: Database session

        Returns:
            UserEnvironment or None

        Raises:
            EnvironmentNotFoundError: If environment not found or access denied
        """
        result = await db.execute(
            select(UserEnvironment).where(
                and_(
                    UserEnvironment.id == environment_id,
                    UserEnvironment.user_id == user_id,
                    UserEnvironment.status != EnvironmentStatus.DELETED
                )
            )
        )
        environment = result.scalar_one_or_none()

        if not environment:
            raise EnvironmentNotFoundError(
                f"Environment {environment_id} not found")

        return environment

    async def list_environments(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
        include_deleted: bool = False
    ) -> List[UserEnvironment]:
        """
        List all environments for a user.

        Args:
            user_id: User UUID
            db: Database session
            include_deleted: Include deleted environments

        Returns:
            List of UserEnvironment
        """
        query = select(UserEnvironment).where(
            UserEnvironment.user_id == user_id)

        if not include_deleted:
            query = query.where(UserEnvironment.status !=
                                EnvironmentStatus.DELETED)

        query = query.order_by(
            UserEnvironment.last_used_at.desc().nulls_first())

        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_environment(
        self,
        environment_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
        **updates
    ) -> UserEnvironment:
        """
        Update environment metadata.

        Args:
            environment_id: Environment UUID
            user_id: User UUID
            db: Database session
            **updates: Fields to update

        Returns:
            Updated UserEnvironment
        """
        environment = await self.get_environment(environment_id, user_id, db)

        # Only allow updating the environment name to avoid inconsistency with Docker volume contents
        allowed_fields = ["name"]
        for field, value in updates.items():
            if field in allowed_fields and hasattr(environment, field):
                setattr(environment, field, value)

        environment.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(environment)

        logger.info(f"Updated environment {environment_id}")
        return environment

    async def delete_environment(
        self,
        environment_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> bool:
        """
        Delete an environment and its Docker volume.

        Args:
            environment_id: Environment UUID
            user_id: User UUID
            db: Database session

        Returns:
            True if successful
        """
        environment = await self.get_environment(environment_id, user_id, db)

        try:
            # Delete Docker volume
            volume_deleted = self.docker_service.delete_volume(
                environment.volume_name)

            if not volume_deleted:
                logger.warning(
                    f"Failed to delete Docker volume: {environment.volume_name}")

            # Mark as deleted in database
            environment.status = EnvironmentStatus.DELETED
            environment.updated_at = datetime.utcnow()
            await db.commit()

            logger.info(f"Deleted environment {environment_id}")
            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete environment: {e}")
            raise EnvironmentServiceError(f"Failed to delete environment: {e}")

    async def reset_environment(
        self,
        environment_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> UserEnvironment:
        """
        Reset an environment (clear packages but keep volume).

        Args:
            environment_id: Environment UUID
            user_id: User UUID
            db: Database session

        Returns:
            Reset UserEnvironment
        """
        environment = await self.get_environment(environment_id, user_id, db)

        try:
            # Delete and recreate Docker volume
            old_volume = environment.volume_name
            self.docker_service.delete_volume(old_volume)

            # Create new volume
            new_volume_created = self.docker_service.create_volume(old_volume)

            if not new_volume_created:
                raise EnvironmentServiceError(
                    "Failed to recreate Docker volume")

            # Clear package records
            # Delete packages
            result = await db.execute(
                select(EnvironmentPackage).where(
                    EnvironmentPackage.environment_id == environment_id
                )
            )
            packages = result.scalars().all()
            for package in packages:
                await db.delete(package)

            # Reset metadata
            environment.total_size_bytes = 0
            environment.package_count = 0
            environment.updated_at = datetime.utcnow()
            environment.last_used_at = datetime.utcnow()

            await db.commit()
            await db.refresh(environment)

            logger.info(f"Reset environment {environment_id}")
            return environment

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to reset environment: {e}")
            raise EnvironmentServiceError(f"Failed to reset environment: {e}")

    async def update_last_used(
        self,
        environment_id: uuid.UUID,
        db: AsyncSession
    ) -> None:
        """
        Update the last_used_at timestamp for an environment.

        Args:
            environment_id: Environment UUID
            db: Database session
        """
        result = await db.execute(
            select(UserEnvironment).where(UserEnvironment.id == environment_id)
        )
        environment = result.scalar_one_or_none()

        if environment:
            environment.last_used_at = datetime.utcnow()
            await db.commit()

    async def get_environment_stats(
        self,
        user_id: uuid.UUID,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get statistics about user's environments.

        Args:
            user_id: User UUID
            db: Database session

        Returns:
            Dictionary with statistics
        """
        # Get user and limits
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise EnvironmentServiceError("User not found")

        limits = self._get_tier_limits(user.role)

        # Count environments
        count_result = await db.execute(
            select(func.count(UserEnvironment.id)).where(
                and_(
                    UserEnvironment.user_id == user_id,
                    UserEnvironment.status != EnvironmentStatus.DELETED
                )
            )
        )
        environment_count = count_result.scalar()

        # Get total size
        size_result = await db.execute(
            select(func.sum(UserEnvironment.total_size_bytes)).where(
                and_(
                    UserEnvironment.user_id == user_id,
                    UserEnvironment.status != EnvironmentStatus.DELETED
                )
            )
        )
        total_size = size_result.scalar() or 0

        # Get total packages
        package_result = await db.execute(
            select(func.sum(UserEnvironment.package_count)).where(
                and_(
                    UserEnvironment.user_id == user_id,
                    UserEnvironment.status != EnvironmentStatus.DELETED
                )
            )
        )
        total_packages = package_result.scalar() or 0

        return {
            "environment_count": environment_count,
            "environment_limit": limits["max_environments"],
            "total_size_bytes": total_size,
            "size_limit_bytes": limits["max_size_bytes"],
            "total_packages": total_packages,
            "package_limit": limits["max_packages"],
            "can_create_environment": environment_count < limits["max_environments"],
        }

    async def get_default_environment(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
        create_if_missing: bool = True
    ) -> Optional[UserEnvironment]:
        """
        Get or create the default environment for a user.

        Args:
            user_id: User UUID
            db: Database session
            create_if_missing: Create default environment if it doesn't exist

        Returns:
            UserEnvironment or None
        """
        # Try to find default environment
        result = await db.execute(
            select(UserEnvironment).where(
                and_(
                    UserEnvironment.user_id == user_id,
                    UserEnvironment.name == "default",
                    UserEnvironment.status == EnvironmentStatus.ACTIVE
                )
            )
        )
        environment = result.scalar_one_or_none()

        if not environment and create_if_missing:
            try:
                environment = await self.create_environment(
                    user_id=user_id,
                    name="default",
                    python_version="3.11",
                    db=db
                )
            except Exception as e:
                logger.error(f"Failed to create default environment: {e}")
                return None

        return environment


# Global instance
environment_service = EnvironmentService()
