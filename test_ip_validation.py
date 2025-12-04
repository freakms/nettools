#!/usr/bin/env python3
"""Test the updated IP validation function"""

import re

def validate_ip_address(ip):
    """Validate IP address or network with CIDR notation"""
    # Pattern for IP with optional CIDR
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(\/(\d{1,2}))?$'
    match = re.match(pattern, ip)
    
    if not match:
        return False
    
    # Validate each octet is 0-255
    octets = [int(match.group(i)) for i in range(1, 5)]
    if any(octet > 255 for octet in octets):
        return False
    
    # Validate CIDR prefix if present
    if match.group(5):  # Has CIDR
        cidr = int(match.group(6))
        if cidr > 32:
            return False
    
    return True

# Test cases
test_cases = [
    ("192.168.1.10", True),
    ("10.0.0.0/24", True),
    ("172.16.0.1/32", True),
    ("0.0.0.0", True),
    ("255.255.255.255", True),
    ("256.1.1.1", False),  # Invalid octet > 255
    ("192.168.1.256", False),  # Invalid octet > 255
    ("192.168.1", False),  # Incomplete
    ("192.168.1.10/", False),  # Missing CIDR value
    ("192.168.1.10/33", False),  # Invalid CIDR > 32
    ("abc.def.ghi.jkl", False),  # Non-numeric
    ("192.168.-1.1", False),  # Negative number
    ("192.168.1.1.1", False),  # Too many octets
]

print("=" * 70)
print("IP VALIDATION TEST")
print("=" * 70)

all_passed = True
for ip, expected in test_cases:
    result = validate_ip_address(ip)
    status = "✓ PASS" if result == expected else "✗ FAIL"
    if result != expected:
        all_passed = False
    print(f"{status:10s} | {ip:25s} → {str(result):5s} (Expected: {expected})")

print("=" * 70)
if all_passed:
    print("✓ All validation tests passed!")
else:
    print("✗ Some tests failed!")
print("=" * 70)
