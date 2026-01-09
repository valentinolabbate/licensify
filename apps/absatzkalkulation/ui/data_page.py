"""
Data Page - Datenimport und -verwaltung UI
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional, Callable

from data.data_manager import get_data_manager


class DataPage(ctk.CTkFrame):
    """Hauptseite für Datenimport und -verwaltung"""
    
    def __init__(self, parent, license_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.license_manager = license_manager
        self.data_manager = get_data_manager(license_manager)
        
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_tabs()
        self._update_status()
    
    def _create_header(self):
        """Header mit Titel und Status"""
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(1, weight=1)
        
        # Titel
        ctk.CTkLabel(
            header,
            text="📊 Datenmanagement",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Status-Bereich
        self.status_frame = ctk.CTkFrame(header)
        self.status_frame.grid(row=0, column=1, padx=20, pady=10, sticky="e")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Lade Status...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10)
        
        # Refresh Button
        ctk.CTkButton(
            self.status_frame,
            text="🔄",
            width=30,
            command=self._update_status
        ).pack(side="left", padx=5)
    
    def _create_tabs(self):
        """Tab-View für verschiedene Import-Optionen"""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Tabs erstellen
        tab_import = self.tabview.add("📁 Datei Import")
        tab_api = self.tabview.add("🌐 API Import")
        tab_data = self.tabview.add("📋 Daten-Übersicht")
        tab_schema = self.tabview.add("📝 Schema")
        
        # Tab-Inhalte
        self._create_file_import_tab(tab_import)
        self._create_api_import_tab(tab_api)
        self._create_data_overview_tab(tab_data)
        self._create_schema_tab(tab_schema)
    
    def _create_file_import_tab(self, parent):
        """Tab für CSV/Excel Import"""
        parent.grid_columnconfigure(0, weight=1)
        
        # Import-Bereich
        import_frame = ctk.CTkFrame(parent)
        import_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        import_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            import_frame,
            text="Datei importieren",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=3, padx=15, pady=10, sticky="w")
        
        # Datei-Auswahl
        ctk.CTkLabel(import_frame, text="Datei:").grid(
            row=1, column=0, padx=15, pady=10, sticky="w"
        )
        
        self.file_path_var = ctk.StringVar()
        self.file_entry = ctk.CTkEntry(
            import_frame,
            textvariable=self.file_path_var,
            placeholder_text="Pfad zur CSV/Excel Datei...",
            width=400
        )
        self.file_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        ctk.CTkButton(
            import_frame,
            text="📂 Durchsuchen",
            width=120,
            command=self._browse_file
        ).grid(row=1, column=2, padx=15, pady=10)
        
        # Optionen
        options_frame = ctk.CTkFrame(import_frame, fg_color="transparent")
        options_frame.grid(row=2, column=0, columnspan=3, padx=15, pady=10, sticky="w")
        
        self.append_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            options_frame,
            text="An bestehende Daten anhängen",
            variable=self.append_var
        ).pack(side="left", padx=10)
        
        self.create_schema_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Schema automatisch erstellen",
            variable=self.create_schema_var
        ).pack(side="left", padx=10)
        
        # Import Button
        ctk.CTkButton(
            import_frame,
            text="⬇️ Importieren",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._import_file
        ).grid(row=3, column=0, columnspan=3, padx=15, pady=20)
        
        # Vorschau-Bereich
        preview_frame = ctk.CTkFrame(parent)
        preview_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            preview_frame,
            text="Vorschau",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.file_preview_text = ctk.CTkTextbox(preview_frame, height=200)
        self.file_preview_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
    
    def _create_api_import_tab(self, parent):
        """Tab für API Import"""
        parent.grid_columnconfigure(0, weight=1)
        
        # Feature-Check Warnung
        self.api_warning_frame = ctk.CTkFrame(parent, fg_color="#4a2020")
        self.api_warning_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.api_warning_label = ctk.CTkLabel(
            self.api_warning_frame,
            text="⚠️ API-Import erfordert das Feature 'data_api' in Ihrer Lizenz",
            text_color="#ff8888"
        )
        self.api_warning_label.pack(padx=15, pady=10)
        
        # API Endpoint Verwaltung
        endpoint_frame = ctk.CTkFrame(parent)
        endpoint_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        endpoint_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            endpoint_frame,
            text="API Endpoints",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=4, padx=15, pady=10, sticky="w")
        
        # Endpoint-Liste
        self.endpoint_list = ctk.CTkScrollableFrame(endpoint_frame, height=150)
        self.endpoint_list.grid(row=1, column=0, columnspan=4, sticky="ew", padx=15, pady=5)
        
        # Neuer Endpoint
        ctk.CTkLabel(endpoint_frame, text="Name:").grid(row=2, column=0, padx=(15, 5), pady=10, sticky="w")
        self.endpoint_name_var = ctk.StringVar()
        ctk.CTkEntry(
            endpoint_frame,
            textvariable=self.endpoint_name_var,
            width=150
        ).grid(row=2, column=1, padx=5, pady=10, sticky="w")
        
        ctk.CTkLabel(endpoint_frame, text="URL:").grid(row=3, column=0, padx=(15, 5), pady=10, sticky="w")
        self.endpoint_url_var = ctk.StringVar()
        ctk.CTkEntry(
            endpoint_frame,
            textvariable=self.endpoint_url_var,
            width=400,
            placeholder_text="https://api.example.com/data"
        ).grid(row=3, column=1, columnspan=2, padx=5, pady=10, sticky="ew")
        
        ctk.CTkButton(
            endpoint_frame,
            text="➕ Hinzufügen",
            width=100,
            command=self._add_endpoint
        ).grid(row=3, column=3, padx=15, pady=10)
        
        # Import Button
        self.api_import_btn = ctk.CTkButton(
            parent,
            text="🌐 Von API importieren",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._import_from_api
        )
        self.api_import_btn.grid(row=2, column=0, padx=10, pady=20)
        
        # Status/Ergebnis
        self.api_result_label = ctk.CTkLabel(parent, text="")
        self.api_result_label.grid(row=3, column=0, padx=10, pady=5)
        
        self._update_api_access()
        self._load_endpoints()
    
    def _create_data_overview_tab(self, parent):
        """Tab für Daten-Übersicht"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # Info-Bereich
        info_frame = ctk.CTkFrame(parent)
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Statistik-Karten
        self.stat_cards = {}
        stats = [
            ("rows", "📊 Zeilen", "0"),
            ("columns", "📑 Spalten", "0"),
            ("size", "💾 Größe", "0 MB"),
            ("modified", "🕒 Geändert", "-")
        ]
        
        for i, (key, label, default) in enumerate(stats):
            card = ctk.CTkFrame(info_frame)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            
            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=12)
            ).pack(pady=(10, 5))
            
            value_label = ctk.CTkLabel(
                card,
                text=default,
                font=ctk.CTkFont(size=18, weight="bold")
            )
            value_label.pack(pady=(0, 10))
            self.stat_cards[key] = value_label
        
        # Aktionen
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.grid(row=0, column=0, sticky="e", padx=20, pady=10)
        
        ctk.CTkButton(
            info_frame,
            text="📥 Als CSV exportieren",
            width=150,
            command=self._export_csv
        ).grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        ctk.CTkButton(
            info_frame,
            text="🗑️ Alle Daten löschen",
            width=150,
            fg_color="#8B0000",
            hover_color="#A00000",
            command=self._clear_data
        ).grid(row=1, column=2, columnspan=2, padx=10, pady=10, sticky="e")
        
        # Daten-Tabelle
        table_frame = ctk.CTkFrame(parent)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            table_frame,
            text="Datenvorschau (erste 100 Zeilen)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.data_preview_text = ctk.CTkTextbox(table_frame)
        self.data_preview_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
    
    def _create_schema_tab(self, parent):
        """Tab für Schema-Verwaltung"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # Schema-Info
        info_frame = ctk.CTkFrame(parent)
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            info_frame,
            text="Aktuelles Schema",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=15, pady=10, sticky="w")
        
        self.schema_name_label = ctk.CTkLabel(
            info_frame,
            text="Kein Schema geladen",
            font=ctk.CTkFont(size=14)
        )
        self.schema_name_label.grid(row=1, column=0, columnspan=2, padx=15, pady=5, sticky="w")
        
        # Aktionen
        btn_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=10, sticky="w")
        
        ctk.CTkButton(
            btn_frame,
            text="📂 Schema laden",
            width=120,
            command=self._load_schema
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Schema exportieren",
            width=130,
            command=self._export_schema
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Schema löschen",
            width=120,
            fg_color="#8B0000",
            hover_color="#A00000",
            command=self._delete_schema
        ).pack(side="left", padx=5)
        
        # Schema-Anzeige
        schema_display = ctk.CTkFrame(parent)
        schema_display.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        schema_display.grid_columnconfigure(0, weight=1)
        schema_display.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            schema_display,
            text="Spalten-Definition",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.schema_text = ctk.CTkTextbox(schema_display)
        self.schema_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
    
    # ==================== Hilfsfunktionen ====================
    
    def _update_status(self):
        """Aktualisiert den Status-Bereich"""
        status = self.data_manager.get_status()
        
        if status["has_data"]:
            text = f"✅ {status['row_count']:,} Zeilen | {status['column_count']} Spalten | {status['file_size_mb']:.2f} MB"
        else:
            text = "📭 Keine Daten geladen"
        
        self.status_label.configure(text=text)
        
        # Statistik-Karten aktualisieren
        if hasattr(self, 'stat_cards'):
            self.stat_cards["rows"].configure(text=f"{status['row_count']:,}")
            self.stat_cards["columns"].configure(text=str(status['column_count']))
            self.stat_cards["size"].configure(text=f"{status['file_size_mb']:.2f} MB")
            if status['last_modified']:
                self.stat_cards["modified"].configure(text=status['last_modified'][:16])
        
        # Schema aktualisieren
        if hasattr(self, 'schema_name_label'):
            if status['has_schema']:
                self.schema_name_label.configure(
                    text=f"📝 {status['schema_name']} ({status['schema_columns']} Spalten)"
                )
                self._show_schema()
            else:
                self.schema_name_label.configure(text="❌ Kein Schema geladen")
                self.schema_text.delete("0.0", "end")
        
        # Daten-Vorschau aktualisieren
        self._update_data_preview()
    
    def _update_data_preview(self):
        """Aktualisiert die Daten-Vorschau"""
        if not hasattr(self, 'data_preview_text'):
            return
        
        preview = self.data_manager.get_data_preview(100)
        self.data_preview_text.delete("0.0", "end")
        
        if preview:
            # Einfache Tabellen-Darstellung
            if preview:
                headers = list(preview[0].keys())
                lines = [" | ".join(headers), "-" * 80]
                for row in preview[:50]:  # Max 50 Zeilen anzeigen
                    values = [str(row.get(h, ""))[:20] for h in headers]
                    lines.append(" | ".join(values))
                self.data_preview_text.insert("0.0", "\n".join(lines))
        else:
            self.data_preview_text.insert("0.0", "Keine Daten vorhanden")
    
    def _show_schema(self):
        """Zeigt das aktuelle Schema an"""
        schema = self.data_manager.schema_manager.current_schema
        if not schema:
            return
        
        self.schema_text.delete("0.0", "end")
        
        lines = [
            f"Schema: {schema.name}",
            f"Beschreibung: {schema.description or '-'}",
            f"Erstellt: {schema.created_at[:10] if schema.created_at else '-'}",
            "",
            "Spalten:",
            "-" * 60
        ]
        
        for col in schema.columns:
            required = "✓" if col.required else " "
            lines.append(f"  [{required}] {col.name}: {col.dtype}")
            if col.description:
                lines.append(f"      └─ {col.description}")
        
        self.schema_text.insert("0.0", "\n".join(lines))
    
    def _update_api_access(self):
        """Prüft und aktualisiert den API-Zugriffsstatus"""
        access = self.data_manager.api_importer.check_feature_access()
        
        if access["has_access"]:
            self.api_warning_frame.configure(fg_color="#204a20")
            self.api_warning_label.configure(
                text="✅ API-Import ist aktiviert",
                text_color="#88ff88"
            )
            self.api_import_btn.configure(state="normal")
        else:
            self.api_warning_frame.configure(fg_color="#4a2020")
            self.api_warning_label.configure(
                text=f"⚠️ {access['message']}",
                text_color="#ff8888"
            )
            self.api_import_btn.configure(state="disabled")
    
    def _load_endpoints(self):
        """Lädt und zeigt gespeicherte API-Endpoints"""
        # Alte Einträge entfernen
        for widget in self.endpoint_list.winfo_children():
            widget.destroy()
        
        endpoints = self.data_manager.api_importer.get_endpoints()
        
        if not endpoints:
            ctk.CTkLabel(
                self.endpoint_list,
                text="Keine Endpoints gespeichert",
                text_color="gray"
            ).pack(pady=10)
            return
        
        for ep in endpoints:
            ep_frame = ctk.CTkFrame(self.endpoint_list)
            ep_frame.pack(fill="x", padx=5, pady=2)
            
            # Radio für Auswahl
            ctk.CTkRadioButton(
                ep_frame,
                text=f"{ep['name']} ({ep['url'][:40]}...)" if len(ep['url']) > 40 else f"{ep['name']} ({ep['url']})",
                variable=self.endpoint_name_var,
                value=ep['name']
            ).pack(side="left", padx=10, pady=5)
            
            ctk.CTkButton(
                ep_frame,
                text="🗑️",
                width=30,
                fg_color="#8B0000",
                command=lambda n=ep['name']: self._delete_endpoint(n)
            ).pack(side="right", padx=5, pady=5)
    
    # ==================== Aktionen ====================
    
    def _browse_file(self):
        """Öffnet Datei-Dialog für CSV/Excel"""
        file_path = filedialog.askopenfilename(
            title="Datei auswählen",
            filetypes=[
                ("CSV Dateien", "*.csv"),
                ("Excel Dateien", "*.xlsx;*.xls"),
                ("Alle Dateien", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self._show_file_preview(Path(file_path))
    
    def _show_file_preview(self, file_path: Path):
        """Zeigt Vorschau der ausgewählten Datei"""
        self.file_preview_text.delete("0.0", "end")
        
        try:
            if file_path.suffix.lower() == '.csv':
                preview = self.data_manager.csv_importer.preview(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                preview = self.data_manager.excel_importer.preview(file_path)
            else:
                self.file_preview_text.insert("0.0", "Nicht unterstütztes Dateiformat")
                return
            
            if preview["success"]:
                lines = [
                    f"Spalten: {', '.join(preview['columns'])}",
                    f"Zeilen: {preview['row_count']}",
                    "",
                    "Vorschau:",
                    "-" * 60
                ]
                for row in preview["preview"]:
                    lines.append(str(row))
                self.file_preview_text.insert("0.0", "\n".join(lines))
            else:
                self.file_preview_text.insert("0.0", f"Fehler: {preview['error']}")
        except Exception as e:
            self.file_preview_text.insert("0.0", f"Fehler beim Laden: {str(e)}")
    
    def _import_file(self):
        """Importiert die ausgewählte Datei"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("Warnung", "Bitte wählen Sie eine Datei aus")
            return
        
        path = Path(file_path)
        if not path.exists():
            messagebox.showerror("Fehler", "Datei nicht gefunden")
            return
        
        append = self.append_var.get()
        create_schema = self.create_schema_var.get()
        
        try:
            if path.suffix.lower() == '.csv':
                result = self.data_manager.import_csv(path, append=append, create_schema=create_schema)
            elif path.suffix.lower() in ['.xlsx', '.xls']:
                result = self.data_manager.import_excel(path, append=append, create_schema=create_schema)
            else:
                messagebox.showerror("Fehler", "Nicht unterstütztes Dateiformat")
                return
            
            if result["success"]:
                messagebox.showinfo("Erfolg", result["message"])
                self._update_status()
            else:
                messagebox.showerror("Fehler", result.get("error", "Unbekannter Fehler"))
        except Exception as e:
            messagebox.showerror("Fehler", f"Import fehlgeschlagen: {str(e)}")
    
    def _add_endpoint(self):
        """Fügt einen neuen API-Endpoint hinzu"""
        name = self.endpoint_name_var.get().strip()
        url = self.endpoint_url_var.get().strip()
        
        if not name or not url:
            messagebox.showwarning("Warnung", "Name und URL sind erforderlich")
            return
        
        from data.importers.api_importer import APIEndpoint
        endpoint = APIEndpoint(name=name, url=url)
        
        self.data_manager.api_importer.save_endpoint(endpoint)
        self.endpoint_name_var.set("")
        self.endpoint_url_var.set("")
        self._load_endpoints()
        messagebox.showinfo("Erfolg", f"Endpoint '{name}' gespeichert")
    
    def _delete_endpoint(self, name: str):
        """Löscht einen API-Endpoint"""
        if messagebox.askyesno("Bestätigen", f"Endpoint '{name}' löschen?"):
            self.data_manager.api_importer.delete_endpoint(name)
            self._load_endpoints()
    
    def _import_from_api(self):
        """Importiert Daten von einem API-Endpoint"""
        endpoint_name = self.endpoint_name_var.get()
        if not endpoint_name:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Endpoint aus")
            return
        
        self.api_result_label.configure(text="⏳ Importiere...")
        self.update_idletasks()
        
        try:
            result = self.data_manager.import_from_api(endpoint_name)
            
            if result["success"]:
                self.api_result_label.configure(text=f"✅ {result['message']}")
                self._update_status()
            else:
                self.api_result_label.configure(text=f"❌ {result.get('error', 'Fehler')}")
        except Exception as e:
            self.api_result_label.configure(text=f"❌ {str(e)}")
    
    def _export_csv(self):
        """Exportiert Daten als CSV"""
        file_path = filedialog.asksaveasfilename(
            title="CSV exportieren",
            defaultextension=".csv",
            filetypes=[("CSV Dateien", "*.csv")]
        )
        if file_path:
            result = self.data_manager.parquet_store.export_to_csv(Path(file_path))
            if result["success"]:
                messagebox.showinfo("Erfolg", result["message"])
            else:
                messagebox.showerror("Fehler", result.get("error", "Export fehlgeschlagen"))
    
    def _clear_data(self):
        """Löscht alle Daten"""
        if messagebox.askyesno(
            "Bestätigen",
            "Alle Daten und das Schema werden unwiderruflich gelöscht!\n\nFortfahren?"
        ):
            result = self.data_manager.clear_all_data()
            if result["success"]:
                messagebox.showinfo("Erfolg", result["message"])
                self._update_status()
            else:
                messagebox.showerror("Fehler", result.get("error"))
    
    def _load_schema(self):
        """Lädt ein Schema aus einer JSON-Datei"""
        file_path = filedialog.askopenfilename(
            title="Schema laden",
            filetypes=[("JSON Dateien", "*.json")]
        )
        if file_path:
            try:
                schema = self.data_manager.schema_manager.load_schema(Path(file_path))
                if schema:
                    messagebox.showinfo("Erfolg", f"Schema '{schema.name}' geladen")
                    self._update_status()
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden: {str(e)}")
    
    def _export_schema(self):
        """Exportiert das aktuelle Schema"""
        if not self.data_manager.schema_manager.has_schema():
            messagebox.showwarning("Warnung", "Kein Schema zum Exportieren vorhanden")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Schema exportieren",
            defaultextension=".json",
            filetypes=[("JSON Dateien", "*.json")]
        )
        if file_path:
            result = self.data_manager.schema_manager.export_schema(Path(file_path))
            if result["success"]:
                messagebox.showinfo("Erfolg", "Schema exportiert")
            else:
                messagebox.showerror("Fehler", result.get("error"))
    
    def _delete_schema(self):
        """Löscht das aktuelle Schema"""
        if messagebox.askyesno("Bestätigen", "Schema löschen?"):
            self.data_manager.schema_manager.delete_schema()
            self._update_status()
            messagebox.showinfo("Erfolg", "Schema gelöscht")
