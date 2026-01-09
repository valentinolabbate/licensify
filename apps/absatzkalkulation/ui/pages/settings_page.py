"""
Settings Page - Einstellungen
"""
import customtkinter as ctk
from ..theme import theme, SPACING, RADIUS
from ..components import Card, PrimaryButton, SecondaryButton, HeadingLabel, BodyLabel


class SettingsPage(ctk.CTkFrame):
    """Einstellungsseite"""
    
    def __init__(self, master, current_theme="dark", on_theme_change=None, on_clear_cache=None):
        super().__init__(master, fg_color="transparent")
        self.current_theme = current_theme
        self.on_theme_change = on_theme_change
        self.on_clear_cache = on_clear_cache
        
        self.setup_ui()
    
    def setup_ui(self):
        """Erstellt die UI"""
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.create_header()
        
        # Erscheinungsbild
        self.create_appearance_card()
        
        # App-Informationen
        self.create_about_card()
        
        # Cache
        self.create_cache_card()
    
    def create_header(self):
        """Header"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=SPACING["xl"], pady=(SPACING["xl"], SPACING["lg"]))
        
        HeadingLabel(header, text="Einstellungen", size="heading_xl").pack(anchor="w")
        BodyLabel(header, text="Passen Sie die App nach Ihren Wünschen an", muted=True).pack(anchor="w")
    
    def create_appearance_card(self):
        """Erscheinungsbild-Einstellungen"""
        card = Card(self)
        card.grid(row=1, column=0, sticky="ew", padx=SPACING["xl"], pady=SPACING["sm"])
        
        HeadingLabel(card, text="Erscheinungsbild", size="heading_md").pack(
            anchor="w", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["sm"])
        )
        BodyLabel(card, text="Wählen Sie zwischen hellem und dunklem Design", muted=True).pack(
            anchor="w", padx=SPACING["lg"]
        )
        
        # Theme Toggle
        toggle_frame = ctk.CTkFrame(card, fg_color="transparent")
        toggle_frame.pack(fill="x", padx=SPACING["lg"], pady=SPACING["lg"])
        
        BodyLabel(toggle_frame, text="Design-Modus").pack(side="left")
        
        self.theme_var = ctk.StringVar(value=self.current_theme)
        theme_menu = ctk.CTkOptionMenu(
            toggle_frame,
            values=["dark", "light"],
            variable=self.theme_var,
            command=self._handle_theme_change,
            fg_color=theme.get_color("accent"),
            button_color=theme.get_color("accent_hover"),
            button_hover_color=theme.get_color("primary"),
            dropdown_fg_color=theme.get_color("bg_card"),
            dropdown_hover_color=theme.get_color("bg_hover"),
            corner_radius=RADIUS["md"]
        )
        theme_menu.pack(side="right")
    
    def create_about_card(self):
        """App-Informationen"""
        from config import APP_NAME, APP_VERSION, APP_AUTHOR
        
        card = Card(self)
        card.grid(row=2, column=0, sticky="ew", padx=SPACING["xl"], pady=SPACING["sm"])
        
        HeadingLabel(card, text="Über die App", size="heading_md").pack(
            anchor="w", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["md"])
        )
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["lg"]))
        
        infos = [
            ("App", APP_NAME),
            ("Version", APP_VERSION),
            ("Entwickler", APP_AUTHOR),
        ]
        
        for label, value in infos:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", pady=SPACING["xs"])
            
            BodyLabel(row, text=label, muted=True).pack(side="left")
            ctk.CTkLabel(
                row,
                text=value,
                font=theme.get_font("body"),
                text_color=theme.get_color("text_primary")
            ).pack(side="right")
    
    def create_cache_card(self):
        """Cache-Verwaltung"""
        card = Card(self)
        card.grid(row=3, column=0, sticky="ew", padx=SPACING["xl"], pady=SPACING["sm"])
        
        HeadingLabel(card, text="Cache & Daten", size="heading_md").pack(
            anchor="w", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["sm"])
        )
        BodyLabel(
            card, 
            text="Löschen Sie temporäre Daten und Cache-Dateien", 
            muted=True
        ).pack(anchor="w", padx=SPACING["lg"])
        
        SecondaryButton(
            card,
            text="🗑️  Cache leeren",
            command=self.on_clear_cache
        ).pack(anchor="w", padx=SPACING["lg"], pady=SPACING["lg"])
    
    def _handle_theme_change(self, new_theme: str):
        """Handler für Theme-Änderung"""
        if self.on_theme_change:
            self.on_theme_change(new_theme)
