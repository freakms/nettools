# NetTools Minimal

Eine reduzierte Version der NetTools Suite ohne externe API-Abhängigkeiten.

## Entfernte Features (im Vergleich zur Vollversion)

| Feature | Grund für Entfernung |
|---------|---------------------|
| MXToolbox API | Externe API-Abhängigkeit |
| DNSDumpster API | Externe API-Abhängigkeit |
| phpIPAM Integration | Server-Abhängigkeit |
| Speedtest | Externe Server-Abhängigkeit |
| Hash Generator | Nicht Netzwerk-relevant |
| API Tester | Für Minimal-Version nicht nötig |
| WHOIS Lookup | Externe Abhängigkeit |
| Bandwidth Test (iPerf) | Server-Abhängigkeit |

## Enthaltene Tools (11 Tools)

### Scanning
- ✅ IPv4 Scanner (mit SNMP für Switches)
- ✅ Port Scanner
- ✅ Traceroute
- ✅ ARP Viewer

### Netzwerk-Tools
- ✅ DNS Lookup (lokal)
- ✅ SSL Checker
- ✅ Subnet Calculator
- ✅ MAC Formatter

### Sicherheit
- ✅ Password Generator

### Advanced
- ✅ Network Profiles
- ✅ PAN-OS Generator
- ✅ Scan Comparison
- ✅ Settings

## Installation

```bash
cd nettools_minimal
pip install -r requirements.txt
python nettools_minimal.py
```

## Build

```bash
python build_exe_minimal.py
```

## Dateigröße

Die Minimal-Version ist ca. 40-50% kleiner als die Vollversion, da weniger Dependencies eingebunden werden.
