"""
Port Scanner Module
Scans for open ports on target hosts using multiple methods
"""

import socket
import subprocess
import platform

# Try to import telnetlib
try:
    import telnetlib
    TELNETLIB_AVAILABLE = True
except ImportError:
    TELNETLIB_AVAILABLE = False


class PortScanner:
    """Port scanning utility with multiple scan methods"""
    
    # Common ports with their services
    COMMON_PORTS = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        445: "SMB",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        5900: "VNC",
        8080: "HTTP-Alt",
        8443: "HTTPS-Alt",
    }
    
    @staticmethod
    def get_common_ports():
        """Get list of common ports"""
        return list(PortScanner.COMMON_PORTS.keys())
    
    @staticmethod
    def get_service_name(port):
        """
        Get common service name for port
        
        Args:
            port (int): Port number
            
        Returns:
            str: Service name or "Unknown"
        """
        return PortScanner.COMMON_PORTS.get(port, "Unknown")
    
    @staticmethod
    def parse_port_range(port_range_str):
        """
        Parse port range string
        
        Args:
            port_range_str (str): Port range (e.g., "80-443" or "80")
            
        Returns:
            list: List of ports or empty list if invalid
        """
        if not port_range_str or not port_range_str.strip():
            return []
        
        try:
            if '-' in port_range_str:
                start, end = port_range_str.split('-')
                start = int(start.strip())
                end = int(end.strip())
                if 1 <= start <= end <= 65535:
                    return list(range(start, end + 1))
            else:
                port = int(port_range_str)
                if 1 <= port <= 65535:
                    return [port]
        except:
            pass
        return []
    
    @staticmethod
    def parse_port_list(ports_str):
        """
        Parse comma-separated port list
        
        Args:
            ports_str (str): Comma-separated ports (e.g., "80,443,8080")
            
        Returns:
            list: List of ports or empty list if invalid
        """
        if not ports_str or not ports_str.strip():
            return []
        
        ports = []
        try:
            for p in ports_str.split(','):
                port = int(p.strip())
                if 1 <= port <= 65535:
                    ports.append(port)
        except:
            return []
        return ports
    
    @staticmethod
    def scan_port_socket(target, port, timeout=1):
        """
        Scan port using socket
        
        Args:
            target (str): Target IP or hostname
            port (int): Port number
            timeout (float): Connection timeout in seconds
            
        Returns:
            tuple: (is_open, service_name)
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            
            if result == 0:
                service = PortScanner.get_service_name(port)
                return True, service
            return False, ""
        except:
            return False, ""
    
    @staticmethod
    def scan_port_telnet(target, port, timeout=2):
        """
        Scan port using telnet
        
        Args:
            target (str): Target IP or hostname
            port (int): Port number
            timeout (float): Connection timeout in seconds
            
        Returns:
            tuple: (is_open, service_name)
        """
        if not TELNETLIB_AVAILABLE:
            return False, ""
        
        try:
            tn = telnetlib.Telnet()
            tn.open(target, port, timeout=timeout)
            tn.close()
            service = PortScanner.get_service_name(port)
            return True, service
        except:
            return False, ""
    
    @staticmethod
    def scan_port_powershell(target, port, timeout=5):
        """
        Scan port using PowerShell Test-NetConnection (Windows only)
        
        Args:
            target (str): Target IP or hostname
            port (int): Port number
            timeout (float): Connection timeout in seconds
            
        Returns:
            tuple: (is_open, service_name)
        """
        if platform.system() != "Windows":
            return False, ""
        
        try:
            cmd = f'powershell -Command "Test-NetConnection -ComputerName {target} -Port {port} -InformationLevel Quiet"'
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True
            )
            
            if result.stdout.strip().lower() == "true":
                service = PortScanner.get_service_name(port)
                return True, service
            return False, ""
        except:
            return False, ""
    
    @staticmethod
    def scan_port(target, port, method="socket", timeout=1):
        """
        Scan a single port using specified method
        
        Args:
            target (str): Target IP or hostname
            port (int): Port number
            method (str): Scan method ("socket", "telnet", or "powershell")
            timeout (float): Connection timeout in seconds
            
        Returns:
            dict: Scan result with port, status, and service
        """
        if method == "telnet":
            is_open, service = PortScanner.scan_port_telnet(target, port, timeout)
        elif method == "powershell":
            is_open, service = PortScanner.scan_port_powershell(target, port, timeout)
        else:  # socket (default)
            is_open, service = PortScanner.scan_port_socket(target, port, timeout)
        
        return {
            "port": port,
            "status": "Open" if is_open else "Closed",
            "service": service if is_open else "",
            "is_open": is_open
        }
    
    @staticmethod
    def scan_ports(target, ports, method="socket", timeout=1, progress_callback=None):
        """
        Scan multiple ports on a target
        
        Args:
            target (str): Target IP or hostname
            ports (list): List of port numbers to scan
            method (str): Scan method ("socket", "telnet", or "powershell")
            timeout (float): Connection timeout in seconds
            progress_callback (callable): Optional callback for progress updates
            
        Returns:
            list: List of open ports with their details
        """
        results = []
        total = len(ports)
        
        for i, port in enumerate(ports):
            result = PortScanner.scan_port(target, port, method, timeout)
            
            if result["is_open"]:
                results.append(result)
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(i + 1, total, result)
        
        return results
    
    @staticmethod
    def validate_target(target):
        """
        Validate target (IP or hostname)
        
        Args:
            target (str): Target to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not target or not target.strip():
            return False
        
        # Try to resolve the target
        try:
            socket.gethostbyname(target.strip())
            return True
        except:
            return False
