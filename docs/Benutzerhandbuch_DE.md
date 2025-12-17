# NetTools Suite - Benutzerhandbuch

**Version 2.0 | Stand: Dezember 2024**

---

## Inhaltsverzeichnis

1. [Einführung](#1-einführung)
2. [Installation & Start](#2-installation--start)
3. [Benutzeroberfläche](#3-benutzeroberfläche)
4. [Tools im Überblick](#4-tools-im-überblick)
5. [Scanning-Tools](#5-scanning-tools)
6. [Netzwerk-Tools](#6-netzwerk-tools)
7. [Test-Tools](#7-test-tools)
8. [Erweiterte Funktionen](#8-erweiterte-funktionen)
9. [Einstellungen](#9-einstellungen)
10. [Tastenkombinationen](#10-tastenkombinationen)
11. [Fehlerbehebung](#11-fehlerbehebung)

---

## 1. Einführung

Die **NetTools Suite** ist eine umfassende Sammlung von Netzwerk-Werkzeugen für IT-Administratoren und Netzwerk-Techniker. Die Anwendung bietet eine moderne, benutzerfreundliche Oberfläche für alltägliche Netzwerk-Diagnose und -Verwaltungsaufgaben.

### Hauptfunktionen:
- Netzwerk-Scanning (IPv4, Ports, ARP)
- DNS-Abfragen und WHOIS-Lookup
- Traceroute und Netzwerkpfad-Analyse
- SSL-Zertifikat-Prüfung
- Subnet-Berechnungen
- Passwort-Generator
- API-Testing
- Scan-Vergleiche
- PAN-OS Konfigurations-Generator

---

## 2. Installation & Start

### Systemvoraussetzungen:
- Windows 10/11 (64-Bit)
- Python 3.10 oder höher
- Mindestens 4 GB RAM
- 100 MB freier Festplattenspeicher

### Installation:

1. **Python-Abhängigkeiten installieren:**
   ```
   pip install -r requirements.txt
   ```

2. **Anwendung starten:**
   ```
   python nettools_app.py
   ```

### Optionale Tools:
- **PSExec** (für Remote-Zugriff): Von Microsoft Sysinternals herunterladen
- **iPerf3** (für Bandbreiten-Tests): Separat installieren

---

## 3. Benutzeroberfläche

### Hauptbereiche:

```
┌─────────────────────────────────────────────────────────┐
│  Logo & Titel                              [─] [□] [X]  │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│  Navigation  │           Hauptinhalt                    │
│  (Sidebar)   │                                          │
│              │                                          │
│  📊 Dashboard│                                          │
│  🔍 Scanner  │                                          │
│  🔌 Ports    │                                          │
│  ...         │                                          │
│              │                                          │
├──────────────┴──────────────────────────────────────────┤
│  Statusleiste                                           │
└─────────────────────────────────────────────────────────┘
```

### Sidebar (Navigation):
- **Kategorien**: Dashboard, Scanning, Tools, Testing, Advanced
- **Suchfeld**: Schnellsuche nach Tools (Strg+K)
- **Favoriten**: Rechtsklick auf Tool → "Zu Favoriten hinzufügen"
- **Ein-/Ausklappen**: Strg+B oder Klick auf Pfeil

### Statusleiste:
Zeigt den aktuellen Status und Beschreibung des aktiven Tools.

---

## 4. Tools im Überblick

| Kategorie | Tool | Beschreibung |
|-----------|------|--------------|
| **Dashboard** | Dashboard | Systemübersicht, externe IP, Netzwerk-Info |
| **Scanning** | IPv4 Scanner | Netzwerk nach aktiven Hosts scannen |
| | Port Scanner | Offene Ports auf Zielsystemen finden |
| | Traceroute | Netzwerkpfad zu einem Ziel verfolgen |
| | ARP Table | Lokale ARP-Tabelle anzeigen |
| **Tools** | DNS Lookup | Hostnamen und IPs auflösen |
| | WHOIS Lookup | Domain-/IP-Eigentümer abfragen |
| | SSL Checker | SSL-Zertifikate prüfen |
| | Subnet Calculator | Subnet-Informationen berechnen |
| | MAC Formatter | MAC-Adressen formatieren |
| | Hash Generator | MD5/SHA-Hashes erzeugen |
| | Password Generator | Sichere Passwörter erstellen |
| **Testing** | API Tester | REST-APIs testen |
| | Bandwidth Test | Bandbreite mit iPerf3 testen |
| | Speedtest | Internet-Geschwindigkeit messen |
| | Scan Comparison | Scan-Ergebnisse vergleichen |
| **Advanced** | Network Profiles | Netzwerk-Konfigurationen verwalten |
| | PAN-OS Generator | PAN-OS CLI-Befehle generieren |
| | phpIPAM | IP-Adress-Verwaltung |
| | Settings | Einstellungen und Anpassungen |

---

## 5. Scanning-Tools

### 5.1 IPv4 Scanner

**Zweck:** Scannt ein Netzwerk nach aktiven Hosts.

**Verwendung:**
1. IP-Bereich eingeben (z.B. `192.168.1.0/24` oder `192.168.1.1-254`)
2. Scan-Methode wählen:
   - **Ping**: Standard ICMP-Ping
   - **ARP**: Schneller, nur im lokalen Netzwerk
   - **TCP**: Verbindungsversuch auf Port 445
3. "Scan starten" klicken

**Ergebnisse:**
- IP-Adresse
- Hostname (wenn auflösbar)
- MAC-Adresse (nur bei ARP)
- Antwortzeit

**Export:** Ergebnisse als CSV oder JSON exportieren.

---

### 5.2 Port Scanner

**Zweck:** Findet offene Ports auf einem Zielsystem.

**Verwendung:**
1. Ziel-IP oder Hostname eingeben
2. Port-Bereich wählen:
   - Einzelne Ports: `80, 443, 8080`
   - Bereich: `1-1000`
   - Vordefiniert: "Common Ports", "All Ports"
3. Scan-Typ:
   - **TCP Connect**: Vollständiger Verbindungsaufbau
   - **SYN Scan**: Halboffener Scan (benötigt Admin-Rechte)

**Ergebnisse:**
- Port-Nummer
- Status (offen/geschlossen)
- Service-Name (wenn bekannt)

---

### 5.3 Traceroute

**Zweck:** Verfolgt den Netzwerkpfad zu einem Ziel.

**Verwendung:**
1. Ziel eingeben (IP oder Hostname)
2. Max. Hops einstellen (Standard: 30)
3. Tool wählen:
   - **Tracert**: Windows Standard
   - **Pathping**: Detaillierter mit Statistiken

**Ergebnisse:**
- Hop-Nummer
- IP-Adresse jedes Routers
- Antwortzeit pro Hop
- Hostname (wenn verfügbar)

**Hinweis:** Traceroute-Ergebnisse werden automatisch gespeichert und können später verglichen werden.

---

### 5.4 ARP Table

**Zweck:** Zeigt die lokale ARP-Tabelle an.

**Funktionen:**
- Alle ARP-Einträge anzeigen
- Nach IP oder MAC filtern
- ARP-Cache leeren
- Einträge in Zwischenablage kopieren
- Automatische Aktualisierung

---

## 6. Netzwerk-Tools

### 6.1 DNS Lookup

**Zweck:** DNS-Abfragen durchführen.

**Record-Typen:**
- **A**: IPv4-Adresse
- **AAAA**: IPv6-Adresse
- **MX**: Mail-Exchange
- **NS**: Nameserver
- **TXT**: Text-Records
- **CNAME**: Kanonischer Name
- **SOA**: Start of Authority

**Verwendung:**
1. Domain oder IP eingeben
2. Record-Typ wählen
3. "Lookup" klicken

---

### 6.2 WHOIS Lookup

**Zweck:** Eigentümer-Informationen zu Domains/IPs abfragen.

**Informationen:**
- Registrar
- Registrierungsdatum
- Ablaufdatum
- Nameserver
- Kontaktdaten (wenn verfügbar)

---

### 6.3 SSL Checker

**Zweck:** SSL/TLS-Zertifikate prüfen.

**Prüfungen:**
- Zertifikat-Gültigkeit
- Ablaufdatum
- Aussteller (CA)
- Verschlüsselungsstärke
- Subject Alternative Names (SAN)
- Zertifikatskette

**Verwendung:**
1. Domain eingeben (ohne https://)
2. Port angeben (Standard: 443)
3. "Prüfen" klicken

**Farbcodes:**
- 🟢 Grün: Gültig, > 30 Tage bis Ablauf
- 🟡 Gelb: < 30 Tage bis Ablauf
- 🔴 Rot: Abgelaufen oder ungültig

---

### 6.4 Subnet Calculator

**Zweck:** Subnet-Informationen berechnen.

**Eingabe:**
- CIDR-Notation: `192.168.1.0/24`
- Oder: IP + Subnetzmaske

**Ergebnisse:**
- Netzwerk-Adresse
- Broadcast-Adresse
- Erste/Letzte nutzbare IP
- Anzahl Hosts
- Subnetzmaske (dezimal und binär)
- Wildcard-Maske

---

### 6.5 Hash Generator

**Zweck:** Kryptografische Hashes erzeugen.

**Algorithmen:**
- MD5
- SHA-1
- SHA-256
- SHA-512
- SHA3-256
- BLAKE2b

**Eingabe:**
- Text direkt eingeben
- Oder Datei auswählen

---

### 6.6 Password Generator

**Zweck:** Sichere Passwörter und Passphrasen erstellen.

**Optionen:**
- Länge (8-128 Zeichen)
- Großbuchstaben
- Kleinbuchstaben
- Zahlen
- Sonderzeichen
- Passphrasen (Wortbasiert)

**Stärke-Anzeige:** Visuelle Bewertung der Passwortstärke.

---

## 7. Test-Tools

### 7.1 API Tester

**Zweck:** REST-APIs testen.

**HTTP-Methoden:**
- GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS

**Funktionen:**
- Custom Headers setzen
- Request Body (JSON, Form-Data)
- URL-Parameter
- Response-Anzeige mit Syntax-Highlighting
- Antwortzeit-Messung

---

### 7.2 Speedtest

**Zweck:** Internet-Geschwindigkeit messen.

**Messungen:**
- Download-Geschwindigkeit
- Upload-Geschwindigkeit
- Ping/Latenz

---

### 7.3 Scan Comparison

**Zweck:** Scan-Ergebnisse vergleichen.

**Vergleichstypen:**
- **Port Scans**: Neu geöffnete/geschlossene Ports
- **Traceroute**: Routenänderungen, Latenz-Unterschiede
- **DNS Lookups**: Geänderte Records

**Verwendung:**
1. Zwei Scans auswählen
2. "Vergleichen" klicken
3. Unterschiede werden farblich hervorgehoben

---

## 8. Erweiterte Funktionen

### 8.1 Network Profiles

**Zweck:** Netzwerk-Konfigurationen speichern und wiederverwenden.

**Gespeicherte Daten:**
- IP-Bereiche
- Häufig verwendete Ziele
- Scan-Einstellungen

---

### 8.2 PAN-OS Generator

**Zweck:** Palo Alto Networks CLI-Befehle generieren.

**Unterstützte Konfigurationen:**
- Sicherheitsregeln
- NAT-Regeln
- Adressobjekte
- Service-Objekte

---

### 8.3 phpIPAM Integration

**Zweck:** Integration mit phpIPAM für IP-Adress-Management.

**Voraussetzung:** phpIPAM-Server mit API-Zugang.

---

## 9. Einstellungen

Zugriff über: **Advanced → Settings**

### Tool-Sichtbarkeit

Aktivieren/Deaktivieren Sie Tools, die Sie nicht benötigen:
1. Checkbox für jedes Tool
2. "Enable All" / "Disable All" für Schnellauswahl
3. "Apply Changes" klicken
4. **App neu starten** für Änderungen

**Hinweis:** Dashboard kann nicht deaktiviert werden.

---

## 10. Tastenkombinationen

| Tastenkombination | Funktion |
|-------------------|----------|
| `Strg+K` | Suchfeld öffnen |
| `Strg+B` | Sidebar ein-/ausklappen |
| `Strg+D` | Zu Dashboard wechseln |
| `Strg+1-9` | Schnellzugriff auf Tools |
| `Escape` | Dialog/Popup schließen |
| `F5` | Aktuelle Ansicht aktualisieren |
| `Strg+S` | Ergebnisse speichern/exportieren |
| `Strg+C` | Ausgewählten Text kopieren |

---

## 11. Fehlerbehebung

### Häufige Probleme:

**Problem:** App startet nicht
**Lösung:** 
- Python-Version prüfen (min. 3.10)
- `pip install -r requirements.txt` erneut ausführen

**Problem:** Scan findet keine Hosts
**Lösung:**
- Firewall-Einstellungen prüfen
- Als Administrator ausführen
- ARP-Scan im lokalen Netzwerk verwenden

**Problem:** DNS-Lookup funktioniert nicht
**Lösung:**
- Netzwerkverbindung prüfen
- DNS-Server erreichbar?
- Firewall blockiert Port 53?

**Problem:** SSL-Prüfung schlägt fehl
**Lösung:**
- Ziel-Port prüfen (Standard: 443)
- Hostname korrekt eingeben
- Firewall-Regeln prüfen

---

## Support & Feedback

Bei Fragen oder Problemen:
- GitHub Issues erstellen
- Log-Dateien prüfen (im Anwendungsordner)

---

**© 2024 NetTools Suite**
