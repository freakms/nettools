"""
History Manager Module
Manages history of scans and MAC addresses for quick access
"""

import json
from pathlib import Path
from datetime import datetime


class HistoryManager:
    """Manage history of scans and MAC addresses"""
    
    def __init__(self):
        self.history_dir = Path.home() / ".nettools"
        self.history_file = self.history_dir / "history.json"
        self.max_items = 10
        self.history = self.load_history()
    
    def load_history(self):
        """Load history from file"""
        if not self.history_dir.exists():
            self.history_dir.mkdir(parents=True)
        
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {"recent_cidrs": [], "recent_macs": []}
    
    def save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Could not save history: {e}")
    
    def add_cidr(self, cidr):
        """Add CIDR to history"""
        if not cidr or cidr.strip() == "":
            return
        
        cidr = cidr.strip()
        
        # Remove if already exists (to move to top)
        self.history["recent_cidrs"] = [
            item for item in self.history["recent_cidrs"]
            if item["cidr"] != cidr
        ]
        
        # Add to beginning
        self.history["recent_cidrs"].insert(0, {
            "cidr": cidr,
            "timestamp": datetime.now().isoformat(),
            "count": 1
        })
        
        # Keep only max_items
        self.history["recent_cidrs"] = self.history["recent_cidrs"][:self.max_items]
        
        self.save_history()
    
    def add_mac(self, mac):
        """Add MAC to history"""
        if not mac or mac.strip() == "":
            return
        
        mac = mac.strip().upper()
        
        # Remove if already exists
        self.history["recent_macs"] = [
            item for item in self.history["recent_macs"]
            if item["mac"] != mac
        ]
        
        # Add to beginning
        self.history["recent_macs"].insert(0, {
            "mac": mac,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only max_items
        self.history["recent_macs"] = self.history["recent_macs"][:self.max_items]
        
        self.save_history()
    
    def get_recent_cidrs(self):
        """Get list of recent CIDRs"""
        return [item["cidr"] for item in self.history["recent_cidrs"]]
    
    def get_recent_macs(self):
        """Get list of recent MACs"""
        return [item["mac"] for item in self.history["recent_macs"]]
    
    def clear_cidr_history(self):
        """Clear CIDR history"""
        self.history["recent_cidrs"] = []
        self.save_history()
    
    def clear_mac_history(self):
        """Clear MAC history"""
        self.history["recent_macs"] = []
        self.save_history()
