# NetTools Suite v2.0 - Feature Implementation Plan

## 🎯 Selected Features for Implementation

Based on your selection, here's a comprehensive plan for the next version:

---

## 1. History & Recent Items ⭐⭐⭐⭐⭐

### Implementation Details

**Storage:**
```python
# Store in JSON file: ~/.nettools/history.json
{
  "recent_cidrs": [
    {"cidr": "192.168.1.0/24", "timestamp": "2025-01-15T10:30:00", "count": 5},
    {"cidr": "10.0.0.0/24", "timestamp": "2025-01-14T14:20:00", "count": 2}
  ],
  "recent_macs": [
    {"mac": "AA:BB:CC:DD:EE:FF", "vendor": "Apple Inc.", "timestamp": "2025-01-15T11:00:00"},
    {"mac": "00:11:22:33:44:55", "vendor": "Cisco", "timestamp": "2025-01-15T10:45:00"}
  ]
}
```

**UI Changes:**
- CIDR field: Add dropdown button with recent scans
- MAC field: Add dropdown button with recent MACs
- Both show last 10 items
- Include "Clear History" option

**Features:**
- Auto-save on each scan/format
- Sort by most recent
- Show usage count
- Quick select from dropdown

**Effort:** 1 day  
**Value:** Very High

---

## 2. OUI Vendor Lookup ⭐⭐⭐⭐⭐

### Implementation Details

**Database:**
```python
# Include IEEE OUI database
# File: oui.txt (from standards.ieee.org)
# Size: ~2-3 MB
# Format: 
# AA-BB-CC   Apple, Inc.
# 00-11-22   Cisco Systems, Inc.
```

**Lookup Logic:**
```python
def get_vendor(mac):
    oui = mac[:8].replace(':', '-').upper()  # AA:BB:CC -> AA-BB-CC
    return oui_database.get(oui, "Unknown Vendor")
```

**UI Integration:**
```
┌─────────────────────────────────────────┐
│ Enter MAC Address:                      │
│ [AA:BB:CC:DD:EE:FF_______________]      │
│ Vendor: Apple Inc. 🍎                   │
├─────────────────────────────────────────┤
│ Standard MAC Formats                    │
│ ...                                     │
└─────────────────────────────────────────┘
```

**Features:**
- Offline lookup (no internet needed)
- Auto-update database (download button)
- Cache results for performance
- Show in scan results too

**Effort:** 2 days  
**Value:** Very High

---

## 3. Scan Comparison 🔄⭐⭐⭐⭐

### Implementation Details

**Storage:**
```python
# Store scans in database
scans = {
  "id": "scan_20250115_103000",
  "cidr": "192.168.1.0/24",
  "timestamp": "2025-01-15T10:30:00",
  "aggression": "Medium",
  "results": [
    {"ip": "192.168.1.1", "status": "Online", "rtt": 2.5},
    {"ip": "192.168.1.2", "status": "Offline", "rtt": null}
  ]
}
```

**Comparison UI:**
```
┌──────────────────────────────────────────────────┐
│ Compare Scans                                    │
├──────────────────────────────────────────────────┤
│ Scan 1: [2025-01-15 10:30 ▼] 192.168.1.0/24     │
│ Scan 2: [2025-01-15 14:45 ▼] 192.168.1.0/24     │
│                                                  │
│ [Compare]                                        │
│                                                  │
│ Changes Found:                                   │
│ ✓ 192.168.1.1   (unchanged - online)            │
│ + 192.168.1.50  (NEW - now online)              │
│ - 192.168.1.100 (MISSING - now offline)         │
│ ✓ 192.168.1.200 (unchanged - online)            │
│                                                  │
│ Summary: 1 new, 1 missing, 252 unchanged        │
│                                                  │
│ [Export Report]                                  │
└──────────────────────────────────────────────────┘
```

**Features:**
- Compare any two scans
- Highlight differences
- Export comparison report
- Show what changed (new/missing/changed)
- Timeline view

**Effort:** 3 days  
**Value:** High (unique feature!)

---

## 4. Design Improvements 🎨

### 4.1 Animated Status Indicators
```python
# Pulsing dot while scanning
# Color-coded response times:
- Green: < 10ms (fast)
- Yellow: 10-50ms (normal)
- Orange: 50-100ms (slow)
- Red: > 100ms (very slow)
```

### 4.2 Tooltips
```python
# Add tooltips everywhere:
CIDR field: "Enter network in CIDR format (e.g., 192.168.1.0/24)"
Aggression: "Gentle: slow networks, Aggressive: fast LANs"
Status dot: "Green = online, Gray = offline"
Copy button: "Click to copy to clipboard"
```

