"""
Revenue Model - Track license payments/revenue
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship

from app.db.base import Base


class Revenue(Base):
    """Revenue/Payment tracking for licenses"""
    __tablename__ = "revenues"
    
    id = Column(Integer, primary_key=True, index=True)
    license_id = Column(Integer, ForeignKey("licenses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)  # Amount in currency
    currency = Column(String(3), default="EUR", nullable=False)  # ISO currency code
    
    # Period this payment covers
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    
    # Additional info
    payment_type = Column(String(50), default="extension")  # 'initial', 'extension', 'upgrade'
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    license = relationship("License", back_populates="revenues")
    user = relationship("User", foreign_keys=[user_id], backref="license_revenues")
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"<Revenue(id={self.id}, license_id={self.license_id}, amount={self.amount})>"
