"""
Local cache manager for offline license validation

Caches successful validations for offline use with a 30-day grace period.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any

from licensify.exceptions import CacheExpiredException


class CacheManager:
    """
    Manages local license cache for offline validation.
    
    Cache is stored as JSON and includes:
    - License key
    - Validation result
    - Cache timestamp
    - Cache expiration (min of 30 days or license expiry)
    """
    
    DEFAULT_CACHE_DAYS = 30
    CACHE_FILENAME = "license_cache.json"
    
    def __init__(self, cache_dir: str = "~/.licensify"):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache file (default: ~/.licensify)
        """
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_file = self.cache_dir / self.CACHE_FILENAME
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, validation_result: Dict[str, Any], license_key: str) -> None:
        """
        Save validation result to cache.
        
        Cache expiration is set to the minimum of:
        - 30 days from now
        - License expiration date
        
        Args:
            validation_result: Validation response from server
            license_key: The license key being cached
        """
        cache_until = datetime.utcnow() + timedelta(days=self.DEFAULT_CACHE_DAYS)
        
        # If license has an expiration, don't cache beyond it
        if validation_result.get('expires_at'):
            try:
                expires_at_str = validation_result['expires_at']
                if isinstance(expires_at_str, str):
                    # Handle ISO format with or without timezone
                    expires_at_str = expires_at_str.replace('Z', '+00:00')
                    license_expiry = datetime.fromisoformat(expires_at_str.replace('+00:00', ''))
                    cache_until = min(cache_until, license_expiry)
            except (ValueError, TypeError):
                pass  # Keep default cache_until
        
        cache_data = {
            "license_key": license_key,
            "validation_result": validation_result,
            "cached_at": datetime.utcnow().isoformat(),
            "cache_until": cache_until.isoformat()
        }
        
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, default=str)
        except (IOError, OSError) as e:
            # Silently fail if we can't write cache
            pass
    
    def load(self, license_key: str) -> Optional[Dict[str, Any]]:
        """
        Load cached validation for a license key.
        
        Args:
            license_key: The license key to look up
            
        Returns:
            Cached validation result if valid, None otherwise
        """
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
        except (json.JSONDecodeError, IOError, OSError):
            return None
        
        # Verify license key matches
        if cache_data.get('license_key') != license_key:
            return None
        
        # Check if cache is still valid
        try:
            cache_until = datetime.fromisoformat(cache_data['cache_until'])
            if datetime.utcnow() > cache_until:
                return None
        except (ValueError, KeyError):
            return None
        
        return cache_data.get('validation_result')
    
    def is_valid(self, license_key: str = None) -> bool:
        """
        Check if there's a valid cache entry.
        
        Args:
            license_key: Optional license key to check (if None, checks any cache)
            
        Returns:
            True if valid cache exists, False otherwise
        """
        if not self.cache_file.exists():
            return False
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
        except (json.JSONDecodeError, IOError, OSError):
            return False
        
        # Check license key if provided
        if license_key and cache_data.get('license_key') != license_key:
            return False
        
        # Check expiration
        try:
            cache_until = datetime.fromisoformat(cache_data['cache_until'])
            return datetime.utcnow() <= cache_until
        except (ValueError, KeyError):
            return False
    
    def get_cache_expiry(self, license_key: str = None) -> Optional[datetime]:
        """
        Get the cache expiration datetime.
        
        Args:
            license_key: Optional license key to check
            
        Returns:
            Cache expiration datetime or None
        """
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
        except (json.JSONDecodeError, IOError, OSError):
            return None
        
        if license_key and cache_data.get('license_key') != license_key:
            return None
        
        try:
            return datetime.fromisoformat(cache_data['cache_until'])
        except (ValueError, KeyError):
            return None
    
    def clear(self) -> None:
        """Clear the cache file"""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except OSError:
            pass
    
    def get_info(self) -> Optional[Dict[str, Any]]:
        """
        Get cache information for debugging.
        
        Returns:
            Dictionary with cache metadata or None
        """
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            return {
                "license_key": cache_data.get('license_key', '')[:8] + '...',
                "cached_at": cache_data.get('cached_at'),
                "cache_until": cache_data.get('cache_until'),
                "is_valid": self.is_valid(),
                "cache_file": str(self.cache_file)
            }
        except (json.JSONDecodeError, IOError, OSError):
            return None
