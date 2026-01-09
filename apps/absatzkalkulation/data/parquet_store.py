"""
Parquet Store - Effizienter Datenspeicher für große Datenmengen
Verwendet Apache Parquet für optimale KI-Daten-Performance
"""
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False
    pd = None
    pa = None
    pq = None


class ParquetStore:
    """
    Verwaltet Parquet-Dateien für effiziente Datenspeicherung.
    Unterstützt partitionierte Speicherung für sehr große Datenmengen.
    """
    
    def __init__(self, data_dir: Path):
        if not PARQUET_AVAILABLE:
            raise ImportError(
                "Parquet-Unterstützung nicht verfügbar. "
                "Bitte installieren Sie: pip install pandas pyarrow"
            )
        
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def main_file(self) -> Path:
        """Hauptdatendatei"""
        return self.data_dir / "data.parquet"
    
    @property
    def metadata_file(self) -> Path:
        """Metadaten-Datei"""
        return self.data_dir / "metadata.json"
    
    def has_data(self) -> bool:
        """Prüft ob Daten vorhanden sind"""
        return self.main_file.exists()
    
    def get_row_count(self) -> int:
        """Gibt die Anzahl der Zeilen zurück"""
        if not self.has_data():
            return 0
        
        try:
            pf = pq.ParquetFile(self.main_file)
            return pf.metadata.num_rows
        except Exception:
            return 0
    
    def get_info(self) -> Dict[str, Any]:
        """Gibt Informationen über die gespeicherten Daten zurück"""
        if not self.has_data():
            return {
                "has_data": False,
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "file_size_mb": 0,
                "last_modified": None
            }
        
        try:
            pf = pq.ParquetFile(self.main_file)
            schema = pf.schema_arrow
            file_size = self.main_file.stat().st_size / (1024 * 1024)
            last_modified = datetime.fromtimestamp(self.main_file.stat().st_mtime)
            
            return {
                "has_data": True,
                "row_count": pf.metadata.num_rows,
                "column_count": len(schema),
                "columns": [{"name": f.name, "type": str(f.type)} for f in schema],
                "file_size_mb": round(file_size, 2),
                "last_modified": last_modified.isoformat()
            }
        except Exception as e:
            return {
                "has_data": True,
                "error": str(e)
            }
    
    def save_dataframe(self, df: pd.DataFrame, append: bool = False) -> Dict[str, Any]:
        """
        Speichert einen DataFrame als Parquet.
        
        Args:
            df: Pandas DataFrame
            append: True = an bestehende Daten anhängen, False = ersetzen
        
        Returns:
            Dict mit Statistiken
        """
        rows_before = self.get_row_count() if append else 0
        
        try:
            if append and self.has_data():
                # Bestehende Daten laden und zusammenführen
                existing_df = pd.read_parquet(self.main_file)
                df = pd.concat([existing_df, df], ignore_index=True)
            
            # Als Parquet speichern mit Kompression
            df.to_parquet(
                self.main_file,
                engine='pyarrow',
                compression='snappy',
                index=False
            )
            
            rows_after = self.get_row_count()
            
            return {
                "success": True,
                "rows_added": rows_after - rows_before,
                "total_rows": rows_after,
                "file_size_mb": round(self.main_file.stat().st_size / (1024 * 1024), 2)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_dataframe(
        self, 
        columns: Optional[List[str]] = None,
        filters: Optional[List] = None,
        limit: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """
        Lädt Daten als DataFrame.
        
        Args:
            columns: Nur diese Spalten laden (Performance-Optimierung)
            filters: PyArrow Filter für Zeilen
            limit: Maximale Anzahl Zeilen
        
        Returns:
            Pandas DataFrame oder None
        """
        if not self.has_data():
            return None
        
        try:
            df = pd.read_parquet(
                self.main_file,
                columns=columns,
                filters=filters,
                engine='pyarrow'
            )
            
            if limit:
                df = df.head(limit)
            
            return df
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return None
    
    def load_sample(self, n: int = 100) -> Optional[pd.DataFrame]:
        """Lädt eine Stichprobe der Daten"""
        return self.load_dataframe(limit=n)
    
    def get_column_stats(self, column: str) -> Dict[str, Any]:
        """Berechnet Statistiken für eine Spalte"""
        df = self.load_dataframe(columns=[column])
        if df is None:
            return {}
        
        col = df[column]
        stats = {
            "count": len(col),
            "null_count": col.isna().sum(),
            "unique_count": col.nunique()
        }
        
        if pd.api.types.is_numeric_dtype(col):
            stats.update({
                "min": float(col.min()) if not pd.isna(col.min()) else None,
                "max": float(col.max()) if not pd.isna(col.max()) else None,
                "mean": float(col.mean()) if not pd.isna(col.mean()) else None,
                "std": float(col.std()) if not pd.isna(col.std()) else None,
            })
        
        return stats
    
    def delete_data(self):
        """Löscht alle Daten"""
        if self.main_file.exists():
            self.main_file.unlink()
        if self.metadata_file.exists():
            self.metadata_file.unlink()
    
    def export_to_csv(self, output_path: Path, **kwargs) -> bool:
        """Exportiert Daten als CSV"""
        df = self.load_dataframe()
        if df is None:
            return False
        
        try:
            df.to_csv(output_path, index=False, **kwargs)
            return True
        except Exception as e:
            print(f"Export-Fehler: {e}")
            return False
