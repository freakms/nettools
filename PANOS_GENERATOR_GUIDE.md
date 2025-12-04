# 🛡️ PAN-OS Generator - User Guide

## Overview

**PAN-OS Generator** is a standalone desktop application designed to streamline the creation of PAN-OS CLI commands for address objects. Built for Palo Alto Networks firewall administrators working with PAN-OS 11.1.

**Author:** freakms  
**Company:** ich schwöre feierlich ich bin ein tunichtgut  
**Version:** 1.0.0

---

## Features

### 1. 🎯 Name Generator
Automatically generates address object names by combining base names with IP addresses, then creates the corresponding CLI commands.

**Use Case:** When you have a list of server names and their corresponding IPs, and you want to create consistent, standardized object names.

**Features:**
- Multiple naming formats (Name_IP, IP_Name, Name Only, Custom)
- Three separator options (Underscore, Dash, Dot)
- Custom format with `{name}` and `{ip}` placeholders
- Preview generated names before creating commands
- Shared or VSYS-specific object creation

**Example:**
```
Input:
  Base Name: WebServer
  IP: 192.168.1.100
  Format: Name_IP
  Separator: _ (Underscore)

Output:
  Object Name: WebServer_192_168_1_100
  CLI Command: set shared address "WebServer_192_168_1_100" ip-netmask 192.168.1.100
```

### 2. 🌐 Address Object Set Command Generator
Directly creates address object CLI commands from object names and IP addresses.

**Use Case:** When you already have standardized object names and just need to generate the CLI commands quickly.

**Features:**
- One-to-one mapping of names to IPs
- Support for CIDR notation (e.g., 192.168.1.0/24)
- Shared or VSYS-specific object creation
- Batch processing of multiple objects

**Example:**
```
Input:
  Object Name: Server1
  IP: 192.168.1.10

Output:
  CLI Command: set shared address "Server1" ip-netmask 192.168.1.10
```

---

## How to Use

### Starting the Application

```bash
cd /app
python3 panos_generator.py
```

### Name Generator Workflow

1. **Switch to Name Generator Tab** (if not already selected)
   - Click "🎯 Name Generator" at the top

2. **Enter Base Names** (Step 1)
   - Enter one base name per line
   - Example:
     ```
     Server1
     Server2
     WebServer
     DBServer
     ```

3. **Enter IP Addresses**
   - Enter one IP per line (must match the number of names)
   - Supports CIDR notation (e.g., 192.168.1.0/24)
   - Example:
     ```
     192.168.1.10
     192.168.1.20
     10.0.0.10
     10.0.0.20
     ```

4. **Choose Format Options**
   - **Separator:** 
     - `_ (Underscore)` → WebServer_192_168_1_100
     - `- (Dash)` → WebServer-192-168-1-100
     - `. (Dot)` → WebServer.192.168.1.100
   
   - **Format:**
     - `Name_IP` → Server1_192_168_1_10
     - `IP_Name` → 192_168_1_10_Server1
     - `Name Only` → Server1
     - `Custom` → Use your own pattern with {name} and {ip}

5. **Generate Object Names**
   - Click "🎯 Generate Object Names"
   - Preview the generated names in the preview area

6. **Generate CLI Commands** (Step 2)
   - Choose "Shared Objects" or leave unchecked for VSYS
   - Click "💻 Generate CLI Commands"
   - Commands appear in the output panel on the right

### Address Object Generator Workflow

1. **Switch to Address Objects Tab**
   - Click "🌐 Address Objects" at the top

2. **Enter Object Names**
   - Enter one object name per line
   - Example:
     ```
     Server1
     Server2
     Network1
     ```

3. **Enter IP Addresses**
   - Enter one IP per line (must match the number of names)
   - Supports CIDR notation
   - Example:
     ```
     192.168.1.10
     192.168.1.20
     192.168.1.0/24
     ```

4. **Choose Options**
   - Check "Create as Shared Objects" if needed
   - Leave unchecked for VSYS-specific objects

5. **Generate Commands**
   - Click "💻 Generate Commands"
   - Commands appear in the output panel

### Working with Generated Commands

The output panel on the right side shows all generated commands:

- **View Commands:** Scroll through the list of generated command blocks
- **Remove Individual Commands:** Click the ✗ button on any command block
- **Copy All:** Click "📋 Copy All" to copy all commands to clipboard
- **Download:** Click "⬇️ Download" to save commands to a text file
- **Clear All:** Click "🗑️" to clear all commands

---

## Command Format

### Shared Objects
```bash
configure
set shared address "ObjectName" ip-netmask 192.168.1.10
set shared address "ObjectName2" ip-netmask 192.168.1.20
commit
```

### VSYS Objects
```bash
configure
set vsys vsys1 address "ObjectName" ip-netmask 192.168.1.10
set vsys vsys1 address "ObjectName2" ip-netmask 192.168.1.20
commit
```

---

## Input Validation

The application validates all inputs to ensure correct PAN-OS command generation:

