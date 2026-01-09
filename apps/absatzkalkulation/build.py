"""
Build-Skript für die Absatzkalkulation App
Erstellt eine ausführbare .exe mit PyInstaller
"""
import subprocess
import sys
import shutil
from pathlib import Path


# Konfiguration
APP_NAME = "Absatzkalkulation"
MAIN_SCRIPT = "main.py"
ICON_PATH = "assets/icon.ico"  # Falls vorhanden
BUILD_DIR = Path("build")
DIST_DIR = Path("dist")


def clean():
    """Entfernt alte Build-Dateien"""
    print("Räume alte Build-Dateien auf...")
    
    for path in [BUILD_DIR, DIST_DIR]:
        if path.exists():
            shutil.rmtree(path)
            print(f"   Gelöscht: {path}")
    
    # .spec Dateien entfernen
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"   Gelöscht: {spec_file}")


def build():
    """Erstellt die .exe"""
    print(f"\nBaue {APP_NAME}...")
    
    # PyInstaller Argumente
    args = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        # CustomTkinter Daten einbinden
        "--collect-data", "customtkinter",
        # Hidden imports
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "licensify",
    ]
    
    # Icon hinzufügen falls vorhanden
    icon = Path(ICON_PATH)
    if icon.exists():
        args.extend(["--icon", str(icon)])
        print(f"   Icon: {icon}")
    else:
        print(f"   Kein Icon gefunden ({icon})")
    
    # Assets-Ordner hinzufügen
    assets_dir = Path("assets")
    if assets_dir.exists():
        args.extend(["--add-data", f"{assets_dir};assets"])
    
    # Hauptskript
    args.append(MAIN_SCRIPT)
    
    print(f"   Führe aus: {' '.join(args[2:8])}...")
    
    # Build starten
    result = subprocess.run(args, capture_output=False)
    
    if result.returncode == 0:
        exe_path = DIST_DIR / f"{APP_NAME}.exe"
        print(f"\n✅ Build erfolgreich!")
        print(f"   Ausgabe: {exe_path.absolute()}")
        return True
    else:
        print(f"\nBuild fehlgeschlagen!")
        return False


def main():
    """Hauptfunktion"""
    print("=" * 50)
    print(f"  {APP_NAME} Build-Tool")
    print("=" * 50)
    
    # Prüfe ob PyInstaller installiert ist
    try:
        import PyInstaller
        print(f"\n✓ PyInstaller v{PyInstaller.__version__} gefunden")
    except ImportError:
        print("\nPyInstaller nicht installiert!")
        print("   Installiere mit: pip install pyinstaller")
        sys.exit(1)
    
    # Prüfe ob main.py existiert
    if not Path(MAIN_SCRIPT).exists():
        print(f"\n{MAIN_SCRIPT} nicht gefunden!")
        sys.exit(1)
    
    # Aufräumen und bauen
    clean()
    success = build()
    
    if success:
        print("\n" + "=" * 50)
        print("  Build abgeschlossen!")
        print("=" * 50)
        print(f"\nSie finden die .exe unter: dist/{APP_NAME}.exe")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
