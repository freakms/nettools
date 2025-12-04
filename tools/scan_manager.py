"""
Scan Manager Module
Manages saved scans for comparison and history tracking
"""

import json
from pathlib import Path
from datetime import datetime


class ScanManager:
    """Manage saved scans for comparison"""
    
    def __init__(self):
        self.history_dir = Path.home() / ".nettools"
        self.scans_file = self.history_dir / "scans.json"
        self.max_scans = 20
        self.scans = self.load_scans()
    
    def load_scans(self):
        """Load saved scans from file"""
        if not self.history_dir.exists():
            self.history_dir.mkdir(parents=True)
        
        if self.scans_file.exists():
            try:
                with open(self.scans_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return []
    
    def save_scans(self):
        """Save scans to file"""
        try:
            with open(self.scans_file, 'w', encoding='utf-8') as f:
                json.dump(self.scans, f, indent=2)
        except Exception as e:
            print(f"Could not save scans: {e}")
    
    def add_scan(self, cidr, results):
        """Add a scan result"""
        scan = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "cidr": cidr,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total": len(results),
                "online": sum(1 for r in results if r["status"] == "Online"),
                "offline": sum(1 for r in results if r["status"] == "Offline")
            }
        }
        
        self.scans.insert(0, scan)
        self.scans = self.scans[:self.max_scans]
        self.save_scans()
        return scan["id"]
    
    def get_scans(self, cidr=None):
        """Get saved scans, optionally filtered by CIDR"""
        if cidr:
            return [s for s in self.scans if s["cidr"] == cidr]
        return self.scans
    
    def get_scan_by_id(self, scan_id):
        """Get a specific scan by ID"""
        for scan in self.scans:
            if scan["id"] == scan_id:
                return scan
        return None
    
    def compare_scans(self, scan1_id, scan2_id):
        """Compare two scans and return differences"""
        scan1 = self.get_scan_by_id(scan1_id)
        scan2 = self.get_scan_by_id(scan2_id)
        
        if not scan1 or not scan2:
            return None
        
        # Create IP lookup dictionaries
        ips1 = {r["ip"]: r for r in scan1["results"]}
        ips2 = {r["ip"]: r for r in scan2["results"]}
        
        # Find differences
        all_ips = sorted(set(ips1.keys()) | set(ips2.keys()), key=lambda ip: tuple(map(int, ip.split('.'))))
        
        comparison = []
        for ip in all_ips:
            if ip in ips1 and ip in ips2:
                # IP exists in both scans
                if ips1[ip]["status"] == ips2[ip]["status"]:
                    comparison.append({
                        "ip": ip,
                        "change": "unchanged",
                        "scan1_status": ips1[ip]["status"],
                        "scan2_status": ips2[ip]["status"],
                        "scan1_rtt": ips1[ip].get("rtt"),
                        "scan2_rtt": ips2[ip].get("rtt")
                    })
                else:
                    comparison.append({
                        "ip": ip,
                        "change": "changed",
                        "scan1_status": ips1[ip]["status"],
                        "scan2_status": ips2[ip]["status"],
                        "scan1_rtt": ips1[ip].get("rtt"),
                        "scan2_rtt": ips2[ip].get("rtt")
                    })
            elif ip in ips2:
                # New in scan2
                comparison.append({
                    "ip": ip,
                    "change": "new",
                    "scan1_status": "N/A",
                    "scan2_status": ips2[ip]["status"],
                    "scan1_rtt": None,
                    "scan2_rtt": ips2[ip].get("rtt")
                })
            else:
                # Missing in scan2
                comparison.append({
                    "ip": ip,
                    "change": "missing",
                    "scan1_status": ips1[ip]["status"],
                    "scan2_status": "N/A",
                    "scan1_rtt": ips1[ip].get("rtt"),
                    "scan2_rtt": None
                })
        
        return {
            "scan1": scan1,
            "scan2": scan2,
            "comparison": comparison,
            "summary": {
                "new": sum(1 for c in comparison if c["change"] == "new"),
                "missing": sum(1 for c in comparison if c["change"] == "missing"),
                "changed": sum(1 for c in comparison if c["change"] == "changed"),
                "unchanged": sum(1 for c in comparison if c["change"] == "unchanged")
            }
        }
