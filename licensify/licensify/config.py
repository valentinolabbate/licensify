"""
Configuration management for Licensify
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LicenseConfig:
    """Configuration for the license validator"""
    
    api_url: str
    """Base URL of the License Manager API"""
    
    license_key: str
    """The license key to validate"""
    
    app_version: str = "1.0.0"
    """Version of the application using the license"""
    
    cache_dir: str = "~/.licensify"
    """Directory for storing license cache"""
    
    timeout: int = 5
    """HTTP request timeout in seconds"""
    
    verify_ssl: bool = True
    """Whether to verify SSL certificates"""
    
    auto_cache: bool = True
    """Automatically cache successful validations"""
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.api_url:
            raise ValueError("api_url is required")
        if not self.license_key:
            raise ValueError("license_key is required")
        
        # Normalize API URL (remove trailing slash)
        self.api_url = self.api_url.rstrip('/')


def get_default_config(api_url: str, license_key: str, **kwargs) -> LicenseConfig:
    """
    Create a configuration with default values.
    
    Args:
        api_url: Base URL of the License Manager API
        license_key: The license key to validate
        **kwargs: Additional configuration options
        
    Returns:
        LicenseConfig instance
    """
    return LicenseConfig(
        api_url=api_url,
        license_key=license_key,
        **kwargs
    )
