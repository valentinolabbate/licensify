"""
Device Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.license_service import LicenseService
from app.services.device_service import DeviceService
from app.api.deps import get_current_verified_user
from app.models.user import User
from app.schemas.device import (
    DeviceUpdate,
    DeviceResponse,
    DeviceListResponse,
)

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("/license/{license_id}", response_model=DeviceListResponse)
async def get_license_devices(
    license_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Get all devices for a license"""
    license_service = LicenseService(db)
    device_service = DeviceService(db)
    
    # Verify license belongs to user
    license = await license_service.get_by_id(license_id, current_user.id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    devices = await device_service.get_license_devices(license_id)
    
    device_responses = []
    for device in devices:
        validation_count = await device_service.count_device_validations(device.id)
        device_responses.append(DeviceResponse(
            id=device.id,
            device_id=device.device_id,
            device_name=device.device_name,
            os=device.os,
            ip_address=device.ip_address,
            first_seen=device.first_seen,
            last_seen=device.last_seen,
            status=device.status,
            validations_count=validation_count
        ))
    
    return DeviceListResponse(
        license_id=license_id,
        max_devices=license.max_devices,
        current_count=len([d for d in devices if d.status == "active"]),
        devices=device_responses
    )


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: int,
    device_data: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Update a device"""
    license_service = LicenseService(db)
    device_service = DeviceService(db)
    
    device = await device_service.get_by_id(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Verify device's license belongs to user
    license = await license_service.get_by_id(device.license_id, current_user.id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    device = await device_service.update(device, device_data)
    validation_count = await device_service.count_device_validations(device.id)
    
    return DeviceResponse(
        id=device.id,
        device_id=device.device_id,
        device_name=device.device_name,
        os=device.os,
        ip_address=device.ip_address,
        first_seen=device.first_seen,
        last_seen=device.last_seen,
        status=device.status,
        validations_count=validation_count
    )


@router.post("/{device_id}/block", response_model=DeviceResponse)
async def block_device(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Block a device"""
    license_service = LicenseService(db)
    device_service = DeviceService(db)
    
    device = await device_service.get_by_id(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Verify device's license belongs to user
    license = await license_service.get_by_id(device.license_id, current_user.id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    device = await device_service.block(device)
    validation_count = await device_service.count_device_validations(device.id)
    
    return DeviceResponse(
        id=device.id,
        device_id=device.device_id,
        device_name=device.device_name,
        os=device.os,
        ip_address=device.ip_address,
        first_seen=device.first_seen,
        last_seen=device.last_seen,
        status=device.status,
        validations_count=validation_count
    )


@router.post("/{device_id}/unblock", response_model=DeviceResponse)
async def unblock_device(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Unblock a device"""
    license_service = LicenseService(db)
    device_service = DeviceService(db)
    
    device = await device_service.get_by_id(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Verify device's license belongs to user
    license = await license_service.get_by_id(device.license_id, current_user.id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    device = await device_service.unblock(device)
    validation_count = await device_service.count_device_validations(device.id)
    
    return DeviceResponse(
        id=device.id,
        device_id=device.device_id,
        device_name=device.device_name,
        os=device.os,
        ip_address=device.ip_address,
        first_seen=device.first_seen,
        last_seen=device.last_seen,
        status=device.status,
        validations_count=validation_count
    )


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Delete a device"""
    license_service = LicenseService(db)
    device_service = DeviceService(db)
    
    device = await device_service.get_by_id(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Verify device's license belongs to user
    license = await license_service.get_by_id(device.license_id, current_user.id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    await device_service.delete(device)
    return None
