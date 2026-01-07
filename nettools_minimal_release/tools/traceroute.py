"""
Traceroute Module
Performs network path tracing using tracert or pathping
"""

import subprocess
import platform


class Traceroute:
    """Network path tracing utility"""
    
    @staticmethod
    def run(target, max_hops=30, tool="tracert", timeout=600):
        """
        Run traceroute or pathping to target
        
        Args:
            target (str): Target hostname or IP address
            max_hops (int): Maximum number of hops (1-255)
            tool (str): Tool to use ("tracert" or "pathping")
            timeout (int): Command timeout in seconds
            
        Returns:
            dict: Results with output and success status
        """
        if not target or not target.strip():
            return {
                "success": False,
                "output": "No target specified",
                "error": "Invalid input"
            }
        
        # Validate max_hops
        if not isinstance(max_hops, int) or not 1 <= max_hops <= 255:
            return {
                "success": False,
                "output": "Max hops must be between 1 and 255",
                "error": "Invalid max_hops"
            }
        
        # Build command
        if tool == "tracert":
            cmd = ["tracert", "-h", str(max_hops), target]
            estimated_time = "~30 seconds"
        elif tool == "pathping":
            cmd = ["pathping", "-h", str(max_hops), target]
            estimated_time = "~5 minutes"
        else:
            return {
                "success": False,
                "output": f"Unknown tool: {tool}",
                "error": "Invalid tool"
            }
        
        try:
            # Run command
            if platform.system() == "Windows":
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
                    shell=False,
                    encoding='cp850',  # Windows console encoding
                    errors='replace'    # Replace invalid characters
                )
            else:
                # Linux/Mac
                if tool == "tracert":
                    cmd = ["traceroute", "-m", str(max_hops), target]
                else:
                    # Pathping not available on Linux, use mtr as alternative
                    cmd = ["mtr", "--report", "--report-cycles", "3", target]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    shell=False
                )
            
            # Get output
            stdout_data = result.stdout if result.stdout else ""
            stderr_data = result.stderr if result.stderr else ""
            
            # Combine output
            if stdout_data and len(stdout_data.strip()) > 0:
                output = stdout_data
                if stderr_data and len(stderr_data.strip()) > 0:
                    output += f"\n\n--- Stderr Output ---\n{stderr_data}"
            elif stderr_data and len(stderr_data.strip()) > 0:
                output = stderr_data
            else:
                output = "Command completed but produced no output."
            
            # Determine success
            success = bool(output and result.returncode in [0, 1])
            
            return {
                "success": success,
                "output": output,
                "return_code": result.returncode,
                "command": ' '.join(cmd),
                "estimated_time": estimated_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": f"Command timeout ({timeout} seconds exceeded)\nCommand: {' '.join(cmd)}",
                "error": "Timeout"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "output": f"Command not found: {cmd[0]}\nThis command may not be available on your system.",
                "error": "Command not found"
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"Error executing command:\n{str(e)}\n\nCommand: {' '.join(cmd)}",
                "error": str(e)
            }
    
    @staticmethod
    def validate_target(target):
        """
        Validate target hostname or IP
        
        Args:
            target (str): Target to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not target or not target.strip():
            return False
        
        # Basic validation - could be more strict
        target = target.strip()
        
        # Check for invalid characters
        invalid_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '"', "'"]
        if any(char in target for char in invalid_chars):
            return False
        
        return True
    
    @staticmethod
    def parse_traceroute_output(output, tool="tracert"):
        """
        Parse traceroute/pathping output into structured data
        
        Args:
            output (str): Raw command output
            tool (str): Tool used ("tracert" or "pathping")
            
        Returns:
            list: List of hops with details
        """
        if not output:
            return []
        
        hops = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or line.startswith('Tracing') or line.startswith('Computing'):
                continue
            
            # Try to parse hop information
            # Format: hop_number  time1  time2  time3  hostname [ip]
            parts = line.split()
            
            if len(parts) >= 2 and parts[0].isdigit():
                hop = {
                    'number': int(parts[0]),
                    'raw_line': line
                }
                hops.append(hop)
        
        return hops
    
    @staticmethod
    def get_available_tools():
        """
        Get list of available traceroute tools on the system
        
        Returns:
            list: Available tools
        """
        available = []
        
        if platform.system() == "Windows":
            # Windows has tracert and pathping
            available.extend(["tracert", "pathping"])
        else:
            # Check for traceroute
            try:
                subprocess.run(["which", "traceroute"], capture_output=True, check=True)
                available.append("tracert")
            except:
                pass
            
            # Check for mtr
            try:
                subprocess.run(["which", "mtr"], capture_output=True, check=True)
                available.append("pathping")
            except:
                pass
        
        return available
