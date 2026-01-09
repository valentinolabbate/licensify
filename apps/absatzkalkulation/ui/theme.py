"""
Absatzkalkulation - Theme Konfiguration
Modernes Dark/Light Theme für CustomTkinter
"""

# Farbpalette
COLORS = {
    "dark": {
        "bg_primary": "#1a1a2e",
        "bg_secondary": "#16213e",
        "bg_card": "#202040",
        "bg_hover": "#2a2a4a",
        "accent": "#0f3460",
        "accent_hover": "#1a4a7a",
        "primary": "#e94560",
        "primary_hover": "#ff6b6b",
        "success": "#00d9a5",
        "warning": "#ffc107",
        "error": "#ff4757",
        "text_primary": "#ffffff",
        "text_secondary": "#a0a0b0",
        "text_muted": "#6c6c7c",
        "border": "#2a2a4a",
    },
    "light": {
        "bg_primary": "#f5f5f5",
        "bg_secondary": "#ffffff",
        "bg_card": "#ffffff",
        "bg_hover": "#e8e8e8",
        "accent": "#e3e3e3",
        "accent_hover": "#d0d0d0",
        "primary": "#e94560",
        "primary_hover": "#d63050",
        "success": "#00b894",
        "warning": "#fdcb6e",
        "error": "#d63031",
        "text_primary": "#2d3436",
        "text_secondary": "#636e72",
        "text_muted": "#b2bec3",
        "border": "#dfe6e9",
    }
}

# Typography
FONTS = {
    "heading_xl": ("Segoe UI", 32, "bold"),
    "heading_lg": ("Segoe UI", 24, "bold"),
    "heading_md": ("Segoe UI", 18, "bold"),
    "heading_sm": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 12),
    "body_sm": ("Segoe UI", 11),
    "caption": ("Segoe UI", 10),
    "mono": ("Consolas", 11),
}

# Spacing
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "xxl": 48,
}

# Border Radius
RADIUS = {
    "sm": 4,
    "md": 8,
    "lg": 12,
    "xl": 16,
    "full": 9999,
}


class Theme:
    """Theme Manager für die App"""
    
    def __init__(self, mode: str = "dark"):
        self.mode = mode
        self.colors = COLORS[mode]
        self.fonts = FONTS
        self.spacing = SPACING
        self.radius = RADIUS
    
    def toggle(self):
        """Wechselt zwischen Dark und Light Mode"""
        self.mode = "light" if self.mode == "dark" else "dark"
        self.colors = COLORS[self.mode]
        return self.mode
    
    def set_mode(self, mode: str):
        """Setzt den Theme Mode"""
        if mode in COLORS:
            self.mode = mode
            self.colors = COLORS[mode]
    
    def get_color(self, name: str) -> str:
        """Holt eine Farbe aus dem aktuellen Theme"""
        return self.colors.get(name, "#ffffff")
    
    def get_font(self, name: str) -> tuple:
        """Holt eine Font-Definition"""
        return self.fonts.get(name, self.fonts["body"])


# Globale Theme-Instanz
theme = Theme("dark")
