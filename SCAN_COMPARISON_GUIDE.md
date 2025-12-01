# Scan Comparison Feature Guide

## Overview

The **Scan Comparison** feature allows you to compare two network scans to identify changes in your network over time. This is incredibly useful for:

- **Security monitoring**: Detect new or missing devices
- **Troubleshooting**: Identify which hosts went offline between scans
- **Auditing**: Track changes in network topology
- **Documentation**: Create change reports for compliance

---

## How It Works

### 1. Automatic Scan Storage

Every time you complete a network scan, the results are **automatically saved** for future comparison. The app stores:
- Up to **20 recent scans** per network
- Complete scan results (IP addresses, online/offline status, response times)
- Timestamp and CIDR information
- Summary statistics (total hosts, online count, offline count)

**Storage location**: `~/.nettools/scans.json` (in your home directory)

### 2. Comparing Scans

Once you have at least 2 saved scans, the "Compare Scans" button becomes available.

**Steps to compare:**
1. Click **"Compare Scans"** button (appears after you run a scan)
2. Select **Scan 1** from the dropdown (older scan)
3. Select **Scan 2** from the dropdown (newer scan)
4. Click **"Compare"** to see the differences

---

## Understanding Comparison Results

### Change Types

The comparison shows four types of changes:

| Icon | Type | Meaning |
|------|------|---------|
| ✅ | **Unchanged** | Host status is the same in both scans |
| 🆕 | **New** | Host appeared in Scan 2 (not in Scan 1) |
| ❌ | **Missing** | Host was in Scan 1 but not in Scan 2 |
| 🔄 | **Changed** | Host changed status (online → offline or vice versa) |

### Summary Statistics

At the top of the comparison results, you'll see:
```
✅ Unchanged: 250  |  🆕 New: 2  |  ❌ Missing: 1  |  🔄 Changed: 1
```

This gives you an instant overview of what changed between scans.

### Detailed Results

Each row shows:
- **Change Type**: Visual indicator (icon)
- **IP Address**: The host IP
- **Scan 1 Status**: Online/Offline in the first scan
- **Scan 2 Status**: Online/Offline in the second scan
- **Scan 1 RTT**: Response time in milliseconds (first scan)
- **Scan 2 RTT**: Response time in milliseconds (second scan)

---

## Exporting Comparison Reports

You can export comparison results to a CSV file:

1. Perform a comparison
2. Click **"Export Comparison"** button
3. Choose save location
4. File is saved with name: `comparison_[scan1]_vs_[scan2].csv`

**CSV Format:**
```
Change,IP Address,Scan 1 Status,Scan 2 Status,Scan 1 RTT,Scan 2 RTT
new,192.168.1.50,N/A,Online,-,3.2
missing,192.168.1.100,Online,N/A,5.1,-
changed,192.168.1.75,Online,Offline,2.5,-
unchanged,192.168.1.1,Online,Online,1.2,1.3
```

---

## Practical Use Cases

### 1. Security Monitoring

**Scenario**: Check for unauthorized devices on your network

**How to use:**
1. Run a baseline scan of your network (e.g., `192.168.1.0/24`)
2. Run the same scan again later (hourly, daily, weekly)
3. Compare the scans
4. Look for 🆕 **New** devices that you don't recognize
5. Investigate any unexpected new hosts

**Example:**
```
🆕 192.168.1.185    N/A → Online
```
→ A new device appeared at 192.168.1.185. Is this authorized?

---

### 2. Troubleshooting Network Issues

**Scenario**: Users report connectivity problems

**How to use:**
1. Run a scan when everything is working (baseline)
2. Run another scan during the reported issue
3. Compare to see which hosts went offline
4. Focus troubleshooting on the affected devices

**Example:**
```
❌ 192.168.1.50    Online → N/A
❌ 192.168.1.51    Online → N/A
```
→ Hosts 192.168.1.50-51 went offline. Check that switch!

---

### 3. Change Documentation

**Scenario**: Document network changes for compliance

**How to use:**
1. Run a scan before maintenance
2. Run a scan after maintenance
3. Compare and export to CSV
4. Include in change documentation

**Example CSV export:**
```
Changed: 3 hosts
New: 5 hosts (newly installed)
Missing: 2 hosts (decommissioned)
```

---

### 4. Scheduled Monitoring

**Scenario**: Regular network health checks

**How to use:**
1. Run scans at regular intervals (e.g., every morning)
2. Compare today's scan with yesterday's
3. Look for unexpected changes
4. Create a daily report

**Example workflow:**
```
Monday 9 AM:    Scan → 250 hosts online
Tuesday 9 AM:   Scan → 252 hosts online
                Compare: 🆕 2 new hosts detected
```

---

## Tips & Best Practices

### 1. Regular Scans
Run scans at consistent times to build a history:
- Daily morning scan for office networks
- Hourly scans for critical infrastructure
- Weekly scans for infrequently-used networks

### 2. Scan Retention
The app keeps the **20 most recent scans** per network. Older scans are automatically removed. Export important comparisons if you need long-term records.

### 3. Same CIDR Comparison
For meaningful comparisons, compare scans of the **same network** (same CIDR). Comparing different networks doesn't make sense!

✅ Good: Compare `192.168.1.0/24` vs `192.168.1.0/24`  
❌ Bad: Compare `192.168.1.0/24` vs `10.0.0.0/24`

### 4. Export Important Changes
If you find critical changes (security issues, outages), export the comparison immediately for documentation.

### 5. Baseline Scans
Create a "golden" baseline scan when your network is in a known-good state. Compare all future scans against this baseline to track drift.

---

## Troubleshooting

### "You need at least 2 saved scans to compare"
**Solution**: Run at least 2 scans of the same network. The first scan creates a baseline, the second scan can be compared.

### "No differences shown"
**Possible causes:**
- You selected the same scan twice (use different scans)
- Network state hasn't actually changed between scans
- Both scans found 0 hosts

### "Scans are gone after app restart"
**This is normal!** Scans are saved to `~/.nettools/scans.json` and persist across app restarts. However:
- Only the 20 most recent scans are kept
- If the file is deleted or corrupted, history is lost

---

## Advanced: Manual Scan Management

Scan data is stored in JSON format at:
```
Windows: C:\Users\<YourName>\.nettools\scans.json
Linux: ~/.nettools/scans.json
```

You can:
- **Backup**: Copy `scans.json` to preserve scan history
- **Share**: Send `scans.json` to colleagues
- **Restore**: Replace `scans.json` to restore old scans
- **Clear**: Delete `scans.json` to start fresh

---

## Coming Soon

Future enhancements planned:
- 📊 Graphical timeline of network changes
- 🔔 Alert notifications for new/missing devices
- 📧 Email comparison reports automatically
- 🔄 Scheduled automatic scanning
- 📈 Trend analysis (show patterns over multiple scans)

---

## Version Info

**Feature added**: v1.1.0  
**Last updated**: November 2024  

For more information, see `FEATURE_IMPLEMENTATION_PLAN.md`
