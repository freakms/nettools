#!/usr/bin/env python3
"""
Test script for NetTools Suite core functionality
"""

import sys
sys.path.insert(0, '/app')

from nettools_app import IPScanner, MACFormatter, NetworkIcon
import ipaddress

def test_ip_scanner():
    """Test IP Scanner CIDR parsing"""
    print("\n" + "="*60)
    print("Testing IP Scanner")
    print("="*60)
    
    scanner = IPScanner()
    
    # Test cases
    test_cidrs = [
        "192.168.1.0/24",      # Standard /24
        "10.0.0.0/30",         # Small network
        "172.16.0.0/32",       # Single host
        "192.168.1.100/31",    # /31 network
    ]
    
    for cidr in test_cidrs:
        try:
            ips = scanner.parse_cidr(cidr)
            network = ipaddress.ip_network(cidr, strict=False)
            print(f"\n✓ {cidr}")
            print(f"  Network: {network}")
            print(f"  Hosts: {len(ips)}")
            if len(ips) <= 5:
                print(f"  IPs: {', '.join(ips)}")
            else:
                print(f"  First 3: {', '.join(ips[:3])}")
                print(f"  Last 3: {', '.join(ips[-3:])}")
        except Exception as e:
            print(f"\n✗ {cidr}: {e}")
    
    print("\n" + "="*60)

def test_mac_formatter():
    """Test MAC Formatter"""
    print("\n" + "="*60)
    print("Testing MAC Formatter")
    print("="*60)
    
    # Test cases
    test_macs = [
        "AA:BB:CC:DD:EE:FF",
        "aabbccddeeff",
        "AA-BB-CC-DD-EE-FF",
        "AABB-CCDD-EEFF",
        "aa bb cc dd ee ff",
    ]
    
    for mac in test_macs:
        print(f"\n✓ Input: {mac}")
        hex_mac, error = MACFormatter.validate_mac(mac)
        
        if error:
            print(f"  Error: {error}")
        else:
            print(f"  Validated: {hex_mac}")
            formats = MACFormatter.format_mac(hex_mac)
            print(f"  Plain:   {formats['plain']}")
            print(f"  Colon:   {formats['colon']}")
            print(f"  Dash-4:  {formats['dash_4']}")
            print(f"  Dash-2:  {formats['dash_2']}")
            
            commands = MACFormatter.generate_switch_commands(formats)
            print(f"  Commands:")
            for vendor, cmd in commands.items():
                print(f"    {vendor}: {cmd}")
    
    # Test invalid MAC
    print(f"\n✗ Input: 12:34:56")
    hex_mac, error = MACFormatter.validate_mac("12:34:56")
    print(f"  Error: {error}")
    
    print("\n" + "="*60)

def test_icon_generation():
    """Test icon generation"""
    print("\n" + "="*60)
    print("Testing Icon Generation")
    print("="*60)
    
    try:
        icon = NetworkIcon.create_icon(256)
        print(f"\n✓ Icon generated successfully")
        print(f"  Size: {icon.size}")
        print(f"  Mode: {icon.mode}")
        print(f"  Format: {icon.format}")
    except Exception as e:
        print(f"\n✗ Icon generation failed: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("NetTools Suite - Core Functionality Tests")
    print("="*60)
    
    test_ip_scanner()
    test_mac_formatter()
    test_icon_generation()
    
    print("\n✓ All core functionality tests completed!\n")
