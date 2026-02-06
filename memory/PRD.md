# NetTools Suite - Product Requirements Document

## Projektstatus: Phase 2 In Arbeit 🔄

**Copyright:** frekms  
**Version:** 1.1.0  
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
- [x] UI-Komponenten (Button, Card, Input, etc.)
- [x] Layout-Komponenten (Sidebar, Header)
- [x] Alle 14 Tool-Seiten implementiert
- [x] State Management (Zustand)
- [x] Persistente Einstellungen

#### Backend (Rust)
- [x] Tauri-Konfiguration
- [x] Alle Command-Module implementiert

### Phase 2: Erweiterte Features (In Arbeit)

#### Dezember 2025 Updates:
- [x] **Live Ping Monitor** - Echtzeit-Ping mit Multi-Host-Support (CIDR, Ranges)
- [x] **Scanner** - History, Vergleich, Profile, Statistiken
- [x] **Port Scanner** - History, Vergleich, Port-Presets
- [x] **DNS Lookup** - Server-Auswahl, externe Lookup-Services
- [x] **MAC Formatter** - Switch-Commands für verschiedene Hersteller
- [x] **Deutsche OS-Kompatibilität** - Parsing für deutsche Windows-Ausgaben

#### Dezember 2025 - Bugfixes:
- [x] **Konsolenfenster-Bug behoben** - `CREATE_NO_WINDOW` Flag implementiert
- [x] **MAC Formatter - Huawei Format** - 3er Blöcke mit Bindestrich (aabb-ccdd-eeff)
- [x] **TypeScript Build-Fehler** - Badge variants, NodeJS.Timeout type fixes
- [x] **Live Monitor Sortierung** - Numerische IP-Sortierung (1, 2, 3... statt 1, 10, 11...)
- [x] **Live Monitor Freeze/Crash** - Abort-Referenz und async cleanup beim Leeren
- [x] **Scanner Performance** - 50 gleichzeitige Pings, Semaphore, kein automatischer Hostname-Lookup

#### Dezember 2025 - Neue Features:
- [x] **Passwort Generator** - Eigene Sonderzeichen definierbar
  - Preset-Auswahl (Standard, Einfach, Sicher, Kompatibel, Minimal)
  - Benutzerdefinierte Zeichenliste
- [x] **MAC Formatter - Echtzeit-Validierung**
  - Zeigt ungültige Zeichen sofort an
  - Prüft auf 0-9 und A-F
  - Längenprüfung (12 Hex-Zeichen)
  - **MAC Vendor Lookup via macvendors.com API**
- [x] **PAN-OS Generator - Vollständig erweitert**
  - Shared Objects Option (Default: aktiviert)
  - Namensformat-Auswahl (IP_Name, Name_IP, Custom Prefix, Nur IP)
  - **Zwei Fenster (Base Names + IP Addresses) für Bulk-Import**
  - Separator-Auswahl (Underscore, Dash, Dot)
  - Security Policies, Services, Schedule, App Filter, URL Category
  - Tags für alle Objekte
- [x] **Subnet Calculator - Erweitert**
  - Split-Funktion: Netzwerk in kleinere Subnetze aufteilen
  - Interaktive Präfix-Auswahl
  - Kopieren aller Subnetze
  - Quick Reference für CIDR-Präfixe

---

## 📋 Ausstehende Aufgaben

### P1 - Hohe Priorität
- [ ] User-Verifizierung: DNS Lookup Fix
- [ ] Traceroute Tool erweitern (History, Vergleich, Profile)
- [ ] Weitere Tools mit History/Vergleich ausstatten

### P2 - Mittlere Priorität
- [ ] Favoriten-System (Tools als Favoriten markieren)
- [ ] Theme-Einstellungen (Akzentfarben anpassen)
- [ ] Keyboard Shortcuts (Ctrl+1 für erstes Tool, etc.)
- [ ] Tool Ein-/Ausblenden aus Sidebar

### P3 - Niedrige Priorität
- [ ] Production Build erstellen (.exe / .msi Installer)
- [ ] Custom App Icon
- [ ] Remote Tools (PSExec/SSH)
- [ ] Rust Code aufräumen (unused imports)
- [ ] Bandwidth Test implementieren (iperf3)

---

## 🔧 Technische Architektur

### Frontend
```
/app/nettools-tauri/src/
├── components/
│   ├── ui/          # Button, Card, Input, Badge, etc.
│   └── layout/      # Sidebar, Header
├── pages/           # Alle Tool-Seiten
├── store/           # Zustand State
└── types/           # TypeScript Types
```

### Backend
```
/app/nettools-tauri/src-tauri/src/
├── main.rs
├── lib.rs
└── commands/
    ├── scanner.rs       # Netzwerk-Scan mit create_hidden_command
    ├── port_scanner.rs
    ├── dns.rs           # DNS Lookup mit create_hidden_command
    ├── traceroute.rs    # Traceroute mit create_hidden_command
    ├── arp.rs           # ARP mit create_hidden_command
    ├── subnet.rs
    ├── whois.rs         # Direkter TCP Socket
    ├── ssl.rs           # PowerShell mit create_hidden_command
    ├── hash.rs
    ├── password.rs      # Mit custom_symbols Support
    ├── mac.rs
    ├── api_tester.rs
    ├── live_monitor.rs  # Mit create_hidden_command
    └── utils.rs         # create_hidden_command Helper
```

### Wichtige Implementierungsdetails

#### CREATE_NO_WINDOW (Konsolenfenster-Fix)
```rust
// In utils.rs:
#[cfg(target_os = "windows")]
pub const CREATE_NO_WINDOW: u32 = 0x08000000;

pub fn create_hidden_command(program: &str) -> Command {
    let mut cmd = Command::new(program);
    #[cfg(target_os = "windows")]
    cmd.creation_flags(CREATE_NO_WINDOW);
    cmd
}
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

## 🚫 Ausgeschlossene Features

- DNSDumpster API
- MXToolbox API  
- Speedtest.net
- phpIPAM Integration

---

## 📝 Bekannte Einschränkungen

- **Build-Umgebung:** Der Benutzer muss lokal kompilieren (Rust + VS Build Tools erforderlich)
- **Bandwidth Test:** Aktuell nur UI-Platzhalter, benötigt iperf3-Integration
- **Fragile Build-Umgebung:** Windows-Build kann bei neuen Rust-Dependencies fehlschlagen

---

## 📁 Projektdateien

- `/app/nettools-tauri/` - Hauptprojekt
- `/app/nettools-tauri/README.md` - Build-Anleitung
- `/app/nettools-tauri/DEVELOPMENT_PLAN.md` - Entwicklungsplan
- `/app/memory/PRD.md` - Dieses Dokument
