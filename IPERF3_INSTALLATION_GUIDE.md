# iperf3 Installation Guide for NetTools Suite

## Overview
The Bandwidth Testing tool in NetTools Suite requires **iperf3** to be installed separately on your system. This guide will walk you through the installation process.

## What is iperf3?
iperf3 is a network performance measurement tool that can test maximum achievable bandwidth between two systems.

---

## Windows Installation

### Step 1: Download iperf3
1. Visit the official iperf3 download page:
   - **Official Site**: [https://iperf.fr/iperf-download.php](https://iperf.fr/iperf-download.php)
   - Look for "Windows" section
   - Download the latest Windows binary (iperf3-win64.zip or similar)

2. Alternative download locations:
   - [https://files.budman.pw/](https://files.budman.pw/) (trusted community builds)

### Step 2: Extract the Files
1. Extract the downloaded ZIP file
2. You will find `iperf3.exe` inside
3. Choose an installation location:
   - **Recommended**: `C:\Tools\iperf3\`
   - **Alternative**: `C:\Program Files\iperf3\`
4. Copy `iperf3.exe` to your chosen location

### Step 3: Add to Windows PATH
To use iperf3 from anywhere (including NetTools Suite), you need to add it to your system PATH:

**Method 1: Using System Properties (Recommended)**
1. Press `Win + Pause/Break` (or right-click "This PC" → Properties)
2. Click "Advanced system settings" on the left
3. Click "Environment Variables" button
4. Under "System variables", find and select "Path"
5. Click "Edit"
6. Click "New"
7. Add your iperf3 folder path (e.g., `C:\Tools\iperf3`)
8. Click "OK" on all windows
9. **Restart** any open Command Prompt or PowerShell windows

**Method 2: Using PowerShell (Quick)**
```powershell
# Run PowerShell as Administrator
$iperf3Path = "C:\Tools\iperf3"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$iperf3Path", "Machine")
```

### Step 4: Verify Installation
1. Open a **new** Command Prompt or PowerShell window
2. Type: `iperf3 --version`
3. You should see version information if installation was successful

Example output:
```
iperf 3.14 (cJSON 1.7.15)
Windows 10 Version 10.0.19044, AMD64
```

---

## Using Bandwidth Testing in NetTools Suite

### Running a Bandwidth Test
1. Launch NetTools Suite
2. Navigate to the "Bandwidth Testing" tool in the sidebar
3. Configure test parameters:
   - **Server**: IP address of the iperf3 server
   - **Port**: Default is 5201
   - **Duration**: Test duration in seconds
   - **Protocol**: TCP or UDP

### Setting Up an iperf3 Server
To test bandwidth, you need an iperf3 server running on the target machine:

**On the target machine:**
```bash
# Start iperf3 in server mode
iperf3 -s

# Or specify a port
iperf3 -s -p 5201
```

**Then in NetTools Suite:**
- Enter the server's IP address
- Click "Start Test"

---

## Troubleshooting

### "iperf3 not found" Error
- **Cause**: iperf3 is not in your system PATH
- **Solution**: 
  1. Verify iperf3.exe location
  2. Re-add to PATH following Step 3 above
  3. Restart NetTools Suite

### "Connection refused" Error
- **Cause**: No iperf3 server is running on the target
- **Solution**: Start iperf3 server on the target machine first

### Permission Denied
- **Cause**: Firewall blocking iperf3
- **Solution**: Add firewall exception for iperf3.exe

### Test Results Show Zero Bandwidth
- **Cause**: Network connectivity issue
- **Solution**: 
  1. Verify network connectivity to target
  2. Check firewall rules
  3. Ensure iperf3 server is running

---

## Command Line Usage (Advanced)

If you want to use iperf3 directly from command line:

### Client Mode (Test to a server)
```bash
# Basic test
iperf3 -c server_ip

# Test with specific duration (10 seconds)
iperf3 -c server_ip -t 10

# Test with specific port
iperf3 -c server_ip -p 5201

# UDP test
iperf3 -c server_ip -u

# Reverse mode (server sends, client receives)
iperf3 -c server_ip -R
```

### Server Mode
```bash
# Start server
iperf3 -s

# Server on specific port
iperf3 -s -p 5201

# Server that runs once and exits
iperf3 -s -1
```

---

## Additional Resources

- **Official iperf3 Documentation**: [https://iperf.fr/](https://iperf.fr/)
- **GitHub Repository**: [https://github.com/esnet/iperf](https://github.com/esnet/iperf)
- **User Guide**: [https://software.es.net/iperf/](https://software.es.net/iperf/)

---

## Support

If you continue to experience issues:
1. Verify iperf3 works from command line first
2. Check NetTools Suite logs for specific error messages
3. Ensure your network allows traffic on port 5201 (or your chosen port)

For NetTools Suite specific issues, please refer to the main application documentation.
