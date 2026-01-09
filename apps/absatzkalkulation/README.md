# Absatzkalkulation

Eine moderne Desktop-App für Absatzkalkulationen mit integrierter Lizenzverwaltung.

## 🚀 Features

- **Moderne UI**: CustomTkinter mit Dark/Light Theme
- **Lizenzverwaltung**: Integration mit licensify für Lizenz-Aktivierung
- **Exportierbar**: Als .exe für Windows exportierbar

## 📦 Installation

### Entwicklungsumgebung

1. Virtuelle Umgebung erstellen:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

3. App starten:
```bash
python main.py
```

### Als .exe exportieren

```bash
python build.py
```

Die fertige `.exe` befindet sich dann unter `dist/Absatzkalkulation.exe`.

## 🔑 Lizenzverwaltung

Die App verwendet das [licensify](https://github.com/valentinolabbate/licensify) Client-Paket zur Kommunikation mit dem Lizenz-Server.

### Konfiguration

Die Server-URL und der Produkt-Slug werden in `config.py` konfiguriert:

```python
LICENSE_SERVER_URL = "https://license.example.com"
PRODUCT_SLUG = "absatzkalkulation"
```

## 📁 Projektstruktur

```
absatzkalkulation/
├── main.py              # App-Einstiegspunkt
├── config.py            # Konfiguration
├── build.py             # PyInstaller Build-Skript
├── requirements.txt     # Python-Abhängigkeiten
├── assets/              # Icons, Bilder
├── ui/
│   ├── theme.py         # Theme-System (Dark/Light)
│   ├── components/      # Wiederverwendbare UI-Komponenten
│   │   └── widgets.py   # Buttons, Cards, Labels, etc.
│   └── pages/           # App-Seiten
│       ├── landing_page.py
│       ├── license_page.py
│       └── settings_page.py
└── utils/
    └── license_manager.py  # Lizenz-Logik
```

## 🎨 Theme-System

Die App unterstützt Dark und Light Mode. Das Theme kann in den Einstellungen gewechselt werden.

### Farben

Das Theme-System in `ui/theme.py` definiert konsistente Farben:
- `bg_primary`, `bg_secondary`, `bg_card` - Hintergrundfarben
- `accent`, `accent_hover` - Akzentfarben
- `success`, `warning`, `error` - Status-Farben
- `text_primary`, `text_secondary`, `text_muted` - Textfarben

## 🛠️ Entwicklung

### Neue Seite hinzufügen

1. Neue Datei in `ui/pages/` erstellen
2. Von `ctk.CTkFrame` erben
3. In `ui/pages/__init__.py` exportieren
4. In `main.py` in der `show_page()` Methode registrieren

### Neue Komponente hinzufügen

1. In `ui/components/widgets.py` die Komponente erstellen
2. In `ui/components/__init__.py` exportieren

## 📄 Lizenz

MIT License

## 👤 Autor

Valentino Labbate
