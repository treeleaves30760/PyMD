"""Authentication endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from pymd.backend.app.core.database import get_db
from pymd.backend.app.core.security import get_current_user
from pymd.backend.app.models.user import User
from pymd.backend.app.models.user_settings import UserSettings
from pymd.backend.app.schemas.user import UserResponse
from pymd.backend.app.schemas.auth import UserProfile

router = APIRouter(prefix="/auth")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current authenticated user profile"""
    result = await db.execute(select(User).where(User.auth0_id == current_user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()

    return user


@router.post("/callback", response_model=UserResponse)
async def auth_callback(
    user_profile: UserProfile,
    db: AsyncSession = Depends(get_db),
):
    """Handle Auth0 callback - create or update user"""
    # Check if user exists
    result = await db.execute(select(User).where(User.auth0_id == user_profile.sub))
    user = result.scalar_one_or_none()

    if user:
        # Update existing user
        user.email = user_profile.email
        user.name = user_profile.name
        user.avatar_url = user_profile.picture
        user.last_login_at = datetime.utcnow()
    else:
        # Create new user
        user = User(
            auth0_id=user_profile.sub,
            email=user_profile.email,
            name=user_profile.name,
            avatar_url=user_profile.picture,
            last_login_at=datetime.utcnow(),
        )
        db.add(user)
        await db.flush()

        # Create default user settings
        user_settings = UserSettings(user_id=user.id)
        db.add(user_settings)

    await db.commit()
    await db.refresh(user)

    return user


@router.post("/logout")
async def logout(
    current_user_id: str = Depends(get_current_user),
):
    """Logout current user"""
    # In a stateless JWT system, logout is handled client-side
    # This endpoint can be used for logging or cleanup
    return {"message": "Logged out successfully"}
