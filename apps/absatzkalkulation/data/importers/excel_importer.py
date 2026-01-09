"""
Excel Importer - Importiert Daten aus Excel-Dateien (.xlsx, .xls)
"""
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class ExcelImporter:
    """Importiert Daten aus Excel-Dateien"""
    
    def __init__(self):
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas nicht installiert: pip install pandas")
        if not OPENPYXL_AVAILABLE:
            raise ImportError("openpyxl nicht installiert: pip install openpyxl")
    
    def get_sheet_names(self, file_path: Path) -> Dict[str, Any]:
        """Gibt alle Tabellenblätter in der Excel-Datei zurück"""
        try:
            xl = pd.ExcelFile(file_path, engine='openpyxl')
            return {
                "success": True,
                "sheets": xl.sheet_names,
                "sheet_count": len(xl.sheet_names)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def preview(
        self,
        file_path: Path,
        sheet_name: Optional[str] = None,
        n_rows: int = 10
    ) -> Dict[str, Any]:
        """
        Lädt eine Vorschau der Excel-Datei.
        
        Args:
            file_path: Pfad zur Excel-Datei
            sheet_name: Name des Tabellenblatts (None = erstes Blatt)
            n_rows: Anzahl Vorschau-Zeilen
        
        Returns:
            Dict mit columns, data, total_rows, etc.
        """
        try:
            # Sheet-Namen abrufen
            xl = pd.ExcelFile(file_path, engine='openpyxl')
            sheet = sheet_name or xl.sheet_names[0]
            
            # Vorschau laden
            df = pd.read_excel(
                file_path,
                sheet_name=sheet,
                nrows=n_rows,
                engine='openpyxl'
            )
            
            # Gesamte Zeilenanzahl
            df_full = pd.read_excel(file_path, sheet_name=sheet, engine='openpyxl')
            total_rows = len(df_full)
            
            return {
                "success": True,
                "sheet_name": sheet,
                "available_sheets": xl.sheet_names,
                "columns": list(df.columns),
                "dtypes": {col: str(df[col].dtype) for col in df.columns},
                "preview_data": df.to_dict(orient="records"),
                "preview_rows": len(df),
                "total_rows": total_rows,
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
        sheet_name: Optional[str] = None,
        columns: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Lädt die gesamte Excel-Datei oder ein Tabellenblatt.
        
        Args:
            file_path: Pfad zur Excel-Datei
            sheet_name: Name des Tabellenblatts (None = erstes Blatt)
            columns: Nur diese Spalten laden (None = alle)
            **kwargs: Weitere pandas read_excel Parameter
        
        Returns:
            Dict mit success, dataframe, row_count, etc.
        """
        try:
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name or 0,
                usecols=columns,
                engine='openpyxl',
                **kwargs
            )
            
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
        sheet_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validiert ob die Excel-Datei die erforderlichen Spalten enthält.
        """
        preview = self.preview(file_path, sheet_name=sheet_name, n_rows=1)
        
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
