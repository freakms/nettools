# Live Ping Monitor - Feature Guide

## Overview
The Live Ping Monitor is a real-time network monitoring tool that continuously pings multiple hosts and displays latency graphs for each host. It provides instant visual feedback on network connectivity and performance.

## Features

### ✅ Core Functionality
- **Continuous Monitoring**: Pings hosts every 1 second automatically
- **Multiple Hosts**: Monitor multiple IPs and hostnames simultaneously
- **Real-Time Graphs**: Each host displays a graph showing the last 30 pings
- **Status Indicators**: Color-coded status dots (green/yellow/red)
- **Hostname Resolution**: Automatically resolves hostnames to IPs
- **Statistics**: Shows average latency and packet loss percentage

### ✅ Controls
- **Start**: Begin monitoring entered hosts
- **Pause**: Temporarily pause monitoring (keeps data)
- **Resume**: Continue monitoring after pause
- **Stop**: Stop monitoring and reset
- **Export**: Save monitoring data to text file

### ✅ Visual Status Indicators
- 🟢 **Green**: Host online with good latency (<50ms)
- 🟡 **Yellow**: Host online with high latency (>50ms)
- 🔴 **Red**: Host offline/unreachable

## How to Use

### 1. Access the Monitor
- Navigate to the **IPv4 Scanner** page
- Click the **"📊 Live Monitor"** button in the scan controls

### 2. Enter Hosts to Monitor
In the input field, enter one or more hosts separated by commas or spaces:

**Examples:**
```
192.168.1.1
192.168.1.1, 8.8.8.8, google.com
192.168.1.1 8.8.8.8 1.1.1.1
server1.local, 10.0.0.1, cloudflare.com
```

### 3. Start Monitoring
- Click **"▶ Start Monitoring"**
- Each host will appear with its own graph
- Graphs update in real-time every second

### 4. Interpret the Results

**For Each Host:**
- **Status Dot**: Shows current connectivity status
- **IP Address**: The monitored IP
- **Hostname**: Original hostname if provided
- **Avg**: Average latency across all pings
- **Loss**: Packet loss percentage
- **Graph**: Visual representation of last 30 pings
  - Green line shows latency over time
  - Gaps indicate timeouts/unreachable

### 5. Control Monitoring

**Pause Monitoring:**
- Click **"⏸ Pause"** to temporarily stop pinging
- Data is preserved and continues displaying
- Resume anytime with **"▶ Resume"**

**Stop Monitoring:**
- Click **"⏹ Stop"** to completely stop monitoring
- Allows entering new hosts

### 6. Export Data
- Click **"📤 Export"** at any time
- Saves detailed monitoring report to text file
- Includes all statistics and ping history

## Export Format

The exported file contains:
```
Live Ping Monitor - Export Data
============================================================

Host: 192.168.1.1
Hostname: router.local
Status: Online (Good Latency)
Average Latency: 1.5 ms
Packet Loss: 0.0%
Total Pings: 120

Recent Pings (last 30):
  1. 1.2 ms
  2. 1.5 ms
  3. 1.8 ms
  ...
```

## Use Cases

### Network Troubleshooting
- Monitor critical servers during maintenance
- Track intermittent connectivity issues
- Identify latency spikes in real-time

### Infrastructure Monitoring
- Monitor multiple network devices simultaneously
- Verify failover events
- Track network performance during load tests

### Home/Office Network
- Monitor internet gateway responsiveness
- Track ISP connectivity quality
- Monitor local servers and devices

## Tips & Best Practices

### Performance
- **Recommended**: Monitor 5-10 hosts simultaneously
- **Maximum**: Can handle 20+ hosts, but UI may slow down
- Each host is pinged in its own thread for efficiency

### Hostname Resolution
- Hostnames are resolved when monitoring starts
- If a hostname fails to resolve, it won't be added
- Use IP addresses for faster setup

### Long-Running Monitors
- The tool keeps only the last 30 pings per host
- Memory usage remains constant regardless of duration
- Safe to run for hours or days

### Interpreting Results
- **Consistent low latency**: Good network path
- **Variable latency**: Network congestion or wireless issues
- **Increasing latency**: Potential network degradation
- **Packet loss**: Connectivity problems or overloaded device

## Technical Details

### Graph Display
- **X-Axis**: Last 30 pings (numbered 1-30)
- **Y-Axis**: Latency in milliseconds (auto-scaling)
- **Update Rate**: 1 second
- **Data Points**: 30 pings retained per host

### Status Thresholds
- **Green (Good)**: Latency < 50ms
- **Yellow (High)**: Latency ≥ 50ms
- **Red (Offline)**: Ping timeout/failure

### Thread Safety
- Each host is monitored in a separate thread
- UI updates are synchronized safely
- Safe to pause/resume/stop at any time

## Troubleshooting

**No data appearing:**
- Check if host is reachable with regular IPv4 scanner first
- Verify firewall allows ICMP (ping) packets
- Try using IP address instead of hostname

**Graphs not updating:**
- Click Stop and Start again
- Close and reopen the Live Monitor window
- Check system resources (CPU/memory)

**High packet loss:**
- Verify with standard scan tool
- Check network path with traceroute tool
- May indicate firewall blocking ICMP

**Window unresponsive:**
- Too many hosts being monitored
- Reduce number of concurrent monitors
- Stop monitoring and restart

## Keyboard Shortcuts

Currently no keyboard shortcuts. Use mouse to interact with controls.

## Future Enhancements

Potential improvements for future versions:
- Audible alerts on status changes
- Threshold customization (latency/loss alerts)
- Save/load monitoring profiles
- CSV export format
- Historical data logging
- Jitter measurement
- Multiple ping windows
