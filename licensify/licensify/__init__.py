"""
Licensify - Python client library for License Manager

A client library to validate licenses in Python applications.
Supports online validation, offline caching, and device binding.
"""

__version__ = "1.0.0"
__author__ = "License Manager Team"

from licensify.client import LicenseValidator
from licensify.exceptions import (
    LicenseException,
    InvalidLicenseKeyException,
    LicenseExpiredException,
    DeviceCountExceededException,
    NetworkException,
    CacheExpiredException,
)
from licensify.device import generate_device_id, get_device_info
from licensify.cache import CacheManager

__all__ = [
    "LicenseValidator",
    "LicenseException",
    "InvalidLicenseKeyException",
    "LicenseExpiredException",
    "DeviceCountExceededException",
    "NetworkException",
    "CacheExpiredException",
    "generate_device_id",
    "get_device_info",
    "CacheManager",
]
