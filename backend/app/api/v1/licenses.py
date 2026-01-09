"""
License Routes
"""
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.license_service import LicenseService
from app.services.device_service import DeviceService
from app.services.revenue_service import RevenueService
from app.api.deps import get_current_verified_user
from app.core.limiter import limiter
from app.models.user import User
from app.schemas.license import (
    LicenseCreate,
    LicenseUpdate,
    LicenseResponse,
    LicenseListResponse,
    LicenseValidationRequest,
    LicenseValidationResponse,
    LicenseDetailResponse,
    LicenseFeatureToggle,
    LicenseFeaturesBulkUpdate,
)
from app.schemas.device import DeviceResponse, ActivityLogResponse

router = APIRouter(prefix="/licenses", tags=["Licenses"])


@router.post("/validate", response_model=LicenseValidationResponse)
@limiter.limit("10/minute")
async def validate_license(
    request: Request,
    validation_data: LicenseValidationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate a license key (PUBLIC - no authentication required).
    
    This endpoint is called by the Python client library to validate licenses.
    It also registers/updates device information.
    """
    license_service = LicenseService(db)
    
    # Get client IP
    client_ip = request.client.host if request.client else None
    
    result = await license_service.validate_license(
        key=validation_data.license_key,
        device_id=validation_data.device_id,
        device_name=validation_data.device_name,
        os_info=validation_data.os_info,
        ip_address=client_ip,
        app_version=validation_data.app_version
    )
    
    return LicenseValidationResponse(**result)


@router.post("", response_model=LicenseResponse, status_code=status.HTTP_201_CREATED)
async def create_license(
    license_data: LicenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """
    Create a new license.
    
    - **license_type**: 'unlimited', 'trial', or 'limited'
    - **max_devices**: Maximum number of devices (0 = unlimited)
    - **name**: Optional friendly name for the license
    - **trial_duration_days**: Required for trial licenses
    - **expires_at**: Required for limited licenses
    """
    license_service = LicenseService(db)
    
    # Validation
    if license_data.license_type.value == "trial" and not license_data.trial_duration_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="trial_duration_days is required for trial licenses"
        )
    
    # Zeitlich begrenzte Lizenzen benötigen duration_days oder expires_at
    time_limited_types = ["limited", "standard", "professional", "enterprise"]
    if license_data.license_type.value in time_limited_types:
        if not license_data.duration_days and not license_data.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="duration_days or expires_at is required for time-limited licenses"
            )
    
    license = await license_service.create(current_user.id, license_data)
    
    # Reload with devices relationship
    license = await license_service.get_by_id(license.id)
    
    # Create initial revenue if provided
    if license_data.initial_revenue:
        revenue_service = RevenueService(db)
        await revenue_service.create(
            license_id=license.id,
            amount=Decimal(str(license_data.initial_revenue.amount)),
            currency=license_data.initial_revenue.currency,
            payment_type="initial",
            notes=license_data.initial_revenue.notes,
            period_start=license.created_at,
            period_end=license.expires_at,
            created_by_id=current_user.id
        )
    
    return LicenseResponse(
        id=license.id,
        key=license.key,
        name=license.name,
        license_type=license.license_type,
        status=license.status,
        max_devices=license.max_devices,
        expires_at=license.expires_at,
        days_remaining=license.days_remaining,
        current_devices=len([d for d in license.devices if d.status == "active"]),
        trial_duration_days=license.trial_duration_days,
        metadata=license.license_metadata,
        created_at=license.created_at,
        updated_at=license.updated_at,
    )


@router.get("", response_model=LicenseListResponse)
async def list_licenses(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Get all licenses for the current user"""
    license_service = LicenseService(db)
    
    licenses = await license_service.get_user_licenses(current_user.id, skip, limit)
    total = await license_service.count_user_licenses(current_user.id)
    
    return LicenseListResponse(
        licenses=[
            LicenseResponse(
                id=lic.id,
                key=lic.key,
                name=lic.name,
                license_type=lic.license_type,
                status=lic.status,
                max_devices=lic.max_devices,
                expires_at=lic.expires_at,
                days_remaining=lic.days_remaining,
                current_devices=len([d for d in lic.devices if d.status == "active"]),
                trial_duration_days=lic.trial_duration_days,
                metadata=lic.license_metadata,
                created_at=lic.created_at,
                updated_at=lic.updated_at,
            )
            for lic in licenses
        ],
        total=total
    )


@router.get("/{license_id}", response_model=LicenseDetailResponse)
async def get_license(
    license_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Get license details with devices and activity"""
    license_service = LicenseService(db)
    device_service = DeviceService(db)
    
    license = await license_service.get_by_id(license_id, current_user.id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    # Get device info with validation counts
    devices = []
    for device in license.devices:
        validation_count = await device_service.count_device_validations(device.id)
        devices.append(DeviceResponse(
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
    
    # Get activity log
    activities = await device_service.get_license_activities(license_id, limit=50)
    
    return LicenseDetailResponse(
        id=license.id,
        key=license.key,
        name=license.name,
        license_type=license.license_type,
        status=license.status,
        max_devices=license.max_devices,
        expires_at=license.expires_at,
        days_remaining=license.days_remaining,
        current_devices=len([d for d in license.devices if d.status == "active"]),
        trial_duration_days=license.trial_duration_days,
        metadata=license.license_metadata,
        created_at=license.created_at,
        updated_at=license.updated_at,
        devices=devices,
        activity=[ActivityLogResponse(**a) for a in activities]
    )


@router.put("/{license_id}", response_model=LicenseResponse)
async def update_license(
    license_id: int,
    license_data: LicenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Update a license"""
    license_service = LicenseService(db)
    
    license = await license_service.get_by_id(license_id, current_user.id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    license = await license_service.update(license, license_data)
    
    # Reload to get updated devices relationship
    license = await license_service.get_by_id(license.id)
    
    return LicenseResponse(
        id=license.id,
        key=license.key,
        name=license.name,
        license_type=license.license_type,
        status=license.status,
        max_devices=license.max_devices,
        expires_at=license.expires_at,
        days_remaining=license.days_remaining,
        current_devices=len([d for d in license.devices if d.status == "active"]),
        trial_duration_days=license.trial_duration_days,
        metadata=license.license_metadata,
        created_at=license.created_at,
        updated_at=license.updated_at,
    )


@router.delete("/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_license(
    license_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Delete a license"""
    license_service = LicenseService(db)
    
    license = await license_service.get_by_id(license_id, current_user.id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    await license_service.delete(license)
    return None


@router.post("/{license_id}/revoke", response_model=LicenseResponse)
async def revoke_license(
    license_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """Revoke a license"""
    license_service = LicenseService(db)
    
    license = await license_service.get_by_id(license_id, current_user.id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    license = await license_service.revoke(license)
    
    # Reload to get updated devices relationship
    license = await license_service.get_by_id(license.id)
    
    return LicenseResponse(
        id=license.id,
        key=license.key,
        name=license.name,
        license_type=license.license_type,
        status=license.status,
        max_devices=license.max_devices,
        expires_at=license.expires_at,
        days_remaining=license.days_remaining,
        current_devices=len([d for d in license.devices if d.status == "active"]),
        trial_duration_days=license.trial_duration_days,
        metadata=license.license_metadata,
        created_at=license.created_at,
        updated_at=license.updated_at,
    )


# ==================== Feature Management ====================

@router.patch("/{license_id}/features", response_model=LicenseResponse)
async def toggle_license_feature(
    license_id: int,
    toggle_data: LicenseFeatureToggle,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """
    Toggle a single feature on a license.
    Enables or disables the specified feature.
    """
    license_service = LicenseService(db)
    
    license = await license_service.get_by_id(license_id, current_user.id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    # Get current features
    current_features = license.features or []
    feature_slug = toggle_data.feature_slug.lower()
    
    # Check if feature is available in product (if product is assigned)
    if license.product:
        available_slugs = []
        for f in (license.product.available_features or []):
            if isinstance(f, dict):
                available_slugs.append(f.get("slug", "").lower())
            else:
                available_slugs.append(str(f).lower())
        
        if feature_slug not in available_slugs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Feature '{toggle_data.feature_slug}' is not available for this product"
            )
    
    if toggle_data.enabled:
        # Add feature if not present
        if feature_slug not in [f.lower() for f in current_features]:
            current_features.append(toggle_data.feature_slug)
    else:
        # Remove feature if present
        current_features = [f for f in current_features if f.lower() != feature_slug]
    
    license.features = current_features
    await db.commit()
    await db.refresh(license)
    
    return LicenseResponse(
        id=license.id,
        key=license.key,
        name=license.name,
        license_type=license.license_type,
        status=license.status,
        product_id=license.product_id,
        max_devices=license.max_devices,
        features=license.features,
        expires_at=license.expires_at,
        days_remaining=license.days_remaining,
        current_devices=len([d for d in license.devices if d.status == "active"]),
        trial_duration_days=license.trial_duration_days,
        metadata=license.license_metadata,
        price=float(license.price) if license.price else None,
        note=license.note,
        created_at=license.created_at,
        updated_at=license.updated_at,
    )


@router.put("/{license_id}/features", response_model=LicenseResponse)
async def update_license_features(
    license_id: int,
    features_data: LicenseFeaturesBulkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """
    Bulk update all features on a license.
    Replaces all current features with the provided list.
    """
    license_service = LicenseService(db)
    
    license = await license_service.get_by_id(license_id, current_user.id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    # Validate features against product if assigned
    if license.product:
        available_slugs = []
        for f in (license.product.available_features or []):
            if isinstance(f, dict):
                available_slugs.append(f.get("slug", "").lower())
            else:
                available_slugs.append(str(f).lower())
        
        for feature in features_data.features:
            if feature.lower() not in available_slugs:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Feature '{feature}' is not available for this product"
                )
    
    license.features = features_data.features
    await db.commit()
    await db.refresh(license)
    
    return LicenseResponse(
        id=license.id,
        key=license.key,
        name=license.name,
        license_type=license.license_type,
        status=license.status,
        product_id=license.product_id,
        max_devices=license.max_devices,
        features=license.features,
        expires_at=license.expires_at,
        days_remaining=license.days_remaining,
        current_devices=len([d for d in license.devices if d.status == "active"]),
        trial_duration_days=license.trial_duration_days,
        metadata=license.license_metadata,
        price=float(license.price) if license.price else None,
        note=license.note,
        created_at=license.created_at,
        updated_at=license.updated_at,
    )


@router.get("/{license_id}/features")
async def get_license_features(
    license_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
):
    """
    Get all features for a license with their enabled status.
    Returns available features from product and which are enabled on the license.
    """
    license_service = LicenseService(db)
    
    license = await license_service.get_by_id(license_id, current_user.id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    enabled_features = [f.lower() for f in (license.features or [])]
    
    # Get available features from product
    available_features = []
    if license.product:
        for f in (license.product.available_features or []):
            if isinstance(f, dict):
                slug = f.get("slug", "")
                available_features.append({
                    "slug": slug,
                    "name": f.get("name", slug.replace("_", " ").title()),
                    "description": f.get("description"),
                    "enabled": slug.lower() in enabled_features
                })
            else:
                available_features.append({
                    "slug": f,
                    "name": str(f).replace("_", " ").title(),
                    "description": None,
                    "enabled": str(f).lower() in enabled_features
                })
    
    return {
        "license_id": license.id,
        "enabled_features": license.features or [],
        "available_features": available_features
    }
