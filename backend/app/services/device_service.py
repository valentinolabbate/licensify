"""
Device Service - Business logic for device operations
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.device import Device
from app.models.device_activity import DeviceActivity
from app.schemas.device import DeviceUpdate


class DeviceService:
    """Service class for device operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, device_id: int) -> Optional[Device]:
        """Get device by ID"""
        result = await self.db.execute(
            select(Device)
            .where(Device.id == device_id)
            .options(selectinload(Device.license))
        )
        return result.scalar_one_or_none()
    
    async def get_license_devices(self, license_id: int) -> List[Device]:
        """Get all devices for a license"""
        result = await self.db.execute(
            select(Device)
            .where(Device.license_id == license_id)
            .options(selectinload(Device.activities))
            .order_by(Device.last_seen.desc())
        )
        return result.scalars().all()
    
    async def update(self, device: Device, device_data: DeviceUpdate) -> Device:
        """Update a device"""
        update_data = device_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value:
                setattr(device, field, value.value)
            else:
                setattr(device, field, value)
        await self.db.commit()
        await self.db.refresh(device)
        return device
    
    async def block(self, device: Device) -> Device:
        """Block a device"""
        device.status = "blocked"
        device.is_active = False
        await self.db.commit()
        await self.db.refresh(device)
        return device
    
    async def unblock(self, device: Device) -> Device:
        """Unblock a device"""
        device.status = "active"
        device.is_active = True
        await self.db.commit()
        await self.db.refresh(device)
        return device
    
    async def delete(self, device: Device) -> None:
        """Delete a device"""
        await self.db.delete(device)
        await self.db.commit()
    
    async def get_device_activities(
        self, 
        device_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[DeviceActivity]:
        """Get activity log for a device"""
        result = await self.db.execute(
            select(DeviceActivity)
            .where(DeviceActivity.device_id == device_id)
            .order_by(DeviceActivity.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_license_activities(
        self, 
        license_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[dict]:
        """Get activity log for all devices of a license"""
        # Get all devices for the license
        devices = await self.get_license_devices(license_id)
        device_ids = [d.id for d in devices]
        device_map = {d.id: d for d in devices}
        
        if not device_ids:
            return []
        
        result = await self.db.execute(
            select(DeviceActivity)
            .where(DeviceActivity.device_id.in_(device_ids))
            .order_by(DeviceActivity.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        activities = result.scalars().all()
        
        # Enrich with device info
        enriched = []
        for activity in activities:
            device = device_map.get(activity.device_id)
            enriched.append({
                "id": activity.id,
                "device_id": device.device_id if device else None,
                "device_name": device.device_name if device else None,
                "action": activity.action,
                "timestamp": activity.timestamp,
                "ip_address": activity.ip_address,
                "metadata": activity.activity_metadata
            })
        
        return enriched
    
    async def count_device_validations(self, device_id: int) -> int:
        """Count total validations for a device"""
        result = await self.db.execute(
            select(func.count(DeviceActivity.id))
            .where(DeviceActivity.device_id == device_id)
            .where(DeviceActivity.action == "validated")
        )
        return result.scalar()
