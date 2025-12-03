"""
MAC Address Formatter and OUI Lookup Tool
Handles MAC address formatting and vendor lookup
"""

import re
import json
import sys
from pathlib import Path


class OUILookup:
    """OUI Vendor Lookup"""
    
    _database = None
    
    @classmethod
    def load_database(cls):
        """Load OUI database from file"""
        if cls._database is not None:
            return cls._database
        
        try:
            # Handle both development and PyInstaller bundled environments
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                bundle_dir = Path(sys._MEIPASS)
            else:
                # Running as script
                bundle_dir = Path(__file__).parent.parent
            
            db_path = bundle_dir / "oui_database.json"
            
            if db_path.exists():
                with open(db_path, 'r', encoding='utf-8') as f:
                    cls._database = json.load(f)
            else:
                print(f"OUI database not found at: {db_path}")
                cls._database = {}
        except Exception as e:
            print(f"Could not load OUI database: {e}")
            cls._database = {}
        
        return cls._database
    
    @classmethod
    def lookup_vendor(cls, mac):
        """Lookup vendor from MAC address"""
        if cls._database is None:
            cls.load_database()
        
        # Extract OUI (first 3 bytes)
        # MAC can be in any format, so we normalize it first
        hex_only = re.sub(r'[^0-9A-Fa-f]', '', mac).upper()
        
        if len(hex_only) < 6:
            return "Unknown"
        
        # Format as XX:XX:XX
        oui = ':'.join([hex_only[i:i+2] for i in range(0, 6, 2)])
        
        return cls._database.get(oui, "Unknown Vendor")


class MACFormatter:
    """MAC Address Formatter"""
    
    @staticmethod
    def validate_mac(mac_input):
        """Validate MAC address input"""
        # Check for invalid characters first
        if re.search(r'[^0-9A-Fa-f:\-\s]', mac_input):
            return None, "Invalid characters! Allowed: 0-9, A-F, '-', ':', and spaces"
        
        # Remove valid separators and spaces
        hex_only = re.sub(r'[^0-9A-Fa-f]', '', mac_input)
        
        if len(hex_only) != 12:
            return None, f"Invalid MAC: {len(hex_only)} hex characters (expected: 12)"
        
        return hex_only.upper(), None
    
    @staticmethod
    def format_mac(hex_mac):
        """Format MAC address in different styles"""
        formats = {
            'plain': hex_mac,
            'colon': ':'.join([hex_mac[i:i+2] for i in range(0, 12, 2)]),
            'dash_4': '-'.join([hex_mac[i:i+4] for i in range(0, 12, 4)]),
            'dash_2': '-'.join([hex_mac[i:i+2] for i in range(0, 12, 2)])
        }
        return formats
    
    @staticmethod
    def generate_switch_commands(formats):
        """Generate vendor-specific switch commands"""
        commands = {
            'EXTREME': f"show fdb {formats['colon']}",
            'Huawei': f"display mac-address {formats['dash_4']}",
            'Huawei Access-User': f"display access-user mac-address {formats['dash_4']}",
            'Dell': f"show mac address-table address {formats['colon']}"
        }
        return commands
