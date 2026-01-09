"""
User Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=True)  # Auto-verify (email verification disabled)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)  # Requires admin approval
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    licenses = relationship("License", back_populates="user", cascade="all, delete-orphan")
    verification_tokens = relationship("EmailVerificationToken", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
