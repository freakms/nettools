# NetTools Suite - Code Review Übersicht

## 📋 Projekt-Steckbrief

| Eigenschaft | Wert |
|-------------|------|
| **Name** | NetTools Suite |
| **Version** | 2.0 |
| **Sprache** | Python 3.10+ |
| **GUI-Framework** | CustomTkinter |
| **Lizenz** | MIT |
| **Plattform** | Windows (primär) |

---

## 🏗️ Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              nettools_app.py (Hauptanwendung)            │   │
│  │         - Fenster-Management, Navigation, Events         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    UI-Module (/ui/)                      │   │
│  │   scanner_ui.py │ dns_ui.py │ traceroute_ui.py │ ...    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Shared Components                           │   │
│  │     ui_components.py │ design_constants.py               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BUSINESS LOGIC LAYER                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 Tools-Module (/tools/)                   │   │
│  │  scanner.py │ dns_lookup.py │ traceroute.py │ ...       │   │
│  │         - Netzwerk-Operationen, Datenverarbeitung        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SYSTEM LAYER                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              System-Aufrufe & Bibliotheken               │   │
│  │   subprocess (ping, tracert, nbtstat, arp)              │   │
│  │   socket (DNS, SNMP, NetBIOS)                           │   │
│  │   pythonping, dnspython, requests                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Verzeichnisstruktur

```
/app/
│
├── nettools_app.py          # 🎯 HAUPTDATEI - Entry Point (~4500 Zeilen)
├── design_constants.py      # 🎨 Farben, Fonts, Abstände
├── ui_components.py         # 🧩 Wiederverwendbare UI-Komponenten
│
├── /ui/                     # 📱 UI-Module (je Tool eine Datei)
│   ├── scanner_ui.py        #    IPv4 Scanner Oberfläche
│   ├── dns_ui.py            #    DNS Lookup Oberfläche
│   ├── traceroute_ui.py     #    Traceroute Oberfläche
│   ├── portscan_ui.py       #    Port Scanner Oberfläche
│   ├── whois_ui.py          #    WHOIS Lookup
│   ├── ssl_checker_ui.py    #    SSL Zertifikat-Prüfer
│   ├── hash_generator_ui.py #    Hash Generator
│   ├── password_generator_ui.py # Passwort Generator
│   ├── api_tester_ui.py     #    REST API Tester
│   ├── arp_viewer_ui.py     #    ARP Tabelle
│   ├── speedtest_ui.py      #    Internet Speedtest
│   ├── bandwidth_ui.py      #    iPerf Bandwidth Test
│   ├── settings_ui.py       #    Einstellungen
│   └── ...
│
├── /tools/                  # ⚙️ Backend-Logik (Netzwerk-Operationen)
│   ├── scanner.py           #    IPv4 Scanner + SNMP/NetBIOS
│   ├── dns_lookup.py        #    DNS Abfragen
│   ├── traceroute.py        #    Traceroute Logik
│   ├── port_scanner.py      #    Port Scanning
│   ├── subnet_calculator.py #    Subnetz-Berechnungen
│   ├── mac_formatter.py     #    MAC-Adressen Formatierung
│   ├── live_ping_monitor.py #    Live Ping Monitoring
│   ├── history_manager.py   #    Verlaufs-Speicherung
│   └── ...
│
├── /docs/                   # 📚 Dokumentation
│   ├── Benutzerhandbuch_DE.md
│   ├── Benutzerhandbuch_DE.pdf
│   ├── Entwickler_Dokumentation_DE.md
│   ├── Entwickler_Dokumentation_DE.pdf
│   └── NetTools_Compliance_Report.pdf
│
├── requirements.txt         # 📦 Python-Abhängigkeiten
├── build_exe_fast.py        # 🔨 PyInstaller Build-Skript
└── LICENSE.txt              # ⚖️ MIT Lizenz
```

---

## 🔧 Kern-Komponenten

### 1. nettools_app.py (Hauptanwendung)

```python
class NetToolsApp(ctk.CTk):
    """
    Zentrale Anwendungsklasse
    - Fenster-Initialisierung
    - Sidebar-Navigation
    - Seiten-Wechsel (Lazy Loading)
    - Keyboard Shortcuts
    - Theme-Management
    """
```

**Wichtige Methoden:**
| Methode | Funktion |
|---------|----------|
| `create_sidebar()` | Erstellt Navigation mit Kategorien |
| `switch_page(id)` | Wechselt Tool-Ansicht (Lazy Loading) |
| `toggle_sidebar()` | Klappt Sidebar ein/aus |
| `show_toast(msg)` | Zeigt Benachrichtigung |

### 2. design_constants.py (Design-System)

```python
COLORS = {
    "bg_primary": "#1A1B26",      # Haupthintergrund
    "electric_violet": "#8B5CF6", # Primärfarbe
    "neon_cyan": "#00D9FF",       # Akzentfarbe
    "success": "#22C55E",         # Erfolg
    "danger": "#EF4444",          # Fehler
}

SPACING = {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32}
```

### 3. ui_components.py (Shared Components)

| Komponente | Beschreibung |
|------------|--------------|
| `StyledButton` | Einheitlicher Button mit Varianten |
| `StyledCard` | Container mit Schatten/Border |
| `StyledEntry` | Eingabefeld mit Icon-Support |
| `SectionTitle` | Abschnitts-Überschrift |
| `Tooltip` | Hover-Hinweise |

---

## 🛠️ Tools-Module im Detail

