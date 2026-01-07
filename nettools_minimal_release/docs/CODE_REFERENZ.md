# NetTools Minimal - Vollständige Code-Referenz

## 📋 Datei-Übersicht

| Datei | Zeilen | Beschreibung |
|-------|--------|--------------|
| `nettools_minimal.py` | ~4970 | Hauptanwendung |
| `design_constants.py` | ~200 | Farben, Fonts, Abstände |
| `ui_components.py` | ~700 | Wiederverwendbare UI-Komponenten |
| `ui/*.py` | ~8000 | UI-Module für jedes Tool |
| `tools/*.py` | ~3000 | Backend-Logik |

---

## 📍 nettools_minimal.py - Code-Struktur

```
Zeile 1-120      → IMPORTS & KONFIGURATION
Zeile 120-400    → KLASSE NetToolsApp - Initialisierung
Zeile 400-700    → KONFIGURATION & EINSTELLUNGEN
Zeile 700-1020   → SIDEBAR & NAVIGATION
Zeile 1020-1100  → SIDEBAR COLLAPSE/EXPAND
Zeile 1100-1300  → SEITEN-WECHSEL (switch_page)
Zeile 1300-1500  → HAUPTINHALT & LAYOUT
Zeile 1500-2500  → TOOL-SPEZIFISCHE INHALTE
Zeile 2500-3500  → SCANNER FUNKTIONALITÄT
Zeile 3500-4000  → HILFSFUNKTIONEN
Zeile 4000-4500  → FAVORITEN & HISTORY
Zeile 4500-4972  → MAIN & APP-START
```

---

## 🔍 DETAILLIERTE CODE-REFERENZ

### ═══════════════════════════════════════════════════════════════
### ABSCHNITT 1: IMPORTS (Zeile 1-120)
### ═══════════════════════════════════════════════════════════════

```python
# Zeile 1-22: Standard-Bibliotheken
import customtkinter as ctk      # GUI-Framework
import threading                 # Für nicht-blockierende Netzwerk-Ops
import subprocess                # System-Befehle (ping, tracert, etc.)
import socket                    # Netzwerk-Sockets (DNS, SNMP)
import json                      # Konfiguration speichern/laden
import os, sys                   # Dateisystem-Operationen
from pathlib import Path         # Plattformunabhängige Pfade
from datetime import datetime    # Zeitstempel

# Zeile 23-40: UI-Module importieren
from ui.dashboard_ui import DashboardUI
from ui.scanner_ui import ScannerUI
from ui.portscan_ui import PortScannerUI
from ui.dns_ui import DNSLookupUI
from ui.subnet_ui import SubnetCalculatorUI
from ui.mac_ui import MACFormatterUI
from ui.traceroute_ui import TracerouteUI
from ui.panos_ui import PANOSUI
from ui.password_generator_ui import PasswordGeneratorUI
from ui.ssl_checker_ui import SSLCheckerUI
from ui.arp_viewer_ui import ARPViewerUI
from ui.settings_ui import SettingsUI

# Zeile 70-90: Backend-Module importieren
from tools.scanner import IPv4Scanner
from tools.scan_manager import ScanManager
from tools.history_manager import HistoryManager
from tools.traceroute_manager import TracerouteManager

# Zeile 95-100: App-Metadaten
APP_NAME = "NetTools Minimal"
APP_VERSION = "1.0.0"
```

**Was passiert hier?**
- Alle benötigten Bibliotheken werden geladen
- UI-Module = Oberflächen für jedes Tool
- Tools-Module = Backend-Logik (Netzwerk-Operationen)
- MINIMAL: phpipam, speedtest, hash, api, whois, bandwidth NICHT importiert

---

### ═══════════════════════════════════════════════════════════════
### ABSCHNITT 2: HAUPTKLASSE INITIALISIERUNG (Zeile 120-400)
### ═══════════════════════════════════════════════════════════════

