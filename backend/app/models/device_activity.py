"""
Device Activity Model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class DeviceActivity(Base):
    """Device activity log database model"""
    __tablename__ = "device_activity"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # 'validated', 'registered', 'updated'
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    activity_metadata = Column(JSON, nullable=True)  # Additional data: Python version, App version, etc.
    
    # Relationships
    device = relationship("Device", back_populates="activities")
    
    def __repr__(self):
        return f"<DeviceActivity(id={self.id}, device_id={self.device_id}, action={self.action})>"
