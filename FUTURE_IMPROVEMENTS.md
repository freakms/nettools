# Future Improvements & Feature Requests

## Priority Improvements

### 1. IPv4 Scanner - Export Options (P1)
**Issue:** Export options window not user-friendly

**Current State:**
- Multiple format buttons in a window
- Not scrollable if many formats
- Excel export requires external application

**Requested Solution:**
- **Best:** Use Windows "Save As" dialog like Port Scanner
- **Alternative:** Dropdown to select format, then save dialog
- **Remove:** Excel export format (requires external app installation)

**Implementation Notes:**
- Copy port scanner export pattern
- Use `filedialog.asksaveasfilename()` with format filter
- Supported formats: CSV, JSON, TXT
- Let OS handle file location and naming

---

### 2. DNS Lookup - Show DNS Server Used (P2)
**Issue:** Results don't show which DNS server resolved the query

**Requested Feature:**
- Display the DNS server that was used for resolution
- Show in results output alongside IP/hostname

**Implementation Notes:**
- Track which DNS server was queried
- Display in format: "Resolved by: 8.8.8.8" or "DNS Server: 1.1.1.1"
- Add to result output string

---

### 3. Subnet Calculator - Subnet Splitting (P2)
**Issue:** No subnet splitting functionality

**Requested Feature:**
- Add function to split subnets
- User can choose:
  - Number of subnets to create
  - Starting CIDR to split from
  
**Example Use Case:**
- User has 192.168.0.0/24
- Wants to split into 4 subnets
- Should show: /26 subnets with ranges

**Implementation Notes:**
- Add "Split Subnet" section to calculator
- Input: Source CIDR, Number of splits
- Calculate new prefix length
- Display all resulting subnets with details:
  - Network address
  - Broadcast address
  - Usable IP range
  - Number of hosts
- Export split results to CSV/TXT

**Math:**
- Splits must be power of 2 (2, 4, 8, 16, 32, etc.)
- New prefix = old prefix + log2(splits)
- Example: /24 split into 4 = /26 (24 + log2(4) = 24 + 2 = 26)

---

## Implementation Priority

**Phase 5 (After Refactoring):**
1. IPv4 Scanner export fix (Quick win, improves UX)
2. DNS Lookup DNS server display (Simple addition)
3. Subnet splitting feature (Larger feature, good utility)

## Notes
- All improvements maintain electric violet theme
- Follow existing UI patterns and components
- Test thoroughly before deployment
- Document any new features

## Date
December 2025
