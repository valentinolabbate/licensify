"""
Product Model - Software products that licenses can be assigned to
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class Product(Base):
    """Product database model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)  # URL-friendly identifier
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=True)  # Current version
    
    # Features this product supports (JSON array)
    # e.g. ["basic", "export", "api_access", "premium_support"]
    available_features = Column(JSON, default=list)
    
    # Default settings for new licenses
    default_max_devices = Column(Integer, default=1)
    default_license_type = Column(String(50), default="limited")
    
    # Product status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    licenses = relationship("License", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, slug={self.slug})>"
