# NetTools Suite - Tauri Edition
## Entwicklungsplan für Windows-optimierte Desktop-Anwendung

**Copyright:** frekms  
**Technologie:** Rust + Tauri + React + TypeScript  
**Zielplattform:** Windows 10/11  

---

## 📋 Projekt-Übersicht

### Was ist Tauri?
Tauri ist ein Framework zum Erstellen von Desktop-Anwendungen mit Web-Technologien (HTML/CSS/JS) und einem Rust-Backend. Es kombiniert:
- **Frontend:** React + TypeScript (UI)
- **Backend:** Rust (System-Operationen, Netzwerk-Tools)
- **Ergebnis:** Native Windows-App mit ~10-20 MB Größe

### Vorteile gegenüber der Python-Version
| Aspekt | Python (customtkinter) | Tauri (Rust + React) |
|--------|------------------------|----------------------|
| EXE-Größe | ~150-200 MB | ~10-20 MB |
| RAM-Verbrauch | ~100-200 MB | ~30-50 MB |
| Startzeit | 3-5 Sekunden | <1 Sekunde |
| UI-Flexibilität | Begrenzt | Unbegrenzt (CSS) |
| Updates | Komplettes Rebuild | Hot-Reload möglich |

---

## 🎯 Features (zu implementieren)

### Phase 1: Kern-Infrastruktur
- [x] Projekt-Setup (Tauri + React)
- [ ] Design-System implementieren
- [ ] Sidebar-Navigation
- [ ] Dark Theme
- [ ] Einstellungen-Persistenz

### Phase 2: Netzwerk-Scanner
- [ ] IPv4/CIDR Scanner
- [ ] Live-Monitoring
- [ ] Scan-Profile speichern/laden
- [ ] Export (CSV, JSON)
- [ ] Scan-Vergleich

### Phase 3: Netzwerk-Tools
- [ ] Port Scanner
- [ ] Traceroute (mit Vergleich)
- [ ] DNS Lookup (mit Vergleich)
- [ ] ARP Viewer
- [ ] Subnet Calculator
- [ ] Bandwidth Test (iperf3)

### Phase 4: Lookup-Tools
- [ ] WHOIS Lookup
- [ ] SSL Checker
- [ ] MAC Formatter & OUI Lookup

### Phase 5: Utilities
- [ ] Hash Generator
- [ ] Password Generator
- [ ] API/HTTP Tester

### Phase 6: Integrationen
- [ ] phpIPAM Integration
- [ ] Palo Alto Networks Config Generator

### Phase 7: Polish & Release
- [ ] Settings Page
- [ ] Keyboard Shortcuts
- [ ] Favoriten-System
- [ ] Command Palette
- [ ] Windows Installer (MSI/EXE)

---

## 🎨 Design-System

### Farbpalette
```css
:root {
  /* Hintergründe */
  --bg-primary: #282C34;
  --bg-secondary: #21252B;
  --bg-tertiary: #353944;
  --bg-card: #2F3336;
  
  /* Akzentfarben */
  --accent-blue: #007BFF;
  --accent-green: #28A745;
  --accent-red: #DC3545;
  --accent-yellow: #FFC107;
  
  /* Text */
  --text-primary: #FFFFFF;
  --text-secondary: #ADB5BD;
  --text-muted: #6C757D;
  
  /* Borders */
  --border-color: #3D4450;
  --border-radius: 8px;
}
```

### Typografie
- **Font:** Segoe UI (Windows-nativ)
- **Headings:** 18-24px, Bold
- **Body:** 14px, Regular
- **Labels:** 12px, Medium

### Komponenten
- Buttons: Abgerundete Ecken, farbkodiert
- Cards: Dunkler Hintergrund mit subtiler Border
- Inputs: Dark Theme mit Fokus-Highlight
- Tables: Striped Rows, sortierbar

---

## 📁 Projektstruktur

```
nettools-tauri/
├── src-tauri/              # Rust Backend
│   ├── src/
│   │   ├── main.rs         # Entry Point
│   │   ├── commands/       # Tauri Commands (API)
│   │   │   ├── mod.rs
│   │   │   ├── scanner.rs
│   │   │   ├── port_scanner.rs
│   │   │   ├── dns.rs
│   │   │   ├── traceroute.rs
│   │   │   ├── whois.rs
│   │   │   ├── ssl.rs
│   │   │   └── ...
│   │   └── utils/          # Hilfsfunktionen
│   │       ├── mod.rs
│   │       ├── network.rs
│   │       └── config.rs
│   ├── Cargo.toml          # Rust Dependencies
│   └── tauri.conf.json     # Tauri Konfiguration
│
├── src/                    # React Frontend
│   ├── components/         # UI-Komponenten
│   │   ├── ui/             # Basis-Komponenten
│   │   ├── layout/         # Layout (Sidebar, Header)
│   │   └── tools/          # Tool-spezifische UI
│   ├── pages/              # Seiten/Views
│   ├── hooks/              # React Hooks
│   ├── store/              # State Management
│   ├── styles/             # CSS/Tailwind
│   ├── types/              # TypeScript Types
│   └── App.tsx             # Root Component
│
├── package.json            # Node Dependencies
├── tailwind.config.js      # Tailwind CSS
├── tsconfig.json           # TypeScript Config
└── README.md               # Dokumentation
```

---

## 🔧 Entwicklungsumgebung (für Ihren Windows-PC)

### Voraussetzungen installieren

1. **Rust installieren:**
   ```powershell
   # PowerShell als Administrator
   winget install Rustlang.Rust.GNU
   # Oder: https://rustup.rs/
   ```

2. **Node.js installieren:**
   ```powershell
   winget install OpenJS.NodeJS.LTS
   ```

3. **Visual Studio Build Tools:**
   ```powershell
   winget install Microsoft.VisualStudio.2022.BuildTools
   # Wählen Sie "Desktop development with C++"
   ```

4. **WebView2 (normalerweise vorinstalliert auf Windows 10/11)**

### Projekt starten

```powershell
# In den Projektordner wechseln
cd nettools-tauri

# Dependencies installieren
npm install

# Entwicklungsserver starten
npm run tauri dev

# Für Production Build
npm run tauri build
```

---

## 📅 Zeitplan

| Phase | Beschreibung | Geschätzte Dateien |
|-------|--------------|-------------------|
| 1 | Infrastruktur & Design | ~15 Dateien |
| 2 | Netzwerk-Scanner | ~10 Dateien |
| 3 | Netzwerk-Tools | ~15 Dateien |
| 4 | Lookup-Tools | ~8 Dateien |
| 5 | Utilities | ~8 Dateien |
| 6 | Integrationen | ~10 Dateien |
| 7 | Polish & Release | ~5 Dateien |

**Gesamt:** ~70+ Dateien

---

## 🚀 Nächste Schritte

1. ✅ Plan erstellt
2. ⏳ Phase 1: Projekt-Setup und Design-System
3. ⏳ Phase 2: Kern-Scanner implementieren
4. ... (fortlaufend)

---

## 📝 Hinweise

- Der **React-Frontend-Code** wird hier auf Emergent entwickelt und getestet
- Der **Rust-Backend-Code** wird vollständig geschrieben, aber auf Ihrem Windows-PC kompiliert
- Alle Dateien werden gut dokumentiert für einfache Wartung
- Build-Anweisungen werden detailliert bereitgestellt
