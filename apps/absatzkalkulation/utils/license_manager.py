"""
Utils - Lizenz-Verwaltung
"""
import json
import hashlib
import platform
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

from config import (
    LICENSE_SERVER_URL, 
    PRODUCT_SLUG, 
    LICENSE_KEY_FILE, 
    DEVICE_ID_FILE,
    CONFIG_DIR,
    APP_VERSION
)


class LicenseManager:
    """Verwaltet die Lizenz-Aktivierung und -Validierung"""
    
    def __init__(self):
        self.server_url = LICENSE_SERVER_URL
        self.product_slug = PRODUCT_SLUG
        self._license_info: Optional[Dict[str, Any]] = None
        self._validator = None
        self._licensify_available = False
        
        # Config-Verzeichnis erstellen
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Versuche licensify zu importieren
        try:
            from licensify import LicenseValidator
            self._licensify_available = True
            
            # Validator nur erstellen wenn ein Key gespeichert ist
            stored_key = self.stored_license_key
            if stored_key:
                self._validator = LicenseValidator(
                    api_url=self.server_url,
                    license_key=stored_key,
                    app_version=APP_VERSION,
                    cache_dir=str(CONFIG_DIR)
                )
        except ImportError:
            print("Warnung: licensify Bibliothek nicht gefunden")
    
    @property
    def device_id(self) -> str:
        """Gibt die eindeutige Geräte-ID zurück"""
        if self._validator:
            return self._validator.get_device_id()
        
        # Fallback: eigene Generierung
        if self._licensify_available:
            from licensify import generate_device_id
            return generate_device_id()
        
        # Manueller Fallback
        system_info = f"{platform.node()}-{platform.machine()}-{uuid.getnode()}"
        return hashlib.sha256(system_info.encode()).hexdigest()[:32]
    
    @property
    def stored_license_key(self) -> Optional[str]:
        """Gibt den gespeicherten Lizenzschlüssel zurück"""
        if LICENSE_KEY_FILE.exists():
            return LICENSE_KEY_FILE.read_text().strip()
        return None
    
    def save_license_key(self, key: str):
        """Speichert den Lizenzschlüssel"""
        LICENSE_KEY_FILE.write_text(key)
    
    def clear_license_key(self):
        """Löscht den gespeicherten Lizenzschlüssel"""
        if LICENSE_KEY_FILE.exists():
            LICENSE_KEY_FILE.unlink()
        self._license_info = None
        self._validator = None
    
    def _create_validator(self, license_key: str):
        """Erstellt einen neuen Validator"""
        if not self._licensify_available:
            return None
        
        from licensify import LicenseValidator
        return LicenseValidator(
            api_url=self.server_url,
            license_key=license_key,
            app_version=APP_VERSION,
            cache_dir=str(CONFIG_DIR)
        )
    
    def activate(self, license_key: str) -> Dict[str, Any]:
        """
        Aktiviert die Lizenz auf diesem Gerät
        
        Returns:
            Dict mit 'success', 'message' und optional 'license_info'
        """
        if not self._licensify_available:
            return {
                "success": False,
                "message": "Lizenz-Client nicht verfügbar"
            }
        
        try:
            # Validator mit neuem Key erstellen
            validator = self._create_validator(license_key)
            
            # Validieren (aktiviert automatisch das Gerät beim ersten Mal)
            is_valid = validator.validate()
            
            if is_valid:
                self.save_license_key(license_key)
                self._validator = validator
                self._license_info = validator.get_license_info()
                return {
                    "success": True,
                    "message": "Lizenz erfolgreich aktiviert",
                    "license_info": self._format_license_info(self._license_info)
                }
            else:
                return {
                    "success": False,
                    "message": "Lizenzschlüssel ungültig"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Fehler bei der Aktivierung: {str(e)}"
            }
    
    def deactivate(self) -> Dict[str, Any]:
        """
        Deaktiviert die Lizenz auf diesem Gerät
        
        Returns:
            Dict mit 'success' und 'message'
        """
        license_key = self.stored_license_key
        if not license_key:
            return {
                "success": False,
                "message": "Keine aktive Lizenz gefunden"
            }
        
        try:
            # Cache leeren und lokale Daten entfernen
            if self._validator:
                self._validator.clear_cache()
            
            self.clear_license_key()
            return {
                "success": True,
                "message": "Lizenz erfolgreich deaktiviert"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Fehler bei der Deaktivierung: {str(e)}"
            }
    
    def validate(self) -> Dict[str, Any]:
        """
        Validiert die aktuelle Lizenz
        
        Returns:
            Dict mit 'valid', 'message' und optional 'license_info'
        """
        if not self._licensify_available:
            return {
                "valid": False,
                "message": "Lizenz-Client nicht verfügbar",
                "license_info": self._get_empty_info()
            }
        
        license_key = self.stored_license_key
        if not license_key:
            return {
                "valid": False,
                "message": "Keine Lizenz aktiviert",
                "license_info": self._get_empty_info()
            }
        
        try:
            # Validator erstellen falls nicht vorhanden
            if not self._validator:
                self._validator = self._create_validator(license_key)
            
            is_valid = self._validator.validate()
            
            if is_valid:
                self._license_info = self._validator.get_license_info()
                return {
                    "valid": True,
                    "message": "Lizenz ist gültig",
                    "license_info": self._format_license_info(self._license_info)
                }
            else:
                return {
                    "valid": False,
                    "message": "Lizenz ungültig oder abgelaufen",
                    "license_info": self._get_empty_info()
                }
        except Exception as e:
            return {
                "valid": False,
                "message": f"Fehler bei der Validierung: {str(e)}",
                "license_info": self._get_empty_info()
            }
    
    def get_license_info(self) -> Dict[str, Any]:
        """Gibt die aktuellen Lizenz-Informationen zurück"""
        if self._license_info:
            return self._format_license_info(self._license_info)
        
        # Versuche zu validieren
        result = self.validate()
        return result.get("license_info", self._get_empty_info())
    
    def _format_license_info(self, raw_info: Dict[str, Any]) -> Dict[str, Any]:
        """Formatiert die Lizenz-Informationen für die UI"""
        # Berechne verbleibende Tage
        days_remaining = raw_info.get("days_remaining")
        if days_remaining is None and raw_info.get("expires_at"):
            from datetime import datetime
            try:
                expires = datetime.fromisoformat(raw_info["expires_at"].replace("Z", "+00:00"))
                days_remaining = (expires - datetime.now(expires.tzinfo)).days
            except:
                pass
        
        return {
            "status": "active" if raw_info.get("valid", raw_info.get("is_active")) else "inactive",
            "key": self.stored_license_key or "",
            "license_type": raw_info.get("license_type", "unknown"),
            "expires_at": raw_info.get("expires_at"),
            "days_remaining": days_remaining,
            "current_devices": raw_info.get("current_devices", raw_info.get("device_count", 0)),
            "max_devices": raw_info.get("max_devices", 1),
            "features": raw_info.get("features", []),
            "product_name": raw_info.get("product_name", self.product_slug.replace("-", " ").title())
        }
    
    def _get_empty_info(self) -> Dict[str, Any]:
        """Gibt leere Lizenz-Informationen zurück"""
        return {
            "status": "inactive",
            "key": "",
            "license_type": "none",
            "expires_at": None,
            "days_remaining": None,
            "current_devices": 0,
            "max_devices": 0,
            "features": [],
            "product_name": self.product_slug.replace("-", " ").title()
        }


# Singleton-Instanz
license_manager = LicenseManager()