```python
# Zeile 125-180: Klassen-Definition und __init__
class NetToolsApp(ctk.CTk):
    """
    Hauptanwendungsklasse - erbt von CustomTkinter Fenster
    Verwaltet: Navigation, Seiten, Scanner, History
    """
    
    def __init__(self):
        super().__init__()  # CTk Fenster initialisieren
        
        # Zeile 135-145: Fenster-Eigenschaften
        self.title("NetTools Minimal")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        
        # Zeile 150-165: Manager-Instanzen erstellen
        self.scanner = IPv4Scanner()              # Netzwerk-Scanner
        self.scan_manager = ScanManager()         # Scan-Verwaltung
        self.history = HistoryManager()           # Verlauf
        self.traceroute_manager = TracerouteManager()
        
        # Zeile 170-180: Zustandsvariablen
        self.current_page = "dashboard"           # Aktive Seite
        self.pages = {}                           # Seiten-Container
        self.pages_loaded = {}                    # Lazy-Loading Tracker
        self.nav_buttons = {}                     # Navigation-Buttons
        self.favorite_tools = set()               # Favorisierte Tools
        self.sidebar_expanded = True              # Sidebar-Status
        
        # Zeile 185-200: Konfiguration laden
        self.config_dir = Path.home() / ".nettools"
        self.config_file = self.config_dir / "config.json"
        self.load_config()
        
        # Zeile 205-220: UI aufbauen (Reihenfolge wichtig!)
        self.create_sidebar()          # 1. Navigation links
        self.create_main_content()     # 2. Hauptbereich
        self.create_status_bar()       # 3. Statusleiste unten
        
        # Zeile 225-240: Tastenkombinationen registrieren
        self.bind('<Control-k>', self.open_quick_switcher)
        self.bind('<Control-b>', lambda e: self.toggle_sidebar())
        self.bind('<Control-d>', lambda e: self.switch_tool("dashboard"))
        self.bind('<Escape>', self.close_dialogs)
```

**Was passiert hier?**
- Fenster wird mit Titel und Größe erstellt
- Backend-Manager werden instanziiert
- Zustandsvariablen für Navigation initialisiert
- Konfiguration aus ~/.nettools/config.json laden
- UI-Komponenten in korrekter Reihenfolge aufbauen
- Keyboard-Shortcuts registrieren

---

### ═══════════════════════════════════════════════════════════════
### ABSCHNITT 3: KONFIGURATION (Zeile 400-700)
### ═══════════════════════════════════════════════════════════════

```python
# Zeile 320-365: Aktivierte Tools ermitteln
def get_enabled_tools(self):
    """Welche Tools sind aktiviert?"""
    # MINIMAL: Reduzierter Tool-Satz
    all_tools = {
        'dashboard', 'scanner', 'portscan', 'dns', 'traceroute', 'arp',
        'subnet', 'mac', 'ssl', 'password',
        'compare', 'profiles', 'panos', 'settings'
    }
    # Aus config.json laden oder alle aktivieren
    return self.config.get('enabled_tools', all_tools)

# Zeile 370-400: Konfiguration laden
def load_config(self):
    """Lädt Einstellungen aus JSON-Datei"""
    try:
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}
    except Exception:
        self.config = {}
    
    # Favoriten laden
    self.favorite_tools = set(self.config.get('favorite_tools', []))
    self.enabled_tools = self.get_enabled_tools()

# Zeile 405-430: Konfiguration speichern
def save_config(self):
    """Speichert Einstellungen in JSON-Datei"""
    self.config_dir.mkdir(parents=True, exist_ok=True)
    self.config['favorite_tools'] = list(self.favorite_tools)
    self.config['enabled_tools'] = list(self.enabled_tools)
    
    with open(self.config_file, 'w') as f:
        json.dump(self.config, f, indent=2)
```

**Was passiert hier?**
- `get_enabled_tools()`: Definiert welche Tools verfügbar sind
- `load_config()`: Lädt Benutzer-Einstellungen beim Start
- `save_config()`: Speichert Änderungen persistent
- Konfigurationsdatei: `~/.nettools/config.json`

---