### 4.3 Statistics Dashboard
```
┌─────────────────────────────────────┐
│ Scan Summary                        │
├─────────────────────────────────────┤
│ 📊 Total Hosts: 254                 │
│ ✅ Online: 12 (4.7%)                │
│ ❌ Offline: 242 (95.3%)             │
│ ⚡ Avg Response: 3.2ms              │
│ ⏱️  Duration: 8.5 seconds           │
│ 🚀 Speed: 29.9 hosts/sec            │
└─────────────────────────────────────┘
```

### 4.4 Progress Details
```
Scanning... (45 / 254)
⬛⬛⬛⬛⬛⬜⬜⬜⬜⬜ 18%
⏱️ Estimated: 15s remaining
⚡ 17 hosts/sec
✅ 3 online | ❌ 42 offline
```

**Effort:** 2 days  
**Value:** High (polish!)

---

## 5. Performance Boosts ⚡

### 5.1 Result Caching
```python
# Cache scan results for 5 minutes
cache = {
  "192.168.1.0/24": {
    "results": [...],
    "timestamp": "2025-01-15T10:30:00",
    "expiry": 300  # seconds
  }
}

# If scanning same CIDR within 5 min:
if cidr in cache and not expired:
    return cache[cidr]
```

### 5.2 Faster Ping Library
```python
# Replace pythonping with icmplib
from icmplib import ping

# Reported 20-30% faster
# Better timeout handling
# More reliable on Windows
```

### 5.3 Lazy Loading
```python
# Only render visible rows in results
# Use virtual scrolling
# Smooth UI even with 10,000+ hosts
```

### 5.4 SQLite Database
```python
# Replace JSON files with SQLite
# Fast queries, efficient storage
# Better for history/comparison
```

**Effort:** 2 days  
**Value:** Medium-High

---

## 6. Additional Tools 🔧

### 6.1 DNS Lookup Integration
```
Scan Results:
┌──────────────────────────────────────────────────┐
│ IP Address     Status  RTT    Hostname           │
├──────────────────────────────────────────────────┤
│ 192.168.1.1    Online  2.5ms  router.local       │
│ 192.168.1.10   Online  5.1ms  pc-john.local      │
│ 192.168.1.50   Online  8.2ms  printer-hp.local   │
└──────────────────────────────────────────────────┘
```

### 6.2 Traceroute
```
New Tab: [Traceroute]
┌─────────────────────────────────────┐
│ Target: [8.8.8.8___________]        │
│ [Start Traceroute]                  │
│                                     │
│ Hop  IP Address      RTT            │
│  1   192.168.1.1     1ms            │
│  2   10.0.0.1        5ms            │
│  3   172.16.0.1      12ms           │
│  4   8.8.8.8         25ms           │
└─────────────────────────────────────┘
```

### 6.3 Port Scanner
```
New Tab: [Port Scanner]
┌─────────────────────────────────────┐
│ Target: [192.168.1.1___________]    │
│ Ports: [1-1024___________] Common   │
│ [Scan Ports]                        │
│                                     │
│ Open Ports:                         │
│  22  SSH                            │
│  80  HTTP                           │
│  443 HTTPS                          │
│  8080 HTTP-Proxy                    │
└─────────────────────────────────────┘
```

### 6.4 Subnet Calculator
```
New Tab: [Subnet Calculator]
┌─────────────────────────────────────┐
│ CIDR: [192.168.1.0/24__________]    │
│ [Calculate]                         │
│                                     │
│ Network:      192.168.1.0           │
│ Broadcast:    192.168.1.255         │
│ Netmask:      255.255.255.0         │
│ Wildcard:     0.0.0.255             │
│ First Host:   192.168.1.1           │
│ Last Host:    192.168.1.254         │
│ Total Hosts:  254                   │
└─────────────────────────────────────┘
```

**Effort:** 4-5 days (all 4 tools)  
**Value:** High (professional toolkit!)

---

## 7. 🆕 Network Interface Profile Manager ⭐⭐⭐⭐⭐

### Why This Is AMAZING

Network admins constantly switch between:
- Office network (DHCP)
- Server network (Static IP)
- Testing network (Different subnet)
- Home network (Different config)

**Windows makes this painful!** This feature makes it ONE CLICK! 🚀

### Implementation Details

