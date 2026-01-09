"""
Test Application for Licensify Client
"""
import sys
import os

# Add licensify to path (for local development)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'licensify'))

from licensify import LicenseValidator
from licensify.exceptions import (
    LicenseException,
    InvalidLicenseKeyException,
    LicenseExpiredException,
    DeviceCountExceededException,
    DeviceBlockedException,
    NetworkException
)


def main():
    # ===== KONFIGURATION =====
    # Passe diese Werte an:
    API_URL = "http://161.97.158.215"  # oder mit nginx: "http://DEINE_SERVER_IP"
    LICENSE_KEY = "TwHPwaICcgyS2cmeGFhKhsrp4gqZeiLY"    # Aus dem Dashboard kopieren
    APP_VERSION = "1.0.0"
    
    print("=" * 50)
    print("  LICENSIFY TEST APPLICATION")
    print("=" * 50)
    print(f"\nAPI URL: {API_URL}")
    print(f"License Key: {LICENSE_KEY[:8]}..." if len(LICENSE_KEY) > 8 else f"License Key: {LICENSE_KEY}")
    print(f"App Version: {APP_VERSION}")
    print()
    
    # Validator erstellen
    try:
        validator = LicenseValidator(
            api_url=API_URL,
            license_key=LICENSE_KEY,
            app_version=APP_VERSION,
            cache_dir=".license_cache"  # Lokaler Cache-Ordner
        )
        
        print("[INFO] Validator erstellt")
        print(f"[INFO] Device ID: {validator.device_info.get('device_id', 'N/A')}")
        print()
        
    except Exception as e:
        print(f"[ERROR] Konnte Validator nicht erstellen: {e}")
        return
    
    # ===== SCHNELLE VALIDIERUNG =====
    print("-" * 50)
    print("SCHNELLE VALIDIERUNG (is_valid)")
    print("-" * 50)
    
    if validator.is_valid():
        print("[✓] Lizenz ist GÜLTIG!")
    else:
        print("[✗] Lizenz ist UNGÜLTIG!")
        return
    
    # ===== DETAILLIERTE VALIDIERUNG =====
    print()
    print("-" * 50)
    print("DETAILLIERTE VALIDIERUNG (validate)")
    print("-" * 50)
    
    try:
        result = validator.validate()
        
        print(f"\n[✓] Validierung erfolgreich!")
        print(f"    Lizenz-Typ:      {result.get('license_type', 'N/A')}")
        print(f"    Läuft ab:        {result.get('expires_at', 'Nie')}")
        print(f"    Tage übrig:      {result.get('days_remaining', '∞')}")
        print(f"    Max Devices:     {result.get('max_devices', '∞')}")
        print(f"    Aktive Devices:  {result.get('current_devices', 0)}")
        print(f"    Cache gültig bis:{result.get('cache_until', 'N/A')}")
        
        if result.get('features'):
            print(f"    Features:        {', '.join(result['features'])}")
            
    except LicenseExpiredException as e:
        print(f"[✗] Lizenz abgelaufen: {e}")
    except InvalidLicenseKeyException as e:
        print(f"[✗] Lizenz ungültig: {e}")
    except DeviceCountExceededException as e:
        print(f"[✗] Gerätelimit erreicht: {e}")
    except DeviceBlockedException as e:
        print(f"[✗] Gerät blockiert: {e}")
    except NetworkException as e:
        print(f"[!] Netzwerkfehler (Offline-Modus wird verwendet): {e}")
    except LicenseException as e:
        print(f"[✗] Lizenzfehler: {e}")
    
    # ===== CACHE INFO =====
    print()
    print("-" * 50)
    print("CACHE STATUS")
    print("-" * 50)
    
    cache_info = validator.get_cache_info()
    if cache_info:
        print(f"    Cache vorhanden: Ja")
        print(f"    Erstellt:        {cache_info.get('cached_at', 'N/A')}")
        print(f"    Gültig bis:      {cache_info.get('valid_until', 'N/A')}")
    else:
        print(f"    Cache vorhanden: Nein")
    
    print()
    print("=" * 50)
    print("  TEST ABGESCHLOSSEN")
    print("=" * 50)


if __name__ == "__main__":
    main()
