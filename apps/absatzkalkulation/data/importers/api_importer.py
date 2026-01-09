"""
API Importer - Importiert Daten von REST APIs
Benötigt das data_api Feature in der Lizenz
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None


class APIEndpoint:
    """Repräsentiert einen gespeicherten API-Endpoint"""
    
    def __init__(
        self,
        name: str,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        body: Optional[Dict] = None,
        data_path: Optional[str] = None,  # JSON-Pfad zu den Daten, z.B. "results.items"
        description: str = ""
    ):
        self.name = name
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.params = params or {}
        self.body = body
        self.data_path = data_path
        self.description = description
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "method": self.method,
            "headers": self.headers,
            "params": self.params,
            "body": self.body,
            "data_path": self.data_path,
            "description": self.description,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "APIEndpoint":
        endpoint = cls(
            name=data.get("name", ""),
            url=data.get("url", ""),
            method=data.get("method", "GET"),
            headers=data.get("headers"),
            params=data.get("params"),
            body=data.get("body"),
            data_path=data.get("data_path"),
            description=data.get("description", "")
        )
        endpoint.created_at = data.get("created_at", datetime.now().isoformat())
        return endpoint


class APIImporter:
    """
    Importiert Daten von REST APIs.
    Benötigt das data_api Feature in der Lizenz.
    """
    
    REQUIRED_FEATURE = "data_api"
    
    def __init__(self, config_dir: Path, license_manager=None):
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests nicht installiert: pip install requests")
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas nicht installiert: pip install pandas")
        
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.endpoints_file = self.config_dir / "api_endpoints.json"
        self.license_manager = license_manager
        self._endpoints: Dict[str, APIEndpoint] = {}
        self._load_endpoints()
    
    def _load_endpoints(self):
        """Lädt gespeicherte API-Endpoints"""
        if self.endpoints_file.exists():
            try:
                with open(self.endpoints_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._endpoints = {
                        name: APIEndpoint.from_dict(ep) 
                        for name, ep in data.items()
                    }
            except Exception as e:
                print(f"Fehler beim Laden der Endpoints: {e}")
    
    def _save_endpoints(self):
        """Speichert API-Endpoints"""
        data = {name: ep.to_dict() for name, ep in self._endpoints.items()}
        with open(self.endpoints_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def check_feature_access(self) -> Dict[str, Any]:
        """
        Prüft ob das data_api Feature lizenziert ist.
        
        Returns:
            Dict mit has_access und message
        """
        if self.license_manager is None:
            return {
                "has_access": False,
                "message": "Lizenz-Manager nicht verfügbar"
            }
        
        # Prüfe Validator
        validator = self.license_manager._validator
        if validator is None:
            return {
                "has_access": False,
                "message": "Keine aktive Lizenz"
            }
        
        try:
            if validator.has_feature(self.REQUIRED_FEATURE):
                return {
                    "has_access": True,
                    "message": "API-Import ist freigeschaltet"
                }
            else:
                return {
                    "has_access": False,
                    "message": f"API-Import erfordert das Feature '{self.REQUIRED_FEATURE}'. Bitte kontaktieren Sie den Support."
                }
        except Exception as e:
            return {
                "has_access": False,
                "message": f"Fehler bei der Lizenzprüfung: {e}"
            }
    
    def get_endpoints(self) -> List[Dict[str, Any]]:
        """Gibt alle gespeicherten Endpoints zurück"""
        return [ep.to_dict() for ep in self._endpoints.values()]
    
    def save_endpoint(self, endpoint: APIEndpoint) -> Dict[str, Any]:
        """Speichert einen API-Endpoint"""
        self._endpoints[endpoint.name] = endpoint
        self._save_endpoints()
        return {
            "success": True,
            "message": f"Endpoint '{endpoint.name}' gespeichert"
        }
    
    def delete_endpoint(self, name: str) -> Dict[str, Any]:
        """Löscht einen API-Endpoint"""
        if name in self._endpoints:
            del self._endpoints[name]
            self._save_endpoints()
            return {"success": True, "message": f"Endpoint '{name}' gelöscht"}
        return {"success": False, "message": f"Endpoint '{name}' nicht gefunden"}
    
    def test_endpoint(self, endpoint: APIEndpoint) -> Dict[str, Any]:
        """
        Testet einen API-Endpoint ohne die Daten zu importieren.
        """
        # Prüfe Lizenz
        access = self.check_feature_access()
        if not access["has_access"]:
            return {
                "success": False,
                "error": access["message"]
            }
        
        try:
            response = self._make_request(endpoint)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
            
            # Versuche JSON zu parsen
            try:
                data = response.json()
                
                # Extrahiere Daten aus Pfad
                if endpoint.data_path:
                    data = self._extract_data(data, endpoint.data_path)
                
                if isinstance(data, list):
                    return {
                        "success": True,
                        "status_code": 200,
                        "row_count": len(data),
                        "sample": data[:3] if len(data) > 3 else data
                    }
                else:
                    return {
                        "success": True,
                        "status_code": 200,
                        "data_type": type(data).__name__,
                        "message": "Daten gefunden, aber nicht als Liste erkannt"
                    }
                    
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "status_code": 200,
                    "error": "Antwort ist kein gültiges JSON"
                }
                
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Verbindungsfehler: {e}"
            }
    
    def fetch_data(self, endpoint: APIEndpoint) -> Dict[str, Any]:
        """
        Ruft Daten von einem API-Endpoint ab.
        
        Returns:
            Dict mit success, dataframe, row_count, etc.
        """
        # Prüfe Lizenz
        access = self.check_feature_access()
        if not access["has_access"]:
            return {
                "success": False,
                "error": access["message"]
            }
        
        try:
            response = self._make_request(endpoint)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
            
            data = response.json()
            
            # Extrahiere Daten aus Pfad
            if endpoint.data_path:
                data = self._extract_data(data, endpoint.data_path)
            
            # Konvertiere zu DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                return {
                    "success": False,
                    "error": "Daten können nicht in DataFrame konvertiert werden"
                }
            
            return {
                "success": True,
                "dataframe": df,
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns)
            }
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Verbindungsfehler: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _make_request(self, endpoint: APIEndpoint) -> requests.Response:
        """Führt die HTTP-Anfrage aus"""
        if endpoint.method == "GET":
            return requests.get(
                endpoint.url,
                headers=endpoint.headers,
                params=endpoint.params,
                timeout=30
            )
        elif endpoint.method == "POST":
            return requests.post(
                endpoint.url,
                headers=endpoint.headers,
                params=endpoint.params,
                json=endpoint.body,
                timeout=30
            )
        else:
            raise ValueError(f"Methode {endpoint.method} nicht unterstützt")
    
    def _extract_data(self, data: Any, path: str) -> Any:
        """
        Extrahiert Daten aus verschachteltem JSON.
        
        path: z.B. "results.items" oder "data.records"
        """
        parts = path.split(".")
        result = data
        
        for part in parts:
            if isinstance(result, dict):
                result = result.get(part)
            elif isinstance(result, list) and part.isdigit():
                result = result[int(part)]
            else:
                return data
        
        return result
