"""User management endpoints"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from pymd.backend.app.core.database import get_db
from pymd.backend.app.core.security import get_current_user
from pymd.backend.app.models.user import User
from pymd.backend.app.models.user_settings import UserSettings
from pymd.backend.app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile"""
    # Get current user
    result = await db.execute(select(User).where(User.auth0_id == current_user_id))
    current_user = result.scalar_one_or_none()

    if not current_user or str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    # Update user
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.get("/{user_id}/settings")
async def get_user_settings(
    user_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user settings"""
    # Verify authorization
    result = await db.execute(select(User).where(User.auth0_id == current_user_id))
    current_user = result.scalar_one_or_none()

    if not current_user or str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these settings",
        )

    # Get settings
    result = await db.execute(select(UserSettings).where(UserSettings.user_id == user_id))
    settings = result.scalar_one_or_none()

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not found",
        )

    return {
        "theme": settings.theme,
        "language": settings.language,
        "editor_settings": settings.editor_settings,
        "render_settings": settings.render_settings,
    }


@router.patch("/{user_id}/settings")
async def update_user_settings(
    user_id: UUID,
    settings_update: dict,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user settings"""
    # Verify authorization
    result = await db.execute(select(User).where(User.auth0_id == current_user_id))
    current_user = result.scalar_one_or_none()

    if not current_user or str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update these settings",
        )

    # Get settings
    result = await db.execute(select(UserSettings).where(UserSettings.user_id == user_id))
    settings = result.scalar_one_or_none()

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not found",
        )

    # Update settings
    if "theme" in settings_update:
        settings.theme = settings_update["theme"]
    if "language" in settings_update:
        settings.language = settings_update["language"]
    if "editor_settings" in settings_update:
        settings.editor_settings = settings_update["editor_settings"]
    if "render_settings" in settings_update:
        settings.render_settings = settings_update["render_settings"]

    await db.commit()

    return {
        "theme": settings.theme,
        "language": settings.language,
        "editor_settings": settings.editor_settings,
        "render_settings": settings.render_settings,
    }
