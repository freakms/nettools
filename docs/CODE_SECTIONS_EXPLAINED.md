# NetTools Suite - Code-Abschnitte Erklärt

## 📍 Wo macht der Code was?

Diese Übersicht zeigt die wichtigsten Code-Stellen mit Erklärungen.

---

## 1️⃣ ANWENDUNGSSTART (nettools_app.py, Zeile 1-50)

```python
#!/usr/bin/env python3
"""
NetTools Suite - IPv4 Scanner & MAC Formatter
"""

# ═══════════════════════════════════════════════════════════════
# IMPORTS - Alle benötigten Bibliotheken
# ═══════════════════════════════════════════════════════════════

import customtkinter as ctk          # GUI-Framework (moderne Oberfläche)
from tkinter import messagebox       # Standard-Dialoge
import threading                     # Parallelverarbeitung (wichtig!)
import subprocess                    # System-Befehle ausführen
import socket                        # Netzwerk-Operationen

# UI-Module importieren (jedes Tool hat eigene Datei)
from ui.dashboard_ui import DashboardUI
from ui.scanner_ui import ScannerUI
from ui.dns_ui import DNSLookupUI
# ... weitere Tools
```

**Was passiert hier?**
- CustomTkinter für moderne GUI laden
- Threading für nicht-blockierende Netzwerk-Operationen
- Alle UI-Module werden importiert

---

## 2️⃣ HAUPTKLASSE INITIALISIERUNG (Zeile 130-220)

```python
class NetToolsApp(ctk.CTk):
    """Hauptanwendung - erbt von CustomTkinter Fenster"""
    
    def __init__(self):
        super().__init__()
        
        # ═══════════════════════════════════════════════════════
        # FENSTER-KONFIGURATION
        # ═══════════════════════════════════════════════════════
        self.title("NetTools Suite")
        self.geometry("1400x900")
        
        # ═══════════════════════════════════════════════════════
        # MANAGER-INSTANZEN (Backend-Logik)
        # ═══════════════════════════════════════════════════════
        self.scanner = IPv4Scanner()           # Netzwerk-Scanner
        self.history = HistoryManager()        # Verlauf speichern
        self.scan_manager = ScanManager()      # Scan-Verwaltung
        self.traceroute_manager = TracerouteManager()  # Traceroute-Verlauf
        
        # ═══════════════════════════════════════════════════════
        # UI AUFBAUEN (Reihenfolge wichtig!)
        # ═══════════════════════════════════════════════════════
        self.create_sidebar()      # 1. Navigation links
        self.create_status_bar()   # 2. Status unten
        self.create_main_content() # 3. Hauptbereich
        
        # ═══════════════════════════════════════════════════════
        # TASTENKOMBINATIONEN
        # ═══════════════════════════════════════════════════════
        self.bind('<Control-k>', self.open_quick_switcher)  # Schnellsuche
        self.bind('<Control-b>', lambda e: self.toggle_sidebar())
```

**Was passiert hier?**
- Fenster-Eigenschaften setzen (Titel, Größe)
- Backend-Manager erstellen
- UI-Komponenten in richtiger Reihenfolge aufbauen
- Keyboard-Shortcuts registrieren

---

## 3️⃣ SIDEBAR-NAVIGATION (Zeile 700-1020)

```python
def create_sidebar(self):
    """Erstellt die linke Navigation mit Kategorien"""
    
    # ═══════════════════════════════════════════════════════════
    # SIDEBAR-CONTAINER
    # ═══════════════════════════════════════════════════════════
    self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
    self.sidebar.pack(side="left", fill="y")
    
    # ═══════════════════════════════════════════════════════════
    # TOOL-KATEGORIEN DEFINIEREN
    # ═══════════════════════════════════════════════════════════
    self.nav_categories = [
        ("🏠 Dashboard", "dashboard", [
            ("dashboard", "🏠", "Dashboard", "Übersicht"),
        ]),
        ("🔍 Scanning", "scanning", [
            ("scanner", "📡", "IPv4 Scanner", "Netzwerk scannen"),
            ("portscan", "🔌", "Port Scanner", "Ports prüfen"),
            ("traceroute", "⤳", "Traceroute", "Route verfolgen"),
        ]),
        ("🌐 Netzwerk", "network", [
            ("dns", "🌐", "DNS Lookup", "DNS abfragen"),
            ("whois", "🔍", "WHOIS", "Domain-Info"),
            ("ssl", "🔒", "SSL Checker", "Zertifikate"),
        ]),
        # ... weitere Kategorien
    ]
    
    # ═══════════════════════════════════════════════════════════
    # BUTTONS FÜR JEDES TOOL ERSTELLEN
    # ═══════════════════════════════════════════════════════════
    for page_id, icon, label, tooltip in items:
        btn = ctk.CTkButton(
            self.nav_scroll,
            text=f"  {icon}   {label}",
            command=lambda p=page_id: self.switch_tool(p),  # ← Klick-Handler
            anchor="w",
            fg_color="transparent"
        )
        btn.pack(fill="x")
        self.nav_buttons[page_id] = btn  # Referenz speichern
```