### IP Address Validation
- ✓ Valid: `192.168.1.10`
- ✓ Valid: `10.0.0.0/24`
- ✓ Valid: `172.16.0.1/32`
- ✗ Invalid: `256.1.1.1` (octet > 255)
- ✗ Invalid: `192.168.1` (incomplete)
- ✗ Invalid: `192.168.1.10/33` (CIDR > 32)

### Line Count Validation
- The number of names MUST equal the number of IPs
- Each name pairs with the corresponding IP (line-by-line)

---

## Tips & Best Practices

### Naming Conventions
1. **Use consistent formats** across your organization
2. **Include context** in base names (e.g., "Prod-WebServer" vs just "WebServer")
3. **Test with small batches** first to verify your naming convention

### Separator Selection
- **Underscore (_):** Most common, works well with most systems
- **Dash (-):** Good for readability
- **Dot (.):** Use with caution, can be confused with IP separators

### Custom Format Examples
- `{name}-{ip}` → Server1-192_168_1_10
- `Host_{name}_{ip}` → Host_Server1_192_168_1_10
- `{ip}_{name}_obj` → 192_168_1_10_Server1_obj

### Batch Processing
1. **Group related objects** together
2. **Generate multiple command sets** for different purposes
3. **Download separate files** for different deployment stages

### Network Objects
- Use CIDR notation for network ranges: `192.168.1.0/24`
- The name will include the CIDR: `Network_192_168_1_0_24`
- Both `/24` and `/32` notations are supported

---

## Troubleshooting

### "Number of names doesn't match number of IPs"
- **Cause:** Unequal number of lines in the two input fields
- **Solution:** Ensure both lists have the exact same number of non-empty lines

### "Invalid IP format"
- **Cause:** IP address doesn't match expected format
- **Solution:** Use format `192.168.1.10` or `192.168.1.0/24`
- Check for:
  - Octets greater than 255
  - Missing octets
  - Invalid characters
  - CIDR prefix greater than 32

### "Please provide a custom format pattern"
- **Cause:** Selected "Custom" format but didn't provide a pattern
- **Solution:** Enter a pattern using `{name}` and `{ip}` placeholders

### Empty Preview
- **Cause:** Need to generate names first
- **Solution:** Click "🎯 Generate Object Names" before generating commands

---

## Technical Details

### Dependencies
- Python 3.11+
- customtkinter
- tkinter (included with Python)
- design_constants.py (UI styling)
- ui_components.py (reusable components)

### File Location
- **Application:** `/app/panos_generator.py`
- **Test Logic:** `/app/test_panos_logic.py`
- **Validation Test:** `/app/test_ip_validation.py`

### Supported PAN-OS Versions
- Designed for PAN-OS 11.1
- Should work with most PAN-OS versions that support the `set address` command structure

---

## Examples

### Example 1: Simple Server Objects
```
Base Names:          IPs:
WebServer1           192.168.1.10
WebServer2           192.168.1.11
AppServer1           192.168.2.20
DBServer1            192.168.3.30

Format: Name_IP
Separator: _

Generated Commands:
set shared address "WebServer1_192_168_1_10" ip-netmask 192.168.1.10
set shared address "WebServer2_192_168_1_11" ip-netmask 192.168.1.11
set shared address "AppServer1_192_168_2_20" ip-netmask 192.168.2.20
set shared address "DBServer1_192_168_3_30" ip-netmask 192.168.3.30
```

### Example 2: Network Objects with CIDR
```
Base Names:          IPs:
Production-Net       10.1.0.0/16
Development-Net      10.2.0.0/16
Management-VLAN      192.168.100.0/24

Format: Name_IP
Separator: _

Generated Commands:
set shared address "Production-Net_10_1_0_0_16" ip-netmask 10.1.0.0/16
set shared address "Development-Net_10_2_0_0_16" ip-netmask 10.2.0.0/16
set shared address "Management-VLAN_192_168_100_0_24" ip-netmask 192.168.100.0/24
```

### Example 3: Custom Format
```
Base Names:          IPs:
WebServer            192.168.1.100
AppServer            192.168.1.101

Format: Custom
Pattern: Host_{name}-{ip}
Separator: _

Generated Commands:
set shared address "Host_WebServer-192_168_1_100" ip-netmask 192.168.1.100
set shared address "Host_AppServer-192_168_1_101" ip-netmask 192.168.1.101
```

---

## Support

For issues or questions:
1. Check the error message displayed in the application
2. Verify your input format matches the examples above
3. Review the validation requirements
4. Test with a small sample first

---

## Version History

### v1.0.0 (Initial Release)
- Name Generator with multiple format options
- Address Object Set Command Generator
- IP validation (including CIDR notation)
- Shared vs VSYS object support
- Command output panel with copy/download functionality
- Modern dark theme UI with customtkinter

---

## License & Copyright

**Copyright © 2024 freakms**  
**Company:** ich schwöre feierlich ich bin ein tunichtgut

---

*This application is a companion tool to the NetTools Suite and operates independently.*