### Scanner (tools/scanner.py)
```
IPv4Scanner
├── parse_cidr()           # IP-Bereich parsen
├── ping_host()            # Einzelnen Host pingen
├── scan_network()         # Netzwerk-Scan durchführen
└── resolve_hostname()     # Hostname auflösen
    ├── resolve_dns()      # DNS Reverse Lookup
    ├── resolve_snmp()     # SNMP sysName (Switches!)
    ├── resolve_netbios_raw() # NetBIOS UDP 137
    ├── resolve_nbtstat()  # Windows nbtstat
    ├── resolve_smb_hostname() # SMB Port 445
    └── resolve_wmi()      # WMI Abfrage
```

### DNS Lookup (tools/dns_lookup.py)
```
DNSLookup
├── lookup()              # DNS Abfrage
├── get_record_types()    # A, AAAA, MX, NS, TXT, CNAME
└── reverse_lookup()      # PTR Record
```

---

## 🔄 Datenfluss

```
┌──────────┐    Click    ┌──────────┐   Callback   ┌──────────┐
│   User   │ ─────────▶  │  UI-Modul │ ──────────▶ │  Tool    │
│          │             │(scanner_ui)│             │(scanner) │
└──────────┘             └──────────┘             └──────────┘
                               │                        │
                               │                        ▼
                               │              ┌──────────────────┐
                               │              │  System-Aufruf   │
                               │              │  (ping, socket)  │
                               │              └──────────────────┘
                               │                        │
                               ▼                        ▼
                         ┌──────────┐           ┌──────────┐
                         │   GUI    │ ◀──────── │ Ergebnis │
                         │  Update  │  after()  │   Dict   │
                         └──────────┘           └──────────┘
```

**Threading-Regel:** Lange Operationen in separatem Thread, UI-Updates über `self.app.after(0, callback)`

---

## 📊 Tool-Übersicht

### Scanning
| Tool | Datei | Funktion |
|------|-------|----------|
| IPv4 Scanner | `scanner.py` / `scanner_ui.py` | Netzwerk nach Hosts scannen |
| Port Scanner | `port_scanner.py` / `portscan_ui.py` | Offene Ports finden |
| Traceroute | `traceroute.py` / `traceroute_ui.py` | Netzwerkpfad verfolgen |
| ARP Viewer | `arp_viewer_ui.py` | ARP-Cache anzeigen |

### Netzwerk-Tools
| Tool | Datei | Funktion |
|------|-------|----------|
| DNS Lookup | `dns_lookup.py` / `dns_ui.py` | DNS Records abfragen |
| WHOIS | `whois_ui.py` | Domain-Eigentümer |
| SSL Checker | `ssl_checker_ui.py` | Zertifikate prüfen |
| Subnet Calc | `subnet_calculator.py` | Subnetz berechnen |

### Sicherheit
| Tool | Datei | Funktion |
|------|-------|----------|
| Hash Generator | `hash_generator_ui.py` | MD5, SHA256, etc. |
| Password Gen | `password_generator_ui.py` | Sichere Passwörter |

### Testing
| Tool | Datei | Funktion |
|------|-------|----------|
| API Tester | `api_tester_ui.py` | REST APIs testen |
| Speedtest | `speedtest_ui.py` | Internet-Geschwindigkeit |
| Bandwidth | `bandwidth_ui.py` | iPerf3 Tests |

---

## 🔑 Wichtige Design-Patterns

### 1. Lazy Loading
```python
# Seiten werden erst bei Bedarf geladen
if page_id not in self.pages_loaded:
    self.create_scanner_content(self.pages[page_id])
    self.pages_loaded[page_id] = True
```

### 2. Threading für Netzwerk-Operationen
```python
def start_scan(self):
    thread = threading.Thread(
        target=self.scanner.scan_network,
        args=(cidr,),
        daemon=True
    )
    thread.start()
```

### 3. UI-Updates über after()
```python
def on_scan_complete(self, results):
    # Sicher im Main-Thread ausführen
    self.app.after(0, lambda: self.display_results(results))
```

### 4. Konfiguration über JSON
```python
# ~/.nettools/config.json
{
    "favorite_tools": ["scanner", "dns"],
    "enabled_tools": ["dashboard", "scanner", ...],
    "theme": "dark"
}
```

---

## 📦 Abhängigkeiten (requirements.txt)

| Bibliothek | Version | Verwendung |
|------------|---------|------------|
| customtkinter | >= 5.2.0 | GUI-Framework |
| pythonping | >= 1.1.4 | ICMP Ping |
| dnspython | >= 2.4.0 | DNS Abfragen |
| requests | >= 2.31.0 | HTTP Requests |
| matplotlib | >= 3.7.0 | Diagramme |
| Pillow | >= 10.0.0 | Bildverarbeitung |
| speedtest-cli | latest | Speedtest |
| pyinstaller | >= 6.0.0 | EXE-Build |

---

## 🚀 Build-Prozess

```bash
# Standalone .exe erstellen
python build_exe_fast.py

# Ergebnis in /dist/NetTools.exe (~50-80 MB)
```

---

## 📈 Statistiken

| Metrik | Wert |
|--------|------|
| Haupt-Datei | ~4.500 Zeilen |
| UI-Module | 15 Dateien |
| Tools-Module | 12 Dateien |
| Gesamt Python | ~15.000 Zeilen |

---

## 🔍 Code-Qualität

### Stärken ✅
- Modulare Architektur (UI/Tools getrennt)
- Einheitliches Design-System
- Lazy Loading für Performance
- Threaded Netzwerk-Operationen
- Konfigurierbare Tools

### Verbesserungspotential 🔄
- Einige bare `except:` Blöcke
- Haupt-Datei könnte aufgeteilt werden
- Unit-Tests ausbaubar
- Type Hints erweitern

---

*Erstellt: Dezember 2024 | Version 2.0*