**Profile Storage:**
```json
{
  "profiles": [
    {
      "name": "Office DHCP",
      "interface": "Ethernet",
      "dhcp": true,
      "dns": "auto"
    },
    {
      "name": "Server Static",
      "interface": "Ethernet",
      "dhcp": false,
      "ip": "192.168.1.100",
      "subnet": "255.255.255.0",
      "gateway": "192.168.1.1",
      "dns": ["8.8.8.8", "8.8.4.4"]
    },
    {
      "name": "Lab Network",
      "interface": "Ethernet",
      "dhcp": false,
      "ip": "10.0.0.50",
      "subnet": "255.255.255.0",
      "gateway": "10.0.0.1",
      "dns": ["10.0.0.1"]
    }
  ]
}
```

**UI Design:**
```
New Tab: [Network Profiles] 🌐
┌──────────────────────────────────────────────────┐
│ Active Interface: Ethernet ▼                     │
│ Current IP: 192.168.1.100 (Static)              │
├──────────────────────────────────────────────────┤
│ Saved Profiles:                                  │
│                                                  │
│ ┌──────────────────────────────────────┐       │
│ │ 🏢 Office DHCP              [Apply]   │       │
│ │ Interface: Ethernet                   │       │
│ │ Type: DHCP                            │       │
│ │ DNS: Automatic                        │       │
│ └──────────────────────────────────────┘       │
│                                                  │
│ ┌──────────────────────────────────────┐ ⭐    │
│ │ 🖥️ Server Static            [Apply]   │ Active│
│ │ Interface: Ethernet                   │       │
│ │ IP: 192.168.1.100/24                 │       │
│ │ Gateway: 192.168.1.1                 │       │
│ │ DNS: 8.8.8.8, 8.8.4.4                │       │
│ └──────────────────────────────────────┘       │
│                                                  │
│ ┌──────────────────────────────────────┐       │
│ │ 🧪 Lab Network              [Apply]   │       │
│ │ Interface: Ethernet                   │       │
│ │ IP: 10.0.0.50/24                     │       │
│ │ Gateway: 10.0.0.1                    │       │
│ │ DNS: 10.0.0.1                        │       │
│ └──────────────────────────────────────┘       │
│                                                  │
│ [+ New Profile]  [Edit]  [Delete]              │
└──────────────────────────────────────────────────┘
```

**Create/Edit Profile:**
```
┌──────────────────────────────────────┐
│ New Network Profile                  │
├──────────────────────────────────────┤
│ Profile Name:                        │
│ [Home Network____________]           │
│                                      │
│ Interface:                           │
│ [Ethernet ▼]                         │
│                                      │
│ Configuration Type:                  │
│ ○ DHCP (Automatic)                   │
│ ● Static IP                          │
│                                      │
│ IP Address:                          │
│ [192.168.1.___]                      │
│                                      │
│ Subnet Mask:                         │
│ [255.255.255.0 ▼]                    │
│                                      │
│ Default Gateway:                     │
│ [192.168.1.1___]                     │
│                                      │
│ DNS Servers:                         │
│ Primary:   [8.8.8.8_______]          │
│ Secondary: [8.8.4.4_______]          │
│                                      │
│ [Save Profile]  [Cancel]             │
└──────────────────────────────────────┘
```

**Windows Implementation:**
```python
import subprocess
import ctypes

def is_admin():
    """Check if running with admin rights"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def apply_dhcp_profile(interface):
    """Set interface to DHCP"""
    subprocess.run([
        'netsh', 'interface', 'ip', 'set', 'address',
        f'name={interface}', 'source=dhcp'
    ], check=True)
    
    subprocess.run([
        'netsh', 'interface', 'ip', 'set', 'dns',
        f'name={interface}', 'source=dhcp'
    ], check=True)

def apply_static_profile(interface, ip, subnet, gateway, dns_servers):
    """Set static IP configuration"""
    # Set IP address
    subprocess.run([
        'netsh', 'interface', 'ip', 'set', 'address',
        f'name={interface}',
        'source=static',
        f'addr={ip}',
        f'mask={subnet}',
        f'gateway={gateway}'
    ], check=True)
    
    # Set DNS servers
    for i, dns in enumerate(dns_servers):
        if i == 0:
            subprocess.run([
                'netsh', 'interface', 'ip', 'set', 'dns',
                f'name={interface}',
                'source=static',
                f'addr={dns}',
                'primary'
            ], check=True)
        else:
            subprocess.run([
                'netsh', 'interface', 'ip', 'add', 'dns',
                f'name={interface}',
                f'addr={dns}',
                f'index={i+1}'
            ], check=True)

def get_interfaces():
    """List available network interfaces"""
    result = subprocess.run(
        ['netsh', 'interface', 'show', 'interface'],
        capture_output=True, text=True
    )
    # Parse output to get interface names
    return parse_interfaces(result.stdout)

def get_current_config(interface):
    """Get current IP configuration"""
    result = subprocess.run(
        ['netsh', 'interface', 'ip', 'show', 'config', f'name={interface}'],
        capture_output=True, text=True
    )
    return parse_config(result.stdout)
```

