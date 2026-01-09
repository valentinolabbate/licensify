"""
Absatzkalkulation - Konfiguration
"""

# App Info
APP_NAME = "Absatzkalkulation"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Valentino Labbate"

# License Server
LICENSE_SERVER_URL = "https://labbdata.de"  # Anpassen an deine Domain
PRODUCT_SLUG = "absatzkalkulation"

# Paths
import os
from pathlib import Path

APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = APP_DIR / "assets"
CONFIG_DIR = Path.home() / ".absatzkalkulation"
LICENSE_FILE = CONFIG_DIR / "license.key"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

# Window
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700

# Theme
DEFAULT_THEME = "dark"  # "dark" oder "light"

# License Files
LICENSE_KEY_FILE = CONFIG_DIR / "license.key"
DEVICE_ID_FILE = CONFIG_DIR / "device.id"
