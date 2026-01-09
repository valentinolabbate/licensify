"""
User Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserUpdate(BaseModel):
    """Schema for user update"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_verified: bool
    is_admin: bool
    is_active: bool
    is_approved: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PasswordChangeRequest(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserInDB(UserResponse):
    """Schema for user in database (includes password hash)"""
    password_hash: str