**Features:**
- Save unlimited profiles
- Quick switch (one click!)
- Auto-detect interfaces
- Show current configuration
- Import/export profiles
- Admin elevation prompt
- Apply and test connection

**User Benefits:**
- NO MORE: Control Panel → Network → Change Adapter Settings → Properties → TCP/IPv4 → ...
- NOW: Click profile → Apply → Done! ✨

**Effort:** 3-4 days  
**Value:** EXTREMELY HIGH (killer feature!)

---

## 8. 🆕 phpIPAM API Integration ⭐⭐⭐⭐⭐

### Why This Is CRITICAL

phpIPAM is the most popular open-source IP address management (IPAM) system. Integration means:
- Automatic documentation of discovered hosts
- Centralized IP management
- Enterprise-level integration
- Professional network management

### Implementation Details

**phpIPAM API Basics:**
```python
import requests

class phpIPAM:
    def __init__(self, url, app_id, username, password):
        self.url = url
        self.app_id = app_id
        self.token = self.authenticate(username, password)
    
    def authenticate(self, username, password):
        """Get API token"""
        response = requests.post(
            f"{self.url}/api/{self.app_id}/user/",
            auth=(username, password)
        )
        return response.json()['data']['token']
    
    def get_subnets(self):
        """List all subnets"""
        headers = {'token': self.token}
        response = requests.get(
            f"{self.url}/api/{self.app_id}/subnets/",
            headers=headers
        )
        return response.json()['data']
    
    def get_subnet_addresses(self, subnet_id):
        """Get all IPs in subnet"""
        headers = {'token': self.token}
        response = requests.get(
            f"{self.url}/api/{self.app_id}/subnets/{subnet_id}/addresses/",
            headers=headers
        )
        return response.json()['data']
    
    def update_address(self, ip, hostname=None, mac=None, description=None):
        """Update IP address info"""
        headers = {'token': self.token}
        data = {}
        if hostname: data['hostname'] = hostname
        if mac: data['mac'] = mac
        if description: data['description'] = description
        
        response = requests.patch(
            f"{self.url}/api/{self.app_id}/addresses/{ip}/",
            headers=headers,
            json=data
        )
        return response.json()
```

**UI Design:**
```
Settings → [phpIPAM Integration] 🔗
┌──────────────────────────────────────────────────┐
│ phpIPAM Connection Settings                      │
├──────────────────────────────────────────────────┤
│ Server URL:                                      │
│ [https://ipam.company.com____________]           │
│                                                  │
│ App ID:                                          │
│ [nettools___________]                            │
│                                                  │
│ Username:                                        │
│ [admin______________]                            │
│                                                  │
│ Password:                                        │
│ [••••••••••••••••••]                            │
│                                                  │
│ [Test Connection]                                │
│ ✓ Connected successfully!                       │
│                                                  │
│ Auto-sync options:                               │
│ ☑ Upload scan results automatically              │
│ ☑ Update existing hosts                          │
│ ☐ Create new hosts                               │
│ ☐ Update MAC addresses                           │
│                                                  │
│ [Save Settings]                                  │
└──────────────────────────────────────────────────┘
```

**Integration in Scan Results:**
```
After Scan:
┌──────────────────────────────────────────────────┐
│ Scan Complete: 192.168.1.0/24                    │
│ 12 hosts online, 242 offline                     │
│                                                  │
│ [Export CSV] [Copy Results] [🔗 Sync to phpIPAM]│
└──────────────────────────────────────────────────┘

Click "Sync to phpIPAM":
┌──────────────────────────────────────┐
│ Syncing to phpIPAM...                │
├──────────────────────────────────────┤
│ ✓ 192.168.1.1   Updated              │
│ ✓ 192.168.1.10  Updated              │
│ + 192.168.1.50  Created (new)        │
│ ✓ 192.168.1.100 Updated              │
│                                      │
│ Summary:                             │
│ Updated: 11                          │
│ Created: 1                           │
│ Errors: 0                            │
│                                      │
│ [Close]                              │
└──────────────────────────────────────┘
```

