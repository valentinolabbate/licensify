"""
License Model
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Numeric, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class License(Base):
    """License database model"""
    __tablename__ = "licenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    key = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    license_type = Column(String(50), nullable=False)  # 'unlimited', 'trial', 'limited'
    status = Column(String(50), default="active", index=True)  # 'active', 'revoked', 'expired'
    max_devices = Column(Integer, nullable=False, default=1)  # 0 = unlimited
    expires_at = Column(DateTime, nullable=True)  # NULL for unlimited
    trial_duration_days = Column(Integer, nullable=True)  # For trial licenses
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    license_metadata = Column(JSON, nullable=True)  # Custom metadata
    
    # Features enabled for this license (overrides product defaults if set)
    # e.g. ["basic", "export"] - subset of product's available_features
    features = Column(JSON, default=list)
    
    # Price and notes
    price = Column(Numeric(10, 2), nullable=True)  # License price
    note = Column(Text, nullable=True)  # Internal notes
    
    # Relationships
    user = relationship("User", back_populates="licenses")
    product = relationship("Product", back_populates="licenses")
    devices = relationship("Device", back_populates="license", cascade="all, delete-orphan")
    revenues = relationship("Revenue", back_populates="license", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<License(id={self.id}, key={self.key[:8]}..., type={self.license_type})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if license is expired"""
        if self.status == "expired":
            return True
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False
    
    @property
    def is_valid(self) -> bool:
        """Check if license is currently valid"""
        return self.status == "active" and not self.is_expired
    
    @property
    def days_remaining(self) -> int | None:
        """Calculate days remaining until expiry"""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def current_device_count(self) -> int:
        """Get current number of active devices"""
        return len([d for d in self.devices if d.status == "active"])
