# NetTools Suite - Product Requirements Document

## Projektstatus: Phase 1 Abgeschlossen ✅

**Copyright:** frekms  
**Version:** 1.0.0  
**Technologie:** Rust + Tauri + React + TypeScript  
**Zielplattform:** Windows 10/11  

---

## 🎯 Original Problem Statement

Der Benutzer hatte eine Python/customtkinter Desktop-Anwendung für Netzwerk-Utilities und wollte diese auf eine Windows-optimierte native Version migrieren. Nach Evaluierung verschiedener Optionen (C#/.NET, WPF, Electron) wurde **Rust + Tauri** als optimale Lösung gewählt.

### Entscheidung gegen .NET
- Benutzer wollte kein .NET Framework
- Tauri bietet: Kleinere EXE (~10-20MB statt 150MB+), bessere Performance, modernes UI

### Design-Anforderungen
- Design aus den bereitgestellten Guidelines
- OHNE "Lünefire" Branding
- OHNE Logo
- Copyright: **frekms**

---

## ✅ Abgeschlossene Arbeiten

### Phase 1: Infrastruktur & Design-System (14.01.2025)

#### Frontend (React + TypeScript)
- [x] Projekt-Setup mit Vite
- [x] Tailwind CSS Design-System
- [x] Dark Theme (gemäß Guidelines)
- [x] UI-Komponenten:
  - Button, Card, Input, Select, Checkbox
  - Toast Notifications
  - DataTable mit Pagination
  - Badge, Alert, Dropdown
  - CopyButton, CodeBlock
- [x] Layout-Komponenten:
  - Sidebar mit Kategorien & Favoriten
  - Header mit Schnellsuche
  - Command Palette (Ctrl+K)
- [x] Seiten:
  - Dashboard mit Statistiken & Schnellzugriff
  - Einstellungen (Tool-Sichtbarkeit)
  - Placeholder-Seiten für alle Tools
- [x] State Management (Zustand)
- [x] Persistente Einstellungen

#### Backend (Rust)
- [x] Tauri-Konfiguration
- [x] Command-Module implementiert:
  - Scanner (Ping, Netzwerk-Scan)
  - Port Scanner
  - DNS Lookup
  - Traceroute
  - ARP Viewer
  - Subnet Calculator
  - WHOIS Lookup
  - SSL Checker
  - Hash Generator
  - Password Generator
  - Utility Commands

---

## 📋 Ausstehende Phasen

### Phase 2: Tool-Frontend Implementation
- [ ] IPv4 Scanner UI mit Live-Monitoring
- [ ] Port Scanner UI
- [ ] Scan-Profile speichern/laden
- [ ] Export (CSV, JSON)
- [ ] Scan-Vergleich

### Phase 3: Netzwerk-Tools UI
- [ ] DNS Lookup UI mit Vergleich
- [ ] Traceroute UI mit Vergleich
- [ ] ARP Viewer UI
- [ ] Subnet Calculator UI
- [ ] Bandwidth Test UI (iperf3)

### Phase 4: Lookup-Tools UI
- [ ] WHOIS Lookup UI
- [ ] SSL Checker UI
- [ ] MAC Formatter & OUI Lookup UI

### Phase 5: Utilities UI
- [ ] Hash Generator UI
- [ ] Password Generator UI
- [ ] API/HTTP Tester UI

### Phase 6: Palo Alto Integration
- [ ] PAN-OS Config Generator UI

### Phase 7: Polish & Release
- [ ] Windows Installer (MSI/NSIS)
- [ ] Auto-Updater
- [ ] Optimierungen

---

## 🔧 Technische Architektur

### Frontend
```
/app/nettools-tauri/src/
├── components/
│   ├── ui/          # Button, Card, Input, etc.
│   └── layout/      # Sidebar, Header, CommandPalette
├── pages/           # Dashboard, Settings, Tools
├── store/           # Zustand State
├── styles/          # Global CSS
├── types/           # TypeScript Types
└── lib/             # Utilities
```

### Backend
```
/app/nettools-tauri/src-tauri/src/
├── main.rs          # Entry Point
└── commands/        # Tauri Commands
    ├── scanner.rs
    ├── port_scanner.rs
    ├── dns.rs
    ├── traceroute.rs
    ├── arp.rs
    ├── subnet.rs
    ├── whois.rs
    ├── ssl.rs
    ├── hash.rs
    ├── password.rs
    └── utils.rs
```

---

## 🎨 Design-System

| Element | Wert |
|---------|------|
| Hintergrund | `#282C34` |
| Sidebar | `#21252B` |
| Cards | `#2F3336` |
| Akzent Blau | `#007BFF` |
| Akzent Grün | `#28A745` |
| Akzent Rot | `#DC3545` |
| Text Primär | `#FFFFFF` |
| Text Sekundär | `#ADB5BD` |
| Schriftart | Segoe UI |

---

## ⌨️ Tastenkürzel

| Kürzel | Aktion |
|--------|--------|
| Ctrl+K | Schnellsuche |
| Ctrl+1-9 | Tool wechseln |
| Ctrl+, | Einstellungen |

---

## 🚫 Ausgeschlossene Features

- DNSDumpster API
- MXToolbox API  
- Speedtest.net
- phpIPAM Integration

---

## 📝 Nächste Schritte

1. **User-Test:** Benutzer kann Frontend auf Emergent testen (http://localhost:1420 während dev)
2. **Windows-Build:** Benutzer lädt Projekt herunter und kompiliert auf Windows-PC
3. **Phase 2-6:** Schrittweise Tool-UIs implementieren
4. **Release:** Windows Installer erstellen

---

## 📁 Projektdateien

- `/app/nettools-tauri/` - Hauptprojekt
- `/app/nettools-tauri/README.md` - Build-Anleitung
- `/app/nettools-tauri/DEVELOPMENT_PLAN.md` - Entwicklungsplan
