"""
Revenue API Endpoints (Admin only)
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.revenue_service import RevenueService
from app.services.license_service import LicenseService
from app.api.deps import get_current_admin_user
from app.schemas.revenue import (
    RevenueCreate,
    RevenueResponse,
    RevenueListResponse,
    RevenueSummary,
    LicenseExtendRequest,
)
from app.schemas.license import LicenseResponse

router = APIRouter(prefix="/admin/revenue", tags=["admin-revenue"])


@router.get("", response_model=RevenueListResponse)
async def get_all_revenues(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    license_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all revenue entries (admin only)"""
    revenue_service = RevenueService(db)
    revenues, total, total_amount = await revenue_service.get_all(
        skip=skip,
        limit=limit,
        license_id=license_id,
        user_id=user_id
    )
    
    # Enrich revenues with license/user info
    enriched = [await revenue_service.enrich_revenue(r) for r in revenues]
    
    return RevenueListResponse(
        revenues=enriched,
        total=total,
        total_amount=total_amount
    )


@router.get("/summary", response_model=RevenueSummary)
async def get_revenue_summary(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get revenue summary/statistics (admin only)"""
    revenue_service = RevenueService(db)
    summary = await revenue_service.get_summary()
    return RevenueSummary(**summary)


@router.post("", response_model=RevenueResponse)
async def create_revenue(
    revenue_data: RevenueCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new revenue entry (admin only)"""
    revenue_service = RevenueService(db)
    license_service = LicenseService(db)
    
    # Verify license exists
    license = await license_service.get_by_id_admin(revenue_data.license_id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    revenue = await revenue_service.create(
        license_id=revenue_data.license_id,
        amount=revenue_data.amount,
        currency=revenue_data.currency,
        payment_type=revenue_data.payment_type.value,
        notes=revenue_data.notes,
        period_start=revenue_data.period_start,
        period_end=revenue_data.period_end,
        created_by_id=current_admin.id
    )
    
    enriched = await revenue_service.enrich_revenue(revenue)
    return RevenueResponse(**enriched)


@router.get("/license/{license_id}", response_model=RevenueListResponse)
async def get_license_revenues(
    license_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all revenue entries for a specific license (admin only)"""
    revenue_service = RevenueService(db)
    license_service = LicenseService(db)
    
    # Verify license exists
    license = await license_service.get_by_id_admin(license_id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    revenues = await revenue_service.get_for_license(license_id)
    enriched = [await revenue_service.enrich_revenue(r) for r in revenues]
    total_amount = sum(r.amount for r in revenues)
    
    return RevenueListResponse(
        revenues=enriched,
        total=len(revenues),
        total_amount=total_amount
    )


@router.delete("/{revenue_id}")
async def delete_revenue(
    revenue_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete a revenue entry (admin only)"""
    revenue_service = RevenueService(db)
    
    success = await revenue_service.delete(revenue_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Revenue entry not found"
        )
    
    return {"message": "Revenue entry deleted successfully"}


@router.post("/license/{license_id}/extend", response_model=LicenseResponse)
async def extend_license(
    license_id: int,
    extend_data: LicenseExtendRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Extend a license and optionally record revenue (admin only)"""
    license_service = LicenseService(db)
    revenue_service = RevenueService(db)
    
    # Get the license
    license = await license_service.get_by_id_admin(license_id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License not found"
        )
    
    # Calculate new expiry date
    old_expires_at = license.expires_at
    if license.expires_at:
        # Extend from current expiry (or now if already expired)
        base_date = max(license.expires_at, datetime.utcnow())
        new_expires_at = base_date + timedelta(days=extend_data.days)
    else:
        # License was unlimited, now set expiry
        new_expires_at = datetime.utcnow() + timedelta(days=extend_data.days)
    
    # Update license
    license.expires_at = new_expires_at
    if license.status == "expired":
        license.status = "active"
    
    await db.commit()
    await db.refresh(license)
    
    # Record revenue if provided
    if extend_data.revenue and extend_data.revenue.amount is not None:
        await revenue_service.create(
            license_id=license_id,
            amount=extend_data.revenue.amount,
            currency=extend_data.revenue.currency,
            payment_type="extension",
            notes=extend_data.revenue.notes,
            period_start=old_expires_at or datetime.utcnow(),
            period_end=new_expires_at,
            created_by_id=current_admin.id
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
        updated_at=license.updated_at
    )
