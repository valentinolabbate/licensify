"""
Authentication Pydantic Schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class AccessTokenResponse(BaseModel):
    """Access token only response"""
    access_token: str
    expires_in: int


class EmailVerificationRequest(BaseModel):
    """Email verification request schema"""
    token: str


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str


class RegisterResponse(BaseModel):
    """Registration response schema"""
    id: int
    email: str
    message: str


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
