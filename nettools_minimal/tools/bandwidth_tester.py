"""
Bandwidth Testing Tool using iperf3
Provides network speed testing capabilities
"""

import subprocess
import json
import threading
import time


class BandwidthTester:
    """Bandwidth testing using iperf3"""
    
    def __init__(self):
        self.testing = False
        self.test_thread = None
        self.results = None
        self.error = None
        
    def test_client(self, server_host, port=5201, duration=10, reverse=False, callback=None):
        """
        Run iperf3 client test
        
        Args:
            server_host: iperf3 server hostname or IP
            port: Server port (default 5201)
            duration: Test duration in seconds
            reverse: True for download test, False for upload
            callback: Function to call with results (optional)
        """
        self.testing = True
        self.results = None
        self.error = None
        
        def run_test():
            try:
                cmd = [
                    'iperf3',
                    '-c', server_host,
                    '-p', str(port),
                    '-t', str(duration),
                    '-J'  # JSON output
                ]
                
                if reverse:
                    cmd.append('-R')  # Reverse mode (download)
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=duration + 10
                )
                
                if result.returncode == 0:
                    # Parse JSON output
                    self.results = json.loads(result.stdout)
                    if callback:
                        callback(self.results, None)
                else:
                    self.error = result.stderr
                    if callback:
                        callback(None, result.stderr)
                        
            except subprocess.TimeoutExpired:
                self.error = "Test timed out"
                if callback:
                    callback(None, "Test timed out")
            except json.JSONDecodeError as e:
                self.error = f"Failed to parse results: {str(e)}"
                if callback:
                    callback(None, f"Failed to parse results: {str(e)}")
            except Exception as e:
                self.error = str(e)
                if callback:
                    callback(None, str(e))
            finally:
                self.testing = False
        
        self.test_thread = threading.Thread(target=run_test, daemon=True)
        self.test_thread.start()
        
    def get_summary(self, results):
        """Extract summary from iperf3 results"""
        if not results:
            return None
        
        try:
            end_data = results.get('end', {})
            
            # Get transfer and bitrate
            sum_sent = end_data.get('sum_sent', {})
            sum_received = end_data.get('sum_received', {})
            
            summary = {
                'sent_bytes': sum_sent.get('bytes', 0),
                'sent_mbps': sum_sent.get('bits_per_second', 0) / 1_000_000,
                'received_bytes': sum_received.get('bytes', 0),
                'received_mbps': sum_received.get('bits_per_second', 0) / 1_000_000,
                'cpu_utilization_local': end_data.get('cpu_utilization_percent', {}).get('host_total', 0),
                'cpu_utilization_remote': end_data.get('cpu_utilization_percent', {}).get('remote_total', 0),
            }
            
            return summary
        except Exception as e:
            return None
    
    def stop_test(self):
        """Stop ongoing test"""
        if self.testing and self.test_thread:
            # iperf3 handles signals, thread will finish naturally
            self.testing = False
    
    def is_iperf3_available(self):
        """Check if iperf3 is installed"""
        try:
            result = subprocess.run(['iperf3', '--version'], capture_output=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def start_server(self, port=5201):
        """
        Start iperf3 server
        Returns: (success, message)
        """
        try:
            # Check if port is already in use
            check = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True
            )
            
            if check.returncode == 0:
                return False, f"Port {port} is already in use"
            
            # Start server in background
            subprocess.Popen(
                ['iperf3', '-s', '-p', str(port), '-D'],  # -D for daemon mode
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Give it a moment to start
            time.sleep(0.5)
            
            return True, f"Server started on port {port}"
            
        except Exception as e:
            return False, str(e)
    
    def stop_server(self, port=5201):
        """
        Stop iperf3 server
        Returns: (success, message)
        """
        try:
            # Find and kill iperf3 processes
            result = subprocess.run(
                ['pkill', '-f', f'iperf3.*-s.*-p {port}'],
                capture_output=True
            )
            
            return True, "Server stopped"
            
        except Exception as e:
            return False, str(e)