### ═══════════════════════════════════════════════════════════════
### ABSCHNITT 4: SIDEBAR NAVIGATION (Zeile 700-1020)
### ═══════════════════════════════════════════════════════════════

```python
# Zeile 700-750: Sidebar-Container erstellen
def create_sidebar(self):
    """Erstellt die linke Navigationsleiste"""
    
    # Sidebar-Frame
    self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
    self.sidebar.pack(side="left", fill="y")
    self.sidebar.pack_propagate(False)  # Feste Breite
    
    # Header mit Logo
    header_frame = ctk.CTkFrame(self.sidebar, height=95)
    # ... Logo und Titel ...

# Zeile 780-870: Tool-Kategorien definieren
self.nav_categories = [
    ("DASHBOARD", "🏠", [
        ("dashboard", "🏠", "Dashboard", "Übersicht"),
    ]),
    ("SCANNING", "🔍", [
        ("scanner", "📡", "IPv4 Scanner", "Netzwerk scannen"),
        ("portscan", "🔌", "Port Scanner", "Ports prüfen"),
        ("traceroute", "⤳", "Traceroute", "Route verfolgen"),
        ("arp", "📊", "ARP Table", "ARP-Cache"),
    ]),
    ("TOOLS", "🛠️", [
        ("dns", "🌐", "DNS Lookup", "DNS abfragen"),
        ("ssl", "🔒", "SSL Checker", "Zertifikate prüfen"),
        ("subnet", "🔢", "Subnet Calculator", "Subnetz berechnen"),
        ("mac", "🔗", "MAC Formatter", "MAC formatieren"),
        ("password", "🔐", "Password Generator", "Passwort erstellen"),
    ]),
    ("TESTING", "🧪", [
        ("compare", "⇔", "Scan Comparison", "Scans vergleichen"),
    ]),
    ("ADVANCED", "⚙️", [
        ("profiles", "📁", "Network Profiles", "Netzwerk-Profile"),
        ("panos", "⛨", "PAN-OS Generator", "Firewall CLI"),
        ("settings", "✦", "Settings", "Einstellungen"),
    ]),
]

# Zeile 880-980: Buttons für jedes Tool erstellen
for category_name, cat_icon, items in self.nav_categories:
    # Kategorie-Label
    category_label = ctk.CTkLabel(
        self.nav_scroll,
        text=f"{cat_icon} {category_name}",
        font=ctk.CTkFont(size=11, weight="bold")
    )
    
    # Tools in dieser Kategorie
    for page_id, icon, label, tooltip in items:
        # Nur aktivierte Tools anzeigen
        if page_id not in self.enabled_tools:
            continue
            
        btn = ctk.CTkButton(
            self.nav_scroll,
            text=f"  {icon}   {label}",
            command=lambda p=page_id: self.switch_tool(p),
            anchor="w",
            fg_color="transparent"
        )
        btn.pack(fill="x", padx=8, pady=1)
        
        # Referenz speichern
        btn._nav_icon = icon
        btn._nav_label = label
        self.nav_buttons[page_id] = btn
```

**Was passiert hier?**
- Sidebar-Container mit fester Breite (250px)
- Tools in Kategorien organisiert (SCANNING, TOOLS, etc.)
- Für jedes Tool wird ein Button erstellt
- Nur `enabled_tools` werden angezeigt
- Button-Klick ruft `switch_tool(page_id)` auf

---

### ═══════════════════════════════════════════════════════════════
### ABSCHNITT 5: SIDEBAR COLLAPSE/EXPAND (Zeile 1020-1100)
### ═══════════════════════════════════════════════════════════════

