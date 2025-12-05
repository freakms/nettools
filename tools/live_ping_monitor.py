"""
Live Ping Monitor Tool
Provides continuous ping monitoring with real-time graphs
"""

import threading
import time
from collections import deque
from pythonping import ping
import socket


class LivePingMonitor:
    """Live ping monitor with real-time latency tracking"""
    
    def __init__(self):
        self.monitoring = False
        self.paused = False
        self.hosts = {}  # {ip: HostData}
        self.threads = []
        
    def add_host(self, address):
        """Add a host to monitor (IP or hostname)"""
        # Resolve hostname if needed
        try:
            # Try to resolve as hostname first
            ip = socket.gethostbyname(address)
            hostname = address if address != ip else ""
        except:
            # Assume it's already an IP
            ip = address
            hostname = ""
        
        if ip not in self.hosts:
            self.hosts[ip] = HostData(ip, hostname)
            return ip
        return None
    
    def remove_host(self, ip):
        """Remove a host from monitoring"""
        if ip in self.hosts:
            del self.hosts[ip]
    
    def start_monitoring(self):
        """Start monitoring all hosts"""
        self.monitoring = True
        self.paused = False
        
        # Start a thread for each host
        for ip, host_data in self.hosts.items():
            thread = threading.Thread(
                target=self._monitor_host,
                args=(ip, host_data),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
    
    def pause_monitoring(self):
        """Pause monitoring"""
        self.paused = True
    
    def resume_monitoring(self):
        """Resume monitoring"""
        self.paused = False
    
    def stop_monitoring(self):
        """Stop monitoring all hosts"""
        self.monitoring = False
        self.paused = False
        # Wait for threads to finish
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=2)
        self.threads.clear()
    
    def _monitor_host(self, ip, host_data):
        """Monitor a single host continuously"""
        while self.monitoring:
            if not self.paused:
                try:
                    # Ping the host
                    response = ping(ip, timeout=1, count=1, verbose=False)
                    
                    if response.success():
                        rtt = response.rtt_avg_ms
                        host_data.add_ping_result(True, rtt)
                    else:
                        host_data.add_ping_result(False, None)
                        
                except Exception:
                    host_data.add_ping_result(False, None)
            
            # Wait 1 second before next ping
            time.sleep(1)
    
    def get_all_hosts_data(self):
        """Get data for all monitored hosts"""
        return self.hosts.copy()
    
    def export_data(self):
        """Export monitoring data to text format"""
        lines = []
        lines.append("Live Ping Monitor - Export Data")
        lines.append("=" * 60)
        lines.append("")
        
        for ip, host_data in self.hosts.items():
            lines.append(f"Host: {ip}")
            if host_data.hostname:
                lines.append(f"Hostname: {host_data.hostname}")
            lines.append(f"Status: {host_data.get_status_text()}")
            lines.append(f"Average Latency: {host_data.get_average_latency():.1f} ms")
            lines.append(f"Packet Loss: {host_data.get_packet_loss():.1f}%")
            lines.append(f"Total Pings: {host_data.get_total_pings()}")
            lines.append("")
            
            # Add recent ping data
            lines.append("Recent Pings (last 30):")
            for i, (success, rtt) in enumerate(host_data.get_recent_pings(), 1):
                if success:
                    lines.append(f"  {i}. {rtt:.1f} ms")
                else:
                    lines.append(f"  {i}. TIMEOUT")
            lines.append("")
            lines.append("-" * 60)
            lines.append("")
        
        return "\n".join(lines)


class HostData:
    """Data container for a monitored host"""
    
    def __init__(self, ip, hostname=""):
        self.ip = ip
        self.hostname = hostname
        self.latencies = deque(maxlen=30)  # Last 30 pings
        self.success_count = 0
        self.fail_count = 0
        self.current_status = "unknown"  # "online", "warning", "offline", "unknown"
        self.last_update = time.time()
    
    def add_ping_result(self, success, rtt):
        """Add a ping result"""
        if success:
            self.latencies.append(rtt)
            self.success_count += 1
            
            # Determine status based on latency
            if rtt < 50:
                self.current_status = "online"
            elif rtt < 150:
                self.current_status = "warning"
            else:
                self.current_status = "warning"
        else:
            self.latencies.append(None)
            self.fail_count += 1
            self.current_status = "offline"
        
        self.last_update = time.time()
    
    def get_recent_pings(self):
        """Get list of (success, rtt) tuples for recent pings"""
        results = []
        for rtt in self.latencies:
            if rtt is not None:
                results.append((True, rtt))
            else:
                results.append((False, 0))
        return results
    
    def get_average_latency(self):
        """Get average latency (excluding timeouts)"""
        valid_latencies = [rtt for rtt in self.latencies if rtt is not None]
        if valid_latencies:
            return sum(valid_latencies) / len(valid_latencies)
        return 0.0
    
    def get_packet_loss(self):
        """Get packet loss percentage"""
        total = self.success_count + self.fail_count
        if total > 0:
            return (self.fail_count / total) * 100
        return 0.0
    
    def get_total_pings(self):
        """Get total number of pings sent"""
        return self.success_count + self.fail_count
    
    def get_status_text(self):
        """Get human-readable status"""
        status_map = {
            "online": "Online (Good Latency)",
            "warning": "Online (High Latency)",
            "offline": "Offline",
            "unknown": "Unknown"
        }
        return status_map.get(self.current_status, "Unknown")
    
    def get_status_color(self):
        """Get status indicator color"""
        color_map = {
            "online": "#00ff00",  # Green
            "warning": "#ffff00",  # Yellow
            "offline": "#ff0000",  # Red
            "unknown": "#808080"   # Gray
        }
        return color_map.get(self.current_status, "#808080")
