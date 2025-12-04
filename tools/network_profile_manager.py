"""
Network Profile Manager Module
Manages network interface profiles for quick configuration switching
"""

import json
from pathlib import Path
from datetime import datetime


class NetworkProfileManager:
    """Manage network interface profiles"""
    
    def __init__(self):
        self.history_dir = Path.home() / ".nettools"
        self.profiles_file = self.history_dir / "network_profiles.json"
        self.profiles = self.load_profiles()
    
    def load_profiles(self):
        """Load saved profiles from file"""
        if not self.history_dir.exists():
            self.history_dir.mkdir(parents=True)
        
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return []
    
    def save_profiles(self):
        """Save profiles to file"""
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            print(f"Could not save profiles: {e}")
    
    def add_profile(self, name, interfaces):
        """Add a new profile"""
        profile = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "name": name,
            "interfaces": interfaces,
            "created": datetime.now().isoformat()
        }
        
        self.profiles.append(profile)
        self.save_profiles()
        return profile["id"]
    
    def delete_profile(self, profile_id):
        """Delete a profile by ID"""
        self.profiles = [p for p in self.profiles if p["id"] != profile_id]
        self.save_profiles()
    
    def get_profile(self, profile_id):
        """Get a specific profile by ID"""
        for profile in self.profiles:
            if profile["id"] == profile_id:
                return profile
        return None