**Was passiert hier?**
- Sidebar-Container links erstellen
- Alle Tools in Kategorien organisieren
- Für jedes Tool einen Button mit Icon erstellen
- Klick ruft `switch_tool()` auf

---

## 4️⃣ SEITEN-WECHSEL MIT LAZY LOADING (Zeile 1200-1290)

```python
def switch_page(self, page_id):
    """Wechselt zur gewählten Tool-Seite"""
    
    # ═══════════════════════════════════════════════════════════
    # LAZY LOADING - Seite nur bei Bedarf erstellen
    # ═══════════════════════════════════════════════════════════
    if page_id not in self.pages_loaded:
        
        # Je nach Tool die richtige UI-Klasse laden
        if page_id == "dashboard":
            DashboardUI(self, self.pages[page_id])
            
        elif page_id == "scanner":
            ScannerUI(self, self.pages[page_id])
            
        elif page_id == "dns":
            DNSLookupUI(self, self.pages[page_id])
            
        elif page_id == "traceroute":
            TracerouteUI(self, self.pages[page_id])
            
        # ... weitere Tools
        
        self.pages_loaded[page_id] = True  # Als geladen markieren
    
    # ═══════════════════════════════════════════════════════════
    # SEITE ANZEIGEN MIT ANIMATION
    # ═══════════════════════════════════════════════════════════
    self.pages[page_id].pack(fill="both", expand=True)
    self._fade_in_page(self.pages[page_id])
```

**Was passiert hier?**
- Prüfen ob Seite schon geladen wurde
- Wenn nicht: UI-Klasse instantiieren
- Seite anzeigen mit Fade-In Animation
- **Vorteil:** Schnellerer App-Start, nur genutzte Tools werden geladen

---

## 5️⃣ SCANNER - NETZWERK SCANNEN (tools/scanner.py, Zeile 600-680)

```python
def scan_network(self, cidr, aggression="normal"):
    """
    Scannt ein Netzwerk nach aktiven Hosts
    
    Args:
        cidr: IP-Bereich z.B. "192.168.1.0/24"
        aggression: "quiet", "normal", oder "aggressive"
    """
    
    # ═══════════════════════════════════════════════════════════
    # IP-BEREICH PARSEN
    # ═══════════════════════════════════════════════════════════
    try:
        ips = self.parse_cidr(cidr)  # z.B. 254 IPs bei /24
    except ValueError as e:
        self.complete_callback({"error": str(e)})
        return
    
    # ═══════════════════════════════════════════════════════════
    # PARALLEL SCANNEN MIT THREAD-POOL
    # ═══════════════════════════════════════════════════════════
    max_workers = {"quiet": 20, "normal": 50, "aggressive": 100}
    
    with ThreadPoolExecutor(max_workers=max_workers[aggression]) as executor:
        # Alle IPs parallel pingen
        futures = {
            executor.submit(self.ping_host, ip): ip 
            for ip in ips
        }
        
        for future in as_completed(futures):
            result = future.result()
            if result and result.get('responding'):
                self.results.append(result)
                
                # UI über Fortschritt informieren
                if self.progress_callback:
                    self.progress_callback(result)
    
    # ═══════════════════════════════════════════════════════════
    # SCAN ABGESCHLOSSEN
    # ═══════════════════════════════════════════════════════════
    if self.complete_callback:
        self.complete_callback(self.results)
```

**Was passiert hier?**
- CIDR-Notation in IP-Liste umwandeln
- ThreadPoolExecutor für parallele Scans (50 gleichzeitig)
- Jeden Host pingen und Ergebnis sammeln
- UI über Callback informieren

---

## 6️⃣ HOSTNAME-AUFLÖSUNG (tools/scanner.py, Zeile 430-500)

