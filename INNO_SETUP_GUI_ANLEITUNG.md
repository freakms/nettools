# Inno Setup GUI - Schritt für Schritt Anleitung

## 🎯 Installer mit Inno Setup GUI erstellen

### Schritt 1: Inno Setup öffnen

1. **Drücken Sie** die Windows-Taste
2. **Tippen Sie:** "Inno Setup Compiler"
3. **Klicken Sie** auf die Anwendung

Oder:
- Start Menu → Inno Setup → Inno Setup Compiler

---

### Schritt 2: Script öffnen

1. **Klicken Sie:** `File` → `Open...` (oder drücken Sie `Ctrl+O`)
2. **Navigieren Sie** zu Ihrem Projekt-Ordner
3. **Wählen Sie:** `nettools_setup.iss`
4. **Klicken Sie:** "Öffnen"

Sie sollten jetzt den Script-Inhalt sehen.

---

### Schritt 3: Kompilieren

1. **Klicken Sie:** `Build` → `Compile` (oder drücken Sie `F9`)

Oder klicken Sie auf das blaue Zahnrad-Symbol in der Toolbar.

---

### Schritt 4: Warten

Sie sehen ein Kompilierungs-Fenster mit:
```
Compiling...
[Progress messages...]
Successful compile (X.XX sec)
```

**Wichtig:** Warten Sie bis "Successful compile" erscheint!

---

### Schritt 5: Ergebnis prüfen

**Der Installer ist fertig!**

**Speicherort:**
```
Ihr-Projekt-Ordner\installer_output\NetTools_Setup_1.0.0.exe
```

**Im Explorer:**
1. Öffnen Sie Ihren Projekt-Ordner
2. Gehen Sie in den `installer_output` Ordner
3. Sie sollten `NetTools_Setup_1.0.0.exe` sehen (~20-30 MB)

---

## ✅ Fertig!

Die Datei `NetTools_Setup_1.0.0.exe` ist Ihr fertiger Installer!

Sie können jetzt:
- ✅ Den Installer testen (einfach ausführen)
- ✅ An andere verteilen
- ✅ Auf einen USB-Stick kopieren
- ✅ Hochladen und teilen

---

## 🔍 Fehlerbehebung

### Problem: "Cannot open file dist\NetTools\*"

**Lösung:** Das ausführbare File wurde nicht erstellt.

**Fix:**
```cmd
python -m PyInstaller nettools.spec --noconfirm
```

Dann nochmal in Inno Setup kompilieren.

---

### Problem: Kompilierung schlägt fehl

**Prüfen Sie:**
- Ist `dist\NetTools\NetTools.exe` vorhanden?
- Sind Sie im richtigen Projekt-Ordner?
- Haben Sie das richtige .iss File geöffnet?

---

## 📋 Zusammenfassung

```
1. Inno Setup Compiler öffnen
2. File → Open → nettools_setup.iss
3. Build → Compile (F9)
4. Fertig! → installer_output\NetTools_Setup_1.0.0.exe
```

**Geschätzte Zeit:** 2 Minuten

---

Viel Erfolg! 🚀
