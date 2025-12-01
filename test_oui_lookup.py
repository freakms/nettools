#!/usr/bin/env python3
"""Test script for OUI Vendor Lookup feature"""

import json
from pathlib import Path

def load_oui_database():
    """Load OUI database from JSON file"""
    try:
        oui_path = Path(__file__).parent / "oui_database.json"
        if oui_path.exists():
            with open(oui_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Could not load OUI database: {e}")
    return {}

def lookup_vendor(mac_address, oui_database):
    """Lookup vendor from MAC address OUI"""
    if not mac_address or len(mac_address) < 8:
        return "Unknown"
    
    # Extract OUI (first 3 octets) and normalize format
    # Handle different MAC formats
    cleaned_mac = mac_address.replace(':', '').replace('-', '').replace('.', '').upper()
    
    if len(cleaned_mac) >= 6:
        # Format as XX:XX:XX for lookup
        oui = f"{cleaned_mac[0:2]}:{cleaned_mac[2:4]}:{cleaned_mac[4:6]}"
        vendor = oui_database.get(oui, "Unknown Vendor")
        return vendor
    
    return "Unknown"

def test_oui_lookup():
    """Test OUI lookup with various MAC addresses"""
    print("Testing OUI Vendor Lookup Feature")
    print("=" * 50)
    
    # Load database
    oui_db = load_oui_database()
    print(f"✓ Loaded OUI database with {len(oui_db)} entries\n")
    
    # Test cases - using MAC addresses from our database
    test_macs = [
        "00:00:0C:12:34:56",  # Cisco
        "00:01:42:AA:BB:CC",  # Cisco
        "00:03:6B:11:22:33",  # Cisco
        "AA:BB:CC:DD:EE:FF",  # Unknown (not in database)
        "00-00-5E-12-34-56",  # IANA (dash format)
        "0000.5E12.3456",     # IANA (Cisco format)
        "invalid",            # Invalid MAC
    ]
    
    for mac in test_macs:
        vendor = lookup_vendor(mac, oui_db)
        print(f"MAC: {mac:20s} → Vendor: {vendor}")
    
    print("\n" + "=" * 50)
    print("✓ OUI Vendor Lookup test completed successfully!")

if __name__ == "__main__":
    test_oui_lookup()
