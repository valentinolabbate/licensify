"""
Landing Page - Hauptseite der App
"""
import customtkinter as ctk
from ..theme import theme, SPACING, RADIUS
from ..components import Card, PrimaryButton, SecondaryButton, HeadingLabel, BodyLabel, InfoCard


class LandingPage(ctk.CTkFrame):
    """Hauptseite mit Willkommen und Übersicht"""
    
    def __init__(self, master, on_navigate=None, license_info=None):
        super().__init__(master, fg_color="transparent")
        self.on_navigate = on_navigate
        self.license_info = license_info or {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Erstellt die UI-Elemente"""
        # Grid konfigurieren
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header
        self.create_header()
        
        # Quick Stats
        self.create_stats()
        
        # Quick Actions
        self.create_actions()
    
    def create_header(self):
        """Header mit Willkommensnachricht"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=SPACING["xl"], pady=(SPACING["xl"], SPACING["lg"]))
        
        # Titel
        title = HeadingLabel(header_frame, text="Willkommen zur Absatzkalkulation", size="heading_xl")
        title.pack(anchor="w")
        
        # Untertitel
        subtitle = BodyLabel(
            header_frame, 
            text="Berechnen Sie Ihre Absätze schnell und präzise",
            muted=True
        )
        subtitle.pack(anchor="w", pady=(SPACING["xs"], 0))
    
    def create_stats(self):
        """Quick Stats Karten"""
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", padx=SPACING["xl"], pady=SPACING["md"])
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="stats")
        
        # Lizenz-Status
        license_status = self.license_info.get("status", "Nicht aktiviert")
        status_icon = "✅" if license_status == "active" else "⚠️"
        status_text = "Aktiv" if license_status == "active" else "Nicht aktiviert"
        
        InfoCard(
            stats_frame, 
            title="Lizenzstatus", 
            value=status_text, 
            icon=status_icon
        ).grid(row=0, column=0, sticky="ew", padx=(0, SPACING["sm"]))
        
        # Tage verbleibend
        days = self.license_info.get("days_remaining", "—")
        days_text = f"{days} Tage" if isinstance(days, int) else days
        
        InfoCard(
            stats_frame, 
            title="Verbleibend", 
            value=days_text, 
            icon="📅"
        ).grid(row=0, column=1, sticky="ew", padx=SPACING["sm"])
        
        # Geräte
        devices = self.license_info.get("current_devices", 0)
        max_devices = self.license_info.get("max_devices", 1)
        max_text = "∞" if max_devices == 0 else str(max_devices)
        
        InfoCard(
            stats_frame, 
            title="Geräte", 
            value=f"{devices} / {max_text}", 
            icon="💻"
        ).grid(row=0, column=2, sticky="ew", padx=(SPACING["sm"], 0))
    
    def create_actions(self):
        """Quick Action Buttons"""
        actions_frame = Card(self)
        actions_frame.grid(row=2, column=0, sticky="new", padx=SPACING["xl"], pady=SPACING["md"])
        
        # Titel
        HeadingLabel(
            actions_frame, 
            text="Schnellaktionen", 
            size="heading_md"
        ).pack(anchor="w", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["sm"]))
        
        BodyLabel(
            actions_frame,
            text="Starten Sie eine neue Kalkulation oder verwalten Sie Ihre Lizenz",
            muted=True
        ).pack(anchor="w", padx=SPACING["lg"], pady=(0, SPACING["md"]))
        
        # Buttons
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["lg"]))
        
        PrimaryButton(
            buttons_frame,
            text="🧮  Neue Kalkulation",
            command=lambda: self.on_navigate("calculator") if self.on_navigate else None
        ).pack(side="left", padx=(0, SPACING["sm"]))
        
        SecondaryButton(
            buttons_frame,
            text="🔑  Lizenz verwalten",
            command=lambda: self.on_navigate("license") if self.on_navigate else None
        ).pack(side="left", padx=SPACING["sm"])
        
        SecondaryButton(
            buttons_frame,
            text="⚙️  Einstellungen",
            command=lambda: self.on_navigate("settings") if self.on_navigate else None
        ).pack(side="left", padx=SPACING["sm"])
    
    def update_license_info(self, license_info: dict):
        """Aktualisiert die Lizenz-Informationen"""
        self.license_info = license_info
        # Stats neu aufbauen
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()
