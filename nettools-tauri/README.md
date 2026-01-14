# NetTools Suite - Tauri Edition

Eine professionelle Sammlung von Netzwerk-Utilities für Windows, entwickelt mit Rust und React.

## 🚀 Schnellstart

### Voraussetzungen

1. **Rust installieren:**
   ```powershell
   # PowerShell als Administrator
   winget install Rustlang.Rust.GNU
   ```
   Oder: https://rustup.rs/

2. **Node.js installieren:**
   ```powershell
   winget install OpenJS.NodeJS.LTS
   ```

3. **Visual Studio Build Tools:**
   ```powershell
   winget install Microsoft.VisualStudio.2022.BuildTools
   ```
   Bei der Installation "Desktop development with C++" auswählen.

### Projekt starten

```powershell
# Dependencies installieren
npm install

# Entwicklungsserver starten (Hot-Reload)
npm run tauri dev

# Production Build erstellen
npm run tauri build
```

## 📁 Projektstruktur

```
nettools-tauri/
├── src-tauri/              # Rust Backend
│   ├── src/
│   │   ├── main.rs         # Entry Point
│   │   └── commands/       # Tauri Commands
│   ├── Cargo.toml          # Rust Dependencies
│   └── tauri.conf.json     # Tauri Konfiguration
│
├── src/                    # React Frontend
│   ├── components/         # UI-Komponenten
│   ├── pages/              # Seiten/Views
│   ├── store/              # State Management (Zustand)
│   └── App.tsx             # Root Component
│
├── package.json            # Node Dependencies
└── tailwind.config.js      # Tailwind CSS
```

## 🎨 Design-System

- **Theme:** Dark Mode
- **Farben:** Siehe `tailwind.config.js`
- **Schriftart:** Segoe UI (Windows-nativ)
- **Icons:** Lucide React

## 🔧 Implementierte Features

### Phase 1: Infrastruktur ✅
- [x] Projekt-Setup
- [x] Design-System
- [x] Sidebar-Navigation
- [x] Command Palette (Ctrl+K)
- [x] Einstellungen-Seite
- [x] Favoriten-System
- [x] Toast-Benachrichtigungen

### Phase 2-6: Tools (Backend implementiert)
- [x] IPv4/CIDR Scanner
- [x] Port Scanner
- [x] DNS Lookup
- [x] Traceroute
- [x] ARP Viewer
- [x] Subnet Calculator
- [x] WHOIS Lookup
- [x] SSL Checker
- [x] Hash Generator
- [x] Password Generator

## 🛠️ Entwicklung

### Frontend testen (ohne Rust)
```powershell
npm run dev
```
Öffnet http://localhost:1420 im Browser.

### Vollständige App testen
```powershell
npm run tauri dev
```

### Production Build
```powershell
npm run tauri build
```
Erzeugt Installer in `src-tauri/target/release/bundle/`.

## 📦 Deployment

Nach `npm run tauri build` finden Sie:
- **MSI-Installer:** `src-tauri/target/release/bundle/msi/`
- **NSIS-Installer:** `src-tauri/target/release/bundle/nsis/`

## 🔑 Tastenkürzel

| Kürzel | Aktion |
|--------|--------|
| Ctrl+K | Schnellsuche |
| Ctrl+1 | Dashboard |
| Ctrl+2 | IPv4 Scanner |
| Ctrl+3 | Port Scanner |
| Ctrl+4 | DNS Lookup |
| Ctrl+5 | Traceroute |
| Ctrl+, | Einstellungen |
| Ctrl+Q | Beenden |

## 📝 Lizenz

© 2024 frekms
