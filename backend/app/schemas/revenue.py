"""
Revenue Pydantic Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class PaymentType(str, Enum):
    """Payment type enum"""
    INITIAL = "initial"
    EXTENSION = "extension"
    UPGRADE = "upgrade"


class RevenueBase(BaseModel):
    """Base revenue schema"""
    amount: Decimal = Field(..., ge=0, description="Payment amount")
    currency: str = Field(default="EUR", max_length=3)
    payment_type: PaymentType = PaymentType.EXTENSION
    notes: Optional[str] = None


class RevenueCreate(RevenueBase):
    """Schema for creating revenue entry"""
    license_id: int
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class RevenueCreateWithExtension(BaseModel):
    """Schema for creating revenue when extending license"""
    amount: Optional[Decimal] = Field(default=None, ge=0, description="Payment amount (optional)")
    currency: str = Field(default="EUR", max_length=3)
    notes: Optional[str] = None


class RevenueResponse(RevenueBase):
    """Schema for revenue response"""
    id: int
    license_id: int
    user_id: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    created_at: datetime
    created_by_id: Optional[int] = None
    
    # Additional fields for display
    license_name: Optional[str] = None
    license_key: Optional[str] = None
    user_email: Optional[str] = None
    
    class Config:
        from_attributes = True


class RevenueListResponse(BaseModel):
    """Schema for revenue list response"""
    revenues: List[RevenueResponse]
    total: int
    total_amount: Decimal
    

class RevenueSummary(BaseModel):
    """Schema for revenue summary/statistics"""
    total_revenue: Decimal
    revenue_this_month: Decimal
    revenue_this_year: Decimal
    total_transactions: int
    transactions_this_month: int
    average_transaction: Decimal
    by_currency: dict  # {"EUR": 1234.56, "USD": 789.00}
    by_payment_type: dict  # {"initial": 500, "extension": 300}
    monthly_breakdown: List[dict]  # [{"month": "2026-01", "amount": 500}, ...]


class LicenseExtendRequest(BaseModel):
    """Schema for extending a license"""
    days: int = Field(..., ge=1, le=3650, description="Days to extend")
    revenue: Optional[RevenueCreateWithExtension] = None
