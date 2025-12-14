"""
Traceroute History Manager
Manages saved traceroute results for comparison and history tracking
"""

import json
from pathlib import Path
from datetime import datetime
import re


class TracerouteManager:
    """Manage saved traceroutes for comparison"""
    
    def __init__(self):
        self.history_dir = Path.home() / ".nettools"
        self.traces_file = self.history_dir / "traceroutes.json"
        self.max_traces = 50
        self.traces = self.load_traces()
    
    def load_traces(self):
        """Load saved traceroutes from file"""
        if not self.history_dir.exists():
            self.history_dir.mkdir(parents=True)
        
        if self.traces_file.exists():
            try:
                with open(self.traces_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return []
    
    def save_traces(self):
        """Save traces to file"""
        try:
            with open(self.traces_file, 'w', encoding='utf-8') as f:
                json.dump(self.traces, f, indent=2)
        except Exception as e:
            print(f"Could not save traceroutes: {e}")
    
    def parse_traceroute_output(self, output, target):
        """Parse traceroute output into structured hop data"""
        hops = []
        lines = output.strip().split('\n')
        
        for line in lines:
            # Skip header lines and empty lines
            if not line.strip() or 'Tracing route' in line or 'Trace complete' in line:
                continue
            if 'over a maximum' in line:
                continue
            
            # Parse hop line - format varies by OS
            # Windows: "  1    <1 ms    <1 ms    <1 ms  192.168.1.1"
            # Linux:   "1  192.168.1.1 (192.168.1.1)  0.123 ms  0.456 ms  0.789 ms"
            
            # Try to extract hop number
            hop_match = re.match(r'^\s*(\d+)', line)
            if hop_match:
                hop_num = int(hop_match.group(1))
                
                # Extract IP address
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                ip_addr = ip_match.group(1) if ip_match else '*'
                
                # Extract latency values (look for ms values)
                latencies = re.findall(r'([<]?\d+(?:\.\d+)?\s*ms)', line)
                
                # Calculate average latency
                avg_latency = None
                if latencies:
                    values = []
                    for lat in latencies:
                        lat_clean = lat.replace('ms', '').replace('<', '').strip()
                        try:
                            values.append(float(lat_clean))
                        except:
                            pass
                    if values:
                        avg_latency = sum(values) / len(values)
                
                # Check for timeout
                is_timeout = ip_addr == '*' or 'Request timed out' in line or '* * *' in line
                
                hops.append({
                    'hop': hop_num,
                    'ip': ip_addr,
                    'latency_ms': round(avg_latency, 2) if avg_latency else None,
                    'timeout': is_timeout,
                    'raw': line.strip()
                })
        
        return hops
    
    def add_trace(self, target, output, success=True):
        """Add a traceroute result"""
        hops = self.parse_traceroute_output(output, target)
        
        trace = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "hops": hops,
            "raw_output": output,
            "summary": {
                "total_hops": len(hops),
                "timeouts": sum(1 for h in hops if h.get('timeout')),
                "avg_latency": round(sum(h['latency_ms'] for h in hops if h.get('latency_ms')) / max(1, sum(1 for h in hops if h.get('latency_ms'))), 2) if any(h.get('latency_ms') for h in hops) else None
            }
        }
        
        self.traces.insert(0, trace)
        self.traces = self.traces[:self.max_traces]
        self.save_traces()
        return trace["id"]
    
    def get_traces(self, target=None):
        """Get saved traces, optionally filtered by target"""
        if target:
            return [t for t in self.traces if t["target"].lower() == target.lower()]
        return self.traces
    
    def get_trace_by_id(self, trace_id):
        """Get a specific trace by ID"""
        for trace in self.traces:
            if trace["id"] == trace_id:
                return trace
        return None
    
    def compare_traces(self, trace1_id, trace2_id):
        """Compare two traceroutes and return differences"""
        trace1 = self.get_trace_by_id(trace1_id)
        trace2 = self.get_trace_by_id(trace2_id)
        
        if not trace1 or not trace2:
            return None
        
        hops1 = {h['hop']: h for h in trace1.get('hops', [])}
        hops2 = {h['hop']: h for h in trace2.get('hops', [])}
        
        all_hops = sorted(set(list(hops1.keys()) + list(hops2.keys())))
        
        comparison = {
            "trace1": {
                "id": trace1["id"],
                "target": trace1["target"],
                "timestamp": trace1["timestamp"],
                "total_hops": len(trace1.get('hops', [])),
                "avg_latency": trace1.get('summary', {}).get('avg_latency')
            },
            "trace2": {
                "id": trace2["id"],
                "target": trace2["target"],
                "timestamp": trace2["timestamp"],
                "total_hops": len(trace2.get('hops', [])),
                "avg_latency": trace2.get('summary', {}).get('avg_latency')
            },
            "hops": [],
            "summary": {
                "total_hops": len(all_hops),
                "route_changes": 0,
                "latency_improved": 0,
                "latency_degraded": 0,
                "new_timeouts": 0,
                "resolved_timeouts": 0
            }
        }
        
        for hop_num in all_hops:
            hop1 = hops1.get(hop_num, {})
            hop2 = hops2.get(hop_num, {})
            
            ip1 = hop1.get('ip', '-')
            ip2 = hop2.get('ip', '-')
            lat1 = hop1.get('latency_ms')
            lat2 = hop2.get('latency_ms')
            to1 = hop1.get('timeout', True) if not hop1 else hop1.get('timeout', False)
            to2 = hop2.get('timeout', True) if not hop2 else hop2.get('timeout', False)
            
            # Determine status
            status = "unchanged"
            if ip1 != ip2 and ip1 != '-' and ip2 != '-':
                status = "route_changed"
                comparison["summary"]["route_changes"] += 1
            elif not hop1:
                status = "new_hop"
            elif not hop2:
                status = "removed_hop"
            elif to1 and not to2:
                status = "resolved_timeout"
                comparison["summary"]["resolved_timeouts"] += 1
            elif not to1 and to2:
                status = "new_timeout"
                comparison["summary"]["new_timeouts"] += 1
            elif lat1 and lat2:
                diff = lat2 - lat1
                if diff < -5:  # More than 5ms improvement
                    status = "improved"
                    comparison["summary"]["latency_improved"] += 1
                elif diff > 5:  # More than 5ms degradation
                    status = "degraded"
                    comparison["summary"]["latency_degraded"] += 1
            
            comparison["hops"].append({
                "hop": hop_num,
                "trace1_ip": ip1,
                "trace2_ip": ip2,
                "trace1_latency": lat1,
                "trace2_latency": lat2,
                "trace1_timeout": to1,
                "trace2_timeout": to2,
                "latency_diff": round(lat2 - lat1, 2) if lat1 and lat2 else None,
                "status": status
            })
        
        return comparison
    
    def delete_trace(self, trace_id):
        """Delete a traceroute by ID"""
        self.traces = [t for t in self.traces if t["id"] != trace_id]
        self.save_traces()
    
    def clear_all_traces(self):
        """Clear all saved traceroutes"""
        self.traces = []
        self.save_traces()
