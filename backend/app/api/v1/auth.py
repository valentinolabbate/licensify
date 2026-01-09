"""
Authentication Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.user_service import UserService
from app.services.email_service import EmailService
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_email_token,
)
from app.core.config import settings
from app.core.limiter import limiter
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    AccessTokenResponse,
    EmailVerificationRequest,
    RegisterResponse,
    MessageResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Password (min 8 characters)
    - **full_name**: Optional full name
    """
    user_service = UserService(db)
    
    # Check if email already exists
    existing_user = await user_service.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await user_service.create(user_data)
    
    # Create verification token
    token = await user_service.create_verification_token(user)
    
    # Send verification email
    await EmailService.send_verification_email(
        to_email=user.email,
        token=token.token,
        full_name=user.full_name
    )
    
    return RegisterResponse(
        id=user.id,
        email=user.email,
        message="Registration successful. Check your email for verification link."
    )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    request: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify user email with token"""
    user_service = UserService(db)
    
    # Verify token
    email = verify_email_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Get user
    user = await user_service.get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        return MessageResponse(message="Email already verified")
    
    # Verify user
    await user_service.verify_email(user)
    
    # Delete verification token
    token_obj = await user_service.get_verification_token(request.token)
    if token_obj:
        await user_service.delete_verification_token(token_obj)
    
    return MessageResponse(message="Email verified successfully")


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    
    Returns JWT access token and refresh token.
    """
    user_service = UserService(db)
    
    # Authenticate user
    user = await user_service.authenticate(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    if not user.is_approved and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account pending admin approval"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    payload = decode_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify user exists
    user_service = UserService(db)
    user = await user_service.get_by_id(int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled"
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return AccessTokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(__import__("app.api.deps", fromlist=["get_current_user"]).get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: __import__("app.schemas.user", fromlist=["PasswordChangeRequest"]).PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(__import__("app.api.deps", fromlist=["get_current_user"]).get_current_user)
):
    """Change current user's password"""
    user_service = UserService(db)
    
    # Verify current password
    from app.core.security import verify_password, get_password_hash
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    await db.commit()
    
    return MessageResponse(message="Password changed successfully")
