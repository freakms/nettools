# NetTools Suite - Usage Guide

**Version:** 1.0.0  
**Platform:** Windows, macOS, Linux

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [IPv4 Scanner](#ipv4-scanner)
3. [MAC Formatter](#mac-formatter)
4. [Keyboard Shortcuts](#keyboard-shortcuts)
5. [Tips & Tricks](#tips--tricks)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## Quick Start

### First Launch

**Windows:**
```batch
REM Double-click NetToolsSuite.exe
REM Or run from command prompt:
NetToolsSuite.exe
```

**Linux:**
```bash
./NetToolsSuite
# Or with sudo if capabilities not granted:
sudo ./NetToolsSuite
```

**macOS:**
```bash
open NetToolsSuite.app
# Or from terminal:
./NetToolsSuite.app/Contents/MacOS/NetToolsSuite
```

### Interface Overview

```
┌─────────────────────────────────────────────────────┐
│  NetTools Suite                    [Theme: Light ▼] │
│  IPv4 Scanner & MAC Formatter                       │
├─────────────────────────────────────────────────────┤
│  [IPv4 Scanner] [MAC Formatter]                     │
│                                                      │
│  Content area (tabs)                                │
│                                                      │
├─────────────────────────────────────────────────────┤
│  Ready.                              © Malte Schad  │
└─────────────────────────────────────────────────────┘
```

---

## IPv4 Scanner

### Purpose

Scan IP networks to discover active hosts using ICMP ping.

### How to Use

#### 1. Enter CIDR Notation

In the "IPv4 / CIDR" field, enter a network range:

**Examples:**
```
192.168.1.0/24     → 254 hosts (192.168.1.1 - 192.168.1.254)
10.0.0.0/30        → 2 hosts (10.0.0.1 - 10.0.0.2)
172.16.5.100/32    → 1 host (172.16.5.100)
192.168.1.50/31    → 2 hosts (192.168.1.50 - 192.168.1.51)
8.8.8.0/28         → 14 hosts (8.8.8.1 - 8.8.8.14)
```

**CIDR Quick Reference:**
```
/32 = 1 host         /24 = 254 hosts
/31 = 2 hosts        /23 = 510 hosts
/30 = 2 hosts        /22 = 1,022 hosts
/29 = 6 hosts        /21 = 2,046 hosts
/28 = 14 hosts       /20 = 4,094 hosts
/27 = 30 hosts       /16 = 65,534 hosts
/26 = 62 hosts       /8  = 16,777,214 hosts
/25 = 126 hosts
```

#### 2. Select Aggressiveness

Choose scan speed based on your network:

**Gentle (longer timeout):**
- Timeout: 600ms per host
- Threads: 32 concurrent
- Best for: Slow/unreliable networks, VPNs
- Speed: Slower but more reliable

**Medium (default):**
- Timeout: 300ms per host
- Threads: 64 concurrent
- Best for: Normal LAN networks
- Speed: Balanced

**Aggressive (short timeout):**
- Timeout: 150ms per host
- Threads: 128 concurrent
- Best for: Fast local networks
- Speed: Fastest, may miss slow hosts

#### 3. Start Scan

Click **"Start Scan"** or press **Enter**

- Progress bar shows completion
- Results appear in real-time
- Status updates: "Scan running... (X / Y)"

#### 4. View Results

Results table shows:

| Status | IP Address    | Status      | Response (ms) |
|--------|---------------|-------------|---------------|
| 🟢     | 192.168.1.1   | Online      | 2.5           |
| ⚫     | 192.168.1.2   | No Response |               |
| 🟢     | 192.168.1.10  | Online      | 5.1           |

**Legend:**
- 🟢 Green dot = Host is online
- ⚫ Gray dot = No response

#### 5. Filter Results

Check **"Show only responding hosts"** to hide offline hosts.

#### 6. Export Results

Click **"Export as CSV"** or press **Ctrl+E**

- Choose save location (default: Desktop)
- File format: `NetToolsScan_YYYYMMDD_HHMMSS.csv`
- Opens in Excel, Google Sheets, etc.

**CSV Format:**
```csv
ip,status,rtt
192.168.1.1,Online,2.5
192.168.1.2,No Response,
192.168.1.10,Online,5.1
```

### Advanced Usage

#### Scanning Large Networks

For networks larger than /20 (~4,000 hosts), you'll get a warning:

```
Large Scan Warning
This range contains 16,382 hosts. The scan may take a long time. Continue?
[Yes] [No]
```

**Estimated scan times:**
```
/24 (254 hosts)   → ~5-10 seconds (Medium)
/22 (1,022 hosts) → ~20-40 seconds (Medium)
/20 (4,094 hosts) → ~1-2 minutes (Medium)
/16 (65,534 hosts) → ~15-30 minutes (Aggressive)
```

**Tips for large scans:**
- Use Aggressive mode
- Ensure stable network connection
- Don't minimize window (may slow updates)
- Can cancel anytime with **Cancel** button

#### Cancelling Scans

Click **"Cancel"** button at any time:
- Gracefully stops scanning
- Keeps results collected so far
- Can still export partial results

---

## MAC Formatter

### Purpose

Convert MAC addresses between formats and generate vendor-specific switch commands.

### How to Use

#### 1. Enter MAC Address

Type MAC address in any format:

**Accepted formats:**
```
AA:BB:CC:DD:EE:FF
aa:bb:cc:dd:ee:ff
AABBCCDDEEFF
aabbccddeeff
AA-BB-CC-DD-EE-FF
AA BB CC DD EE FF
```

**Auto-conversion happens instantly!**

#### 2. View Standard Formats

Four formats appear automatically:

```
Format 1 (Plain):   AABBCCDDEEFF
Format 2 (Colon):   AA:BB:CC:DD:EE:FF
Format 3 (Dash-4):  AABB-CCDD-EEFF
Format 4 (Dash-2):  AA-BB-CC-DD-EE-FF
```

**Copy any format:**
- Click **Copy** button next to format
- Or press **Enter** to copy Format 1

#### 3. View Switch Commands

Vendor-specific commands appear below:

**EXTREME CLI:**
```
show fdb AA:BB:CC:DD:EE:FF
```

**Huawei CLI:**
```
display mac-address AABB-CCDD-EEFF
```

**Huawei Access-User CLI:**
```
display access-user mac-address AABB-CCDD-EEFF
```

**Dell CLI:**
```
show mac address-table address AA:BB:CC:DD:EE:FF
```

**Toggle commands visibility:**
- Click **"Hide Commands"** / **"Show Commands"**

#### 4. Copy Commands

Click **Copy** button next to any command to copy it to clipboard.

### Validation

**Valid input:**
- 12 hexadecimal characters (0-9, A-F)
- Separators: `:`, `-`, space
- Case insensitive

**Invalid input examples:**
```
12:34:56          → Too short (6 chars, need 12)
XX:BB:CC:DD:EE:FF → Invalid character 'X'
00-11-22          → Too short (6 chars, need 12)
```

---

## Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action                          |
|----------|---------------------------------|
| Enter    | Start scan (IPv4 tab)           |
| Enter    | Copy Format 1 (MAC tab)         |
| Ctrl+E   | Export CSV (after scan)         |
| Alt+F4   | Close application (Windows)     |
| Cmd+Q    | Quit application (macOS)        |

### Tab Navigation

| Shortcut | Action                          |
|----------|---------------------------------|
| Ctrl+Tab | Switch to next tab              |
| Ctrl+Shift+Tab | Switch to previous tab    |

---

## Tips & Tricks

### IPv4 Scanner Tips

1. **Test connectivity first:**
   - Before large scan, test with `/32` (single IP)
   - Verify your network allows ICMP ping

2. **Optimize scan speed:**
   - Local network: Use Aggressive
   - VPN/slow network: Use Gentle
   - Unknown network: Start with Medium

3. **Scan your own subnet:**
   - Find your IP: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
   - If IP is `192.168.1.50`, scan `192.168.1.0/24`

4. **Export regularly:**
   - Save results before starting new scan
   - Old results are lost when starting new scan

5. **Use filtering:**
   - Large networks: Enable "Only responding hosts"
   - Reduces clutter in results

### MAC Formatter Tips

1. **Quick copy workflow:**
   - Type/paste MAC → Press Enter → Done!
   - Format 1 (plain) copied to clipboard

2. **Batch processing:**
   - Keep app open, process multiple MACs
   - Previous results stay visible until new input

3. **Command templates:**
   - Use generated commands as templates
   - Modify as needed for your switches

4. **Documentation:**
   - Export scan results with MAC addresses
   - Use formatter to generate lookup commands

### Theme Tips

1. **Choose based on environment:**
   - Light: Bright office, daytime
   - Dark: Dark room, nighttime, reduce eye strain

2. **System integration:**
   - Theme persists during session
   - Resets to Light on restart

---

## Troubleshooting

### IPv4 Scanner Issues

#### "All hosts show No Response"

**Possible causes:**
1. **Firewall blocking ICMP:**
   - Windows: Allow ICMP in firewall
   - Network: Check if ICMP is allowed

2. **Wrong network range:**
   - Verify CIDR is correct
   - Check your actual subnet

3. **Timeout too short:**
   - Try Gentle mode
   - Increase timeout in code if needed

4. **No network connectivity:**
   - Check internet/network connection
   - Ping a known host manually

#### "Scan takes too long"

**Solutions:**
1. Use Aggressive mode
2. Scan smaller subnets
3. Check network speed
4. Close other network-heavy apps

#### "Application freezes during scan"

**This is normal:**
- Progress updates every 5 hosts
- Large scans may appear frozen briefly
- Wait for progress bar to update
- If truly frozen (>5 min no update), restart

### MAC Formatter Issues

#### "No output appears"

**Causes:**
1. **Invalid MAC format:**
   - Check error message in red
   - Ensure 12 hex characters

2. **Empty input:**
   - Type or paste MAC address

#### "Copy button doesn't work"

**Solutions:**
1. **Try again:**
   - Sometimes clipboard access delayed

2. **Manual copy:**
   - Select text and Ctrl+C

3. **Check permissions:**
   - Some Linux systems need clipboard access

### General Issues

#### "Application won't start"

**Windows:**
1. Antivirus blocking → Add exception
2. Missing dependencies → Rebuild
3. Corrupted file → Re-download

**Linux:**
1. Missing libraries → `sudo apt install python3-tk`
2. No permissions → `chmod +x NetToolsSuite`
3. Need capabilities → `sudo setcap cap_net_raw+ep $(which python3)`

**macOS:**
1. Gatekeeper → Right-click → Open
2. Network permission → Grant in System Preferences

#### "Theme doesn't change"

**Solutions:**
1. Click theme dropdown again
2. Restart application
3. Check system theme settings

---

## FAQ

### General Questions

**Q: Do I need admin/root privileges?**  
A: 
- Windows: No
- Linux: Yes (or grant capabilities)
- macOS: No (but network permission needed)

**Q: Does it work offline?**  
A: Yes, if scanning local network. Internet not required.

**Q: Is my data sent anywhere?**  
A: No, everything runs locally. No telemetry.

**Q: Can I use it commercially?**  
A: Check with the author (Malte Schad) for licensing.

### IPv4 Scanner Questions

**Q: What is CIDR notation?**  
A: Format: `IP/PREFIX` where PREFIX is subnet size (0-32)  
Example: `192.168.1.0/24` = 192.168.1.1 to 192.168.1.254

**Q: Can I scan the entire internet?**  
A: Technically yes (/0), but:
- Would take months/years
- Likely illegal in most jurisdictions
- Will get your IP blocked
- **Don't do it!**

**Q: Why are some online hosts not detected?**  
A: 
- Host firewall blocking ICMP
- Network ACLs blocking ping
- Timeout too short
- Host legitimately offline

**Q: Can I scan IPv6?**  
A: No, currently IPv4 only. IPv6 support planned.

**Q: What's the largest network I can scan?**  
A: Any size, but practical limit is /16 (~65k hosts) due to time.

### MAC Formatter Questions

**Q: Does it validate real MAC addresses?**  
A: Only format validation, not vendor lookup (no OUI database).

**Q: Can I look up MAC vendor?**  
A: No, but you can add this feature with an OUI database.

**Q: Do the switch commands work on all models?**  
A: Most modern models, but syntax may vary. Check your switch docs.

**Q: Can I add more switch vendors?**  
A: Yes, modify `generate_switch_commands()` in code.

### Performance Questions

**Q: Why is startup slow?**  
A: Single-file executables extract to temp first (~2-3 sec).

**Q: How to make scans faster?**  
A:
1. Use Aggressive mode
2. Scan smaller subnets
3. Ensure good network connection

**Q: How much RAM does it use?**  
A: ~50-80 MB while running, ~100-150 MB during large scans.

---

## Support

For issues not covered here:

1. Check [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for build issues
2. Check [README.md](README.md) for technical details
3. Contact: Malte Schad

---

**Enjoy using NetTools Suite!** 🚀

*Last updated: 2025*