**Advanced Features:**
```
New Tab: [IPAM Browser] 📚
┌──────────────────────────────────────────────────┐
│ phpIPAM Subnets                                  │
├──────────────────────────────────────────────────┤
│ Search: [________] 🔍                            │
│                                                  │
│ 📁 Production                                    │
│   └─ 192.168.1.0/24    (254 hosts, 12 used)    │
│   └─ 192.168.2.0/24    (254 hosts, 45 used)    │
│                                                  │
│ 📁 Management                                    │
│   └─ 10.0.0.0/24       (254 hosts, 8 used)     │
│                                                  │
│ 📁 Guest Network                                 │
│   └─ 172.16.0.0/24     (254 hosts, 23 used)    │
│                                                  │
│ Selected: 192.168.1.0/24                         │
│ [Scan This Subnet] [View Details]               │
└──────────────────────────────────────────────────┘

Details View:
┌──────────────────────────────────────────────────┐
│ Subnet: 192.168.1.0/24 (Production)              │
├──────────────────────────────────────────────────┤
│ IP Address     Status  Hostname      MAC         │
│ 192.168.1.1    Used    router        AA:BB:CC... │
│ 192.168.1.2    Free    -             -           │
│ 192.168.1.10   Used    pc-john       11:22:33... │
│ 192.168.1.50   Used    printer-hp    00:11:22... │
│                                                  │
│ [Export] [Scan Network] [Refresh from IPAM]     │
└──────────────────────────────────────────────────┘
```

**Features:**
- Two-way sync (scan → IPAM, IPAM → scan)
- Browse phpIPAM subnets
- Scan directly from IPAM
- Auto-update on scan
- Bulk operations
- Conflict detection
- Audit logging

**User Benefits:**
- Automated documentation
- Central IP management
- No manual data entry
- Always up-to-date
- Enterprise integration

**Effort:** 4-5 days  
**Value:** EXTREMELY HIGH (enterprise feature!)

---

## 📊 Implementation Summary

### Total Effort Estimate
- History & Recent Items: 1 day
- OUI Vendor Lookup: 2 days
- Scan Comparison: 3 days
- Design Improvements: 2 days
- Performance Boosts: 2 days
- Additional Tools: 5 days
- Network Profile Manager: 4 days
- phpIPAM Integration: 5 days

**TOTAL: ~24 days (3-4 weeks)**

### Priority Phases

**Phase 1: Quick Wins (1 week)**
1. History & Recent Items
2. OUI Vendor Lookup
3. Design Improvements (tooltips, stats)
4. Basic performance boosts

**Phase 2: Advanced Features (1 week)**
1. Scan Comparison
2. Network Profile Manager
3. Additional Tools (DNS, Subnet calc)

**Phase 3: Enterprise Integration (1 week)**
1. phpIPAM Integration
2. Advanced performance (SQLite, caching)
3. Port scanner & Traceroute

**Phase 4: Polish & Testing (3-5 days)**
1. Bug fixes
2. Documentation
3. Testing
4. Build & release

---

## 🎯 Recommended Approach

### Option A: Full Implementation
Build everything over 3-4 weeks for a complete professional suite.

### Option B: Phased Releases
- v1.1: History + OUI + Design improvements (1 week)
- v1.2: Scan Comparison + Profile Manager (1 week)
- v1.3: phpIPAM + Additional Tools (2 weeks)

### Option C: Custom Selection
Pick the features you want most!

---

## 💡 My Strong Recommendation

**Start with Phase 1 (Quick Wins):**
1. History & Recent Items (saves so much time!)
2. OUI Vendor Lookup (professional & useful)
3. Design improvements (polish)

**Then add the KILLER FEATURES:**
4. Network Profile Manager (unique! admins will love it!)
5. phpIPAM Integration (enterprise-level!)

These 5 features would make this tool absolutely **ESSENTIAL** for any network admin! 🚀

---

## 🤔 Questions for You

1. **Timeline:** How quickly do you want these features?
   - Rush: Focus on Phase 1 only
   - Balanced: Phased releases
   - Complete: All features

2. **Priority:** Which is most important to you?
   - Time-saving (History, Profiles)
   - Information (OUI, DNS lookup)
   - Enterprise (phpIPAM, comparison)

3. **Start with:** Which feature should I implement FIRST?
   - A) History dropdown (quickest value)
   - B) Network Profile Manager (unique feature)
   - C) phpIPAM integration (enterprise)
   - D) OUI vendor lookup (useful for everyone)

**Let me know and I'll start implementing immediately!** 🎯
