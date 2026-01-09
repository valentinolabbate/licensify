# Test Application für Licensify

Diese kleine Anwendung testet die Licensify Client Library.

## Setup

1. **Licensify installieren:**
   ```bash
   cd ../licensify
   pip install -e .
   ```

2. **Konfiguration anpassen:**
   
   Öffne `main.py` und passe an:
   ```python
   API_URL = "http://DEINE_SERVER_IP:8000"
   LICENSE_KEY = "DEIN_LICENSE_KEY_HIER"
   ```

3. **Test starten:**
   ```bash
   python main.py
   ```

## Erwartete Ausgabe

```
==================================================
  LICENSIFY TEST APPLICATION
==================================================

API URL: http://your-server:8000
License Key: CfatTyCG...
App Version: 1.0.0

[INFO] Validator erstellt
[INFO] Device ID: abc123...

--------------------------------------------------
SCHNELLE VALIDIERUNG (is_valid)
--------------------------------------------------
[✓] Lizenz ist GÜLTIG!

--------------------------------------------------
DETAILLIERTE VALIDIERUNG (validate)
--------------------------------------------------

[✓] Validierung erfolgreich!
    Lizenz-Typ:      trial
    Läuft ab:        2026-01-13T16:26:10
    Tage übrig:      5
    Max Devices:     1
    Aktive Devices:  1
    Cache gültig bis:2026-01-09T16:30:00
```

## Offline-Test

Um den Offline-Modus zu testen:
1. Führe das Programm einmal mit Internetverbindung aus (Cache wird erstellt)
2. Trenne die Internetverbindung oder stoppe den Server
3. Führe das Programm erneut aus - es sollte den Cache verwenden
