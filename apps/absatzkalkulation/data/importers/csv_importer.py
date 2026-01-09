"""
CSV Importer - Importiert Daten aus CSV-Dateien
"""
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None


class CSVImporter:
    """Importiert Daten aus CSV-Dateien"""
    
    def __init__(self):
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas nicht installiert: pip install pandas")
    
    def preview(
        self, 
        file_path: Path, 
        n_rows: int = 10,
        encoding: str = "utf-8",
        delimiter: str = ","
    ) -> Dict[str, Any]:
        """
        Lädt eine Vorschau der CSV-Datei.
        
        Returns:
            Dict mit columns, data, total_rows, etc.
        """
        try:
            # Versuche zuerst Encoding zu erkennen
            encodings = [encoding, "utf-8", "latin-1", "cp1252"]
            df = None
            used_encoding = encoding
            
            for enc in encodings:
                try:
                    df = pd.read_csv(
                        file_path, 
                        nrows=n_rows, 
                        encoding=enc,
                        delimiter=delimiter
                    )
                    used_encoding = enc
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                return {
                    "success": False,
                    "error": "Konnte Datei-Encoding nicht erkennen"
                }
            
            # Gesamte Zeilenanzahl zählen
            with open(file_path, 'r', encoding=used_encoding) as f:
                total_rows = sum(1 for _ in f) - 1  # Minus Header
            
            return {
                "success": True,
                "columns": list(df.columns),
                "dtypes": {col: str(df[col].dtype) for col in df.columns},
                "preview_data": df.to_dict(orient="records"),
                "preview_rows": len(df),
                "total_rows": total_rows,
                "encoding": used_encoding,
                "file_size_mb": round(file_path.stat().st_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def load(
        self,
        file_path: Path,
        columns: Optional[List[str]] = None,
        encoding: str = "utf-8",
        delimiter: str = ",",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Lädt die gesamte CSV-Datei.
        
        Args:
            file_path: Pfad zur CSV
            columns: Nur diese Spalten laden (None = alle)
            encoding: Datei-Encoding
            delimiter: Spalten-Trenner
            **kwargs: Weitere pandas read_csv Parameter
        
        Returns:
            Dict mit success, dataframe, row_count, etc.
        """
        try:
            # Encoding-Erkennung
            encodings = [encoding, "utf-8", "latin-1", "cp1252"]
            df = None
            
            for enc in encodings:
                try:
                    df = pd.read_csv(
                        file_path,
                        encoding=enc,
                        delimiter=delimiter,
                        usecols=columns,
                        **kwargs
                    )
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                return {
                    "success": False,
                    "error": "Konnte Datei-Encoding nicht erkennen"
                }
            
            return {
                "success": True,
                "dataframe": df,
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_columns(
        self,
        file_path: Path,
        required_columns: List[str],
        encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """
        Validiert ob die CSV die erforderlichen Spalten enthält.
        """
        preview = self.preview(file_path, n_rows=1, encoding=encoding)
        
        if not preview["success"]:
            return preview
        
        file_columns = set(preview["columns"])
        required = set(required_columns)
        
        missing = required - file_columns
        extra = file_columns - required
        
        return {
            "success": len(missing) == 0,
            "valid": len(missing) == 0,
            "missing_columns": list(missing),
            "extra_columns": list(extra),
            "message": f"Fehlende Spalten: {', '.join(missing)}" if missing else "Alle Spalten vorhanden"
        }
