# phpIPAM Integration - Quick Troubleshooting Guide

## Common Errors and Solutions

---

### ❌ SSL Certificate Verification Failed

**What it means:**
Your phpIPAM server is using an SSL certificate that cannot be verified (usually self-signed certificate).

**Quick Fix (Development/Testing):**
1. Open NetTools Suite
2. Go to phpIPAM page → Settings
3. **Uncheck** "Verify SSL Certificates"
4. Save
5. Try connection test again

**Production Fix:**
- Install a valid SSL certificate on your phpIPAM server
- Use Let's Encrypt for free SSL certificates
- Or add your CA certificate to Windows trusted certificates

⚠️ **Warning:** Only disable SSL verification for testing with self-signed certificates. Never disable in production!

---

### ❌ HTTP 403 - Forbidden

**What it means:**
The phpIPAM server is reachable but rejecting your request.

**Most Common Cause: App ID doesn't exist**

**Fix:**
1. Log into phpIPAM web interface
2. Go to: **Administration → API**
3. Check if your App ID exists in the list
4. If not, click **"Create API Key"**:
   - Enter App ID (e.g., "NetTools")
   - Set App permissions (read/write as needed)
   - Choose security method
   - Save
5. Use the **exact** App ID in NetTools Settings

**Other Possible Causes:**

**API Not Enabled:**
- Administration → phpIPAM Settings
- Check "Enable API"

**App is Disabled:**
- Administration → API
- Find your App ID
- Make sure it's not disabled

**Wrong Permissions:**
- Administration → API → [Your App]
- Check permissions are set correctly

---

### ❌ HTTP 404 - Not Found

**What it means:**
The API endpoint doesn't exist at the URL you specified.

**Common Causes:**

**1. Wrong URL Format**
```
❌ Wrong: https://ipam.example.com/api/
✅ Correct: https://ipam.example.com

❌ Wrong: https://ipam.example.com/phpipam
✅ Correct: https://ipam.example.com
```

**2. phpIPAM Installed in Subdirectory**
If phpIPAM is at: `https://example.com/phpipam/`

Then use: `https://example.com/phpipam`

**3. API Not Enabled**
- Log into phpIPAM
- Administration → phpIPAM Settings → API
- Enable "Enable API"
- Save

---

### ❌ Connection Timeout

**What it means:**
Cannot reach the phpIPAM server within 5 seconds.

**Check:**
1. **Is phpIPAM running?**
   - Try accessing it in web browser
   
2. **Network connectivity**
   - Can you ping the server?
   - Are you on VPN if required?

3. **Firewall blocking**
   - Check Windows Firewall
   - Check phpIPAM server firewall

4. **Slow server**
   - Server might be overloaded
   - Check server resources

---

### ❌ Authentication Failed: HTTP 401

**What it means:**
Username/password or token is incorrect.

**For Dynamic Auth (Username/Password):**
1. Verify username is correct
2. Verify password is correct
3. Check if user account is active in phpIPAM
4. Check user has API access permissions:
   - Administration → Users → [Your User]
   - Module permissions → API access

**For Static Token:**
1. Verify token is correct
2. Copy token exactly (no extra spaces)
3. Check token hasn't expired
4. Regenerate token in phpIPAM if needed

---

### ❌ No Results Found (When Searching)

**Possible Causes:**

1. **IP doesn't exist in phpIPAM**
   - Check in phpIPAM web interface first

2. **No permissions to view**
   - Check user permissions in phpIPAM
   - Administration → Users → [Your User]
   - Module permissions

3. **Wrong subnet/section**
   - Verify IP is in a subnet you have access to

4. **API App has limited permissions**
   - Administration → API → [Your App]
   - Check read permissions are enabled

---

## Testing Your Setup

### Step-by-Step Test:

**1. Test in Web Browser First**
```
Open: https://your-phpipam-url/
Can you log in? → Yes? Continue...
```

**2. Check API is Enabled**
```
In phpIPAM: Administration → phpIPAM Settings
Look for: API settings
Verify: "Enable API" is checked
```

**3. Create/Verify App ID**
```
In phpIPAM: Administration → API
Action: Create new or find existing App ID
Note: The exact App ID name
```

**4. Configure NetTools**
```
In NetTools: phpIPAM → Settings
Enter: URL (without /api/)
Enter: App ID (exact match)
Choose: Auth method
Enter: Credentials
```

**5. Disable SSL Verify (if self-signed)**
```
In NetTools: phpIPAM → Settings
Uncheck: "Verify SSL Certificates"
Save
```

**6. Test Connection**
```
In NetTools: Click "Test Connection"
Expected: "Connection successful"
```

**7. Authenticate**
```
In NetTools: Click "Authenticate"
Expected: "Authenticated successfully"
```

**8. Try an Operation**
```
In NetTools: Search for a known IP
Expected: Results displayed
```

---

## Still Having Issues?

### Check phpIPAM Logs

**Location (typical):**
```
/var/log/apache2/error.log  (Apache)
/var/log/nginx/error.log    (Nginx)
```

**Look for:**
- API-related errors
- Authentication errors
- Permission errors

### Check Network Tools App Logs

If running from source:
- Console output shows connection details
- Shows exact URLs being called
- Shows HTTP status codes

### Verify API Endpoint Manually

Test with curl (Linux/Mac) or PowerShell (Windows):

**PowerShell:**
```powershell
$url = "https://your-phpipam-url/api/YourAppID/user/"
Invoke-WebRequest -Uri $url -Method Get
```

**Expected Result:**
- HTTP 401 (means API is working, needs auth)
- HTTP 403 (means App ID issue)
- HTTP 404 (means wrong URL or API disabled)

---

## Getting Help

### Information to Provide:

When asking for help, include:
1. Exact error message from NetTools
2. phpIPAM version
3. Your phpIPAM URL format
4. Whether you're using self-signed certificate
5. Which authentication method
6. Have you tested in web browser?
7. What HTTP status code you're getting

### phpIPAM Resources:
- Documentation: https://phpipam.net/api/api_documentation/
- GitHub Issues: https://github.com/phpipam/phpipam/issues
- Forum: https://phpipam.net/forum/

---

## Quick Reference

### Correct URL Formats:
```
✅ https://ipam.company.com
✅ https://192.168.1.100
✅ https://server.local/phpipam
✅ http://localhost  (dev only)

❌ https://ipam.company.com/api/
❌ https://ipam.company.com/api/AppID/
```

### App ID Examples:
```
✅ NetTools
✅ MyApp
✅ network-tools
✅ API_Client_1

❌ NetTools App (spaces not recommended)
❌ net-tools! (special chars)
```

### Authentication Methods:

**Dynamic (Recommended):**
- Uses username & password
- Token expires after period
- Auto-renews in app
- More secure

**Static:**
- Uses pre-generated token
- Never expires
- No password in app
- Easier to set up

---

**Last Updated:** v1.10.0
