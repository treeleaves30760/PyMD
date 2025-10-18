"""User schemas"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from pymd.backend.app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""

    auth0_id: str = Field(..., min_length=1, max_length=255)


class UserUpdate(BaseModel):
    """User update schema"""

    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""

    id: UUID
    role: UserRole
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
