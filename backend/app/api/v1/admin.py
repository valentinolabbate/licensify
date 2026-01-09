"""
Admin Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User
from app.models.license import License
from app.models.device import Device
from app.models.device_activity import DeviceActivity
from app.schemas.user import UserResponse
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"])


class SystemStats(BaseModel):
    """System statistics response"""
    total_users: int
    verified_users: int
    total_licenses: int
    active_licenses: int
    total_devices: int
    active_devices: int
    total_validations: int


class UserListResponse(BaseModel):
    """User list response"""
    users: List[UserResponse]
    total: int


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get system statistics (Admin only)"""
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar()
    
    # Verified users
    result = await db.execute(select(func.count(User.id)).where(User.is_verified == True))
    verified_users = result.scalar()
    
    # Total licenses
    result = await db.execute(select(func.count(License.id)))
    total_licenses = result.scalar()
    
    # Active licenses
    result = await db.execute(select(func.count(License.id)).where(License.status == "active"))
    active_licenses = result.scalar()
    
    # Total devices
    result = await db.execute(select(func.count(Device.id)))
    total_devices = result.scalar()
    
    # Active devices
    result = await db.execute(select(func.count(Device.id)).where(Device.status == "active"))
    active_devices = result.scalar()
    
    # Total validations
    result = await db.execute(
        select(func.count(DeviceActivity.id)).where(DeviceActivity.action == "validated")
    )
    total_validations = result.scalar()
    
    return SystemStats(
        total_users=total_users,
        verified_users=verified_users,
        total_licenses=total_licenses,
        active_licenses=active_licenses,
        total_devices=total_devices,
        active_devices=active_devices,
        total_validations=total_validations
    )


@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List all users (Admin only)"""
    result = await db.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    
    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar()
    
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total
    )


@router.put("/users/{user_id}/toggle-admin", response_model=UserResponse)
async def toggle_user_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Toggle admin status for a user (Admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin status"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_admin = not user.is_admin
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}/toggle-active", response_model=UserResponse)
async def toggle_user_active(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Toggle active status for a user (Admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = not user.is_active
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}/approve", response_model=UserResponse)
async def approve_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Approve a user account (Admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_approved = True
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}/reject", response_model=UserResponse)
async def reject_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Reject/Revoke user approval (Admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reject your own account"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_approved = False
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)
