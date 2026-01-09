"""
Models module initialization
Import all models here for Alembic to discover them
"""
from app.models.user import User
from app.models.email_token import EmailVerificationToken
from app.models.product import Product
from app.models.license import License
from app.models.device import Device
from app.models.device_activity import DeviceActivity
from app.models.revenue import Revenue

__all__ = [
    "User",
    "EmailVerificationToken",
    "Product",
    "License",
    "Device",
    "DeviceActivity",
    "Revenue",
]
