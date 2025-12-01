#!/usr/bin/env python3
"""
Test script to verify Palo Alto OUI lookup
Run this to confirm the database is working correctly
"""

import json
from pathlib import Path

def test_oui_lookup():
    print("=" * 70)
    print("Testing Palo Alto Networks OUI Lookup")
    print("=" * 70)
    
    # Load database
    try:
        db_path = Path(__file__).parent / "oui_database.json"
        with open(db_path, 'r', encoding='utf-8') as f:
            oui_db = json.load(f)
        print(f"✓ Database loaded: {len(oui_db)} entries\n")
    except Exception as e:
        print(f"✗ Error loading database: {e}")
        return False
    
    # Test Palo Alto MAC addresses
    test_cases = [
        ("00:1B:17:AA:BB:CC", "00:1B:17", "Palo Alto Networks"),
        ("00:1b:17:11:22:33", "00:1B:17", "Palo Alto Networks"),  # lowercase
        ("00-1B-17-44-55-66", "00:1B:17", "Palo Alto Networks"),  # dash format
        ("001B.1777.8899", "00:1B:17", "Palo Alto Networks"),     # Cisco format
    ]
    
    all_pass = True
    
    for mac_input, expected_oui, expected_vendor in test_cases:
        # Normalize MAC
        cleaned = mac_input.replace(':', '').replace('-', '').replace('.', '').upper()
        oui = f"{cleaned[0:2]}:{cleaned[2:4]}:{cleaned[4:6]}"
        
        # Lookup
        vendor = oui_db.get(oui, "Unknown Vendor")
        
        # Check
        passed = (vendor == expected_vendor)
        symbol = "✓" if passed else "✗"
        
        print(f"{symbol} MAC: {mac_input:20s} → OUI: {oui} → Vendor: {vendor}")
        
        if not passed:
            print(f"   ERROR: Expected '{expected_vendor}', got '{vendor}'")
            all_pass = False
    
    print("\n" + "=" * 70)
    
    if all_pass:
        print("✅ ALL TESTS PASSED!")
        print("✅ Palo Alto Networks OUI lookup is working correctly")
        print("\nThe database is correct. If you see 'Unknown' in the app:")
        print("  1. Close the app completely")
        print("  2. Delete any old .exe files")
        print("  3. Rebuild: python build_exe.py")
        print("  4. Or run directly: python nettools_app.py")
    else:
        print("❌ SOME TESTS FAILED!")
        print("❌ There may be a database issue")
    
    print("=" * 70)
    
    return all_pass

if __name__ == "__main__":
    test_oui_lookup()
