"""
Custom Exceptions for Licensify
"""


class LicenseException(Exception):
    """Base exception for all licensify errors"""
    pass


class InvalidLicenseKeyException(LicenseException):
    """Raised when the license key is invalid"""
    def __init__(self, message: str = "Invalid license key"):
        super().__init__(message)


class LicenseExpiredException(LicenseException):
    """Raised when the license has expired"""
    def __init__(self, expires_at: str = None):
        message = "License has expired"
        if expires_at:
            message += f" on {expires_at}"
        super().__init__(message)
        self.expires_at = expires_at


class LicenseRevokedException(LicenseException):
    """Raised when the license has been revoked"""
    def __init__(self, message: str = "License has been revoked"):
        super().__init__(message)


class DeviceCountExceededException(LicenseException):
    """Raised when maximum device count is exceeded"""
    def __init__(self, max_devices: int = None, current_devices: int = None):
        message = "Maximum device count exceeded"
        if max_devices and current_devices:
            message = f"Device limit exceeded: {current_devices}/{max_devices} devices"
        super().__init__(message)
        self.max_devices = max_devices
        self.current_devices = current_devices


class DeviceBlockedException(LicenseException):
    """Raised when the device is blocked"""
    def __init__(self, message: str = "This device has been blocked"):
        super().__init__(message)


class NetworkException(LicenseException):
    """Raised when there's a network error during validation"""
    def __init__(self, message: str = "Network error during license validation"):
        super().__init__(message)


class CacheExpiredException(LicenseException):
    """Raised when cache has expired and offline mode is not available"""
    def __init__(self, message: str = "License cache expired. Online validation required."):
        super().__init__(message)


class ValidationException(LicenseException):
    """Raised when validation fails for an unknown reason"""
    def __init__(self, reason: str = "unknown"):
        message = f"License validation failed: {reason}"
        super().__init__(message)
        self.reason = reason