```python
def resolve_hostname(self, ip, timeout=1):
    """
    Löst Hostname auf mit mehreren Methoden (wie Advanced IP Scanner)
    
    Reihenfolge:
    1. DNS Reverse Lookup
    2. SNMP sysName (für Switches!)
    3. NetBIOS
    4. nbtstat
    """
    
    # ═══════════════════════════════════════════════════════════
    # METHODE 1: DNS REVERSE LOOKUP
    # ═══════════════════════════════════════════════════════════
    hostname = self.resolve_dns(ip, timeout=0.5)
    if hostname:
        return hostname
    
    # ═══════════════════════════════════════════════════════════
    # METHODE 2: SNMP (für Switches, Router, Drucker)
    # ═══════════════════════════════════════════════════════════
    hostname = self.resolve_snmp(ip, timeout=1)
    if hostname:
        return hostname
    
    # ═══════════════════════════════════════════════════════════
    # METHODE 3: NetBIOS (Windows-Geräte)
    # ═══════════════════════════════════════════════════════════
    hostname = self.resolve_netbios_raw(ip, timeout=1)
    if hostname:
        return hostname
    
    return ""  # Kein Hostname gefunden
```

**Was passiert hier?**
- Mehrere Methoden nacheinander probieren
- DNS für registrierte Hosts
- SNMP für Netzwerkgeräte (Switches!)
- NetBIOS für Windows-PCs

---

## 7️⃣ SNMP-ABFRAGE FÜR SWITCHES (tools/scanner.py, Zeile 480-540)

```python
def _snmp_get_sysname(self, ip, community, timeout):
    """Fragt Switch/Router nach seinem Namen via SNMP"""
    
    # ═══════════════════════════════════════════════════════════
    # SNMP-PAKET AUFBAUEN (OID 1.3.6.1.2.1.1.5.0 = sysName)
    # ═══════════════════════════════════════════════════════════
    oid_bytes = bytes([0x2b, 0x06, 0x01, 0x02, 0x01, 0x01, 0x05, 0x00])
    
    # ... Paket zusammenbauen ...
    
    # ═══════════════════════════════════════════════════════════
    # UDP-PAKET AN PORT 161 SENDEN
    # ═══════════════════════════════════════════════════════════
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    sock.sendto(message, (ip, 161))  # SNMP Port
    
    # ═══════════════════════════════════════════════════════════
    # ANTWORT PARSEN
    # ═══════════════════════════════════════════════════════════
    response, _ = sock.recvfrom(2048)
    return self._parse_snmp_response(response)
```

**Was passiert hier?**
- SNMP GET-Request für sysName OID bauen
- UDP-Paket an Port 161 senden
- Antwort parsen und Hostname extrahieren
- **Wichtig:** Das ermöglicht Hostnamen von Switches!

---

## 8️⃣ UI-MODUL STRUKTUR (ui/scanner_ui.py)

```python
class ScannerUI:
    """UI-Modul für den IPv4 Scanner"""
    
    def __init__(self, app, parent):
        """
        Args:
            app: Referenz zur Hauptanwendung (NetToolsApp)
            parent: Container-Frame für dieses Tool
        """
        self.app = app      # Für Zugriff auf Scanner, Toast, etc.
        self.parent = parent
        self.create_ui()
    
    def create_ui(self):
        """Baut die Benutzeroberfläche auf"""
        
        # ═══════════════════════════════════════════════════════
        # EINGABE-BEREICH
        # ═══════════════════════════════════════════════════════
        input_card = StyledCard(self.parent)
        
        self.ip_entry = ctk.CTkEntry(input_card, placeholder_text="192.168.1.0/24")
        self.scan_btn = StyledButton(input_card, text="Scan starten",
                                     command=self.start_scan)
        
        # ═══════════════════════════════════════════════════════
        # ERGEBNIS-TABELLE
        # ═══════════════════════════════════════════════════════
        self.results_tree = ttk.Treeview(columns=["IP", "Hostname", "MAC"])
    
    def start_scan(self):
        """Startet den Scan in separatem Thread"""
        
        cidr = self.ip_entry.get()
        
        # ═══════════════════════════════════════════════════════
        # WICHTIG: Netzwerk-Operation in Thread!
        # ═══════════════════════════════════════════════════════
        thread = threading.Thread(
            target=self.app.scanner.scan_network,
            args=(cidr,),
            daemon=True  # Thread beendet sich mit App
        )
        thread.start()
    
    def on_scan_complete(self, results):
        """Callback wenn Scan fertig - UI aktualisieren"""
        
        # ═══════════════════════════════════════════════════════
        # WICHTIG: UI-Update nur im Main-Thread!
        # ═══════════════════════════════════════════════════════
        self.app.after(0, lambda: self.display_results(results))
```