```python
# Zeile 1020-1060: Sidebar einklappen
def _collapse_sidebar(self):
    """Klappt Sidebar auf Icon-Ansicht ein"""
    self.sidebar_expanded = False
    self.sidebar.configure(width=70)
    
    # Buttons auf Icon-only umstellen
    for page_id, btn in self.nav_buttons.items():
        icon = getattr(btn, '_nav_icon', '•')
        btn.configure(
            text=icon,
            anchor="center",
            width=48
        )
        # Aktiver Button hervorheben
        if page_id == self.current_page:
            btn.configure(fg_color=COLORS['electric_violet'])

# Zeile 1065-1100: Sidebar ausklappen
def _expand_sidebar(self):
    """Klappt Sidebar auf volle Breite aus"""
    self.sidebar_expanded = True
    self.sidebar.configure(width=250)
    
    # Buttons auf Icon + Text umstellen
    for page_id, btn in self.nav_buttons.items():
        icon = getattr(btn, '_nav_icon', '•')
        label = getattr(btn, '_nav_label', page_id)
        btn.configure(
            text=f"  {icon}   {label}",
            anchor="w",
            width=220
        )
```

**Was passiert hier?**
- `_collapse_sidebar()`: Zeigt nur Icons (70px breit)
- `_expand_sidebar()`: Zeigt Icons + Text (250px breit)
- Aktuelle Seite bleibt hervorgehoben
- Toggle mit Strg+B oder Collapse-Button

---

### ═══════════════════════════════════════════════════════════════
### ABSCHNITT 6: SEITEN-WECHSEL (Zeile 1100-1300)
### ═══════════════════════════════════════════════════════════════

```python
# Zeile 1150-1270: Seite wechseln mit Lazy Loading
def switch_page(self, page_id):
    """Wechselt zur gewählten Tool-Seite"""
    
    # Alte Seite ausblenden
    if self.current_page in self.pages:
        self.pages[self.current_page].pack_forget()
    
    # Seiten-Container erstellen falls nicht vorhanden
    if page_id not in self.pages:
        self.pages[page_id] = ctk.CTkFrame(self.main_content)
    
    # ═══════════════════════════════════════════════════
    # LAZY LOADING - UI nur bei erstem Aufruf erstellen
    # ═══════════════════════════════════════════════════
    if page_id not in self.pages_loaded:
        
        if page_id == "dashboard":
            DashboardUI(self, self.pages[page_id])
            
        elif page_id == "scanner":
            ScannerUI(self, self.pages[page_id])
            
        elif page_id == "portscan":
            PortScannerUI(self, self.pages[page_id])
            
        elif page_id == "dns":
            DNSLookupUI(self, self.pages[page_id])
            
        elif page_id == "traceroute":
            TracerouteUI(self, self.pages[page_id])
            
        elif page_id == "arp":
            ARPViewerUI(self, self.pages[page_id])
            
        elif page_id == "ssl":
            SSLCheckerUI(self, self.pages[page_id])
            
        elif page_id == "subnet":
            self.create_subnet_content(self.pages[page_id])
            
        elif page_id == "mac":
            MACFormatterUI(self, self.pages[page_id])
            
        elif page_id == "password":
            PasswordGeneratorUI(self, self.pages[page_id])
            
        elif page_id == "panos":
            PANOSUI(self, self.pages[page_id])
            
        elif page_id == "compare":
            self.create_comparison_content(self.pages[page_id])
            
        elif page_id == "profiles":
            self.create_profiles_content(self.pages[page_id])
            
        elif page_id == "settings":
            SettingsUI(self, self.pages[page_id])
        
        # Als geladen markieren
        self.pages_loaded[page_id] = True
    
    # Seite anzeigen
    self.current_page = page_id
    self.pages[page_id].pack(fill="both", expand=True)
    
    # Navigation-Buttons aktualisieren
    for btn_id, btn in self.nav_buttons.items():
        if btn_id == page_id:
            btn.configure(fg_color=COLORS['electric_violet'], text_color="white")
        else:
            btn.configure(fg_color="transparent", text_color=COLORS['text_primary'])
```

**Was passiert hier?**
- **Lazy Loading**: UI-Klassen werden erst beim ersten Aufruf erstellt
- Je nach `page_id` wird die richtige UI-Klasse instantiiert
- `pages_loaded` verhindert doppeltes Laden
- Navigation-Buttons werden aktualisiert (aktiver = violett)

---

