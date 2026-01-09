"""
License Page - Lizenz-Verwaltung und Informationen
"""
import customtkinter as ctk
from ..theme import theme, SPACING, RADIUS
from ..components import (
    Card, PrimaryButton, SecondaryButton, 
    HeadingLabel, BodyLabel, StatusBadge, InfoCard
)


class LicensePage(ctk.CTkFrame):
    """Seite für Lizenz-Informationen und Verwaltung"""
    
    def __init__(self, master, license_info=None, on_activate=None, on_deactivate=None):
        super().__init__(master, fg_color="transparent")
        self.license_info = license_info or {}
        self.on_activate = on_activate
        self.on_deactivate = on_deactivate
        
        self.setup_ui()
    
    def setup_ui(self):
        """Erstellt die UI"""
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.create_header()
        
        # Lizenz-Status Card
        self.create_status_card()
        
        # Lizenz-Details
        self.create_details_card()
        
        # Features
        self.create_features_card()
        
        # Lizenzschlüssel eingeben
        self.create_activation_card()
    
    def create_header(self):
        """Header"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=SPACING["xl"], pady=(SPACING["xl"], SPACING["lg"]))
        
        HeadingLabel(header, text="Lizenz-Verwaltung", size="heading_xl").pack(anchor="w")
        BodyLabel(header, text="Verwalten Sie Ihre Lizenz und sehen Sie Details ein", muted=True).pack(anchor="w")
    
    def create_status_card(self):
        """Lizenz-Status Karte"""
        status = self.license_info.get("status", "inactive")
        is_active = status == "active"
        
        card = Card(self)
        card.grid(row=1, column=0, sticky="ew", padx=SPACING["xl"], pady=SPACING["sm"])
        
        # Header mit Status
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING["lg"], pady=SPACING["lg"])
        
        HeadingLabel(header_frame, text="Status", size="heading_md").pack(side="left")
        
        status_text = "Aktiv" if is_active else "Nicht aktiviert"
        badge_status = "success" if is_active else "warning"
        StatusBadge(header_frame, text=status_text, status=badge_status).pack(side="right")
        
        if is_active:
            # Lizenzschlüssel anzeigen (maskiert)
            key = self.license_info.get("key", "")
            masked_key = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else key
            
            key_frame = ctk.CTkFrame(card, fg_color=theme.get_color("bg_secondary"), corner_radius=RADIUS["md"])
            key_frame.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["lg"]))
            
            ctk.CTkLabel(
                key_frame,
                text=masked_key,
                font=theme.get_font("mono"),
                text_color=theme.get_color("text_secondary")
            ).pack(padx=SPACING["md"], pady=SPACING["sm"])
    
    def create_details_card(self):
        """Lizenz-Details"""
        card = Card(self)
        card.grid(row=2, column=0, sticky="ew", padx=SPACING["xl"], pady=SPACING["sm"])
        
        HeadingLabel(card, text="Details", size="heading_md").pack(anchor="w", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["md"]))
        
        # Details Grid
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["lg"]))
        details_frame.grid_columnconfigure((0, 1), weight=1)
        
        details = [
            ("Lizenztyp", self.license_info.get("license_type", "—").title()),
            ("Ablaufdatum", self.license_info.get("expires_at", "Unbegrenzt") or "Unbegrenzt"),
            ("Verbleibende Tage", f"{self.license_info.get('days_remaining', '∞')} Tage"),
            ("Geräte", f"{self.license_info.get('current_devices', 0)} / {self.license_info.get('max_devices', 1) or '∞'}"),
            ("Produkt", self.license_info.get("product_name", "Absatzkalkulation")),
        ]
        
        for i, (label, value) in enumerate(details):
            row = i // 2
            col = i % 2
            
            item_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            item_frame.grid(row=row, column=col, sticky="w", pady=SPACING["xs"])
            
            BodyLabel(item_frame, text=label, muted=True).pack(anchor="w")
            ctk.CTkLabel(
                item_frame,
                text=str(value),
                font=theme.get_font("heading_sm"),
                text_color=theme.get_color("text_primary")
            ).pack(anchor="w")
    
    def create_features_card(self):
        """Features der Lizenz"""
        card = Card(self)
        card.grid(row=3, column=0, sticky="ew", padx=SPACING["xl"], pady=SPACING["sm"])
        
        HeadingLabel(card, text="Enthaltene Features", size="heading_md").pack(
            anchor="w", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["md"])
        )
        
        features = self.license_info.get("features", [])
        if not features:
            features = ["Basis-Funktionen"]  # Standard wenn keine Features
        
        features_frame = ctk.CTkFrame(card, fg_color="transparent")
        features_frame.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["lg"]))
        
        for feature in features:
            feature_item = ctk.CTkFrame(features_frame, fg_color="transparent")
            feature_item.pack(fill="x", pady=SPACING["xs"])
            
            ctk.CTkLabel(
                feature_item,
                text="✓",
                font=theme.get_font("body"),
                text_color=theme.get_color("success")
            ).pack(side="left")
            
            BodyLabel(feature_item, text=f"  {feature}").pack(side="left")
    
    def create_activation_card(self):
        """Lizenz aktivieren/deaktivieren"""
        card = Card(self)
        card.grid(row=4, column=0, sticky="ew", padx=SPACING["xl"], pady=SPACING["sm"])
        
        status = self.license_info.get("status", "inactive")
        is_active = status == "active"
        
        if is_active:
            HeadingLabel(card, text="Lizenz deaktivieren", size="heading_md").pack(
                anchor="w", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["sm"])
            )
            BodyLabel(
                card,
                text="Deaktivieren Sie die Lizenz auf diesem Gerät, um sie auf einem anderen zu nutzen.",
                muted=True
            ).pack(anchor="w", padx=SPACING["lg"])
            
            SecondaryButton(
                card,
                text="Lizenz deaktivieren",
                command=self.on_deactivate
            ).pack(anchor="w", padx=SPACING["lg"], pady=SPACING["lg"])
        else:
            HeadingLabel(card, text="Lizenz aktivieren", size="heading_md").pack(
                anchor="w", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["sm"])
            )
            BodyLabel(
                card,
                text="Geben Sie Ihren Lizenzschlüssel ein, um die Software zu aktivieren.",
                muted=True
            ).pack(anchor="w", padx=SPACING["lg"])
            
            # Eingabefeld
            input_frame = ctk.CTkFrame(card, fg_color="transparent")
            input_frame.pack(fill="x", padx=SPACING["lg"], pady=SPACING["md"])
            
            self.license_entry = ctk.CTkEntry(
                input_frame,
                placeholder_text="XXXX-XXXX-XXXX-XXXX",
                font=theme.get_font("mono"),
                height=40,
                corner_radius=RADIUS["md"]
            )
            self.license_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING["sm"]))
            
            PrimaryButton(
                input_frame,
                text="Aktivieren",
                command=self._handle_activate
            ).pack(side="left")
    
    def _handle_activate(self):
        """Handler für Lizenz-Aktivierung"""
        if self.on_activate and hasattr(self, 'license_entry'):
            key = self.license_entry.get().strip()
            if key:
                self.on_activate(key)
    
    def update_license_info(self, license_info: dict):
        """Aktualisiert die Lizenz-Informationen"""
        self.license_info = license_info
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()
