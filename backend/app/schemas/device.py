"""
Device Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel
from enum import Enum


class DeviceStatus(str, Enum):
    """Device status enum"""
    ACTIVE = "active"
    BLOCKED = "blocked"


class DeviceBase(BaseModel):
    """Base device schema"""
    device_name: Optional[str] = None


class DeviceUpdate(BaseModel):
    """Schema for device update"""
    device_name: Optional[str] = None
    status: Optional[DeviceStatus] = None


class DeviceResponse(BaseModel):
    """Schema for device response"""
    id: int
    device_id: str
    device_name: Optional[str] = None
    os: Optional[str] = None
    ip_address: Optional[str] = None
    first_seen: datetime
    last_seen: datetime
    status: str
    validations_count: int = 0
    
    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """Schema for device list response"""
    license_id: int
    max_devices: int
    current_count: int
    devices: List[DeviceResponse]


class ActivityLogResponse(BaseModel):
    """Schema for activity log response"""
    id: int
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    action: str
    timestamp: datetime
    ip_address: Optional[str] = None
    metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True
