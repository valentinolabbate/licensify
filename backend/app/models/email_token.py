"""
Email Verification Token Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class EmailVerificationToken(Base):
    """Email verification token database model"""
    __tablename__ = "email_verification_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="verification_tokens")
    
    def __repr__(self):
        return f"<EmailVerificationToken(id={self.id}, user_id={self.user_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at