### ═══════════════════════════════════════════════════════════════
### ABSCHNITT 7: SCANNER-INTEGRATION (Zeile 2500-3500)
### ═══════════════════════════════════════════════════════════════

```python
# Zeile 2600-2700: Scanner-Callbacks setzen
def setup_scanner_callbacks(self):
    """Verbindet Scanner mit UI-Updates"""
    
    # Fortschritts-Callback (während Scan)
    self.scanner.progress_callback = self.on_scan_progress
    
    # Abschluss-Callback (Scan fertig)
    self.scanner.complete_callback = self.on_scan_complete

# Zeile 2750-2850: Scan starten
def start_network_scan(self, cidr, aggression="normal"):
    """Startet Netzwerk-Scan in separatem Thread"""
    
    # ═══════════════════════════════════════════════════
    # WICHTIG: Netzwerk-Operation MUSS in Thread laufen!
    # ═══════════════════════════════════════════════════
    self.scan_thread = threading.Thread(
        target=self.scanner.scan_network,
        args=(cidr, aggression),
        daemon=True  # Thread beendet sich mit App
    )
    self.scan_thread.start()
    
    # UI in "Scanning..." Zustand versetzen
    self.scan_btn.configure(state="disabled")
    self.progress_bar.start()

# Zeile 2900-2950: Scan-Fortschritt anzeigen
def on_scan_progress(self, result):
    """Callback: Einzelnes Scan-Ergebnis empfangen"""
    
    # ═══════════════════════════════════════════════════
    # WICHTIG: UI-Update nur im Main-Thread!
    # ═══════════════════════════════════════════════════
    self.after(0, lambda: self._update_scan_result(result))

def _update_scan_result(self, result):
    """Fügt Ergebnis zur Tabelle hinzu (Main-Thread)"""
    if result.get('responding'):
        self.results_tree.insert('', 'end', values=(
            result['ip'],
            result.get('hostname', ''),
            result.get('mac', ''),
            f"{result.get('response_time', 0):.1f} ms"
        ))

# Zeile 3000-3050: Scan abgeschlossen
def on_scan_complete(self, results):
    """Callback: Scan ist fertig"""
    self.after(0, lambda: self._finish_scan(results))

def _finish_scan(self, results):
    """Scan abschließen (Main-Thread)"""
    self.progress_bar.stop()
    self.scan_btn.configure(state="normal")
    self.show_toast(f"Scan complete: {len(results)} hosts found", "success")
```

**Was passiert hier?**
- **Callbacks**: Scanner informiert UI über Fortschritt
- **Threading**: `scan_network()` läuft in separatem Thread
- **after(0, ...)**: UI-Updates werden im Main-Thread ausgeführt
- **daemon=True**: Thread beendet sich automatisch mit der App

---

### ═══════════════════════════════════════════════════════════════
### ABSCHNITT 8: TOAST-BENACHRICHTIGUNGEN (Zeile 3500-3600)
### ═══════════════════════════════════════════════════════════════

```python
# Zeile 3520-3580: Toast anzeigen
def show_toast(self, message, toast_type="info"):
    """Zeigt temporäre Benachrichtigung an"""
    
    # Farbe je nach Typ
    colors = {
        "success": COLORS['success'],
        "error": COLORS['danger'],
        "warning": COLORS['warning'],
        "info": COLORS['electric_violet']
    }
    
    # Toast-Frame erstellen
    toast = ctk.CTkFrame(
        self,
        fg_color=colors.get(toast_type, colors['info']),
        corner_radius=8
    )
    toast.place(relx=0.5, rely=0.95, anchor="center")
    
    # Nachricht
    label = ctk.CTkLabel(toast, text=message, text_color="white")
    label.pack(padx=20, pady=10)
    
    # Nach 3 Sekunden ausblenden
    self.after(3000, toast.destroy)
```

**Was passiert hier?**
- Toast erscheint am unteren Bildschirmrand
- Farbe zeigt Typ an (grün=Erfolg, rot=Fehler, etc.)
- Verschwindet automatisch nach 3 Sekunden

---

