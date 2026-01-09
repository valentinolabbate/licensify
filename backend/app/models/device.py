"""
Device Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import INET

from app.db.base import Base


class Device(Base):
    """Device database model"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    license_id = Column(Integer, ForeignKey("licenses.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(String(255), nullable=False, index=True)  # Hardware ID hash
    device_name = Column(String(255), nullable=True)
    os = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    status = Column(String(50), default="active")  # 'active', 'blocked'
    
    # Relationships
    license = relationship("License", back_populates="devices")
    activities = relationship("DeviceActivity", back_populates="device", cascade="all, delete-orphan")
    
    # Unique constraint for license + device combination
    __table_args__ = (
        UniqueConstraint('license_id', 'device_id', name='uq_device_license_combo'),
    )
    
    def __repr__(self):
        return f"<Device(id={self.id}, device_id={self.device_id[:16]}...)>"
