# Installing iperf3 on Windows

## Quick Summary
The Bandwidth Testing feature requires **iperf3** to be installed on your system. Here are several ways to install it on Windows.

---

## Option 1: Chocolatey (Easiest - Recommended)

### Step 1: Install Chocolatey
1. Open **PowerShell as Administrator**
2. Visit: https://chocolatey.org/install
3. Copy and run the installation command

### Step 2: Install iperf3
```powershell
choco install iperf3
```

### Step 3: Verify Installation
```powershell
iperf3 --version
```

### Step 4: Restart NetTools App
Close and reopen the application, then try Bandwidth Test again.

---

## Option 2: Scoop (Alternative Package Manager)

### Step 1: Install Scoop
1. Open **PowerShell** (doesn't need admin)
2. Visit: https://scoop.sh
3. Run the installation command

### Step 2: Install iperf3
```powershell
scoop install iperf3
```

### Step 3: Verify
```powershell
iperf3 --version
```

---

## Option 3: Manual Installation

### Step 1: Download iperf3
1. Visit: https://iperf.fr/iperf-download.php
2. Download **iperf 3.x for Windows**
3. Extract the ZIP file

### Step 2: Add to PATH
**Method A: Copy to System Folder**
- Copy `iperf3.exe` to `C:\Windows\System32\`

**Method B: Add Folder to PATH**
1. Create folder: `C:\iperf3\`
2. Copy `iperf3.exe` there
3. Open **System Properties** → **Environment Variables**
4. Edit **PATH** variable
5. Add: `C:\iperf3\`
6. Click OK

### Step 3: Verify
Open new Command Prompt:
```cmd
iperf3 --version
```

---

## Option 4: WSL (Windows Subsystem for Linux)

If you have WSL installed:

### In WSL Terminal:
```bash
sudo apt update
sudo apt install iperf3
```

### Use from WSL:
You'll need to run iperf3 commands from WSL terminal, not from the NetTools app.

---

## Verification

After installation, verify iperf3 is working:

```powershell
# Check version
iperf3 --version

# Should output something like:
# iperf 3.x.x (date)
```

---

## Troubleshooting

### "iperf3 is not recognized"
- Make sure you added it to PATH
- Restart Command Prompt/PowerShell after adding to PATH
- Restart the NetTools application

### Still not working?
1. Open Command Prompt as Administrator
2. Run: `where iperf3`
3. If it shows a path, it's installed
4. If not, repeat installation steps

### Permission Issues
- Run installation as Administrator
- Check antivirus isn't blocking it
- Try manual installation method

---

## Using iperf3 for Testing

### You Need a Server
iperf3 works by connecting to a server. You have two options:

**Option A: Public Servers**
Search for "public iperf3 servers" to find free servers to test against.

Examples:
- `iperf.he.net` (Hurricane Electric)
- `ping.online.net`
- Various university and ISP servers

**Option B: Your Own Server**
On another computer (or cloud server):
```bash
iperf3 -s
```

Then test against that server's IP address.

---

## Quick Test

After installation, test it works:

```powershell
# Try a public server (example)
iperf3 -c iperf.he.net
```

If you see throughput results, it's working!

---

## Additional Resources

- **Official Site**: https://iperf.fr
- **Documentation**: https://iperf.fr/iperf-doc.php
- **GitHub**: https://github.com/esnet/iperf
- **Public Servers**: Search "public iperf3 servers"

---

## Back to NetTools

Once installed:
1. Restart NetTools application
2. Go to **Bandwidth Test** page
3. Click **"Check Again"** button
4. Enter a server hostname/IP
5. Click **Upload Test** or **Download Test**

---

## Alternative: Online Speed Tests

If you don't want to install iperf3, you can use:
- **Speedtest.net** - Fast and easy
- **Fast.com** - By Netflix
- **Google Speed Test** - Search "internet speed test"

These work in your web browser without any installation!