**Was passiert hier?**
- UI-Klasse bekommt App-Referenz und Parent-Container
- Eingabefelder und Buttons erstellen
- **Scan in Thread starten** (blockiert nicht die GUI!)
- **UI-Updates über `after()`** (Thread-sicher)

---

## 9️⃣ DESIGN-KONSTANTEN (design_constants.py)

```python
# ═══════════════════════════════════════════════════════════════
# FARBSCHEMA (Dark Theme)
# ═══════════════════════════════════════════════════════════════
COLORS = {
    # Hintergrund
    "bg_primary": ("#1A1B26", "#1A1B26"),      # Dunkel
    "bg_secondary": ("#24253A", "#24253A"),    # Etwas heller
    
    # Akzentfarben
    "electric_violet": ("#8B5CF6", "#A78BFA"), # Primär (Lila)
    "neon_cyan": ("#00D9FF", "#67E8F9"),       # Sekundär (Cyan)
    
    # Status
    "success": ("#22C55E", "#4ADE80"),         # Grün
    "danger": ("#EF4444", "#F87171"),          # Rot
    "warning": ("#F59E0B", "#FBBF24"),         # Gelb
    
    # Text
    "text_primary": ("#E2E8F0", "#E2E8F0"),    # Hell
    "text_secondary": ("#94A3B8", "#94A3B8"),  # Gedimmt
}

# ═══════════════════════════════════════════════════════════════
# ABSTÄNDE (Einheitliches Spacing)
# ═══════════════════════════════════════════════════════════════
SPACING = {
    "xs": 4,    # Minimal
    "sm": 8,    # Klein
    "md": 16,   # Standard
    "lg": 24,   # Groß
    "xl": 32,   # Extra groß
}

# ═══════════════════════════════════════════════════════════════
# SCHRIFTGRÖSSEN
# ═══════════════════════════════════════════════════════════════
FONT_SIZES = {
    "title": 24,
    "heading": 18,
    "subheading": 14,
    "body": 12,
    "small": 10,
}
```

**Was passiert hier?**
- Zentrale Definition aller Farben
- Einheitliche Abstände für konsistentes Layout
- Schriftgrößen-Hierarchie

---

## 🔟 THREADING-MUSTER (Wichtig!)

```python
# ═══════════════════════════════════════════════════════════════
# FALSCH ❌ - Blockiert die GUI
# ═══════════════════════════════════════════════════════════════
def start_scan(self):
    results = self.scanner.scan_network(cidr)  # GUI friert ein!
    self.display_results(results)


# ═══════════════════════════════════════════════════════════════
# RICHTIG ✅ - Separater Thread + Callback
# ═══════════════════════════════════════════════════════════════
def start_scan(self):
    # Scanner Callbacks setzen
    self.scanner.progress_callback = self.on_progress
    self.scanner.complete_callback = self.on_complete
    
    # In Thread ausführen
    thread = threading.Thread(
        target=self.scanner.scan_network,
        args=(cidr,),
        daemon=True
    )
    thread.start()

def on_complete(self, results):
    # UI-Update im Main-Thread!
    self.app.after(0, lambda: self.display_results(results))
```

**Regel:** Alle Netzwerk-Operationen in Thread, alle UI-Updates über `after()`

---

## 📊 Zusammenfassung: Code-Fluss

```
┌─────────────────────────────────────────────────────────────┐
│ 1. APP-START                                                │
│    nettools_app.py → __init__() → create_sidebar()          │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. USER KLICKT TOOL                                         │
│    nav_button.command → switch_tool() → switch_page()       │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. LAZY LOADING                                             │
│    if not loaded: ScannerUI(app, parent)                    │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. USER STARTET AKTION                                      │
│    scan_btn.command → start_scan()                          │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. THREAD STARTET                                           │
│    Thread(target=scanner.scan_network).start()              │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. BACKEND ARBEITET                                         │
│    scanner.py → ping_host() → resolve_hostname()            │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. CALLBACK → UI UPDATE                                     │
│    complete_callback() → app.after(0, display_results)      │
└─────────────────────────────────────────────────────────────┘
```

---

*Erstellt für Code Review | NetTools Suite v2.0*
