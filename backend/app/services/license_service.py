"""
License Service - Business logic for license operations
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.license import License
from app.models.device import Device
from app.models.device_activity import DeviceActivity
from app.schemas.license import LicenseCreate, LicenseUpdate, LicenseType
from app.core.config import settings


class LicenseService:
    """Service class for license operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @staticmethod
    def generate_license_key(length: int = 32) -> str:
        """Generate cryptographically secure license key"""
        # Use alphanumeric characters (Base62)
        alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    async def get_by_id(self, license_id: int, user_id: Optional[int] = None) -> Optional[License]:
        """Get license by ID, optionally filtered by user"""
        query = select(License).where(License.id == license_id)
        if user_id:
            query = query.where(License.user_id == user_id)
        query = query.options(selectinload(License.devices))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_id_admin(self, license_id: int) -> Optional[License]:
        """Get license by ID (admin - no user filter)"""
        result = await self.db.execute(
            select(License)
            .where(License.id == license_id)
            .options(selectinload(License.devices))
        )
        return result.scalar_one_or_none()
    
    async def get_by_key(self, key: str) -> Optional[License]:
        """Get license by license key"""
        from app.models.product import Product
        result = await self.db.execute(
            select(License)
            .where(License.key == key)
            .options(
                selectinload(License.devices),
                selectinload(License.product)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_licenses(self, user_id: int, skip: int = 0, limit: int = 100) -> List[License]:
        """Get all licenses for a user"""
        result = await self.db.execute(
            select(License)
            .where(License.user_id == user_id)
            .options(selectinload(License.devices))
            .offset(skip)
            .limit(limit)
            .order_by(License.created_at.desc())
        )
        return result.scalars().all()
    
    async def count_user_licenses(self, user_id: int) -> int:
        """Count total licenses for a user"""
        result = await self.db.execute(
            select(func.count(License.id)).where(License.user_id == user_id)
        )
        return result.scalar()
    
    async def create(self, user_id: int, license_data: LicenseCreate) -> License:
        """Create a new license"""
        # Generate unique license key
        key = self.generate_license_key(settings.LICENSE_KEY_LENGTH)
        
        # Calculate expiry date based on license type
        expires_at = None
        if license_data.license_type == LicenseType.TRIAL:
            days = license_data.trial_duration_days or 14
            expires_at = datetime.utcnow() + timedelta(days=days)
        elif license_data.license_type in [LicenseType.LIMITED, LicenseType.STANDARD, LicenseType.PROFESSIONAL, LicenseType.ENTERPRISE]:
            # Nutze duration_days wenn vorhanden, sonst expires_at
            if license_data.duration_days:
                expires_at = datetime.utcnow() + timedelta(days=license_data.duration_days)
            else:
                expires_at = license_data.expires_at
        
        license = License(
            user_id=user_id,
            product_id=license_data.product_id,
            key=key,
            name=license_data.name,
            license_type=license_data.license_type.value,
            max_devices=license_data.max_devices,
            expires_at=expires_at,
            trial_duration_days=license_data.trial_duration_days,
            license_metadata=license_data.metadata,
            features=license_data.features or [],
            price=license_data.price,
            note=license_data.note,
        )
        self.db.add(license)
        await self.db.commit()
        await self.db.refresh(license)
        return license
    
    async def update(self, license: License, license_data: LicenseUpdate) -> License:
        """Update a license"""
        update_data = license_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value:
                setattr(license, field, value.value)
            elif field == "metadata":
                setattr(license, "license_metadata", value)
            else:
                setattr(license, field, value)
        license.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(license)
        return license
    
    async def delete(self, license: License) -> None:
        """Delete a license"""
        await self.db.delete(license)
        await self.db.commit()
    
    async def revoke(self, license: License) -> License:
        """Revoke a license"""
        license.status = "revoked"
        license.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(license)
        return license
    
    async def validate_license(
        self, 
        key: str, 
        device_id: str, 
        device_name: Optional[str] = None,
        os_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        app_version: Optional[str] = None
    ) -> dict:
        """
        Validate a license and register/update device
        Returns validation result dict
        """
        # Get license
        license = await self.get_by_key(key)
        
        if not license:
            return {"valid": False, "reason": "invalid_key"}
        
        # Check status
        if license.status == "revoked":
            return {"valid": False, "reason": "license_revoked"}
        
        # Check expiry
        if license.is_expired:
            return {
                "valid": False, 
                "reason": "license_expired",
                "expires_at": license.expires_at.isoformat() if license.expires_at else None
            }
        
        # Get or create device
        device = await self._get_or_create_device(
            license, device_id, device_name, os_info, ip_address
        )
        
        # Check if device is blocked
        if device.status == "blocked":
            return {"valid": False, "reason": "device_blocked"}
        
        # Check device limit
        active_devices = [d for d in license.devices if d.status == "active"]
        if license.max_devices > 0 and len(active_devices) > license.max_devices:
            # Device is over limit and not in list
            if device not in active_devices[:license.max_devices]:
                return {
                    "valid": False, 
                    "reason": "device_limit_exceeded",
                    "max_devices": license.max_devices,
                    "current_devices": len(active_devices)
                }
        
        # Log activity
        await self._log_device_activity(device, "validated", ip_address, app_version)
        
        # Calculate cache expiry
        cache_until = datetime.utcnow() + timedelta(days=settings.DEFAULT_CACHE_DAYS)
        if license.expires_at:
            cache_until = min(cache_until, license.expires_at)
        
        # Build product info if available
        product_info = None
        if license.product:
            product_info = {
                "id": license.product.id,
                "name": license.product.name,
                "slug": license.product.slug,
                "version": license.product.version
            }
        
        # Get features (from license, or from product defaults)
        features = license.features or []
        if not features and license.product and license.product.available_features:
            features = license.product.available_features
        
        return {
            "valid": True,
            "license_type": license.license_type,
            "expires_at": license.expires_at.isoformat() if license.expires_at else None,
            "days_remaining": license.days_remaining,
            "max_devices": license.max_devices,
            "current_devices": len(active_devices),
            "cache_until": cache_until.isoformat(),
            "features": features,
            "product": product_info
        }
    
    async def _get_or_create_device(
        self,
        license: License,
        device_id: str,
        device_name: Optional[str],
        os_info: Optional[str],
        ip_address: Optional[str]
    ) -> Device:
        """Get existing device or create new one"""
        # Look for existing device
        for device in license.devices:
            if device.device_id == device_id:
                # Update device info
                device.last_seen = datetime.utcnow()
                if device_name:
                    device.device_name = device_name
                if os_info:
                    device.os = os_info
                if ip_address:
                    device.ip_address = ip_address
                await self.db.commit()
                return device
        
        # Create new device
        device = Device(
            license_id=license.id,
            device_id=device_id,
            device_name=device_name,
            os=os_info,
            ip_address=ip_address,
        )
        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        
        # Log registration
        await self._log_device_activity(device, "registered", ip_address)
        
        return device
    
    async def _log_device_activity(
        self, 
        device: Device, 
        action: str, 
        ip_address: Optional[str] = None,
        app_version: Optional[str] = None
    ) -> None:
        """Log device activity"""
        metadata = {}
        if app_version:
            metadata["app_version"] = app_version
        
        activity = DeviceActivity(
            device_id=device.id,
            action=action,
            ip_address=ip_address,
            metadata=metadata if metadata else None
        )
        self.db.add(activity)
        await self.db.commit()
