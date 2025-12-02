# Network Profile Manager - Fixes Applied

## Issue 1: Profile Display Order ✅ FIXED

**Problem:** Newly created profiles appeared at the bottom of the list instead of at the top.

**Solution:** 
- Modified `refresh_profiles()` method to display profiles in reverse order
- Now uses `reversed(profiles)` to show newest profiles first
- This matches user expectation that recent items appear at the top

**Code change:**
```python
# Display profiles in reverse order (newest first)
for profile in reversed(profiles):
    self.create_profile_card(profile)
```

---

## Issue 2: Static IP Not Applying ✅ FIXED

**Problem:** When applying a profile with static IP configuration, the network changes were not being applied successfully.

**Root Causes Identified:**
1. Incorrect netsh command format - parameters weren't using `name=`, `address=`, `mask=`, `gateway=` format
2. Missing encoding parameter for Windows command output
3. Insufficient error reporting to diagnose failures
4. DNS command format issues

**Solutions Applied:**

### 1. Fixed netsh Command Format
Changed from positional arguments to explicit parameter format:
```python
cmd = [
    "netsh", "interface", "ipv4", "set", "address",
    "name=" + interface_name,
    "source=static",
    "address=" + config["ip"],
    "mask=" + subnet_mask,
    "gateway=" + gateway
]
```

### 2. Added Proper Encoding
Added `encoding='cp850'` to subprocess calls for correct Windows console output:
```python
result = self.run_subprocess(
    cmd,
    capture_output=True,
    text=True,
    encoding='cp850',  # Windows console encoding
    timeout=15
)
```

### 3. Improved DNS Configuration
- Primary DNS now uses proper netsh format with `source=static`
- Additional DNS servers use `add dns` command with index
- Empty DNS entries are filtered out

**Primary DNS:**
```python
dns_cmd = [
    "netsh", "interface", "ipv4", "set", "dns",
    "name=" + interface_name,
    "source=static",
    "address=" + dns,
    "register=primary"
]
```

**Additional DNS:**
```python
dns_cmd = [
    "netsh", "interface", "ipv4", "add", "dns",
    "name=" + interface_name,
    "address=" + dns,
    "index=" + str(i + 1)
]
```

### 4. Enhanced Error Reporting
- Now captures and displays stderr output from failed netsh commands
- Better error messages showing specific interface and failure reason
- Improved timeout handling (increased to 15 seconds for IP configuration)

### 5. Added User Feedback
- Progress indicator shown while applying profile
- Progress label automatically removed when operation completes
- Clear success/failure messages with detailed error information

---

## Testing Recommendations

### Test Case 1: Profile Order
1. Create a new profile named "Test 1"
2. Create another profile named "Test 2"
3. **Expected:** "Test 2" should appear above "Test 1" in the list

### Test Case 2: Static IP Application
1. Create a profile with static IP configuration:
   - IP Address: 192.168.1.100
   - Subnet Mask: 255.255.255.0
   - Gateway: 192.168.1.1
   - DNS: 8.8.8.8
2. Apply the profile
3. **Expected:** 
   - Progress indicator appears
   - Success message after configuration
   - Run `ipconfig` to verify settings were applied

### Test Case 3: DHCP Application
1. Create a profile with DHCP configuration
2. Apply the profile
3. **Expected:** Interface switches to DHCP successfully

### Test Case 4: Error Handling
1. Try applying a profile with an interface that no longer exists
2. **Expected:** Clear error message explaining which interface failed

---

## Technical Notes

- **Windows netsh Format:** The key issue was using the old positional parameter format. Modern Windows versions prefer/require the explicit `name=`, `address=`, etc. format
- **Encoding:** Windows console uses CP850 encoding by default, which must be specified for proper error message capture
- **Thread Safety:** Profile application runs in background thread to prevent GUI freezing
- **Progress Feedback:** Using `CTkLabel.place()` with center anchor for overlay progress indicator

---

## Files Modified
- `/app/nettools_app.py`
  - `refresh_profiles()` - Line ~3460
  - `apply_profile()` - Line ~4005
