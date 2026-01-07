"""
Subnet Calculator Module
Calculates subnet information from CIDR notation
"""

import ipaddress


class SubnetCalculator:
    """Calculate subnet information from CIDR notation"""
    
    @staticmethod
    def calculate(cidr):
        """
        Calculate subnet information from CIDR notation
        
        Args:
            cidr (str): Network in CIDR notation (e.g., "192.168.1.0/24")
            
        Returns:
            dict: Subnet information or None if invalid
        """
        if not cidr or not cidr.strip():
            return None
        
        try:
            network = ipaddress.ip_network(cidr.strip(), strict=False)
            
            # Calculate subnet information
            info = {
                "network": str(network.network_address),
                "netmask": str(network.netmask),
                "cidr": f"/{network.prefixlen}",
                "wildcard": str(network.hostmask),
                "broadcast": str(network.broadcast_address),
                "first_host": str(network.network_address + 1) if network.num_addresses > 2 else "N/A",
                "last_host": str(network.broadcast_address - 1) if network.num_addresses > 2 else "N/A",
                "total_hosts": network.num_addresses,
                "usable_hosts": max(0, network.num_addresses - 2),
                "network_class": SubnetCalculator.get_network_class(network.network_address),
                "type": "Private" if network.is_private else "Public"
            }
            
            return info
            
        except ValueError as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_network_class(ip):
        """
        Get network class from IP address
        
        Args:
            ip: IP address object or string
            
        Returns:
            str: Network class (A, B, C, D, E)
        """
        first_octet = int(str(ip).split('.')[0])
        
        if 1 <= first_octet <= 126:
            return "A"
        elif 128 <= first_octet <= 191:
            return "B"
        elif 192 <= first_octet <= 223:
            return "C"
        elif 224 <= first_octet <= 239:
            return "D (Multicast)"
        elif 240 <= first_octet <= 255:
            return "E (Reserved)"
        else:
            return "Unknown"
    
    @staticmethod
    def validate_cidr(cidr):
        """
        Validate CIDR notation
        
        Args:
            cidr (str): CIDR notation to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not cidr:
            return False
        
        try:
            ipaddress.ip_network(cidr.strip(), strict=False)
            return True
        except ValueError:
            return False
