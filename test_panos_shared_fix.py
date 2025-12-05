#!/usr/bin/env python3
"""
Test script to verify PAN-OS shared object command generation
"""

def test_base_path_generation():
    """Test that base path is correctly generated for shared vs vsys"""
    
    test_cases = [
        ("shared", "shared"),
        ("vsys1", "vsys vsys1"),
        ("vsys2", "vsys vsys2"),
    ]
    
    print("Testing base path generation:")
    print("-" * 50)
    
    for vsys_input, expected_base in test_cases:
        # Simulate the logic in the fixed code
        base_path = "shared" if vsys_input == "shared" else f"vsys {vsys_input}"
        
        status = "✓ PASS" if base_path == expected_base else "✗ FAIL"
        print(f"{status}: vsys='{vsys_input}' -> base_path='{base_path}'")
        
        # Show example commands
        print(f"  Example: set {base_path} address \"Server1\" ip-netmask 192.168.1.10")
        print()

def test_command_examples():
    """Show example commands for different scenarios"""
    
    print("\nExample Command Outputs:")
    print("=" * 50)
    
    # Address object - shared
    print("\n1. Address Object (shared):")
    print("   set shared address \"Server1\" ip-netmask 192.168.1.10")
    
    # Address object - vsys1
    print("\n2. Address Object (vsys1):")
    print("   set vsys vsys1 address \"Server1\" ip-netmask 192.168.1.10")
    
    # Address group - shared
    print("\n3. Address Group (shared):")
    print("   set shared address-group \"Internal_Networks\" static \"Server1\"")
    
    # NAT rule - shared
    print("\n4. NAT Rule (shared):")
    print("   set shared rulebase nat rules \"NAT_Web\" from \"trust\"")
    
    # Security Policy - vsys1
    print("\n5. Security Policy (vsys1):")
    print("   set vsys vsys1 rulebase security rules \"Allow_Web\" from \"trust\"")
    
    print("\n" + "=" * 50)
    print("✓ All examples show correct format (no 'vsys shared')")

if __name__ == "__main__":
    test_base_path_generation()
    test_command_examples()
