"""
Device identification module

Generates unique device IDs based on hardware characteristics.
"""

import hashlib
import uuid
import platform
from typing import Dict, Optional


def generate_device_id() -> str:
    """
    Generate a unique device identifier based on hardware characteristics.
    
    Uses a combination of:
    - MAC address
    - Hostname
    - OS information
    - Processor information
    
    Returns:
        SHA256 hash of combined hardware identifiers
    """
    try:
        # Get MAC address
        mac = str(uuid.getnode())
        
        # Get hostname
        hostname = platform.node()
        
        # Get OS info
        os_info = f"{platform.system()}-{platform.release()}"
        
        # Get processor info
        processor = platform.processor() or platform.machine()
        
        # Combine and hash
        combined = f"{mac}:{hostname}:{os_info}:{processor}"
        device_id = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
        return device_id
    
    except Exception:
        # Fallback: generate a persistent UUID based on hostname
        try:
            hostname = platform.node()
            return hashlib.sha256(f"fallback:{hostname}:{uuid.getnode()}".encode()).hexdigest()
        except Exception:
            # Last resort: random UUID (not persistent across restarts)
            return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()


def get_device_info() -> Dict[str, Optional[str]]:
    """
    Collect device information for registration.
    
    Returns:
        Dictionary containing device details:
        - device_id: Unique hardware identifier
        - device_name: Hostname/computer name
        - os_info: Operating system information
        - python_version: Python version
    """
    device_id = generate_device_id()
    
    try:
        device_name = platform.node()
    except Exception:
        device_name = "Unknown"
    
    try:
        os_info = f"{platform.system()} {platform.release()}"
        # Add more detail if available
        if platform.system() == "Windows":
            os_info = f"Windows {platform.release()} ({platform.version()})"
        elif platform.system() == "Darwin":
            os_info = f"macOS {platform.mac_ver()[0]}"
        elif platform.system() == "Linux":
            try:
                # Try to get distribution info
                import distro
                os_info = f"{distro.name()} {distro.version()}"
            except ImportError:
                os_info = f"Linux {platform.release()}"
    except Exception:
        os_info = platform.system() or "Unknown OS"
    
    try:
        python_version = platform.python_version()
    except Exception:
        python_version = "Unknown"
    
    return {
        "device_id": device_id,
        "device_name": device_name,
        "os_info": os_info,
        "python_version": python_version
    }


def get_machine_fingerprint() -> str:
    """
    Generate a shorter fingerprint for display purposes.
    
    Returns:
        First 16 characters of the device ID
    """
    return generate_device_id()[:16]
