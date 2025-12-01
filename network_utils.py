"""
Network Utilities
Shared network-related helper functions
"""

import ipaddress
import socket
from pythonping import ping
from typing import Dict, List, Optional


def validate_cidr(cidr: str) -> tuple[bool, str]:
    """
    Validate CIDR notation
    
    Returns:
        (is_valid, error_message)
    """
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return True, ""
    except ValueError as e:
        return False, str(e)


def calculate_host_count(cidr: str) -> Optional[int]:
    """
    Calculate number of hosts in CIDR range
    
    Returns:
        Number of hosts or None if invalid
    """
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return network.num_addresses
    except ValueError:
        return None


def get_all_hosts(cidr: str) -> List[str]:
    """
    Get all host IPs in CIDR range
    
    Returns:
        List of IP addresses as strings
    """
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError:
        return []


def ping_host(ip: str, timeout: int = 1) -> tuple[bool, Optional[float]]:
    """
    Ping a single host
    
    Returns:
        (is_online, rtt_ms)
    """
    try:
        response = ping(ip, count=1, timeout=timeout)
        if response.success():
            rtt = response.rtt_avg_ms
            return True, rtt
        else:
            return False, None
    except Exception:
        return False, None


def resolve_hostname(hostname: str) -> Optional[str]:
    """
    Resolve hostname to IP address
    
    Returns:
        IP address string or None
    """
    try:
        return socket.gethostbyname(hostname)
    except socket.error:
        return None


def reverse_dns_lookup(ip: str) -> Optional[str]:
    """
    Perform reverse DNS lookup
    
    Returns:
        Hostname or None
    """
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except socket.error:
        return None


def is_port_open(host: str, port: int, timeout: float = 1.0) -> tuple[bool, str]:
    """
    Check if a port is open using socket connection
    
    Returns:
        (is_open, service_name)
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            # Try to get service name
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"
            return True, service
        else:
            return False, ""
    except Exception:
        return False, ""


def format_mac_address(mac: str, format_type: str) -> str:
    """
    Format MAC address to different styles
    
    Args:
        mac: MAC address string
        format_type: One of: colon, hyphen, dot, none
    
    Returns:
        Formatted MAC address
    """
    # Remove all separators
    clean_mac = mac.replace(':', '').replace('-', '').replace('.', '').upper()
    
    # Validate length
    if len(clean_mac) != 12:
        return mac  # Return original if invalid
    
    # Format based on type
    if format_type == "colon":
        return ':'.join(clean_mac[i:i+2] for i in range(0, 12, 2))
    elif format_type == "hyphen":
        return '-'.join(clean_mac[i:i+2] for i in range(0, 12, 2))
    elif format_type == "dot":
        return '.'.join(clean_mac[i:i+4] for i in range(0, 12, 4))
    elif format_type == "none":
        return clean_mac
    else:
        return mac


def get_oui_from_mac(mac: str) -> str:
    """
    Extract OUI (first 6 hex digits) from MAC address
    
    Returns:
        OUI string (e.g., "00:1A:2B")
    """
    clean_mac = mac.replace(':', '').replace('-', '').replace('.', '').upper()
    if len(clean_mac) >= 6:
        oui = clean_mac[:6]
        return ':'.join(oui[i:i+2] for i in range(0, 6, 2))
    return ""


def calculate_subnet_info(cidr: str) -> Optional[Dict]:
    """
    Calculate detailed subnet information
    
    Returns:
        Dictionary with subnet details or None
    """
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        
        return {
            'network': str(network.network_address),
            'netmask': str(network.netmask),
            'broadcast': str(network.broadcast_address),
            'first_host': str(list(network.hosts())[0]) if network.num_addresses > 2 else str(network.network_address),
            'last_host': str(list(network.hosts())[-1]) if network.num_addresses > 2 else str(network.broadcast_address),
            'total_hosts': network.num_addresses,
            'usable_hosts': max(0, network.num_addresses - 2),
            'prefix': network.prefixlen,
            'wildcard': str(network.hostmask),
        }
    except ValueError:
        return None
