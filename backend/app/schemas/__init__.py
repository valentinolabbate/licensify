"""
Schemas module initialization
"""
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    AccessTokenResponse,
    EmailVerificationRequest,
    RegisterResponse,
    MessageResponse,
)
from app.schemas.license import (
    LicenseType,
    LicenseStatus,
    LicenseCreate,
    LicenseUpdate,
    LicenseResponse,
    LicenseListResponse,
    LicenseValidationRequest,
    LicenseValidationResponse,
    LicenseDetailResponse,
)
from app.schemas.device import (
    DeviceStatus,
    DeviceUpdate,
    DeviceResponse,
    DeviceListResponse,
    ActivityLogResponse,
)
from app.schemas.revenue import (
    PaymentType,
    RevenueCreate,
    RevenueCreateWithExtension,
    RevenueResponse,
    RevenueListResponse,
    RevenueSummary,
    LicenseExtendRequest,
)
