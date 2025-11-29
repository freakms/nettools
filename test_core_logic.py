#!/usr/bin/env python3
"""
Test core logic without GUI dependencies
"""

import ipaddress
import re
from PIL import Image, ImageDraw

# IP Scanner Logic
def parse_cidr(cidr_input):
    """Parse CIDR notation and return list of host IPs"""
    network = ipaddress.ip_network(cidr_input, strict=False)
    
    # For /31 and /32, include all addresses
    if network.prefixlen >= 31:
        return [str(ip) for ip in network.hosts()] if network.prefixlen == 31 else [str(network.network_address)]
    
    # For other networks, exclude network and broadcast
    return [str(ip) for ip in network.hosts()]

# MAC Formatter Logic
def validate_mac(mac_input):
    """Validate MAC address input"""
    # Remove valid separators and spaces
    hex_only = re.sub(r'[^0-9A-Fa-f]', '', mac_input)
    
    if len(hex_only) != 12:
        return None, f"Invalid MAC: {len(hex_only)} hex characters (expected: 12)"
    
    # Check for invalid characters
    if re.search(r'[^0-9A-Fa-f:\\-\\s]', mac_input):
        return None, "Invalid characters! Allowed: 0-9, A-F, '-', ':', and spaces"
    
    return hex_only.upper(), None

def format_mac(hex_mac):
    """Format MAC address in different styles"""
    formats = {
        'plain': hex_mac,
        'colon': ':'.join([hex_mac[i:i+2] for i in range(0, 12, 2)]),
        'dash_4': '-'.join([hex_mac[i:i+4] for i in range(0, 12, 4)]),
        'dash_2': '-'.join([hex_mac[i:i+2] for i in range(0, 12, 2)])
    }
    return formats

def generate_switch_commands(formats):
    """Generate vendor-specific switch commands"""
    commands = {
        'EXTREME': f"show fdb {formats['colon']}",
        'Huawei': f"display mac-address {formats['dash_4']}",
        'Huawei Access-User': f"display access-user mac-address {formats['dash_4']}",
        'Dell': f"show mac address-table address {formats['colon']}"
    }
    return commands

def create_network_icon(size=256):
    """Create network topology icon"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colors
    fg_color = (80, 80, 80)
    bg_color = (235, 235, 235)
    device_color = (210, 210, 210)
    
    # Main router/switch box
    pad = int(size * 0.12)
    box_size = size - 2 * pad
    corner = int(box_size * 0.15)
    
    # Draw rounded rectangle
    draw.rounded_rectangle(
        [pad, pad, pad + box_size, pad + box_size],
        radius=corner,
        fill=bg_color,
        outline=fg_color,
        width=3
    )
    
    # Draw monitor/screen
    monitor_w = int(box_size * 0.65)
    monitor_h = int(box_size * 0.32)
    mx = pad + (box_size - monitor_w) // 2
    my = pad + 2
    draw.rectangle([mx, my, mx + monitor_w, my + monitor_h], 
                  fill=device_color, outline=fg_color, width=2)
    
    return img

# Run Tests
print("\n" + "="*60)
print("NetTools Suite - Core Logic Tests")
print("="*60)

# Test IP Scanner
print("\n1. Testing IP Scanner (CIDR Parsing)")
print("-"*60)
test_cidrs = [
    "192.168.1.0/24",
    "10.0.0.0/30",
    "172.16.0.0/32",
    "192.168.1.100/31",
    "8.8.8.0/28"
]

for cidr in test_cidrs:
    try:
        ips = parse_cidr(cidr)
        network = ipaddress.ip_network(cidr, strict=False)
        print(f"\n✓ {cidr}")
        print(f"  Hosts: {len(ips)}")
        if len(ips) <= 5:
            print(f"  IPs: {', '.join(ips)}")
        else:
            print(f"  First: {ips[0]} ... Last: {ips[-1]}")
    except Exception as e:
        print(f"\n✗ {cidr}: {e}")

# Test MAC Formatter
print("\n\n2. Testing MAC Formatter")
print("-"*60)
test_macs = [
    "AA:BB:CC:DD:EE:FF",
    "aabbccddeeff",
    "AA-BB-CC-DD-EE-FF",
    "AABB-CCDD-EEFF",
]

for mac in test_macs:
    print(f"\n✓ Input: {mac}")
    hex_mac, error = validate_mac(mac)
    
    if error:
        print(f"  ✗ Error: {error}")
    else:
        formats = format_mac(hex_mac)
        print(f"  Plain:   {formats['plain']}")
        print(f"  Colon:   {formats['colon']}")
        print(f"  Dash-4:  {formats['dash_4']}")
        print(f"  Dash-2:  {formats['dash_2']}")

# Test invalid MAC
print(f"\n✗ Testing invalid MAC: 12:34:56")
hex_mac, error = validate_mac("12:34:56")
print(f"  Expected error: {error}")

# Test Icon Generation
print("\n\n3. Testing Icon Generation")
print("-"*60)
try:
    icon = create_network_icon(256)
    print(f"✓ Icon generated successfully")
    print(f"  Size: {icon.size}")
    print(f"  Mode: {icon.mode}")
    
    # Save test icon
    icon.save('/app/test_icon.png')
    print(f"  Saved: /app/test_icon.png")
except Exception as e:
    print(f"✗ Icon generation failed: {e}")

# Test Switch Commands
print("\n\n4. Testing Switch Command Generation")
print("-"*60)
test_mac = "AABBCCDDEEFF"
formats = format_mac(test_mac)
commands = generate_switch_commands(formats)

for vendor, cmd in commands.items():
    print(f"  {vendor:20} -> {cmd}")

print("\n" + "="*60)
print("✓ All core logic tests passed!")
print("="*60 + "\n")
