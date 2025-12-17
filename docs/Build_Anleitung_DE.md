# NetTools Suite - Standalone Executable erstellen

## Übersicht

Nach dem Build mit PyInstaller enthält die erstellte `.exe` Datei:
- Den kompletten Python-Interpreter
- Alle benötigten Bibliotheken (customtkinter, requests, etc.)
- Die NetTools-Anwendung selbst

**Der Endbenutzer braucht KEIN Python installiert!**

---

## Build-Optionen

### Option 1: Directory Mode (EMPFOHLEN - Schneller Start)

```batch
python build_exe_fast.py
```

**Ergebnis:**
```
dist/
└── NetToolsSuite/
    ├── NetToolsSuite.exe    ← Hauptprogramm
    ├── python3.dll
    ├── *.dll                 ← Bibliotheken
    └── _internal/            ← Abhängigkeiten
```

**Vorteile:**
- ✅ Sehr schneller Start (~0.5 Sekunden)
- ✅ Einfacher zu debuggen
- ✅ Updates einzelner Dateien möglich

**Nachteile:**
- ❌ Viele Dateien (~40-50 MB Ordner)
- ❌ Muss als kompletter Ordner weitergegeben werden

**Verteilung:**
- Den gesamten `NetToolsSuite`-Ordner als ZIP verpacken
- Benutzer entpackt und startet `NetToolsSuite.exe`

---

### Option 2: Single File Mode (Eine Datei)

```batch
python build_exe.py
```

Oder manuell:
```batch
pyinstaller --onefile --windowed nettools_app.py
```

**Ergebnis:**
```
dist/
└── NetToolsSuite.exe    ← Eine einzelne Datei (~30-40 MB)
```

**Vorteile:**
- ✅ Nur eine Datei
- ✅ Einfach zu verteilen (E-Mail, USB, etc.)

**Nachteile:**
- ❌ Langsamer Start (5-15 Sekunden beim ersten Mal)
- ❌ Entpackt temporär bei jedem Start

---

## Build-Anleitung (Schritt für Schritt)

### 1. Voraussetzungen (nur auf dem Build-PC):

```batch
pip install pyinstaller
pip install -r requirements.txt
```

### 2. Build ausführen:

```batch
cd C:\Pfad\zu\nettools

REM Für Directory-Mode (schnell):
python build_exe_fast.py

REM Für Single-File-Mode:
python build_exe.py
```

### 3. Ergebnis finden:

Die fertige Anwendung liegt im `dist/`-Ordner.

---

## Verteilung an Benutzer

### Directory Mode:

1. Den Ordner `dist/NetToolsSuite/` komplett kopieren
2. Als ZIP verpacken: `NetToolsSuite.zip`
3. Benutzer entpackt das ZIP
4. Benutzer startet `NetToolsSuite.exe`

### Single File Mode:

1. Die Datei `dist/NetToolsSuite.exe` kopieren
2. Direkt weitergeben (E-Mail, Netzlaufwerk, USB)
3. Benutzer doppelklickt auf `NetToolsSuite.exe`

---

## Was ist im Build enthalten?

PyInstaller packt automatisch ein:

| Komponente | Beschreibung |
|------------|--------------|
| Python 3.x Runtime | Kompletter Python-Interpreter |
| customtkinter | GUI-Bibliothek |
| tkinter | Basis-GUI |
| requests | HTTP-Bibliothek |
| dnspython | DNS-Abfragen |
| PIL/Pillow | Bildverarbeitung |
| Alle `ui/*.py` | UI-Module |
| Alle `tools/*.py` | Backend-Module |
| `oui_database.json` | MAC-Hersteller-Datenbank |

---

## Häufige Probleme

### Problem: "DLL not found" Fehler
**Lösung:** Visual C++ Redistributable auf Ziel-PC installieren:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### Problem: Antivirus blockiert EXE
**Lösung:** 
- EXE signieren (Code Signing Certificate)
- Oder: Ausnahme im Antivirus hinzufügen

### Problem: Start dauert sehr lange (Single File)
**Lösung:** Directory Mode verwenden (`build_exe_fast.py`)

### Problem: "Module not found" nach Build
**Lösung:** Hidden Imports in build_exe.py hinzufügen:
```python
args.append('--hidden-import=fehlende_bibliothek')
```

---

## Zusammenfassung

| Aspekt | Directory Mode | Single File Mode |
|--------|----------------|------------------|
| **Python nötig?** | ❌ Nein | ❌ Nein |
| **Startzeit** | ~0.5 Sek | 5-15 Sek |
| **Dateigröße** | ~50 MB (Ordner) | ~35 MB (1 Datei) |
| **Verteilung** | Als ZIP-Ordner | Einzelne EXE |
| **Empfohlen für** | Tägliche Nutzung | Einfache Weitergabe |

**Fazit:** Für Endbenutzer ohne Python ist der **Directory Mode** die beste Wahl wegen des schnellen Starts!
