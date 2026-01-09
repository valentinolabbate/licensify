"""
Data Manager - Zentrale Datenverwaltung
Koordiniert Schema, Storage und Importer
"""
from pathlib import Path
from typing import Dict, Any, Optional, List

from config import CONFIG_DIR

from .schema_manager import SchemaManager, DataSchema
from .parquet_store import ParquetStore
from .importers import CSVImporter, ExcelImporter, APIImporter


class DataManager:
    """
    Zentrale Klasse für die Datenverwaltung.
    Koordiniert Schema-Validierung, Speicherung und Import.
    """
    
    def __init__(self, data_dir: Optional[Path] = None, license_manager=None):
        self.data_dir = data_dir or (CONFIG_DIR / "data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Manager initialisieren
        self.schema_manager = SchemaManager(self.data_dir / "schemas")
        self.parquet_store = ParquetStore(self.data_dir / "store")
        
        # Importer
        self._csv_importer = None
        self._excel_importer = None
        self._api_importer = None
        self._license_manager = license_manager
    
    @property
    def csv_importer(self) -> CSVImporter:
        if self._csv_importer is None:
            self._csv_importer = CSVImporter()
        return self._csv_importer
    
    @property
    def excel_importer(self) -> ExcelImporter:
        if self._excel_importer is None:
            self._excel_importer = ExcelImporter()
        return self._excel_importer
    
    @property
    def api_importer(self) -> APIImporter:
        if self._api_importer is None:
            self._api_importer = APIImporter(
                CONFIG_DIR, 
                license_manager=self._license_manager
            )
        return self._api_importer
    
    def get_status(self) -> Dict[str, Any]:
        """Gibt den Status des Datenspeichers zurück"""
        store_info = self.parquet_store.get_info()
        schema = self.schema_manager.current_schema
        
        return {
            "has_data": store_info.get("has_data", False),
            "row_count": store_info.get("row_count", 0),
            "column_count": store_info.get("column_count", 0),
            "file_size_mb": store_info.get("file_size_mb", 0),
            "has_schema": self.schema_manager.has_schema(),
            "schema_name": schema.name if schema else None,
            "schema_columns": len(schema.columns) if schema else 0,
            "last_modified": store_info.get("last_modified")
        }
    
    def import_csv(
        self, 
        file_path: Path, 
        append: bool = False,
        create_schema: bool = True
    ) -> Dict[str, Any]:
        """
        Importiert Daten aus einer CSV-Datei.
        
        Args:
            file_path: Pfad zur CSV-Datei
            append: An bestehende Daten anhängen
            create_schema: Schema erstellen wenn nicht vorhanden
        
        Returns:
            Dict mit success, message, row_count, etc.
        """
        # Vorschau laden
        preview = self.csv_importer.preview(file_path)
        if not preview["success"]:
            return preview
        
        # Spalten validieren
        if self.schema_manager.has_schema():
            validation = self.schema_manager.validate_columns(preview["columns"])
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["message"],
                    "missing_columns": validation.get("missing", [])
                }
        
        # Daten laden
        result = self.csv_importer.load(file_path)
        if not result["success"]:
            return result
        
        df = result["dataframe"]
        
        # Schema erstellen wenn nötig
        if create_schema and not self.schema_manager.has_schema():
            schema = self.schema_manager.create_schema_from_dataframe(
                df, 
                name="imported_data",
                description=f"Importiert aus {file_path.name}"
            )
            self.schema_manager.save_schema(schema)
        
        # Spalten auf Schema beschränken wenn vorhanden
        if self.schema_manager.has_schema():
            schema_columns = self.schema_manager.current_schema.get_column_names()
            df = df[[c for c in df.columns if c in schema_columns]]
        
        # Speichern
        save_result = self.parquet_store.save_dataframe(df, append=append)
        
        if save_result["success"]:
            return {
                "success": True,
                "message": f"Import erfolgreich: {save_result['rows_added']} Zeilen hinzugefügt",
                "rows_added": save_result["rows_added"],
                "total_rows": save_result["total_rows"],
                "file_size_mb": save_result["file_size_mb"]
            }
        else:
            return save_result
    
    def import_excel(
        self,
        file_path: Path,
        sheet_name: Optional[str] = None,
        append: bool = False,
        create_schema: bool = True
    ) -> Dict[str, Any]:
        """
        Importiert Daten aus einer Excel-Datei.
        """
        # Vorschau laden
        preview = self.excel_importer.preview(file_path, sheet_name=sheet_name)
        if not preview["success"]:
            return preview
        
        # Spalten validieren
        if self.schema_manager.has_schema():
            validation = self.schema_manager.validate_columns(preview["columns"])
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["message"],
                    "missing_columns": validation.get("missing", [])
                }
        
        # Daten laden
        result = self.excel_importer.load(file_path, sheet_name=sheet_name)
        if not result["success"]:
            return result
        
        df = result["dataframe"]
        
        # Schema erstellen wenn nötig
        if create_schema and not self.schema_manager.has_schema():
            schema = self.schema_manager.create_schema_from_dataframe(
                df,
                name="imported_data",
                description=f"Importiert aus {file_path.name}"
            )
            self.schema_manager.save_schema(schema)
        
        # Spalten auf Schema beschränken
        if self.schema_manager.has_schema():
            schema_columns = self.schema_manager.current_schema.get_column_names()
            df = df[[c for c in df.columns if c in schema_columns]]
        
        # Speichern
        save_result = self.parquet_store.save_dataframe(df, append=append)
        
        if save_result["success"]:
            return {
                "success": True,
                "message": f"Import erfolgreich: {save_result['rows_added']} Zeilen hinzugefügt",
                "rows_added": save_result["rows_added"],
                "total_rows": save_result["total_rows"],
                "file_size_mb": save_result["file_size_mb"]
            }
        else:
            return save_result
    
    def import_from_api(
        self,
        endpoint_name: str,
        append: bool = True,
        create_schema: bool = True
    ) -> Dict[str, Any]:
        """
        Importiert Daten von einem gespeicherten API-Endpoint.
        """
        # Endpoint finden
        endpoints = {ep["name"]: ep for ep in self.api_importer.get_endpoints()}
        if endpoint_name not in endpoints:
            return {
                "success": False,
                "error": f"Endpoint '{endpoint_name}' nicht gefunden"
            }
        
        from .importers.api_importer import APIEndpoint
        endpoint = APIEndpoint.from_dict(endpoints[endpoint_name])
        
        # Daten abrufen
        result = self.api_importer.fetch_data(endpoint)
        if not result["success"]:
            return result
        
        df = result["dataframe"]
        
        # Spalten validieren
        if self.schema_manager.has_schema():
            validation = self.schema_manager.validate_columns(list(df.columns))
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["message"],
                    "missing_columns": validation.get("missing", [])
                }
        
        # Schema erstellen wenn nötig
        if create_schema and not self.schema_manager.has_schema():
            schema = self.schema_manager.create_schema_from_dataframe(
                df,
                name="api_data",
                description=f"Importiert von API: {endpoint.name}"
            )
            self.schema_manager.save_schema(schema)
        
        # Spalten auf Schema beschränken
        if self.schema_manager.has_schema():
            schema_columns = self.schema_manager.current_schema.get_column_names()
            df = df[[c for c in df.columns if c in schema_columns]]
        
        # Speichern
        save_result = self.parquet_store.save_dataframe(df, append=append)
        
        if save_result["success"]:
            return {
                "success": True,
                "message": f"API-Import erfolgreich: {save_result['rows_added']} Zeilen hinzugefügt",
                "rows_added": save_result["rows_added"],
                "total_rows": save_result["total_rows"],
                "file_size_mb": save_result["file_size_mb"]
            }
        else:
            return save_result
    
    def get_data_preview(self, n_rows: int = 100) -> Optional[List[Dict]]:
        """Gibt eine Vorschau der gespeicherten Daten zurück"""
        df = self.parquet_store.load_sample(n_rows)
        if df is None:
            return None
        return df.to_dict(orient="records")
    
    def clear_all_data(self) -> Dict[str, Any]:
        """Löscht alle Daten und das Schema"""
        try:
            self.parquet_store.delete_data()
            self.schema_manager.delete_schema()
            return {
                "success": True,
                "message": "Alle Daten wurden gelöscht"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Lazy-loaded Singleton
_data_manager: Optional[DataManager] = None

def get_data_manager(license_manager=None) -> DataManager:
    """Gibt die DataManager-Instanz zurück"""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager(license_manager=license_manager)
    return _data_manager

# Für einfachen Import
data_manager = None  # Wird in main.py initialisiert
