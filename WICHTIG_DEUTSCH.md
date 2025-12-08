# WICHTIG - Verwenden Sie Command Prompt (CMD), nicht PowerShell!

## ⚠️ Problem Identifiziert

Sie verwenden **PowerShell** - das Build-Script benötigt **Command Prompt (CMD)**.

---

## ✅ Lösung: Command Prompt (CMD) verwenden

### Methode 1: CMD öffnen

1. **Drücken Sie:** `Windows-Taste + R`
2. **Tippen Sie:** `cmd`
3. **Drücken Sie:** Enter
4. **Navigieren Sie** zum Projekt-Ordner:
   ```cmd
   cd C:\Pfad\Zu\Ihrem\Projekt
   ```
5. **Ausführen:**
   ```cmd
   build_installer.bat
   ```

### Methode 2: Aus dem Ordner

1. **Öffnen Sie** den Projekt-Ordner im Windows Explorer
2. **Klicken Sie** in die Adressleiste
3. **Tippen Sie:** `cmd` und drücken Sie Enter
4. **Ausführen:**
   ```cmd
   build_installer.bat
   ```

---

## 🔍 Warum passiert das?

- **PowerShell** interpretiert `/` als Division-Operator
- **CMD** (Command Prompt) interpretiert `/` als Parameter
- Das Build-Script ist für **CMD** geschrieben

---

## ✅ Nach dem Ausführen in CMD

Sie sollten sehen:
```
installer_output\NetTools_Setup_1.0.0.exe
```

---

## 🎯 Schnelltest in CMD

In Command Prompt (nicht PowerShell):
```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /?
```

Das sollte jetzt funktionieren!

Dann:
```cmd
build_installer.bat
```
