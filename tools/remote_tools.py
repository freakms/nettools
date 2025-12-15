"""
Remote Tools Module - PSExec and iPerf Integration
Provides remote command execution and bandwidth testing capabilities.
"""

import subprocess
import platform
import os
import threading
import shutil
from pathlib import Path
from typing import Optional, Callable, Dict, Any


class PSExecTool:
    """
    PSExec integration for remote command execution.
    Allows running commands on remote Windows hosts.
    """
    
    def __init__(self):
        self.psexec_path = self._find_psexec()
        self.is_available = self.psexec_path is not None
    
    def _find_psexec(self) -> Optional[str]:
        """Find PSExec executable in system PATH or common locations"""
        # Check PATH first
        psexec_name = "PsExec.exe" if platform.system() == "Windows" else "psexec"
        psexec_path = shutil.which(psexec_name)
        
        if psexec_path:
            return psexec_path
        
        # Check common Windows locations
        if platform.system() == "Windows":
            common_paths = [
                r"C:\PsTools\PsExec.exe",
                r"C:\Windows\System32\PsExec.exe",
                r"C:\Tools\PsExec.exe",
                os.path.expanduser(r"~\Downloads\PsExec.exe"),
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    return path
        
        return None
    
    def set_psexec_path(self, path: str) -> bool:
        """Manually set PSExec path"""
        if os.path.exists(path):
            self.psexec_path = path
            self.is_available = True
            return True
        return False
    
    def _establish_network_session(
        self,
        target_host: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Establish a network session to the remote host using net use.
        This is required for cross-domain authentication.
        
        Args:
            target_host: Target hostname or IP
            username: Username for authentication
            password: Password for authentication
            domain: Domain name
            
        Returns:
            Dictionary with 'success', 'error', 'already_connected'
        """
        if not username or not password:
            return {'success': False, 'error': 'Username and password required', 'already_connected': False}
        
        # Build the user string
        if domain:
            user_string = f"{domain}\\{username}"
        else:
            user_string = username
        
        # First, try to delete any existing connection (ignore errors)
        delete_cmd = f'net use "\\\\{target_host}\\IPC$" /delete /y'
        try:
            subprocess.run(
                delete_cmd,
                shell=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
        except:
            pass
        
        # Establish new connection
        connect_cmd = f'net use "\\\\{target_host}\\IPC$" /user:"{user_string}" "{password}"'
        
        try:
            result = subprocess.run(
                connect_cmd,
                shell=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            # Decode output with error handling for German/special characters
            def safe_decode(byte_data):
                if not byte_data:
                    return ""
                try:
                    return byte_data.decode('utf-8', errors='replace')
                except:
                    try:
                        return byte_data.decode('cp850', errors='replace')
                    except:
                        return byte_data.decode('latin-1', errors='replace')
            
            stdout_text = safe_decode(result.stdout)
            stderr_text = safe_decode(result.stderr)
            
            if result.returncode == 0:
                return {'success': True, 'error': None, 'already_connected': False}
            else:
                # Check if already connected
                if "1219" in stderr_text or "already" in stderr_text.lower() or "bereits" in stderr_text.lower():
                    return {'success': True, 'error': None, 'already_connected': True}
                return {'success': False, 'error': stderr_text.strip() or stdout_text.strip(), 'already_connected': False}
                
        except Exception as e:
            return {'success': False, 'error': str(e), 'already_connected': False}
    
    def _disconnect_network_session(self, target_host: str):
        """Disconnect the network session"""
        try:
            delete_cmd = f'net use "\\\\{target_host}\\IPC$" /delete /y'
            subprocess.run(
                delete_cmd,
                shell=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
        except:
            pass
    
    def execute_remote_command(
        self,
        target_host: str,
        command: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        domain: Optional[str] = None,
        copy_file: Optional[str] = None,
        interactive: bool = False,
        elevated: bool = False,
        run_as_system: bool = False,
        use_current_credentials: bool = False,
        use_net_session: bool = True,
        callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Execute a command on a remote host using PSExec.
        
        Args:
            target_host: Target hostname or IP address
            command: Command to execute
            username: Remote username (optional)
            password: Remote password (optional)
            domain: Domain name (optional)
            copy_file: Path to file to copy before execution (optional)
            interactive: Run interactively (-i flag)
            elevated: Run with elevated privileges (-h flag)
            run_as_system: Run as SYSTEM account (-s flag)
            use_current_credentials: Don't pass explicit credentials, use current session
            use_net_session: Establish network session first with net use (for cross-domain)
            callback: Function to call with output lines
            
        Returns:
            Dictionary with 'success', 'output', 'error', 'return_code'
        """
        if not self.is_available:
            return {
                'success': False,
                'output': '',
                'error': 'PSExec not found. Please download from Microsoft Sysinternals.',
                'return_code': -1
            }
        
        # For cross-domain: establish network session first
        session_established = False
        if use_net_session and not use_current_credentials and username and password:
            if callback:
                callback(f"Establishing network session to {target_host}...")
            
            session_result = self._establish_network_session(target_host, username, password, domain)
            
            if not session_result['success']:
                return {
                    'success': False,
                    'output': '',
                    'error': f"Failed to establish network session: {session_result['error']}",
                    'return_code': -1
                }
            
            session_established = True
            if callback:
                callback("Network session established. Running PSExec...")
        
        # Build PSExec command - when using net session, don't pass credentials to PSExec
        cmd = [self.psexec_path, f"\\\\{target_host}"]
        
        # Only pass credentials to PSExec if NOT using net session
        if not use_current_credentials and not (use_net_session and session_established):
            if username:
                if domain:
                    cmd.extend(["-u", f"{domain}\\{username}"])
                else:
                    cmd.extend(["-u", username])
            
            if password:
                cmd.extend(["-p", password])
        
        # Add flags
        if interactive:
            cmd.append("-i")
        
        if elevated:
            cmd.append("-h")
        
        if run_as_system:
            cmd.append("-s")
        
        # Accept EULA silently
        cmd.append("-accepteula")
        
        # Add copy file flag if specified
        if copy_file and os.path.exists(copy_file):
            cmd.extend(["-c", copy_file])
        
        # Add the command to execute
        cmd.extend(["cmd", "/c", command])
        
        try:
            # Execute with CREATE_NO_WINDOW on Windows
            creation_flags = 0
            if platform.system() == "Windows":
                creation_flags = subprocess.CREATE_NO_WINDOW
            
            # Use bytes mode and decode manually to handle encoding issues
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=creation_flags
            )
            
            output_lines = []
            
            # Read output line by line (as bytes, then decode with error handling)
            for line in process.stdout:
                try:
                    decoded_line = line.decode('utf-8', errors='replace').rstrip()
                except:
                    try:
                        decoded_line = line.decode('cp850', errors='replace').rstrip()
                    except:
                        decoded_line = line.decode('latin-1', errors='replace').rstrip()
                
                output_lines.append(decoded_line)
                if callback:
                    callback(decoded_line)
            
            process.wait()
            
            # Read stderr with same error handling
            stderr_bytes = process.stderr.read()
            try:
                stderr = stderr_bytes.decode('utf-8', errors='replace')
            except:
                try:
                    stderr = stderr_bytes.decode('cp850', errors='replace')
                except:
                    stderr = stderr_bytes.decode('latin-1', errors='replace')
            
            return {
                'success': process.returncode == 0,
                'output': '\n'.join(output_lines),
                'error': stderr,
                'return_code': process.returncode
            }
            
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'return_code': -1
            }
    
    def start_remote_cmd(
        self,
        target_host: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        domain: Optional[str] = None,
        use_current_credentials: bool = False
    ) -> Dict[str, Any]:
        """
        Start an interactive remote CMD session.
        Opens a new command window connected to the remote host.
        
        For cross-domain: Uses PowerShell Start-Process with -Credential
        to establish proper credential context.
        
        Returns:
            Dictionary with 'success' and 'error' if failed
        """
        if not self.is_available:
            return {
                'success': False,
                'error': 'PSExec not found.'
            }
        
        if use_current_credentials or not username or not password:
            # Simple case: use current session
            cmd = [self.psexec_path, f"\\\\{target_host}", "-accepteula", "-i", "cmd"]
            try:
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == "Windows" else 0)
                return {'success': True}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        # Cross-domain case: Use PowerShell with -Credential
        # This properly passes credentials without prompting
        
        try:
            import tempfile
            
            # Build user string
            if domain:
                user_string = f"{domain}\\{username}"
            else:
                user_string = username
            
            # Escape special characters in password for PowerShell
            # Single quotes in PowerShell need to be doubled
            escaped_password = password.replace("'", "''")
            
            # Escape backslashes in PSExec path for PowerShell
            psexec_path_escaped = self.psexec_path.replace("\\", "\\\\")
            
            # Create PowerShell script that:
            # 1. Creates a credential object
            # 2. Starts a new CMD process with those credentials
            # 3. That CMD runs a batch file with PSExec
            
            # First create a batch file with the PSExec command
            batch_content = f'''@echo off
title PSExec Session to {target_host}
echo ============================================
echo  Connecting to {target_host}
echo  User: {user_string}
echo ============================================
echo.
"{self.psexec_path}" \\\\{target_host} -accepteula cmd
echo.
echo Connection closed. Press any key to exit.
pause > nul
'''
            batch_file = temp_dir / "nettools_psexec.bat"
            batch_file.write_text(batch_content, encoding='utf-8')
            
            # PowerShell script runs the batch file with credentials
            ps_script = f'''
$ErrorActionPreference = "Stop"
try {{
    $password = ConvertTo-SecureString '{escaped_password}' -AsPlainText -Force
    $cred = New-Object System.Management.Automation.PSCredential ('{user_string}', $password)
    
    Start-Process -FilePath "{str(batch_file)}" -Credential $cred -WorkingDirectory "C:\\Windows\\System32"
    
    Write-Host "SUCCESS"
}} catch {{
    Write-Host "ERROR: $($_.Exception.Message)"
    exit 1
}}
'''
            
            # Write PowerShell script to temp file
            temp_dir = Path(tempfile.gettempdir())
            ps_file = temp_dir / "nettools_psexec_session.ps1"
            ps_file.write_text(ps_script, encoding='utf-8-sig')  # UTF-8 with BOM for PowerShell
            
            # Execute PowerShell script
            result = subprocess.run(
                [
                    'powershell', '-ExecutionPolicy', 'Bypass', 
                    '-NoProfile', '-File', str(ps_file)
                ],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            # Decode output
            stdout = result.stdout.decode('utf-8', errors='replace').strip() if result.stdout else ''
            stderr = result.stderr.decode('utf-8', errors='replace').strip() if result.stderr else ''
            
            if result.returncode == 0 and 'SUCCESS' in stdout:
                return {'success': True}
            else:
                error_msg = stderr or stdout or 'PowerShell execution failed'
                # Clean up the error message
                error_msg = error_msg.replace('~', '').strip()
                return {'success': False, 'error': error_msg}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def copy_file_to_remote(
        self,
        target_host: str,
        local_path: str,
        remote_path: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Copy a file to a remote host using administrative share.
        
        Args:
            target_host: Target hostname or IP
            local_path: Path to local file
            remote_path: Destination path on remote host (e.g., C:\\Tools\\file.exe)
            username: Credentials
            password: Credentials
            domain: Domain
            
        Returns:
            Dictionary with 'success', 'error'
        """
        if not os.path.exists(local_path):
            return {'success': False, 'error': f'Local file not found: {local_path}'}
        
        # Convert remote path to UNC path
        # C:\Tools\file.exe -> \\host\C$\Tools\file.exe
        if len(remote_path) >= 2 and remote_path[1] == ':':
            drive = remote_path[0]
            path_rest = remote_path[2:]
            unc_path = f"\\\\{target_host}\\{drive}${path_rest}"
        else:
            return {'success': False, 'error': 'Invalid remote path format. Use drive letter path (e.g., C:\\folder\\file)'}
        
        try:
            # Use net use to connect if credentials provided
            if username and password:
                net_cmd = f"net use \\\\{target_host}\\IPC$ /user:{domain + chr(92) if domain else ''}{username} {password}"
                subprocess.run(net_cmd, shell=True, capture_output=True)
            
            # Copy file
            shutil.copy2(local_path, unc_path)
            
            return {'success': True}
            
        except PermissionError:
            return {'success': False, 'error': 'Access denied. Check credentials and permissions.'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class IPerfTool:
    """
    iPerf3 integration for bandwidth testing.
    """
    
    def __init__(self):
        self.iperf_path = self._find_iperf()
        self.is_available = self.iperf_path is not None
        self.current_process = None
    
    def _find_iperf(self) -> Optional[str]:
        """Find iPerf3 executable"""
        # Check PATH
        for name in ["iperf3", "iperf3.exe", "iperf", "iperf.exe"]:
            path = shutil.which(name)
            if path:
                return path
        
        # Check common Windows locations
        if platform.system() == "Windows":
            common_paths = [
                r"C:\iperf3\iperf3.exe",
                r"C:\Tools\iperf3.exe",
                r"C:\Program Files\iperf3\iperf3.exe",
                os.path.expanduser(r"~\Downloads\iperf3.exe"),
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    return path
        
        return None
    
    def set_iperf_path(self, path: str) -> bool:
        """Manually set iPerf path"""
        if os.path.exists(path):
            self.iperf_path = path
            self.is_available = True
            return True
        return False
    
    def run_client_test(
        self,
        server_host: str,
        port: int = 5201,
        duration: int = 10,
        parallel: int = 1,
        reverse: bool = False,
        udp: bool = False,
        bandwidth: Optional[str] = None,
        callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Run iPerf3 client test.
        
        Args:
            server_host: Server IP or hostname
            port: Server port (default 5201)
            duration: Test duration in seconds
            parallel: Number of parallel streams
            reverse: Reverse mode (server sends, client receives)
            udp: Use UDP instead of TCP
            bandwidth: Target bandwidth for UDP (e.g., "100M")
            callback: Function to call with output lines
            
        Returns:
            Dictionary with test results
        """
        if not self.is_available:
            return {
                'success': False,
                'error': 'iPerf3 not found. Please install iPerf3.',
                'results': None
            }
        
        cmd = [
            self.iperf_path,
            "-c", server_host,
            "-p", str(port),
            "-t", str(duration),
            "-P", str(parallel),
            "-J"  # JSON output for parsing
        ]
        
        if reverse:
            cmd.append("-R")
        
        if udp:
            cmd.append("-u")
            if bandwidth:
                cmd.extend(["-b", bandwidth])
        
        try:
            creation_flags = 0
            if platform.system() == "Windows":
                creation_flags = subprocess.CREATE_NO_WINDOW
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creation_flags
            )
            
            self.current_process = process
            
            output_lines = []
            for line in process.stdout:
                output_lines.append(line)
                if callback:
                    callback(line.rstrip())
            
            process.wait()
            self.current_process = None
            
            output = ''.join(output_lines)
            stderr = process.stderr.read()
            
            # Parse JSON results
            results = None
            try:
                import json
                results = json.loads(output)
            except Exception:
                pass
            
            return {
                'success': process.returncode == 0,
                'output': output,
                'error': stderr,
                'results': results,
                'return_code': process.returncode
            }
            
        except Exception as e:
            self.current_process = None
            return {
                'success': False,
                'error': str(e),
                'results': None,
                'return_code': -1
            }
    
    def start_server(
        self,
        port: int = 5201,
        one_off: bool = True,
        callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Start iPerf3 server.
        
        Args:
            port: Port to listen on
            one_off: Exit after one client connection
            callback: Function to call with output
            
        Returns:
            Process handle if successful
        """
        if not self.is_available:
            return {
                'success': False,
                'error': 'iPerf3 not found.',
                'process': None
            }
        
        cmd = [self.iperf_path, "-s", "-p", str(port)]
        
        if one_off:
            cmd.append("-1")
        
        try:
            creation_flags = 0
            if platform.system() == "Windows":
                creation_flags = subprocess.CREATE_NO_WINDOW
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creation_flags
            )
            
            return {
                'success': True,
                'process': process
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'process': None
            }
    
    def stop_current_test(self):
        """Stop any running test"""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process = None
            except Exception:
                pass
    
    def copy_to_remote(
        self,
        target_host: str,
        remote_path: str,
        psexec_tool: Optional[PSExecTool] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Copy iPerf3 to a remote host.
        
        Args:
            target_host: Target hostname/IP
            remote_path: Destination folder (e.g., C:\\Tools)
            psexec_tool: Optional PSExecTool instance for credential-based copy
            username, password, domain: Credentials for remote access
            
        Returns:
            Dictionary with 'success', 'remote_iperf_path', 'error'
        """
        if not self.is_available:
            return {
                'success': False,
                'error': 'iPerf3 not found locally.',
                'remote_iperf_path': None
            }
        
        local_iperf = self.iperf_path
        iperf_filename = os.path.basename(local_iperf)
        full_remote_path = os.path.join(remote_path, iperf_filename)
        
        if psexec_tool:
            result = psexec_tool.copy_file_to_remote(
                target_host, local_iperf, full_remote_path,
                username, password, domain
            )
            if result['success']:
                return {
                    'success': True,
                    'remote_iperf_path': full_remote_path,
                    'error': None
                }
            return {
                'success': False,
                'error': result['error'],
                'remote_iperf_path': None
            }
        
        # Try direct UNC copy
        try:
            if len(remote_path) >= 2 and remote_path[1] == ':':
                drive = remote_path[0]
                path_rest = remote_path[2:]
                unc_folder = f"\\\\{target_host}\\{drive}${path_rest}"
            else:
                return {'success': False, 'error': 'Invalid remote path', 'remote_iperf_path': None}
            
            # Create folder if needed
            os.makedirs(unc_folder, exist_ok=True)
            
            unc_file_path = os.path.join(unc_folder, iperf_filename)
            shutil.copy2(local_iperf, unc_file_path)
            
            return {
                'success': True,
                'remote_iperf_path': full_remote_path,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'remote_iperf_path': None
            }


def get_remote_tools() -> tuple:
    """Get instances of remote tools"""
    return PSExecTool(), IPerfTool()
