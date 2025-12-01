# OUI Vendor Lookup Feature

## What is OUI?

**OUI** stands for **Organizationally Unique Identifier**. It's the first 3 bytes (6 hex digits) of a MAC address that identifies the manufacturer of a network device.

Example: In the MAC address `00:0C:29:12:34:56`:
- OUI: `00:0C:29` → Identifies the vendor (VMware in this case)
- Device ID: `12:34:56` → Unique to the specific device

## Feature Description

The **OUI Vendor Lookup** feature automatically identifies the manufacturer of a network device when you enter its MAC address in the MAC Formatter tab.

### How It Works

1. **Enter a MAC address** in any format:
   - `AA:BB:CC:DD:EE:FF` (Colon format)
   - `AA-BB-CC-DD-EE-FF` (Dash format)
   - `AABBCCDDEEFF` (Plain format)
   - `AABB.CCDD.EEFF` (Cisco format)

2. **Vendor is displayed automatically** below the input field:
   - Shows the manufacturer name (e.g., "Cisco Systems, Inc", "Apple, Inc.", "Intel Corporate")
   - Displays "Unknown Vendor" if the OUI is not in our database

3. **Visual indicator**:
   - 🏢 icon before the vendor name
   - Green color for easy visibility

## Database Coverage

The app includes an OUI database (`oui_database.json`) with **1,177+ manufacturer entries**, including:

- **Network Equipment**: Cisco, Dell, HP, Palo Alto Networks, Sophos, Extreme Networks, Aruba, Huawei, Juniper
- **Computer Manufacturers**: Apple, Microsoft, Intel, AMD, Dell, HP
- **Mobile Devices**: Samsung, Xiaomi, Huawei
- **IoT & Smart Devices**: Various manufacturers
- **Special Addresses**: IANA (Internet Assigned Numbers Authority)

**Enterprise Network Equipment Coverage:**
- Dell Inc. (29 OUI prefixes)
- Hewlett Packard / HP (87 OUI prefixes)
- Palo Alto Networks (24 OUI prefixes)
- Sophos (10 OUI prefixes)
- Extreme Networks (13 OUI prefixes)
- Aruba Networks (22 OUI prefixes)
- Huawei Technologies (103+ OUI prefixes)
- Juniper Networks (53 OUI prefixes)

## Usage Example

```
Input: 00:0C:29:AB:CD:EF
Output: 🏢 Vendor: VMware, Inc.

Input: 3C:22:FB:12:34:56
Output: 🏢 Vendor: Apple, Inc.

Input: AA:BB:CC:DD:EE:FF
Output: 🏢 Vendor: Unknown
```

## Benefits

- **Network troubleshooting**: Quickly identify device manufacturers on your network
- **Security analysis**: Detect unauthorized or unexpected devices
- **Inventory management**: Catalog network equipment by vendor
- **Educational**: Learn about MAC address structure and vendor assignments

## Technical Details

- **Database format**: JSON file with OUI-to-vendor mappings
- **Database size**: 1,177 entries (~180KB)
- **Lookup speed**: Instant (hash-based lookup)
- **Memory footprint**: Minimal (~200KB in memory)
- **Compatibility**: Works with all MAC address formats
- **Last updated**: v1.2.1 (November 2024)

## Future Enhancements

Potential improvements for future versions:
- Download updated OUI database from IEEE
- Show vendor logo/icon
- Display additional vendor information (country, website)
- Export vendor information with scan results

---

**Version**: 1.1.0  
**Feature added**: November 2024
