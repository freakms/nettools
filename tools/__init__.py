"""
NetTools Suite - Tool Modules
Individual tool implementations for better code organization
"""

# Core scanner and formatting tools
from .scanner import IPv4Scanner
from .mac_formatter import OUILookup, MACFormatter

# Manager classes
from .scan_manager import ScanManager
from .network_profile_manager import NetworkProfileManager
from .history_manager import HistoryManager
from .network_icon import NetworkIcon

# Future tool modules (to be extracted)
# from .port_scanner import PortScanner
# from .dns_lookup import DNSLookup
# from .subnet_calc import SubnetCalculator
# from .traceroute import TracerouteTool
# from .phpipam_tool import PhpIpamTool

__all__ = [
    # Scanner and formatters
    'IPv4Scanner',
    'OUILookup',
    'MACFormatter',
    # Managers
    'ScanManager',
    'NetworkProfileManager',
    'HistoryManager',
    'NetworkIcon',
    # Future tools
    # 'PortScanner',
    # 'DNSLookup',
    # 'SubnetCalculator',
    # 'TracerouteTool',
    # 'PhpIpamTool',
]
