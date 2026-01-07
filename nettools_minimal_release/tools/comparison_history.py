"""
Comparison History Manager
Stores scan results for comparison features
"""
import json
import os
from datetime import datetime
from pathlib import Path


class ComparisonHistory:
    """Manages history storage for comparison features"""
    
    def __init__(self):
        """Initialize comparison history manager"""
        self.history_dir = Path.home() / ".nettools_history"
        self.history_dir.mkdir(exist_ok=True)
        
        self.port_scan_file = self.history_dir / "port_scan_history.json"
        self.dns_lookup_file = self.history_dir / "dns_lookup_history.json"
        
        # Max entries to keep
        self.max_entries = 50
    
    def save_port_scan(self, target, results):
        """
        Save port scan results
        
        Args:
            target: Target IP/hostname
            results: List of port scan results
        """
        history = self._load_history(self.port_scan_file)
        
        # Debug output
        print(f"DEBUG: Saving port scan for {target}")
        print(f"DEBUG: Total results: {len(results)}")
        if results:
            print(f"DEBUG: First result sample: {results[0]}")
        
        # Filter open and closed ports (case-insensitive check)
        open_ports = [r for r in results if r.get("state", "").lower() == "open"]
        closed_ports = [r for r in results if r.get("state", "").lower() == "closed"]
        
        print(f"DEBUG: Open ports found: {len(open_ports)}")
        print(f"DEBUG: Closed ports found: {len(closed_ports)}")
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "open_ports": open_ports,
            "closed_ports": closed_ports,
            "total_scanned": len(results)
        }
        
        history.append(entry)
        
        # Keep only last max_entries
        if len(history) > self.max_entries:
            history = history[-self.max_entries:]
        
        self._save_history(self.port_scan_file, history)
    
    def get_port_scan_history(self, target=None):
        """
        Get port scan history
        
        Args:
            target: Optional filter by target
            
        Returns:
            List of scan history entries
        """
        history = self._load_history(self.port_scan_file)
        
        if target:
            history = [h for h in history if h["target"] == target]
        
        return history
    
    def save_dns_lookup(self, query, record_type, results):
        """
        Save DNS lookup results
        
        Args:
            query: Domain/IP queried
            record_type: Type of DNS record
            results: DNS lookup results
        """
        history = self._load_history(self.dns_lookup_file)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "record_type": record_type,
            "results": results
        }
        
        history.append(entry)
        
        # Keep only last max_entries
        if len(history) > self.max_entries:
            history = history[-self.max_entries:]
        
        self._save_history(self.dns_lookup_file, history)
    
    def get_dns_lookup_history(self, query=None):
        """
        Get DNS lookup history
        
        Args:
            query: Optional filter by query
            
        Returns:
            List of DNS lookup history entries
        """
        history = self._load_history(self.dns_lookup_file)
        
        if query:
            history = [h for h in history if h["query"] == query]
        
        return history
    
    def _load_history(self, file_path):
        """Load history from JSON file"""
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_history(self, file_path, history):
        """Save history to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def compare_port_scans(self, scan1, scan2):
        """
        Compare two port scans
        
        Args:
            scan1: Earlier scan entry
            scan2: Later scan entry
            
        Returns:
            Dictionary with comparison results
        """
        # Get open ports from each scan
        ports1 = set(p["port"] for p in scan1["open_ports"])
        ports2 = set(p["port"] for p in scan2["open_ports"])
        
        # Find differences
        newly_opened = ports2 - ports1
        newly_closed = ports1 - ports2
        unchanged = ports1 & ports2
        
        # Get service info
        def get_port_info(ports, scan):
            return {p["port"]: p for p in scan["open_ports"] if p["port"] in ports}
        
        return {
            "scan1_time": scan1["timestamp"],
            "scan2_time": scan2["timestamp"],
            "target": scan1["target"],
            "newly_opened": list(newly_opened),
            "newly_opened_details": get_port_info(newly_opened, scan2),
            "newly_closed": list(newly_closed),
            "newly_closed_details": get_port_info(newly_closed, scan1),
            "unchanged": list(unchanged),
            "unchanged_details": get_port_info(unchanged, scan2),
            "total_changes": len(newly_opened) + len(newly_closed)
        }
    
    def compare_dns_lookups(self, lookup1, lookup2):
        """
        Compare two DNS lookups
        
        Args:
            lookup1: Earlier lookup entry
            lookup2: Later lookup entry
            
        Returns:
            Dictionary with comparison results
        """
        # Convert results to sets for comparison
        results1 = set(lookup1["results"].get("result", [])) if isinstance(lookup1["results"].get("result"), list) else {lookup1["results"].get("result", "")}
        results2 = set(lookup2["results"].get("result", [])) if isinstance(lookup2["results"].get("result"), list) else {lookup2["results"].get("result", "")}
        
        # Find differences
        added = results2 - results1
        removed = results1 - results2
        unchanged = results1 & results2
        
        return {
            "lookup1_time": lookup1["timestamp"],
            "lookup2_time": lookup2["timestamp"],
            "query": lookup1["query"],
            "record_type": lookup1["record_type"],
            "added": list(added),
            "removed": list(removed),
            "unchanged": list(unchanged),
            "has_changes": len(added) > 0 or len(removed) > 0
        }
