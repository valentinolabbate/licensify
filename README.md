# 🔐 AuthLib - Lizenzmanagement-System

Ein vollständiges Lizenzmanagement-System mit Backend-API, Web-Frontend und Desktop-Anwendungen.

## 📁 Projektstruktur

```
AuthLib/
├── backend/          # FastAPI Backend-Server
├── frontend/         # React Web-Frontend
├── licensify/        # Python Lizenz-Client-Bibliothek
├── apps/             # Desktop-Anwendungen
│   └── absatzkalkulation/  # Beispiel-App mit CustomTkinter
└── test-app/         # Test-Anwendung
```

## 🚀 Komponenten

### Backend (FastAPI)

Das Backend stellt eine REST-API für die Lizenzverwaltung bereit.

**Features:**
- Produkt- und Lizenzverwaltung
- Feature-basierte Lizenzierung
- Hardware-ID Binding
- Aktivierungslimits
- Admin-Dashboard API

**Starten:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**API-Dokumentation:** `http://localhost:8000/docs`

---

### Frontend (React)

Modernes Web-Dashboard zur Verwaltung von Produkten und Lizenzen.

**Features:**
- Produkt-Management (CRUD)
- Lizenz-Erstellung und -Verwaltung
- Feature-Toggle pro Lizenz
- Benutzer-Aktivierungen einsehen
- Responsive Design

**Starten:**
```bash
cd frontend
npm install
npm run dev
```

---

### Licensify (Python Client)

Python-Bibliothek zur Integration der Lizenzprüfung in Desktop-Anwendungen.

**Installation:**
```bash
pip install git+https://github.com/valentinolabbate/licensify.git
```

**Verwendung:**
```python
from licensify import LicenseValidator

validator = LicenseValidator(
    api_url="https://api.example.com",
    product_slug="mein-produkt"
)

# Lizenz aktivieren
result = validator.activate("XXXX-XXXX-XXXX-XXXX")

# Lizenz validieren
if validator.validate():
    print("Lizenz gültig!")
    
# Feature prüfen
if validator.has_feature("premium"):
    print("Premium-Feature verfügbar")
```

---

### Absatzkalkulation (Desktop-App)

Eine Beispiel-Desktop-Anwendung mit CustomTkinter und integrierter Lizenzverwaltung.

**Features:**
- Moderne CustomTkinter UI
- Lizenzaktivierung/-deaktivierung
- Datenmanagement-System:
  - CSV/Excel Import
  - API Import (lizenzgesteuert)
  - Parquet-Speicherung für große Datenmengen
  - Schema-Validierung

**Starten:**
```bash
cd apps/absatzkalkulation
pip install -r requirements.txt
python main.py
```

**Als EXE bauen:**
```bash
python build.py
```

---

## 🔧 Konfiguration

### Backend (.env)
```env
DATABASE_URL=sqlite:///./licenses.db
SECRET_KEY=your-secret-key
ADMIN_PASSWORD=your-admin-password
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

### Desktop-Apps
Die Konfiguration erfolgt in `config.py`:
```python
API_URL = "http://161.97.158.215"
PRODUCT_SLUG = "absatzkalkulation"
```

---

## 📋 API-Endpunkte

### Produkte
| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/v1/products` | Alle Produkte |
| POST | `/api/v1/products` | Produkt erstellen |
| GET | `/api/v1/products/{id}` | Produkt abrufen |
| PUT | `/api/v1/products/{id}` | Produkt aktualisieren |
| DELETE | `/api/v1/products/{id}` | Produkt löschen |

### Lizenzen
| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/v1/licenses` | Alle Lizenzen |
| POST | `/api/v1/licenses` | Lizenz erstellen |
| POST | `/api/v1/licenses/activate` | Lizenz aktivieren |
| POST | `/api/v1/licenses/deactivate` | Lizenz deaktivieren |
| POST | `/api/v1/licenses/validate` | Lizenz validieren |
| PATCH | `/api/v1/licenses/{id}/features` | Feature umschalten |

### Features
| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| GET | `/api/v1/products/{id}/features` | Features eines Produkts |
| POST | `/api/v1/products/{id}/features` | Feature hinzufügen |
| PUT | `/api/v1/products/{id}/features/{slug}` | Feature aktualisieren |
| DELETE | `/api/v1/products/{id}/features/{slug}` | Feature löschen |

---

## 🔒 Lizenz-Features

Features können pro Produkt definiert und pro Lizenz aktiviert/deaktiviert werden:

```json
{
  "slug": "data_api",
  "name": "API-Datenimport",
  "description": "Ermöglicht den Import von Daten über externe APIs"
}
```

In der Desktop-App:
```python
if license_manager.has_feature("data_api"):
    # API-Import erlauben
    api_importer.fetch_data(endpoint)
```

---

## 📦 Technologie-Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite/PostgreSQL
- Pydantic

### Frontend
- React 18
- Vite
- Tailwind CSS
- Axios

### Desktop
- Python 3.11+
- CustomTkinter
- Pandas
- PyArrow (Parquet)
- Requests

---

## 🛠️ Entwicklung

### Voraussetzungen
- Python 3.11+
- Node.js 18+
- Git

### Lokale Entwicklung
```bash
# Backend starten
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend starten (neues Terminal)
cd frontend
npm install
npm run dev

# Desktop-App testen
cd apps/absatzkalkulation
pip install -r requirements.txt
python main.py
```

---

## 📝 Lizenz

Dieses Projekt ist proprietär. Alle Rechte vorbehalten.

---

## 👤 Autor

Valentino Labbate

---

## 🤝 Support

Bei Fragen oder Problemen erstellen Sie bitte ein Issue oder kontaktieren Sie den Support.
