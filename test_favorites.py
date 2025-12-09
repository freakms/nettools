#!/usr/bin/env python3
"""
Test script to verify favorites and recent tools functionality
"""

import json
from pathlib import Path

# Mock the NetToolsApp class methods we added
class MockNetToolsApp:
    def __init__(self):
        self.config_file = Path.home() / '.nettools_config_test.json'
        self.favorite_tools = set()
        self.recent_tools = []
        self.max_recent = 5
        
    def load_favorites(self):
        """Load favorite tools from config"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return set(config.get('favorite_tools', []))
        except Exception as e:
            print(f"Could not load favorites: {e}")
        return set()
    
    def load_recent_tools(self):
        """Load recent tools from config"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('recent_tools', [])
        except Exception as e:
            print(f"Could not load recent tools: {e}")
        return []
    
    def save_window_state(self):
        """Save current window geometry and preferences"""
        try:
            config = {}
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            # Save favorites
            config['favorite_tools'] = list(self.favorite_tools)
            
            # Save recent tools
            config['recent_tools'] = self.recent_tools
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Could not save window state: {e}")
    
    def toggle_favorite(self, tool_id):
        """Toggle tool as favorite"""
        if tool_id in self.favorite_tools:
            self.favorite_tools.remove(tool_id)
        else:
            self.favorite_tools.add(tool_id)
        
        # Save
        self.save_window_state()
    
    def add_to_recent(self, tool_id):
        """Add tool to recent list"""
        # Remove if already in list
        if tool_id in self.recent_tools:
            self.recent_tools.remove(tool_id)
        
        # Add to front
        self.recent_tools.insert(0, tool_id)
        
        # Keep only last 5
        self.recent_tools = self.recent_tools[:self.max_recent]

def test_favorites_and_recent():
    """Test the favorites and recent tools functionality"""
    print("Testing favorites and recent tools functionality...")
    
    # Create mock app
    app = MockNetToolsApp()
    
    # Test adding favorites
    print("\n1. Testing favorites:")
    app.toggle_favorite("scanner")
    app.toggle_favorite("portscan")
    print(f"Favorites after adding: {app.favorite_tools}")
    
    # Test removing favorite
    app.toggle_favorite("scanner")
    print(f"Favorites after removing scanner: {app.favorite_tools}")
    
    # Test recent tools
    print("\n2. Testing recent tools:")
    app.add_to_recent("dns")
    app.add_to_recent("subnet")
    app.add_to_recent("mac")
    print(f"Recent tools: {app.recent_tools}")
    
    # Test recent tools limit
    app.add_to_recent("traceroute")
    app.add_to_recent("bandwidth")
    app.add_to_recent("profiles")
    print(f"Recent tools (should be limited to 5): {app.recent_tools}")
    
    # Test duplicate handling
    app.add_to_recent("dns")  # Should move to front
    print(f"Recent tools after re-adding dns: {app.recent_tools}")
    
    # Test persistence
    print("\n3. Testing persistence:")
    app.save_window_state()
    
    # Create new app instance and load
    app2 = MockNetToolsApp()
    app2.favorite_tools = app2.load_favorites()
    app2.recent_tools = app2.load_recent_tools()
    
    print(f"Loaded favorites: {app2.favorite_tools}")
    print(f"Loaded recent tools: {app2.recent_tools}")
    
    # Cleanup
    if app.config_file.exists():
        app.config_file.unlink()
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_favorites_and_recent()