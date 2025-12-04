# 🛡️ PAN-OS Generator

A standalone desktop application for generating PAN-OS CLI commands for address objects.

## Quick Start

```bash
cd /app
python3 panos_generator.py
```

## What It Does

Creates PAN-OS firewall CLI commands quickly and consistently:

### 1. Name Generator 🎯
Combines base names with IPs to create standardized object names, then generates CLI commands.

**Example:**
- Input: `WebServer` + `192.168.1.100`
- Output: `set shared address "WebServer_192_168_1_100" ip-netmask 192.168.1.100`

### 2. Address Object Generator 🌐
Directly creates CLI commands from object names and IPs.

**Example:**
- Input: `Server1` + `192.168.1.10`
- Output: `set shared address "Server1" ip-netmask 192.168.1.10`

## Features

✅ Multiple naming formats (Name_IP, IP_Name, Custom)  
✅ Three separator options (_, -, .)  
✅ Custom format with placeholders  
✅ CIDR notation support (/24, /32, etc.)  
✅ Shared vs VSYS objects  
✅ Batch processing  
✅ Copy/Download commands  
✅ Input validation  

## How to Use

1. **Name Generator Tab:**
   - Enter base names (one per line)
   - Enter IPs (one per line)
   - Choose format and separator
   - Click "Generate Object Names"
   - Review preview
   - Click "Generate CLI Commands"

2. **Address Objects Tab:**
   - Enter object names (one per line)
   - Enter IPs (one per line)
   - Choose shared/vsys option
   - Click "Generate Commands"

3. **Output Panel:**
   - View all generated commands
   - Copy to clipboard
   - Download to file
   - Remove unwanted commands

## Examples

### Basic Server Objects
```
Names:        IPs:           Output:
Server1  →    192.168.1.10   Server1_192_168_1_10
Server2  →    192.168.1.20   Server2_192_168_1_20
```

### Network Objects
```
Names:         IPs:            Output:
ProdNet   →    10.1.0.0/16     ProdNet_10_1_0_0_16
DevNet    →    10.2.0.0/16     DevNet_10_2_0_0_16
```

### Custom Format
```
Pattern: Host_{name}_{ip}
Input:   WebServer + 192.168.1.100
Output:  Host_WebServer_192_168_1_100
```

## Command Output

### Shared Objects
```bash
configure
set shared address "ObjectName" ip-netmask 192.168.1.10
commit
```

### VSYS Objects
```bash
configure
set vsys vsys1 address "ObjectName" ip-netmask 192.168.1.10
commit
```

## Requirements

- Python 3.11+
- customtkinter
- tkinter
- design_constants.py
- ui_components.py

## Documentation

See **PANOS_GENERATOR_GUIDE.md** for detailed documentation, troubleshooting, and advanced usage.

## Testing

Logic tests available:
```bash
python3 test_panos_logic.py      # Test command generation logic
python3 test_ip_validation.py    # Test IP validation
```

## Version

**v1.0.0** - Initial Release

## Author

**freakms**  
Company: ich schwöre feierlich ich bin ein tunichtgut

---

*Standalone companion tool to NetTools Suite*
