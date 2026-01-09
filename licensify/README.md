# Licensify

Python client library for License Manager - validate licenses in your Python applications.

## Installation

```bash
pip install licensify
```

## Quick Start

```python
from licensify import LicenseValidator

# Initialize validator
validator = LicenseValidator(
    api_url="https://license-manager.example.com",
    license_key="YOUR_LICENSE_KEY"
)

# Validate license
if validator.is_valid():
    print("License is valid!")
    # Run your application
else:
    print("License is invalid or expired")
```

## Features

- **Online Validation**: Validates license against the License Manager server
- **Offline Support**: 30-day grace period with local cache
- **Device Binding**: Hardware-based device identification
- **Background Checking**: Optional periodic license validation
- **Type Support**: Full type hints for better IDE support

## Usage

### Basic Validation

```python
from licensify import LicenseValidator, LicenseException

validator = LicenseValidator(
    api_url="https://license-manager.example.com",
    license_key="ABC123XYZ789DEF456GHI",
    app_version="1.2.3"
)

try:
    result = validator.validate()
    if result['valid']:
        print(f"License valid until {result['expires_at']}")
        print(f"Days remaining: {result['days_remaining']}")
        print(f"Devices: {result['current_devices']}/{result['max_devices']}")
except LicenseException as e:
    print(f"Validation error: {e}")
```

### Simple Check

```python
# Quick boolean check (handles exceptions internally)
if validator.is_valid():
    run_your_app()
else:
    show_license_error()
```

### Background Validation

```python
# Start background checker (validates every hour)
validator.start_background_check(interval_hours=1)

# Your app runs here...

# Stop background checker when done
validator.stop_background_check()
```

### Offline Mode

The library automatically caches successful validations locally. If the server is unreachable:

1. Uses cached validation (up to 30 days)
2. Cache expires at license expiry date (whichever is sooner)
3. Raises `CacheExpiredException` if no valid cache exists

```python
result = validator.validate()
if result.get('from_cache'):
    print(f"Using cached validation, expires: {result['cache_expires_at']}")
```

## Configuration

```python
validator = LicenseValidator(
    api_url="https://license-manager.example.com",  # Your server URL
    license_key="YOUR_LICENSE_KEY",                  # License key
    app_version="1.0.0",                            # Your app version
    cache_dir="~/.licensify",                       # Cache directory
    timeout=5                                        # Request timeout in seconds
)
```

## License Types

| Type | Description |
|------|-------------|
| `unlimited` | Never expires, unlimited devices |
| `trial` | Expires after X days (e.g., 14 days) |
| `limited` | Expires on specific date, limited devices |

## Exceptions

```python
from licensify import (
    LicenseException,           # Base exception
    InvalidLicenseKeyException, # Invalid license key
    LicenseExpiredException,    # License has expired
    DeviceCountExceededException, # Too many devices
    NetworkException,           # Network error
    CacheExpiredException       # Cache expired, offline not possible
)
```

## Requirements

- Python 3.8+
- `requests` library

## License

MIT License
