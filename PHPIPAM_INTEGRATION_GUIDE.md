# phpIPAM Integration Guide

## Overview

NetTools Suite v1.10.0 includes **optional** phpIPAM API integration, allowing you to manage IP addresses directly from the application. This feature is completely optional and can be enabled/disabled at any time.

---

## Features

### Core Capabilities:
- ✅ **Connection Testing** - Verify phpIPAM server accessibility
- ✅ **Dual Authentication** - Support for both dynamic (username/password) and static token methods
- ✅ **IP Address Search** - Find IP addresses in your phpIPAM database
- ✅ **Subnet Viewing** - Browse all configured subnets
- ✅ **Secure Credentials** - Encrypted storage of passwords and tokens
- ✅ **Optional Integration** - Enable/disable without affecting other tools

---

## Requirements

### phpIPAM Server Requirements:
1. phpIPAM instance with API enabled
2. API application ID configured in phpIPAM
3. User account with appropriate permissions OR static API token

### Python Dependencies:
These are automatically installed with NetTools Suite:
- `requests` - HTTP client for API communication
- `cryptography` - Secure credential encryption
- `urllib3` - HTTP connection handling

---

## Setup Instructions

### Step 1: Enable API in phpIPAM

1. Log into your phpIPAM admin panel
2. Navigate to **Administration → phpIPAM Settings → API**
3. Enable the API
4. Note your **API Application ID** (you'll create this in the next step)

### Step 2: Create API Application

1. In phpIPAM admin, go to **Administration → API**
2. Click **Create API Key**
3. Configure:
   - **App ID**: Choose a name (e.g., "NetTools")
   - **App permissions**: Set appropriate access level
   - **Security**: Choose authentication method
     - **User token (recommended)**: Requires username/password
     - **SSL with App code token**: Uses static token
4. Save and note your **App ID**

### Step 3: Configure NetTools Suite

1. Open NetTools Suite
2. Click **📡 phpIPAM** in the sidebar
3. Click **⚙️ Settings** button
4. Fill in configuration:

#### Basic Settings:
- **Enable phpIPAM Integration**: ✅ Check this box
- **phpIPAM URL**: Full URL (e.g., `https://ipam.example.com`)
- **App ID**: The application ID from Step 2

#### Authentication Method:

**Option A: Dynamic Authentication (Recommended)**
- Select: **Dynamic (Username + Password)**
- Enter your phpIPAM username
- Enter your phpIPAM password
- ⚠️ Password is encrypted before storage

**Option B: Static Token**
- Select: **Static Token**
- Enter your static API token
- ⚠️ Token is encrypted before storage

#### SSL Options:
- **Verify SSL Certificates**: ✅ Recommended for production
- Uncheck only for development with self-signed certificates

5. Click **💾 Save**

### Step 4: Test Connection

1. Click **🔌 Test Connection** button
2. Verify you see: ✅ Connection successful
3. Click **🔑 Authenticate** button
4. Verify successful authentication

---

## Usage

### Searching for IP Addresses

1. Navigate to **📡 phpIPAM** page
2. Enter IP address in search field (e.g., `192.168.1.10`)
3. Click **🔍 Search**
4. View results in the Results section

**What you'll see:**
- IP address details
- Hostname (if configured)
- Description
- MAC address
- Owner information
- Subnet association

### Viewing All Subnets

1. Navigate to **📡 phpIPAM** page
2. Click **📋 View All Subnets**
3. Browse the list of configured subnets

**Displayed information:**
- Subnet address and mask
- Description
- VLAN information
- Usage statistics

---

## Security Features

### Credential Encryption

All sensitive data is encrypted before storage:
- **Passwords** - Encrypted using Fernet symmetric encryption
- **Static Tokens** - Encrypted using Fernet symmetric encryption
- **Encryption Key** - Stored separately in `~/.nettools/phpipam.key`

**Storage Location:**
- Config: `~/.nettools/phpipam_config.json`
- Encryption Key: `~/.nettools/phpipam.key`

⚠️ **Important**: Keep your `.nettools` directory secure. Do not share these files.

### SSL Certificate Verification

By default, SSL certificates are verified for all HTTPS connections. This protects against man-in-the-middle attacks.

**Development Environments:**
If using self-signed certificates for testing:
1. Go to Settings
2. Uncheck "Verify SSL Certificates"
3. **Never disable this in production!**

---

## Troubleshooting

### Connection Issues

**Problem**: "Cannot connect to phpIPAM server"

**Solutions:**
1. Verify the URL is correct (include https://)
2. Check if phpIPAM is accessible from your network
3. Test URL in web browser first
4. Check firewall settings

---

**Problem**: "SSL verification failed"

**Solutions:**
1. Verify your phpIPAM has valid SSL certificate
2. For self-signed certs (dev only), disable SSL verify
3. Update your system's CA certificates

---

### Authentication Issues

**Problem**: "Authentication failed: HTTP 401"

**Solutions:**
1. Verify username and password are correct
2. Check user has API access permissions in phpIPAM
3. Verify App ID matches your phpIPAM configuration
4. Check if user account is active

---

**Problem**: "Static token not configured"

**Solutions:**
1. Go to Settings
2. Select "Static Token" authentication method
3. Enter your token
4. Save settings

---

### API Issues

**Problem**: "No results found" when searching

**Solutions:**
1. Verify IP exists in phpIPAM
2. Check user has permissions to view that subnet
3. Try different IP address
4. Check phpIPAM API logs

---

**Problem**: Token expired errors

**Solutions:**
1. Click **🔑 Authenticate** again
2. For dynamic auth, application auto-re-authenticates
3. Check token expiration settings in phpIPAM

---

## Advanced Configuration

### Token Caching

Dynamic authentication tokens are cached to reduce API calls:
- **Cache Location**: `~/.nettools/phpipam_config.json`
- **Auto-refresh**: Tokens auto-renew when expired
- **Manual Clear**: Save new settings to clear cache

### Multiple phpIPAM Instances

Currently, NetTools Suite supports one phpIPAM instance at a time. To switch:
1. Open Settings
2. Update URL and credentials
3. Save
4. Re-authenticate

---

## API Permissions

### Minimum Required Permissions:

For **read-only** operations:
- Read access to Sections
- Read access to Subnets
- Read access to Addresses

For **write** operations (future features):
- Write access to Addresses
- Write access to Subnets

Configure these in phpIPAM: **Administration → Users → [Your User] → Module Permissions**

---

## Disabling phpIPAM Integration

To completely disable the feature:
1. Go to **📡 phpIPAM** page
2. Click **⚙️ Settings**
3. Uncheck **Enable phpIPAM Integration**
4. Click **💾 Save**

The integration is now disabled but configuration is preserved. Re-enable anytime.

---

## Data Privacy

### What is Stored Locally:
- phpIPAM URL
- App ID
- Username (if using dynamic auth)
- Encrypted password/token
- Cached authentication token
- SSL verification preference

### What is NOT Stored:
- IP address data from phpIPAM
- Subnet information
- Search history
- API responses

All phpIPAM data is fetched fresh on each request.

---

## Future Enhancements

Planned features for future releases:
- ✨ Add new IP addresses
- ✨ Update existing IP information
- ✨ Reserve/release IP addresses
- ✨ Bulk operations
- ✨ Export phpIPAM data
- ✨ Subnet management
- ✨ Custom fields support

---

## Support

### phpIPAM Documentation:
- Official API Docs: https://phpipam.net/api/api_documentation/
- phpIPAM Forum: https://github.com/phpipam/phpipam/issues

### NetTools Suite:
- For integration issues, check the application logs
- Verify all requirements are met
- Test with phpIPAM's built-in API tools first

---

## Version History

### v1.10.0 (Initial Release)
- ✅ Optional phpIPAM integration
- ✅ Dual authentication support
- ✅ IP search functionality
- ✅ Subnet viewing
- ✅ Secure credential storage
- ✅ Connection testing

---

**Note**: This is an optional feature. All other NetTools Suite functionality works independently of phpIPAM integration.
