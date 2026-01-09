"""
Schema Manager - Verwaltet das Daten-Schema (Spalten-Definitionen)
Speichert Schemas als JSON für Flexibilität
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ColumnDefinition:
    """Definition einer Datenspalte"""
    name: str
    dtype: str  # string, int64, float64, datetime, bool
    required: bool = True
    description: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "ColumnDefinition":
        return cls(**data)


@dataclass
class DataSchema:
    """Komplettes Daten-Schema"""
    name: str
    version: str
    columns: List[ColumnDefinition]
    created_at: str
    updated_at: str
    description: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "columns": [c.to_dict() for c in self.columns],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DataSchema":
        columns = [ColumnDefinition.from_dict(c) for c in data.get("columns", [])]
        return cls(
            name=data.get("name", "default"),
            version=data.get("version", "1.0"),
            description=data.get("description"),
            columns=columns,
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )
    
    def get_column_names(self) -> List[str]:
        """Gibt Liste der Spaltennamen zurück"""
        return [c.name for c in self.columns]
    
    def get_required_columns(self) -> List[str]:
        """Gibt Liste der erforderlichen Spalten zurück"""
        return [c.name for c in self.columns if c.required]


class SchemaManager:
    """Verwaltet Daten-Schemas"""
    
    def __init__(self, schema_dir: Path):
        self.schema_dir = schema_dir
        self.schema_dir.mkdir(parents=True, exist_ok=True)
        self._current_schema: Optional[DataSchema] = None
    
    @property
    def schema_file(self) -> Path:
        return self.schema_dir / "schema.json"
    
    @property
    def current_schema(self) -> Optional[DataSchema]:
        """Gibt das aktuelle Schema zurück"""
        if self._current_schema is None:
            self._current_schema = self.load_schema()
        return self._current_schema
    
    def has_schema(self) -> bool:
        """Prüft ob ein Schema existiert"""
        return self.schema_file.exists()
    
    def load_schema(self) -> Optional[DataSchema]:
        """Lädt das gespeicherte Schema"""
        if not self.schema_file.exists():
            return None
        
        try:
            with open(self.schema_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return DataSchema.from_dict(data)
        except Exception as e:
            print(f"Fehler beim Laden des Schemas: {e}")
            return None
    
    def save_schema(self, schema: DataSchema):
        """Speichert das Schema"""
        schema.updated_at = datetime.now().isoformat()
        
        with open(self.schema_file, "w", encoding="utf-8") as f:
            json.dump(schema.to_dict(), f, indent=2, ensure_ascii=False)
        
        self._current_schema = schema
    
    def create_schema_from_dataframe(self, df, name: str = "default", description: str = None) -> DataSchema:
        """Erstellt ein Schema aus einem Pandas DataFrame"""
        columns = []
        
        for col_name in df.columns:
            dtype = str(df[col_name].dtype)
            
            # Typ-Mapping
            if "int" in dtype:
                mapped_dtype = "int64"
            elif "float" in dtype:
                mapped_dtype = "float64"
            elif "datetime" in dtype:
                mapped_dtype = "datetime"
            elif "bool" in dtype:
                mapped_dtype = "bool"
            else:
                mapped_dtype = "string"
            
            columns.append(ColumnDefinition(
                name=col_name,
                dtype=mapped_dtype,
                required=True,
                description=None
            ))
        
        schema = DataSchema(
            name=name,
            version="1.0",
            description=description,
            columns=columns,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        
        return schema
    
    def validate_columns(self, column_names: List[str]) -> Dict[str, Any]:
        """
        Validiert Spalten gegen das aktuelle Schema.
        
        Returns:
            Dict mit:
            - valid: bool
            - missing: List[str] - fehlende erforderliche Spalten
            - extra: List[str] - zusätzliche Spalten
            - message: str
        """
        if not self.has_schema():
            return {
                "valid": True,
                "missing": [],
                "extra": [],
                "message": "Kein Schema vorhanden - Spalten werden übernommen"
            }
        
        schema = self.current_schema
        required_columns = set(schema.get_required_columns())
        provided_columns = set(column_names)
        
        missing = required_columns - provided_columns
        extra = provided_columns - set(schema.get_column_names())
        
        if missing:
            return {
                "valid": False,
                "missing": list(missing),
                "extra": list(extra),
                "message": f"Fehlende erforderliche Spalten: {', '.join(missing)}"
            }
        
        if extra:
            return {
                "valid": True,
                "missing": [],
                "extra": list(extra),
                "message": f"Zusätzliche Spalten werden ignoriert: {', '.join(extra)}"
            }
        
        return {
            "valid": True,
            "missing": [],
            "extra": [],
            "message": "Alle Spalten stimmen überein"
        }
    
    def delete_schema(self):
        """Löscht das aktuelle Schema"""
        if self.schema_file.exists():
            self.schema_file.unlink()
        self._current_schema = None
