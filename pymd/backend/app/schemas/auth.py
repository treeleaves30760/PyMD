"""Authentication schemas"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfile(BaseModel):
    """User profile from Auth0"""

    sub: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: bool = False


class AuthCallbackRequest(BaseModel):
    """Auth callback request"""

    code: str
    state: Optional[str] = None
