"""
Wiederverwendbare UI-Komponenten
"""
import customtkinter as ctk
from ..theme import theme, SPACING, RADIUS


class Card(ctk.CTkFrame):
    """Moderne Card-Komponente"""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=theme.get_color("bg_card"),
            corner_radius=RADIUS["lg"],
            border_width=1,
            border_color=theme.get_color("border"),
            **kwargs
        )


class PrimaryButton(ctk.CTkButton):
    """Primärer Action-Button"""
    
    def __init__(self, master, text: str, **kwargs):
        super().__init__(
            master,
            text=text,
            fg_color=theme.get_color("primary"),
            hover_color=theme.get_color("primary_hover"),
            text_color="#ffffff",
            font=theme.get_font("heading_sm"),
            corner_radius=RADIUS["md"],
            height=40,
            **kwargs
        )


class SecondaryButton(ctk.CTkButton):
    """Sekundärer Button"""
    
    def __init__(self, master, text: str, **kwargs):
        super().__init__(
            master,
            text=text,
            fg_color=theme.get_color("accent"),
            hover_color=theme.get_color("accent_hover"),
            text_color=theme.get_color("text_primary"),
            font=theme.get_font("body"),
            corner_radius=RADIUS["md"],
            height=36,
            **kwargs
        )


class IconButton(ctk.CTkButton):
    """Icon-Button ohne Text"""
    
    def __init__(self, master, icon: str = "⚙", **kwargs):
        super().__init__(
            master,
            text=icon,
            fg_color="transparent",
            hover_color=theme.get_color("bg_hover"),
            text_color=theme.get_color("text_secondary"),
            font=("Segoe UI", 18),
            corner_radius=RADIUS["md"],
            width=40,
            height=40,
            **kwargs
        )


class HeadingLabel(ctk.CTkLabel):
    """Überschrift-Label"""
    
    def __init__(self, master, text: str, size: str = "heading_lg", **kwargs):
        super().__init__(
            master,
            text=text,
            font=theme.get_font(size),
            text_color=theme.get_color("text_primary"),
            **kwargs
        )


class BodyLabel(ctk.CTkLabel):
    """Standard Text-Label"""
    
    def __init__(self, master, text: str, muted: bool = False, **kwargs):
        color = "text_muted" if muted else "text_secondary"
        super().__init__(
            master,
            text=text,
            font=theme.get_font("body"),
            text_color=theme.get_color(color),
            **kwargs
        )


class StatusBadge(ctk.CTkLabel):
    """Status-Badge (aktiv, abgelaufen, etc.)"""
    
    def __init__(self, master, text: str, status: str = "success", **kwargs):
        colors = {
            "success": ("#00d9a5", "#0a2a20"),
            "warning": ("#ffc107", "#2a2510"),
            "error": ("#ff4757", "#2a1015"),
            "info": ("#3498db", "#102030"),
        }
        fg, bg = colors.get(status, colors["info"])
        
        super().__init__(
            master,
            text=text,
            font=theme.get_font("caption"),
            text_color=fg,
            fg_color=bg,
            corner_radius=RADIUS["sm"],
            padx=SPACING["sm"],
            pady=SPACING["xs"],
            **kwargs
        )


class InfoCard(Card):
    """Info-Karte mit Titel und Wert"""
    
    def __init__(self, master, title: str, value: str, icon: str = "📊", **kwargs):
        super().__init__(master, **kwargs)
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=("Segoe UI Emoji", 24),
            text_color=theme.get_color("primary"),
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=SPACING["md"], pady=SPACING["md"])
        
        # Titel
        title_label = BodyLabel(self, text=title, muted=True)
        title_label.grid(row=0, column=1, sticky="sw", padx=(0, SPACING["md"]), pady=(SPACING["md"], 0))
        
        # Wert
        value_label = HeadingLabel(self, text=value, size="heading_md")
        value_label.grid(row=1, column=1, sticky="nw", padx=(0, SPACING["md"]), pady=(0, SPACING["md"]))


class NavButton(ctk.CTkButton):
    """Navigations-Button für Sidebar"""
    
    def __init__(self, master, text: str = "", icon: str = "", active: bool = False, **kwargs):
        fg = theme.get_color("primary") if active else "transparent"
        hover = theme.get_color("primary_hover") if active else theme.get_color("bg_hover")
        
        # anchor aus kwargs entfernen falls vorhanden (wird von uns gesetzt)
        kwargs.pop("anchor", None)
        
        display_text = f"  {icon}  {text}" if icon else text
        
        super().__init__(
            master,
            text=display_text,
            fg_color=fg,
            hover_color=hover,
            text_color=theme.get_color("text_primary"),
            font=theme.get_font("body"),
            corner_radius=RADIUS["md"],
            height=44,
            anchor="w",
            **kwargs
        )