### ═══════════════════════════════════════════════════════════════
### ABSCHNITT 9: FAVORITEN-SYSTEM (Zeile 4000-4500)
### ═══════════════════════════════════════════════════════════════

```python
# Zeile 4050-4100: Favorit hinzufügen/entfernen
def toggle_favorite(self, tool_id):
    """Fügt Tool zu Favoriten hinzu oder entfernt es"""
    if tool_id in self.favorite_tools:
        self.favorite_tools.remove(tool_id)
        self.show_toast(f"Removed from favorites", "info")
    else:
        self.favorite_tools.add(tool_id)
        self.show_toast(f"Added to favorites", "success")
    
    # Speichern und UI aktualisieren
    self.save_config()
    self.update_nav_button_stars()
    self.refresh_favorites_section()

# Zeile 4150-4200: Sterne in Navigation aktualisieren
def update_nav_button_stars(self):
    """Zeigt ⭐ bei favorisierten Tools"""
    for tool_id, btn in self.nav_buttons.items():
        icon = getattr(btn, '_nav_icon', '•')
        label = getattr(btn, '_nav_label', tool_id)
        
        if tool_id in self.favorite_tools:
            btn.configure(text=f"  {icon}   {label} ⭐")
        else:
            btn.configure(text=f"  {icon}   {label}")
```

**Was passiert hier?**
- Rechtsklick auf Tool → Favorit toggle
- Favoriten werden in config.json gespeichert
- ⭐ erscheint neben favorisierten Tools

---

### ═══════════════════════════════════════════════════════════════
### ABSCHNITT 10: APP-START (Zeile 4900-4972)
### ═══════════════════════════════════════════════════════════════

```python
# Zeile 4950-4972: Main Entry Point
def main():
    """Startet die Anwendung"""
    
    # App erstellen
    app = NetToolsApp()
    
    # Fenster-Schließen-Event
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Event-Loop starten (blockiert bis Fenster geschlossen)
    app.mainloop()

if __name__ == "__main__":
    main()
```

**Was passiert hier?**
- `NetToolsApp()` erstellt das Hauptfenster
- `mainloop()` startet die Event-Schleife
- App läuft bis Benutzer Fenster schließt

---

## 📊 ZUSAMMENFASSUNG

### Architektur-Überblick
```
┌─────────────────────────────────────────────────────────────┐
│                    nettools_minimal.py                       │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │   Sidebar      │  │   Main Content │  │   Status Bar │  │
│  │   Navigation   │  │   (Tool-Seite) │  │              │  │
│  │   700-1020     │  │   1300-1500    │  │   1500+      │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Lazy Loading (switch_page)               │  │
│  │                    Zeile 1100-1300                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│          ┌───────────────────┼───────────────────┐         │
│          ▼                   ▼                   ▼         │
│    ┌──────────┐        ┌──────────┐        ┌──────────┐   │
│    │ /ui/*.py │        │ /ui/*.py │        │ /ui/*.py │   │
│    │ Scanner  │        │   DNS    │        │   SSL    │   │
│    └──────────┘        └──────────┘        └──────────┘   │
│          │                   │                   │         │
│          ▼                   ▼                   ▼         │
│    ┌──────────┐        ┌──────────┐        ┌──────────┐   │
│    │/tools/*.py│       │/tools/*.py│       │/tools/*.py│  │
│    │ scanner  │        │dns_lookup│        │ssl_check │   │
│    └──────────┘        └──────────┘        └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Wichtige Patterns
| Pattern | Verwendung | Zeilen |
|---------|------------|--------|
| **Lazy Loading** | Seiten bei Bedarf laden | 1100-1300 |
| **Threading** | Netzwerk-Ops nicht blockierend | 2750-2850 |
| **Callbacks** | Scanner → UI Kommunikation | 2600-2700 |
| **after()** | Thread-sichere UI-Updates | 2900-2950 |
| **MVC-ähnlich** | UI/Logic getrennt | Gesamtstruktur |

---

*Erstellt für NetTools Minimal v1.0 | Dezember 2024*
