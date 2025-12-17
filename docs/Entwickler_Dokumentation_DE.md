# NetTools Suite - Technische Dokumentation für Entwickler

**Version 2.0 | Stand: Dezember 2024**

---

## Inhaltsverzeichnis

1. [Projektübersicht](#1-projektübersicht)
2. [Architektur](#2-architektur)
3. [Verzeichnisstruktur](#3-verzeichnisstruktur)
4. [Technologie-Stack](#4-technologie-stack)
5. [Hauptkomponenten](#5-hauptkomponenten)
6. [UI-Komponenten](#6-ui-komponenten)
7. [Tools-Module](#7-tools-module)
8. [Design-System](#8-design-system)
9. [Konfiguration & Persistenz](#9-konfiguration--persistenz)
10. [Neue Tools hinzufügen](#10-neue-tools-hinzufügen)
11. [Best Practices](#11-best-practices)
12. [Bekannte Probleme](#12-bekannte-probleme)
13. [Weiterentwicklung](#13-weiterentwicklung)

---

## 1. Projektübersicht

Die NetTools Suite ist eine Desktop-Anwendung für Netzwerk-Administration, entwickelt mit Python und CustomTkinter. Die Anwendung folgt einer modularen Architektur, die einfache Erweiterung und Wartung ermöglicht.

### Kernziele:
- Moderne, benutzerfreundliche GUI
- Modulare Tool-Architektur
- Plattformübergreifend (primär Windows)
- Einfache Erweiterbarkeit

---

## 2. Architektur

### Schichtenmodell:

```
┌─────────────────────────────────────────────┐
│             Benutzeroberfläche              │
│         (CustomTkinter / CTk)               │
├─────────────────────────────────────────────┤
│              UI-Komponenten                 │
│    (StyledCard, StyledButton, etc.)         │
├─────────────────────────────────────────────┤
│              Tool-UI-Module                 │
│    (scanner_ui, dns_ui, settings_ui)        │
├─────────────────────────────────────────────┤
│            Backend/Tools-Module             │
│    (scanner.py, dns_tool.py, etc.)          │
├─────────────────────────────────────────────┤
│         System/Netzwerk-Schnittstellen      │
│    (subprocess, socket, requests)           │
└─────────────────────────────────────────────┘
```

### Kommunikationsfluss:

```
Benutzer-Aktion
    │
    ▼
UI-Modul (z.B. scanner_ui.py)
    │
    ├── Validierung der Eingabe
    │
    ▼
Backend-Modul (z.B. scanner.py)
    │
    ├── Async-Threading für lange Operationen
    │
    ▼
System-Aufruf (ping, tracert, etc.)
    │
    ▼
Ergebnis-Callback
    │
    ▼
UI-Update (in Haupt-Thread via app.after())
```

---

## 3. Verzeichnisstruktur

```
nettools/
│
├── nettools_app.py          # Hauptanwendung & Entry Point
├── design_constants.py      # Farben, Schriften, Abstände
├── ui_components.py         # Wiederverwendbare UI-Komponenten
├── requirements.txt         # Python-Abhängigkeiten
│
├── ui/                      # UI-Module für jeden Tool
│   ├── __init__.py
│   ├── dashboard_ui.py      # Dashboard-Ansicht
│   ├── scanner_ui.py        # IPv4-Scanner UI (inline in nettools_app.py)
│   ├── portscan_ui.py       # Port-Scanner UI (inline)
│   ├── dns_ui.py            # DNS-Lookup UI (inline)
│   ├── traceroute_ui.py     # Traceroute UI
│   ├── arp_viewer_ui.py     # ARP-Table Viewer
│   ├── whois_ui.py          # WHOIS Lookup
│   ├── ssl_checker_ui.py    # SSL-Zertifikat-Prüfer
│   ├── hash_generator_ui.py # Hash-Generator
│   ├── api_tester_ui.py     # API/HTTP-Tester
│   ├── password_generator_ui.py # Passwort-Generator
│   ├── speedtest_ui.py      # Internet Speedtest
│   ├── subnet_ui.py         # Subnet-Rechner
│   ├── mac_ui.py            # MAC-Adress-Formatter
│   ├── bandwidth_ui.py      # iPerf3 Bandbreiten-Test
│   ├── panos_ui.py          # PAN-OS Generator
│   ├── phpipam_ui.py        # phpIPAM Integration
│   ├── settings_ui.py       # Einstellungen
│   └── ...
│
├── tools/                   # Backend-Logik
│   ├── __init__.py
│   ├── scanner.py           # IPv4-Scanner Logik
│   ├── port_scanner.py      # Port-Scanner Logik
│   ├── dns_tool.py          # DNS-Abfrage Logik
│   ├── traceroute.py        # Traceroute Logik
│   ├── traceroute_manager.py # Traceroute-Verlauf
│   ├── scan_manager.py      # Scan-Speicherung
│   ├── comparison_history.py # Vergleichs-Verlauf
│   ├── history_manager.py   # Allg. Verlaufs-Manager
│   ├── network_profiles.py  # Netzwerk-Profile
│   ├── remote_tools.py      # PSExec/iPerf (deaktiviert)
│   └── phpipam_tool.py      # phpIPAM API
│
├── docs/                    # Dokumentation
│   ├── Benutzerhandbuch_DE.md
│   └── Entwickler_Dokumentation_DE.md
│
└── assets/                  # Bilder, Icons (falls vorhanden)
```

---

## 4. Technologie-Stack

### Hauptabhängigkeiten:

| Bibliothek | Version | Verwendung |
|------------|---------|------------|
| `customtkinter` | ≥5.2.0 | Moderne GUI-Komponenten |
| `tkinter` | (builtin) | Basis-GUI-Framework |
| `requests` | ≥2.31.0 | HTTP-Anfragen |
| `dnspython` | ≥2.4.0 | DNS-Abfragen |
| `python-whois` | ≥0.8.0 | WHOIS-Lookup |
| `beautifulsoup4` | ≥4.12.0 | HTML-Parsing |
| `pyinstaller` | ≥6.0.0 | Executable-Erstellung |

### System-Tools (extern):
- `ping` / `tracert` / `pathping` - Windows-Netzwerktools
- `arp` - ARP-Tabelle
- `nslookup` - DNS-Abfragen (Fallback)
- `psexec` - Remote-Ausführung (optional)
- `iperf3` - Bandbreiten-Tests (optional)

---

## 5. Hauptkomponenten

### 5.1 nettools_app.py - Hauptanwendung

Dies ist der zentrale Entry Point und enthält:

```python
class NetToolsApp(ctk.CTk):
    """Hauptfenster der Anwendung"""
    
    def __init__(self):
        # Fenster-Initialisierung
        # Konfiguration laden
        # UI aufbauen
        
    def create_sidebar(self):
        """Erstellt die Navigation"""
        
    def switch_page(self, page_id):
        """Wechselt zwischen Tools"""
        
    def show_toast(self, message, type):
        """Zeigt Benachrichtigungen"""
```

### Wichtige Methoden:

| Methode | Beschreibung |
|---------|--------------|
| `__init__()` | Initialisiert App, lädt Config, baut UI |
| `create_sidebar()` | Erstellt Navigation mit Kategorien |
| `switch_page(page_id)` | Wechselt zu einem Tool |
| `switch_tool(tool_id)` | Alias für switch_page |
| `show_toast(msg, type)` | Zeigt Toast-Benachrichtigung |
| `get_enabled_tools()` | Lädt aktivierte Tools aus Config |
| `set_enabled_tools(tools)` | Speichert Tool-Einstellungen |
| `load_favorites()` | Lädt Favoriten |
| `save_favorites()` | Speichert Favoriten |
| `is_admin()` | Prüft Admin-Rechte |
| `restart_as_admin()` | Startet App mit Admin-Rechten neu |

### Navigation-Struktur:

```python
nav_categories = [
    ("KATEGORIE_NAME", "📊", [
        ("tool_id", "🔧", "Tool Name", "Tooltip-Text"),
        # weitere Tools...
    ]),
    # weitere Kategorien...
]
```

### Seiten-Wechsel (switch_page):

```python
def switch_page(self, page_id):
    # 1. Altes Tool ausblenden
    # 2. Navigations-Buttons aktualisieren
    # 3. Neues Tool laden (lazy loading)
    # 4. Mit Animation einblenden
```

---

### 5.2 design_constants.py - Design-System

Zentrale Definition aller visuellen Konstanten:

```python
# Farbpalette (Light/Dark Mode Tupel)
COLORS = {
    "bg_primary": ("#1A1B26", "#1A1B26"),
    "electric_violet": ("#8B5CF6", "#A78BFA"),
    "neon_cyan": ("#00D9FF", "#67E8F9"),
    "success": ("#22C55E", "#4ADE80"),
    "danger": ("#EF4444", "#F87171"),
    "warning": ("#F59E0B", "#FBBF24"),
    # ...
}

# Abstände
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

# Schriftgrößen
FONT_SIZES = {
    "title": 24,
    "heading": 18,
    "subheading": 14,
    "body": 12,
    "small": 11,
}
```

### Verwendung:

```python
from design_constants import COLORS, SPACING, FONT_SIZES

# In UI-Code:
button = ctk.CTkButton(
    parent,
    fg_color=COLORS['electric_violet'],
    text_color=COLORS['text_primary']
)
frame.pack(padx=SPACING['md'], pady=SPACING['sm'])
```

---

### 5.3 ui_components.py - Wiederverwendbare Komponenten

Enthält gestylte Basiskomponenten:

#### StyledCard
```python
class StyledCard(ctk.CTkFrame):
    """Gestylte Karte mit Schatten-Effekt"""
    
    def __init__(self, parent, variant="default"):
        # variant: "default", "elevated", "outlined"
```

#### StyledButton
```python
class StyledButton(ctk.CTkButton):
    """Gestylter Button mit Varianten"""
    
    def __init__(self, parent, variant="primary"):
        # variant: "primary", "secondary", "danger", "success", "neutral"
```

#### StyledEntry
```python
class StyledEntry(ctk.CTkEntry):
    """Gestyltes Eingabefeld"""
```

#### Tooltip
```python
class Tooltip:
    """Hover-Tooltip für Widgets"""
    
    def __init__(self, widget, text):
```

#### SmartCommandPalette
```python
class SmartCommandPalette(ctk.CTkFrame):
    """Suchfeld mit Autovervollständigung"""
```

#### ContextMenu
```python
class ContextMenu:
    """Rechtsklick-Kontextmenü"""
    
    def show(self, event, items):
        # items: [(label, command), ...]
```

---

## 6. UI-Module

### Struktur eines UI-Moduls:

```python
"""
Tool Name UI Module
Beschreibung des Tools
"""

import customtkinter as ctk
from design_constants import COLORS, SPACING
from ui_components import StyledCard, StyledButton, StyledEntry


class ToolNameUI:
    """UI für Tool Name"""
    
    def __init__(self, app, parent):
        """
        Args:
            app: Referenz auf NetToolsApp
            parent: Parent-Frame für dieses Tool
        """
        self.app = app
        self.parent = parent
        self.create_ui()
    
    def create_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Haupt-Container
        main_frame = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title = ctk.CTkLabel(
            main_frame,
            text="🔧 Tool Name",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(anchor="w")
        
        # Eingabebereich
        input_card = StyledCard(main_frame, variant="elevated")
        input_card.pack(fill="x", pady=15)
        
        # ... weitere UI-Elemente
    
    def _do_action(self):
        """Führt die Hauptaktion aus"""
        # Validierung
        # Threading für lange Operationen
        # UI-Update via self.app.after()
```

### Threading-Pattern für lange Operationen:

```python
def _start_scan(self):
    """Startet einen Scan"""
    # UI deaktivieren
    self.start_btn.configure(state="disabled")
    
    # In Thread ausführen
    def scan_thread():
        result = self._perform_scan()
        # UI-Update im Haupt-Thread!
        self.app.after(0, lambda: self._display_results(result))
    
    thread = threading.Thread(target=scan_thread, daemon=True)
    thread.start()

def _display_results(self, result):
    """Zeigt Ergebnisse an (im Haupt-Thread)"""
    # UI aktivieren
    self.start_btn.configure(state="normal")
    # Ergebnisse anzeigen
```

---

## 7. Tools-Module

### Struktur eines Tools-Moduls:

```python
"""
Tool Name Backend Module
Enthält die Logik für Tool Name
"""

import subprocess
from typing import Dict, List, Optional


class ToolName:
    """Backend-Logik für Tool Name"""
    
    @staticmethod
    def run(target: str, options: dict = None) -> Dict:
        """
        Führt die Tool-Operation aus.
        
        Args:
            target: Ziel (IP, Hostname, etc.)
            options: Optionale Parameter
            
        Returns:
            Dict mit 'success', 'output', 'error'
        """
        try:
            # Validierung
            if not target:
                return {"success": False, "error": "Kein Ziel angegeben"}
            
            # System-Befehl ausführen
            result = subprocess.run(
                ["tool", target],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

### Beispiel: TracerouteManager

```python
class TracerouteManager:
    """Verwaltet Traceroute-Verlauf für Vergleiche"""
    
    def __init__(self):
        self.history_dir = Path.home() / ".nettools"
        self.traces_file = self.history_dir / "traceroutes.json"
        self.traces = self.load_traces()
    
    def add_trace(self, target, output, success=True):
        """Speichert ein Traceroute-Ergebnis"""
        
    def get_traces(self, target=None):
        """Lädt gespeicherte Traces"""
        
    def compare_traces(self, trace1_id, trace2_id):
        """Vergleicht zwei Traceroutes"""
```

---

## 8. Design-System

### Farbschema:

| Farbe | Hex | Verwendung |
|-------|-----|------------|
| Electric Violet | #8B5CF6 | Primärfarbe, aktive Elemente |
| Neon Cyan | #00D9FF | Akzente, Links |
| Success Green | #22C55E | Erfolg, positive Werte |
| Danger Red | #EF4444 | Fehler, negative Werte |
| Warning Yellow | #F59E0B | Warnungen |
| Background | #1A1B26 | Haupt-Hintergrund |
| Card Background | #24253A | Karten-Hintergrund |

### Komponenten-Hierarchie:

```
App Window (bg_primary)
├── Sidebar (bg_secondary)
│   ├── Logo
│   ├── Search (SmartCommandPalette)
│   └── Navigation (Buttons)
│
└── Main Content (bg_primary)
    └── Tool UI
        ├── Title
        ├── StyledCard (elevated)
        │   ├── Inputs (StyledEntry)
        │   └── Buttons (StyledButton)
        │
        └── Results Area
```

### Abstands-System:

```
xs:  4px  - Minimal (zwischen Icons)
sm:  8px  - Klein (zwischen verwandten Elementen)
md: 16px  - Standard (Padding in Cards)
lg: 24px  - Groß (zwischen Sektionen)
xl: 32px  - Extra groß (Seiten-Ränder)
```

---

## 9. Konfiguration & Persistenz

### Konfigurations-Datei:

Speicherort: `~/.nettools/config.json`

```json
{
    "favorite_tools": ["scanner", "dns", "traceroute"],
    "enabled_tools": ["dashboard", "scanner", "dns", "..."],
    "window": {
        "width": 1400,
        "height": 900,
        "x": 100,
        "y": 100
    },
    "scan_profiles": {
        "office": {
            "ip_range": "192.168.1.0/24",
            "ports": "22,80,443"
        }
    }
}
```

### Laden & Speichern:

```python
class NetToolsApp:
    def __init__(self):
        self.config_file = Path.home() / ".nettools" / "config.json"
        
    def get_enabled_tools(self):
        """Lädt aktivierte Tools"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return set(config.get('enabled_tools', []))
        except:
            return self.default_tools
    
    def set_enabled_tools(self, tools):
        """Speichert Tool-Einstellungen"""
        config = self._load_config()
        config['enabled_tools'] = list(tools)
        self._save_config(config)
```

### Verlaufs-Speicherung:

```
~/.nettools/
├── config.json          # Haupt-Konfiguration
├── scans.json           # Scan-Verlauf
├── traceroutes.json     # Traceroute-Verlauf
├── dns_lookups.json     # DNS-Verlauf
└── port_scans.json      # Port-Scan-Verlauf
```

---

## 10. Neue Tools hinzufügen

### Schritt 1: Backend-Modul erstellen

`tools/neues_tool.py`:

```python
"""
Neues Tool Backend
"""

class NeuesTool:
    @staticmethod
    def run(target: str) -> dict:
        # Implementierung
        return {"success": True, "output": "..."}
```

### Schritt 2: UI-Modul erstellen

`ui/neues_tool_ui.py`:

```python
"""
Neues Tool UI Module
"""

import customtkinter as ctk
from design_constants import COLORS, SPACING
from ui_components import StyledCard, StyledButton


class NeuesToolUI:
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.create_ui()
    
    def create_ui(self):
        # UI-Code hier
        pass
```

### Schritt 3: In nettools_app.py registrieren

```python
# 1. Import hinzufügen
from ui.neues_tool_ui import NeuesToolUI

# 2. In nav_categories einfügen
nav_categories = [
    ("TOOLS", "🛠️", [
        # ...
        ("neues_tool", "🆕", "Neues Tool", "Beschreibung"),
    ]),
]

# 3. In switch_page hinzufügen
elif page_id == "neues_tool":
    NeuesToolUI(self, self.pages[page_id])

# 4. Status-Text hinzufügen
elif page_id == "neues_tool":
    self.status_label.configure(text="Beschreibung für Statusleiste")

# 5. In get_enabled_tools Default hinzufügen
all_tools = {
    # ...
    'neues_tool',
}
```

### Schritt 4: In settings_ui.py registrieren

```python
ALL_TOOLS = {
    # ...
    "neues_tool": {
        "name": "Neues Tool",
        "icon": "🆕",
        "category": "Tools",
        "default": True
    },
}
```

### Schritt 5: Command Palette (optional)

```python
# In nettools_app.py, tool_search_data:
("neues_tool", "🆕", "Neues Tool", ["keyword1", "keyword2"]),
```

---

## 11. Best Practices

### Threading:
- **IMMER** lange Operationen in separatem Thread
- UI-Updates **NUR** über `self.app.after(0, callback)`
- `daemon=True` für Threads setzen

### Error Handling:
```python
try:
    result = dangerous_operation()
except SpecificError as e:
    self.app.show_toast(f"Fehler: {e}", "error")
except Exception as e:
    print(f"Unerwarteter Fehler: {e}")
    self.app.show_toast("Ein Fehler ist aufgetreten", "error")
```

### UI-Konsistenz:
- Immer `COLORS` aus design_constants verwenden
- Immer `SPACING` für Abstände
- StyledCard für Container
- StyledButton für Aktionen

### Encoding:
```python
# Bei subprocess:
result = subprocess.run(
    cmd,
    capture_output=True,
    # NICHT text=True bei möglichen Sonderzeichen
)
# Manuell dekodieren:
output = result.stdout.decode('utf-8', errors='replace')
```

### Validierung:
```python
def _validate_input(self, value):
    if not value or not value.strip():
        self.app.show_toast("Bitte Wert eingeben", "warning")
        return None
    return value.strip()
```

---

## 12. Bekannte Probleme

### Emoji-Breite:
Emojis haben unterschiedliche Breiten je nach Font. 
**Lösung:** Einfache Zeichen verwenden oder fixe Breite mit `width` Parameter.

### Windows-Encoding:
Deutsche Sonderzeichen (ü, ö, ä) in Subprocess-Output.
**Lösung:** Bytes-Modus mit manueller Dekodierung.

### Admin-Rechte:
Manche Tools benötigen Admin-Rechte (ARP, manche Scans).
**Lösung:** `is_admin()` prüfen, `restart_as_admin()` anbieten.

### PSExec Cross-Domain:
PSExec funktioniert nicht zuverlässig über Domain-Grenzen.
**Status:** Feature temporär deaktiviert.

---

## 13. Weiterentwicklung

### Geplante Features:
1. **Netzwerk-Topologie-Visualisierung**
2. **PDF-Export für Berichte**
3. **Automatische Updates**
4. **Plugin-System**
5. **Dark/Light Mode Toggle**

### Refactoring-Bedarf:
1. **nettools_app.py** ist sehr groß → In Module aufteilen
2. **Inline-UI-Code** (Scanner, DNS) → In separate Dateien verschieben
3. **Test-Coverage** → Unit-Tests hinzufügen

### Beitragen:
1. Fork erstellen
2. Feature-Branch anlegen
3. Code nach Best Practices
4. Pull Request mit Beschreibung

---

## Anhang: Code-Referenz

### Wichtige Klassen:

| Klasse | Datei | Beschreibung |
|--------|-------|--------------|
| `NetToolsApp` | nettools_app.py | Hauptanwendung |
| `StyledCard` | ui_components.py | Karten-Container |
| `StyledButton` | ui_components.py | Gestylter Button |
| `SmartCommandPalette` | ui_components.py | Suchfeld |
| `TracerouteManager` | tools/traceroute_manager.py | Traceroute-Verlauf |
| `ScanManager` | tools/scan_manager.py | Scan-Speicherung |
| `SettingsUI` | ui/settings_ui.py | Einstellungen-UI |

### Wichtige Funktionen:

| Funktion | Datei | Beschreibung |
|----------|-------|--------------|
| `switch_page()` | nettools_app.py | Seiten-Wechsel |
| `show_toast()` | nettools_app.py | Benachrichtigung |
| `get_enabled_tools()` | nettools_app.py | Tool-Einstellungen laden |
| `is_admin()` | nettools_app.py | Admin-Prüfung |

---

**© 2024 NetTools Suite - Technische Dokumentation**
