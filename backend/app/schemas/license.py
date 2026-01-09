"""
License Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class LicenseType(str, Enum):
    """License type enum"""
    UNLIMITED = "unlimited"
    TRIAL = "trial"
    LIMITED = "limited"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class LicenseStatus(str, Enum):
    """License status enum"""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class LicenseBase(BaseModel):
    """Base license schema"""
    name: Optional[str] = None
    license_type: LicenseType
    max_devices: int = Field(default=1, ge=0, description="Maximum devices (0 = unlimited)")
    metadata: Optional[dict] = None
    features: List[str] = []


class InitialRevenueData(BaseModel):
    """Optional revenue data for license creation"""
    amount: float = Field(..., ge=0)
    currency: str = Field(default="EUR", max_length=3)
    notes: Optional[str] = None


class LicenseCreate(LicenseBase):
    """Schema for license creation"""
    product_id: Optional[int] = None
    trial_duration_days: Optional[int] = Field(default=None, ge=1, le=365)
    duration_days: Optional[int] = Field(default=None, ge=1, le=3650, description="Gültigkeit in Tagen für zeitlich begrenzte Lizenzen")
    expires_at: Optional[datetime] = None
    price: Optional[float] = Field(default=None, ge=0)
    note: Optional[str] = None
    initial_revenue: Optional[InitialRevenueData] = None


class LicenseUpdate(BaseModel):
    """Schema for license update"""
    name: Optional[str] = None
    max_devices: Optional[int] = Field(default=None, ge=0)
    status: Optional[LicenseStatus] = None
    metadata: Optional[dict] = None
    features: Optional[List[str]] = None
    price: Optional[float] = Field(default=None, ge=0)
    note: Optional[str] = None


class LicenseFeatureToggle(BaseModel):
    """Schema for toggling a single feature on a license"""
    feature_slug: str = Field(..., min_length=1, max_length=100)
    enabled: bool = Field(..., description="True to enable, False to disable")


class LicenseFeaturesBulkUpdate(BaseModel):
    """Schema for bulk updating features on a license"""
    features: List[str] = Field(..., description="Complete list of enabled features")


class LicenseResponse(LicenseBase):
    """Schema for license response"""
    id: int
    key: str
    status: LicenseStatus
    product_id: Optional[int] = None
    product: Optional["ProductSimple"] = None
    expires_at: Optional[datetime] = None
    days_remaining: Optional[int] = None
    current_devices: int = 0
    trial_duration_days: Optional[int] = None
    price: Optional[float] = None
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LicenseListResponse(BaseModel):
    """Schema for license list response"""
    licenses: List[LicenseResponse]
    total: int


class LicenseValidationRequest(BaseModel):
    """Schema for license validation request"""
    license_key: str = Field(..., min_length=1)
    device_id: str = Field(..., min_length=1)
    device_name: Optional[str] = None
    os_info: Optional[str] = None
    app_version: Optional[str] = None
    product_slug: Optional[str] = None  # Optional: validate for specific product


class ProductInfo(BaseModel):
    """Product info in validation response"""
    id: int
    name: str
    slug: str
    version: Optional[str] = None


class LicenseValidationResponse(BaseModel):
    """Schema for license validation response"""
    valid: bool
    license_type: Optional[str] = None
    expires_at: Optional[datetime] = None
    days_remaining: Optional[int] = None
    max_devices: Optional[int] = None
    current_devices: Optional[int] = None
    cache_until: Optional[datetime] = None
    features: List[str] = []
    product: Optional[ProductInfo] = None
    reason: Optional[str] = None
    from_cache: bool = False


class LicenseDetailResponse(LicenseResponse):
    """Schema for license detail with devices"""
    devices: List["DeviceResponse"] = []
    activity: List["ActivityLogResponse"] = []


# Forward references for nested models
from app.schemas.device import DeviceResponse, ActivityLogResponse
from app.schemas.product import ProductSimple
LicenseDetailResponse.model_rebuild()
LicenseResponse.model_rebuild()
