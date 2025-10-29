"""Environment API endpoints"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pymd.backend.app.core.database import get_db
from pymd.backend.app.core.security import get_current_user
from pymd.backend.app.models.user import User
from pymd.backend.app.schemas.environment import (
    EnvironmentCreate,
    EnvironmentUpdate,
    EnvironmentResponse,
    EnvironmentListResponse,
    EnvironmentStatsResponse,
)
from pymd.backend.app.services.environment_service import (
    EnvironmentService,
    QuotaExceededError,
    EnvironmentServiceError,
)

router = APIRouter(prefix="/environments", tags=["environments"])


async def get_user_from_auth0_id(auth0_id: str, db: AsyncSession) -> User:
    """Helper to get User object from auth0_id"""
    result = await db.execute(select(User).where(User.auth0_id == auth0_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post(
    "",
    response_model=EnvironmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new environment",
)
async def create_environment(
    environment_data: EnvironmentCreate,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new Python environment for the current user.

    - **name**: Environment name (required, 1-100 characters, alphanumeric + hyphens/underscores)
    - **python_version**: Python version to use (default: "3.11")

    The environment will be isolated in a Docker container with its own volume
    for package storage. Each user has a quota based on their tier:
    - FREE: 3 environments
    - PRO: 10 environments

    Returns a 409 error if the quota is exceeded or if an environment with the
    same name already exists.
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    try:
        environment_service = EnvironmentService()
        environment = await environment_service.create_environment(
            user_id=user.id,
            name=environment_data.name,
            db=db,
            python_version=environment_data.python_version,
        )
        return environment

    except QuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except EnvironmentServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "",
    response_model=EnvironmentListResponse,
    summary="List user's environments",
)
async def list_environments(
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all environments for the current user.

    Returns all environments owned by the user, including information about:
    - Environment status (active, creating, error, deleted)
    - Number of installed packages
    - Total storage used
    - Last time the environment was used
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    environment_service = EnvironmentService()
    environments = await environment_service.list_environments(
        user_id=user.id,
        db=db,
    )

    return EnvironmentListResponse(
        environments=environments,
        total=len(environments),
    )


@router.get(
    "/stats",
    response_model=EnvironmentStatsResponse,
    summary="Get environment usage statistics",
)
async def get_environment_stats(
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get statistics about the user's environment usage.

    Returns:
    - Total number of environments
    - Total storage used across all environments
    - Total number of packages installed
    - Quota information based on user tier
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    environment_service = EnvironmentService()
    stats = await environment_service.get_environment_stats(
        user_id=user.id,
        db=db,
    )

    return stats


@router.get(
    "/{environment_id}",
    response_model=EnvironmentResponse,
    summary="Get an environment",
)
async def get_environment(
    environment_id: UUID,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific environment by ID.

    Only the environment owner can access it.
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    environment_service = EnvironmentService()
    environment = await environment_service.get_environment(
        environment_id=environment_id,
        user_id=user.id,
        db=db,
    )

    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment not found",
        )

    return environment


@router.patch(
    "/{environment_id}",
    response_model=EnvironmentResponse,
    summary="Update an environment",
)
async def update_environment(
    environment_id: UUID,
    environment_data: EnvironmentUpdate,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an environment.

    Only the environment owner can update it.
    Currently only the name can be updated.

    - **name**: New environment name (optional)
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    environment_service = EnvironmentService()

    try:
        environment = await environment_service.update_environment(
            environment_id=environment_id,
            user_id=user.id,
            name=environment_data.name,
            db=db,
        )

        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )

        return environment

    except EnvironmentServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{environment_id}/reset",
    response_model=EnvironmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset an environment",
)
async def reset_environment(
    environment_id: UUID,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Reset an environment by removing all installed packages.

    This will:
    - Delete the Docker volume containing installed packages
    - Create a new empty volume
    - Reset package count and size to 0
    - Keep the environment configuration (name, python_version)

    Only the environment owner can reset it.
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    environment_service = EnvironmentService()

    try:
        environment = await environment_service.reset_environment(
            environment_id=environment_id,
            user_id=user.id,
            db=db,
        )

        if not environment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found",
            )

        return environment

    except EnvironmentServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete(
    "/{environment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an environment",
)
async def delete_environment(
    environment_id: UUID,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an environment.

    This will:
    - Mark the environment as deleted in the database
    - Delete the Docker volume containing installed packages
    - Remove all package records

    The default environment cannot be deleted.
    Only the environment owner can delete it.
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    environment_service = EnvironmentService()

    try:
        success = await environment_service.delete_environment(
            environment_id=environment_id,
            user_id=user.id,
            db=db,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found or cannot be deleted",
            )

        return None

    except EnvironmentServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
