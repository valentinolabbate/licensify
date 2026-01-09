"""
Main License Validator Client

This is the primary interface for validating licenses in Python applications.
"""

import threading
import time
from typing import Dict, Any, Optional

import requests

from licensify.device import get_device_info
from licensify.cache import CacheManager
from licensify.config import LicenseConfig
from licensify.exceptions import (
    LicenseException,
    InvalidLicenseKeyException,
    LicenseExpiredException,
    LicenseRevokedException,
    DeviceCountExceededException,
    DeviceBlockedException,
    NetworkException,
    CacheExpiredException,
    ValidationException,
)


class LicenseValidator:
    """
    License validation client for Python applications.
    
    Validates licenses against a License Manager server with support for:
    - Online validation
    - Offline caching (30-day grace period)
    - Device binding
    - Background validation
    
    Example:
        ```python
        from licensify import LicenseValidator
        
        validator = LicenseValidator(
            api_url="https://license-manager.example.com",
            license_key="YOUR_LICENSE_KEY"
        )
        
        if validator.is_valid():
            print("License valid!")
        ```
    """
    
    def __init__(
        self,
        api_url: str,
        license_key: str,
        app_version: str = "1.0.0",
        cache_dir: str = "~/.licensify",
        timeout: int = 5,
        verify_ssl: bool = True
    ):
        """
        Initialize the license validator.
        
        Args:
            api_url: Base URL of the License Manager API
            license_key: The license key to validate
            app_version: Version of your application
            cache_dir: Directory for license cache
            timeout: HTTP request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.config = LicenseConfig(
            api_url=api_url,
            license_key=license_key,
            app_version=app_version,
            cache_dir=cache_dir,
            timeout=timeout,
            verify_ssl=verify_ssl
        )
        
        self.cache_manager = CacheManager(cache_dir)
        self.device_info = get_device_info()
        
        # Background check state
        self._background_thread: Optional[threading.Thread] = None
        self._stop_background = threading.Event()
        self._last_validation: Optional[Dict[str, Any]] = None
    
    def validate(self, force_online: bool = False) -> Dict[str, Any]:
        """
        Validate the license.
        
        Attempts online validation first. If that fails, falls back to
        cached validation (if available and not expired).
        
        Args:
            force_online: If True, skip cache fallback on failure
            
        Returns:
            Validation result dictionary containing:
            - valid: bool
            - license_type: str
            - expires_at: str (ISO format)
            - days_remaining: int
            - max_devices: int
            - current_devices: int
            - cache_until: str (ISO format)
            - from_cache: bool
            
        Raises:
            LicenseException: Various subclasses based on failure reason
        """
        if force_online:
            return self._validate_online()
        
        try:
            # Attempt online validation
            result = self._validate_online()
            
            # Cache successful validation
            if result.get('valid'):
                self.cache_manager.save(result, self.config.license_key)
            
            self._last_validation = result
            return result
            
        except (requests.RequestException, NetworkException) as e:
            # Network error - try cache
            cached_result = self.cache_manager.load(self.config.license_key)
            
            if cached_result:
                cached_result['from_cache'] = True
                cached_result['cache_expires_at'] = self.cache_manager.get_cache_expiry(
                    self.config.license_key
                )
                self._last_validation = cached_result
                return cached_result
            
            # No cache available
            raise CacheExpiredException(
                f"Online validation failed and no valid cache: {e}"
            )
    
    def _validate_online(self) -> Dict[str, Any]:
        """
        Perform online validation against the server.
        
        Returns:
            Validation result from server
            
        Raises:
            Various LicenseException subclasses
        """
        payload = {
            "license_key": self.config.license_key,
            "device_id": self.device_info["device_id"],
            "device_name": self.device_info.get("device_name"),
            "os_info": self.device_info.get("os_info"),
            "app_version": self.config.app_version
        }
        
        try:
            response = requests.post(
                f"{self.config.api_url}/api/v1/licenses/validate",
                json=payload,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
        except requests.Timeout:
            raise NetworkException("Request timed out")
        except requests.ConnectionError:
            raise NetworkException("Could not connect to license server")
        except requests.RequestException as e:
            raise NetworkException(f"Network error: {e}")
        
        # Handle response
        if response.status_code == 429:
            raise NetworkException("Rate limit exceeded. Please try again later.")
        
        if response.status_code != 200:
            raise NetworkException(f"Server returned status {response.status_code}")
        
        try:
            result = response.json()
        except ValueError:
            raise NetworkException("Invalid response from server")
        
        # Handle invalid license
        if not result.get('valid'):
            reason = result.get('reason', 'unknown')
            
            if reason == 'invalid_key':
                raise InvalidLicenseKeyException()
            elif reason == 'license_expired':
                raise LicenseExpiredException(result.get('expires_at'))
            elif reason == 'license_revoked':
                raise LicenseRevokedException()
            elif reason == 'device_blocked':
                raise DeviceBlockedException()
            elif reason == 'device_limit_exceeded':
                raise DeviceCountExceededException(
                    result.get('max_devices'),
                    result.get('current_devices')
                )
            else:
                raise ValidationException(reason)
        
        result['from_cache'] = False
        return result
    
    def is_valid(self) -> bool:
        """
        Quick check if the license is valid.
        
        Handles all exceptions internally and returns a simple boolean.
        Use validate() for detailed error information.
        
        Returns:
            True if license is valid (online or cached), False otherwise
        """
        try:
            result = self.validate()
            return result.get('valid', False)
        except LicenseException:
            return False
        except Exception:
            return False
    
    def get_last_validation(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent validation result.
        
        Returns:
            Last validation result or None
        """
        return self._last_validation
    
    def get_features(self) -> list:
        """
        Get the list of enabled features for this license.
        
        Returns:
            List of feature strings (e.g. ["basic", "export", "api_access"])
        """
        if self._last_validation:
            return self._last_validation.get('features', [])
        
        cached = self.cache_manager.load(self.config.license_key)
        if cached:
            return cached.get('features', [])
        
        return []
    
    def has_feature(self, feature: str) -> bool:
        """
        Check if the license has a specific feature enabled.
        
        Args:
            feature: The feature name to check
            
        Returns:
            True if the feature is enabled, False otherwise
        """
        return feature.lower() in [f.lower() for f in self.get_features()]
    
    def get_product(self) -> Optional[Dict[str, Any]]:
        """
        Get the product information for this license.
        
        Returns:
            Product info dict with id, name, slug, version or None
        """
        if self._last_validation:
            return self._last_validation.get('product')
        
        cached = self.cache_manager.load(self.config.license_key)
        if cached:
            return cached.get('product')
        
        return None
    
    def get_product_name(self) -> Optional[str]:
        """
        Get the product name for this license.
        
        Returns:
            Product name or None
        """
        product = self.get_product()
        return product.get('name') if product else None
    
    def get_product_version(self) -> Optional[str]:
        """
        Get the product version for this license.
        
        Returns:
            Product version or None
        """
        product = self.get_product()
        return product.get('version') if product else None
    
    def get_license_info(self) -> Optional[Dict[str, Any]]:
        """
        Get license information without triggering a new validation.
        
        Returns cached information if available.
        
        Returns:
            License info dict or None
        """
        if self._last_validation:
            return self._last_validation
        
        return self.cache_manager.load(self.config.license_key)
    
    def clear_cache(self) -> None:
        """Clear the local license cache"""
        self.cache_manager.clear()
        self._last_validation = None
    
    def start_background_check(self, interval_hours: float = 1.0) -> None:
        """
        Start periodic background license validation.
        
        The background thread validates the license at regular intervals
        to keep the cache fresh.
        
        Args:
            interval_hours: Hours between validation checks
        """
        if self._background_thread and self._background_thread.is_alive():
            return  # Already running
        
        self._stop_background.clear()
        
        def _check_loop():
            interval_seconds = interval_hours * 3600
            
            while not self._stop_background.is_set():
                try:
                    self.validate()
                except LicenseException:
                    pass  # Silently continue
                except Exception:
                    pass
                
                # Wait for interval or stop signal
                self._stop_background.wait(timeout=interval_seconds)
        
        self._background_thread = threading.Thread(
            target=_check_loop,
            daemon=True,
            name="licensify-background"
        )
        self._background_thread.start()
    
    def stop_background_check(self) -> None:
        """Stop the background validation thread"""
        self._stop_background.set()
        
        if self._background_thread:
            self._background_thread.join(timeout=5)
            self._background_thread = None
    
    def get_device_id(self) -> str:
        """
        Get the device ID for this machine.
        
        Returns:
            Device ID string (SHA256 hash)
        """
        return self.device_info["device_id"]
    
    def get_device_fingerprint(self) -> str:
        """
        Get a short device fingerprint for display.
        
        Returns:
            First 16 characters of device ID
        """
        return self.device_info["device_id"][:16]
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop background thread"""
        self.stop_background_check()
        return False
    
    def __repr__(self) -> str:
        return (
            f"LicenseValidator("
            f"api_url='{self.config.api_url}', "
            f"license_key='{self.config.license_key[:8]}...')"
        )
