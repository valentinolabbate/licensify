"""
Utility functions for Licensify
"""

from datetime import datetime
from typing import Optional


def parse_iso_datetime(dt_string: Optional[str]) -> Optional[datetime]:
    """
    Parse an ISO format datetime string.
    
    Handles various ISO formats including:
    - 2025-01-08T15:22:00Z
    - 2025-01-08T15:22:00+00:00
    - 2025-01-08T15:22:00
    
    Args:
        dt_string: ISO format datetime string
        
    Returns:
        datetime object or None if parsing fails
    """
    if not dt_string:
        return None
    
    try:
        # Handle 'Z' suffix
        dt_string = dt_string.replace('Z', '+00:00')
        
        # Try parsing with timezone
        try:
            return datetime.fromisoformat(dt_string)
        except ValueError:
            # Try without timezone
            dt_string = dt_string.split('+')[0].split('-')[0]
            return datetime.fromisoformat(dt_string)
    except (ValueError, TypeError):
        return None


def format_datetime(dt: Optional[datetime], include_time: bool = True) -> str:
    """
    Format a datetime for display.
    
    Args:
        dt: datetime to format
        include_time: whether to include time portion
        
    Returns:
        Formatted string or "Never" if None
    """
    if not dt:
        return "Never"
    
    if include_time:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt.strftime("%Y-%m-%d")


def days_until(dt: Optional[datetime]) -> Optional[int]:
    """
    Calculate days until a datetime.
    
    Args:
        dt: target datetime
        
    Returns:
        Number of days (negative if past) or None
    """
    if not dt:
        return None
    
    delta = dt - datetime.utcnow()
    return delta.days


def mask_license_key(key: str, visible_chars: int = 8) -> str:
    """
    Mask a license key for safe display.
    
    Args:
        key: Full license key
        visible_chars: Number of characters to show
        
    Returns:
        Masked key (e.g., "ABC12345...")
    """
    if not key:
        return ""
    
    if len(key) <= visible_chars:
        return key
    
    return key[:visible_chars] + "..."
