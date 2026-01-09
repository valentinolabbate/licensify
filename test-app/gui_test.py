"""
GUI Test Application for Licensify
Eine einfache GUI zum Testen der Lizenzvalidierung
"""
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add licensify to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'licensify'))

try:
    from licensify import LicenseValidator
    from licensify.exceptions import LicenseException
except ImportError:
    print("Licensify nicht gefunden! Installiere es mit: pip install -e ../licensify")
    sys.exit(1)


class LicenseTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Licensify Test App")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.validator = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main Frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="🔑 Licensify Test", font=("Helvetica", 18, "bold"))
        title.pack(pady=(0, 20))
        
        # API URL
        ttk.Label(main_frame, text="API URL:").pack(anchor=tk.W)
        self.api_url = ttk.Entry(main_frame, width=60)
        self.api_url.insert(0, "http://localhost:8000")
        self.api_url.pack(fill=tk.X, pady=(0, 10))
        
        # License Key
        ttk.Label(main_frame, text="License Key:").pack(anchor=tk.W)
        self.license_key = ttk.Entry(main_frame, width=60)
        self.license_key.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.validate_btn = ttk.Button(btn_frame, text="Lizenz validieren", command=self.validate)
        self.validate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.quick_btn = ttk.Button(btn_frame, text="Schnellcheck", command=self.quick_check)
        self.quick_btn.pack(side=tk.LEFT)
        
        # Status
        self.status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        self.status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(self.status_frame, height=10, state=tk.DISABLED, font=("Consolas", 10))
        self.status_text.pack(fill=tk.BOTH, expand=True)
    
    def log(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def get_validator(self):
        api_url = self.api_url.get().strip()
        license_key = self.license_key.get().strip()
        
        if not api_url or not license_key:
            messagebox.showerror("Fehler", "Bitte API URL und License Key eingeben!")
            return None
        
        return LicenseValidator(
            api_url=api_url,
            license_key=license_key,
            app_version="1.0.0"
        )
    
    def quick_check(self):
        self.clear_log()
        self.log("Schnellcheck gestartet...")
        
        try:
            validator = self.get_validator()
            if not validator:
                return
            
            self.log(f"Device ID: {validator.device_id}")
            
            if validator.is_valid():
                self.log("\n✅ LIZENZ GÜLTIG!")
                messagebox.showinfo("Erfolg", "Lizenz ist gültig!")
            else:
                self.log("\n❌ LIZENZ UNGÜLTIG!")
                messagebox.showwarning("Warnung", "Lizenz ist ungültig!")
                
        except Exception as e:
            self.log(f"\n❌ Fehler: {e}")
            messagebox.showerror("Fehler", str(e))
    
    def validate(self):
        self.clear_log()
        self.log("Validierung gestartet...")
        
        try:
            validator = self.get_validator()
            if not validator:
                return
            
            self.log(f"Device ID: {validator.device_id}")
            self.log("Verbinde zum Server...")
            
            result = validator.validate()
            
            self.log("\n✅ VALIDIERUNG ERFOLGREICH!\n")
            self.log(f"Lizenz-Typ:     {result.get('license_type', 'N/A')}")
            self.log(f"Läuft ab:       {result.get('expires_at', 'Nie')}")
            self.log(f"Tage übrig:     {result.get('days_remaining', '∞')}")
            self.log(f"Max Devices:    {result.get('max_devices', '∞')}")
            self.log(f"Aktive Devices: {result.get('current_devices', 0)}")
            
            messagebox.showinfo("Erfolg", "Lizenz erfolgreich validiert!")
            
        except LicenseException as e:
            self.log(f"\n❌ Lizenzfehler: {e}")
            messagebox.showerror("Lizenzfehler", str(e))
        except Exception as e:
            self.log(f"\n❌ Fehler: {e}")
            messagebox.showerror("Fehler", str(e))


def main():
    root = tk.Tk()
    app = LicenseTestApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
