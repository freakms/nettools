# NetTools Suite - Tauri 2.x Edition

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
# In den Projektordner wechseln
cd nettools-tauri

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
│   │   ├── lib.rs          # Library (Tauri 2.x)
│   │   └── commands/       # Tauri Commands
│   ├── capabilities/       # Tauri 2.x Permissions
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

## 🔧 Wichtige Hinweise für Tauri 2.x

Diese Version verwendet **Tauri 2.x**, das einige Unterschiede zu Tauri 1.x aufweist:

- **Capabilities statt Allowlist**: Berechtigungen werden über `src-tauri/capabilities/` konfiguriert
- **Plugins**: Shell, FS, Dialog etc. sind jetzt separate Plugins
- **API Import**: Frontend importiert von `@tauri-apps/plugin-*` statt `@tauri-apps/api`

## 🎨 Design-System

- **Theme:** Dark Mode
- **Farben:** Siehe `tailwind.config.js`
- **Schriftart:** Segoe UI (Windows-nativ)
- **Icons:** Lucide React

## 🔧 Implementierte Features

### Phase 1: Infrastruktur ✅
- [x] Projekt-Setup (Tauri 2.x)
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

## 📦 Build für Windows

```powershell
npm run tauri build
```

Nach dem Build finden Sie die Installer unter:
- `src-tauri/target/release/bundle/msi/` - MSI Installer
- `src-tauri/target/release/bundle/nsis/` - NSIS Installer

## 🐛 Troubleshooting

### "tauri command not found"
```powershell
npm install @tauri-apps/cli@latest
```

### Rust Compilation Fehler
```powershell
rustup update
```

### WebView2 nicht installiert
Windows 10/11 sollte WebView2 vorinstalliert haben. Falls nicht:
https://developer.microsoft.com/en-us/microsoft-edge/webview2/

## 📝 Lizenz

© 2024 frekms
