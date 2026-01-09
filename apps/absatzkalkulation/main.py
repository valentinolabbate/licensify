"""
Absatzkalkulation - Hauptanwendung
Eine moderne Desktop-App für Absatzkalkulationen mit Lizenzverwaltung
"""
import customtkinter as ctk
from pathlib import Path
import sys

# Pfad für Imports hinzufügen
sys.path.insert(0, str(Path(__file__).parent))

from config import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, DEFAULT_THEME
from ui.theme import theme, SPACING, RADIUS
from ui.components import NavButton, HeadingLabel
from ui.pages import LandingPage, LicensePage, SettingsPage
from ui.data_page import DataPage
from utils import license_manager


class App(ctk.CTk):
    """Hauptanwendung"""
    
    def __init__(self):
        super().__init__()
        
        # Fenster-Konfiguration
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(800, 600)
        
        # Theme setzen
        self.current_theme = DEFAULT_THEME
        ctk.set_appearance_mode(self.current_theme)
        theme.set_mode(self.current_theme)
        
        # Lizenz-Info laden
        self.license_info = {}
        self._load_license_info()
        
        # UI aufbauen
        self.setup_ui()
        
        # Startseite anzeigen
        self.show_page("home")
    
    def _load_license_info(self):
        """Lädt Lizenz-Informationen"""
        try:
            result = license_manager.validate()
            self.license_info = result.get("license_info", {})
        except Exception as e:
            print(f"Fehler beim Laden der Lizenz: {e}")
            self.license_info = license_manager._get_empty_info()
    
    def setup_ui(self):
        """Erstellt die Haupt-UI"""
        # Haupt-Container
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.create_sidebar()
        
        # Content-Bereich
        self.content_frame = ctk.CTkFrame(
            self, 
            fg_color=theme.get_color("bg_primary"),
            corner_radius=0
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Seiten-Container
        self.pages = {}
        self.current_page = None
    
    def create_sidebar(self):
        """Erstellt die Sidebar"""
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=theme.get_color("bg_secondary")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(4, weight=1)  # Spacer
        
        # App-Logo/Titel
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=SPACING["md"], pady=SPACING["lg"])
        
        ctk.CTkLabel(
            logo_frame,
            text="🧮",
            font=("Segoe UI Emoji", 32)
        ).pack(side="left", padx=(0, SPACING["sm"]))
        
        HeadingLabel(
            logo_frame,
            text="Absatz\nKalkulation",
            size="heading_sm"
        ).pack(side="left")
        
        # Trennlinie
        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=theme.get_color("border")
        ).grid(row=1, column=0, sticky="ew", padx=SPACING["md"], pady=SPACING["sm"])
        
        # Navigation
        self.nav_buttons = {}
        nav_items = [
            ("home", "🏠", "Startseite"),
            ("calculator", "🧮", "Kalkulation"),
            ("data", "📊", "Daten"),
            ("license", "🔑", "Lizenz"),
            ("settings", "⚙️", "Einstellungen"),
        ]
        
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.grid(row=2, column=0, sticky="new", padx=SPACING["md"], pady=SPACING["sm"])
        
        for page_id, icon, label in nav_items:
            btn = NavButton(
                nav_frame,
                text=f"  {icon}  {label}",
                command=lambda p=page_id: self.show_page(p),
                anchor="w"
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[page_id] = btn
        
        # Spacer (row 4)
        
        # Footer mit Lizenz-Status
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.grid(row=5, column=0, sticky="sew", padx=SPACING["md"], pady=SPACING["md"])
        
        status = self.license_info.get("status", "inactive")
        status_icon = "🟢" if status == "active" else "🔴"
        status_text = "Lizenz aktiv" if status == "active" else "Nicht aktiviert"
        
        self.status_label = ctk.CTkLabel(
            footer,
            text=f"{status_icon} {status_text}",
            font=theme.get_font("caption"),
            text_color=theme.get_color("text_muted")
        )
        self.status_label.pack(anchor="w")
        
        ctk.CTkLabel(
            footer,
            text=f"v{APP_VERSION}",
            font=theme.get_font("caption"),
            text_color=theme.get_color("text_muted")
        ).pack(anchor="w")
    
    def show_page(self, page_id: str):
        """Zeigt eine Seite an"""
        # Aktiven Button markieren
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == page_id:
                btn.configure(
                    fg_color=theme.get_color("bg_hover"),
                    text_color=theme.get_color("accent")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=theme.get_color("text_secondary")
                )
        
        # Alte Seite entfernen
        if self.current_page:
            self.current_page.destroy()
        
        # Neue Seite erstellen
        if page_id == "home":
            self.current_page = LandingPage(
                self.content_frame,
                on_navigate=self.show_page,
                license_info=self.license_info
            )
        elif page_id == "calculator":
            self.current_page = self._create_calculator_page()
        elif page_id == "data":
            self.current_page = DataPage(
                self.content_frame,
                license_manager=license_manager
            )
        elif page_id == "license":
            self.current_page = LicensePage(
                self.content_frame,
                license_info=self.license_info,
                on_activate=self._handle_activate,
                on_deactivate=self._handle_deactivate
            )
        elif page_id == "settings":
            self.current_page = SettingsPage(
                self.content_frame,
                current_theme=self.current_theme,
                on_theme_change=self._handle_theme_change,
                on_clear_cache=self._handle_clear_cache
            )
        else:
            # Fallback
            self.current_page = ctk.CTkLabel(
                self.content_frame,
                text=f"Seite '{page_id}' nicht gefunden",
                font=theme.get_font("heading_lg")
            )
        
        self.current_page.grid(row=0, column=0, sticky="nsew")
    
    def _create_calculator_page(self):
        """Erstellt eine Platzhalter-Kalkulator-Seite"""
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        HeadingLabel(
            frame,
            text="🧮 Absatzkalkulation",
            size="heading_xl"
        ).pack(pady=(SPACING["xl"], SPACING["md"]))
        
        ctk.CTkLabel(
            frame,
            text="Hier kommt die Kalkulationsfunktion hin.\n\nDiese Seite wird in einer zukünftigen Version implementiert.",
            font=theme.get_font("body"),
            text_color=theme.get_color("text_muted")
        ).pack(pady=SPACING["lg"])
        
        return frame
    
    def _handle_activate(self, license_key: str):
        """Handler für Lizenz-Aktivierung"""
        result = license_manager.activate(license_key)
        
        if result.get("success"):
            self.license_info = result.get("license_info", {})
            self._update_status_display()
            self._show_message("Erfolg", result.get("message", "Lizenz aktiviert"))
            self.show_page("license")  # Seite neu laden
        else:
            self._show_message("Fehler", result.get("message", "Aktivierung fehlgeschlagen"))
    
    def _handle_deactivate(self):
        """Handler für Lizenz-Deaktivierung"""
        result = license_manager.deactivate()
        
        if result.get("success"):
            self.license_info = license_manager._get_empty_info()
            self._update_status_display()
            self._show_message("Erfolg", result.get("message", "Lizenz deaktiviert"))
            self.show_page("license")  # Seite neu laden
        else:
            self._show_message("Fehler", result.get("message", "Deaktivierung fehlgeschlagen"))
    
    def _handle_theme_change(self, new_theme: str):
        """Handler für Theme-Wechsel"""
        self.current_theme = new_theme
        ctk.set_appearance_mode(new_theme)
        theme.set_mode(new_theme)

        # UI neu aufbauen für konsistente Farben
        self._rebuild_ui()
    
    def _handle_clear_cache(self):
        """Handler für Cache leeren"""
        # Hier könnte Cache-Logik implementiert werden
        self._show_message("Info", "Cache wurde geleert")
    
    def _update_status_display(self):
        """Aktualisiert die Status-Anzeige in der Sidebar"""
        status = self.license_info.get("status", "inactive")
        status_icon = "🟢" if status == "active" else "🔴"
        status_text = "Lizenz aktiv" if status == "active" else "Nicht aktiviert"
        self.status_label.configure(text=f"{status_icon} {status_text}")
    
    def _rebuild_ui(self):
        """Baut die UI nach Theme-Wechsel neu auf"""
        # Sidebar Farben aktualisieren
        self.sidebar.configure(fg_color=theme.get_color("bg_secondary"))
        self.content_frame.configure(fg_color=theme.get_color("bg_primary"))
        
        # Aktuelle Seite neu laden
        if self.current_page:
            current_page_name = None
            for page_id, btn in self.nav_buttons.items():
                if btn.cget("fg_color") == theme.get_color("bg_hover"):
                    current_page_name = page_id
                    break
            
            if current_page_name:
                self.show_page(current_page_name)
    
    def _show_message(self, title: str, message: str):
        """Zeigt eine Nachricht an"""
        # Einfaches Popup
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Zentrieren
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(dialog, fg_color=theme.get_color("bg_card"))
        frame.pack(fill="both", expand=True, padx=SPACING["sm"], pady=SPACING["sm"])
        
        HeadingLabel(frame, text=title, size="heading_md").pack(pady=(SPACING["lg"], SPACING["sm"]))
        
        ctk.CTkLabel(
            frame,
            text=message,
            font=theme.get_font("body"),
            text_color=theme.get_color("text_secondary"),
            wraplength=300
        ).pack(pady=SPACING["sm"])
        
        ctk.CTkButton(
            frame,
            text="OK",
            command=dialog.destroy,
            fg_color=theme.get_color("accent"),
            hover_color=theme.get_color("accent_hover"),
            corner_radius=RADIUS["md"]
        ).pack(pady=SPACING["md"])


def main():
    """Startet die Anwendung"""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
