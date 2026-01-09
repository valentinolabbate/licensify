"""
User Service - Business logic for user operations
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.email_token import EmailVerificationToken
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, create_email_verification_token


class UserService:
    """Service class for user operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_verified=False,
            is_admin=False,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update(self, user: User, user_data: UserUpdate) -> User:
        """Update user"""
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        user.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    async def verify_email(self, user: User) -> User:
        """Mark user email as verified"""
        user.is_verified = True
        user.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def create_verification_token(self, user: User) -> EmailVerificationToken:
        """Create email verification token"""
        token_str = create_email_verification_token(user.email)
        token = EmailVerificationToken(
            user_id=user.id,
            token=token_str,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)
        return token
    
    async def get_verification_token(self, token: str) -> Optional[EmailVerificationToken]:
        """Get verification token"""
        result = await self.db.execute(
            select(EmailVerificationToken).where(EmailVerificationToken.token == token)
        )
        return result.scalar_one_or_none()
    
    async def delete_verification_token(self, token: EmailVerificationToken) -> None:
        """Delete verification token"""
        await self.db.delete(token)
        await self.db.commit()
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users (admin only)"""
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()
