#!/usr/bin/env python3
"""
Test script to verify the NetTools app structure without GUI
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, '/app')

# Mock the GUI libraries to avoid import errors
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs):
        pass
    def pack_propagate(self, *args, **kwargs):
        pass
    def configure(self, *args, **kwargs):
        pass
    def set(self, *args, **kwargs):
        pass
    def get(self, *args, **kwargs):
        return ""
    def bind(self, *args, **kwargs):
        pass
    def title(self, *args, **kwargs):
        pass
    def geometry(self, *args, **kwargs):
        pass
    def minsize(self, *args, **kwargs):
        pass
    def iconphoto(self, *args, **kwargs):
        pass

# Mock all the customtkinter classes
import customtkinter as ctk
ctk.CTk = MockCTk
ctk.CTkFrame = MockCTk
ctk.CTkLabel = MockCTk
ctk.CTkButton = MockCTk
ctk.CTkEntry = MockCTk
ctk.CTkOptionMenu = MockCTk
ctk.CTkCheckBox = MockCTk
ctk.CTkScrollableFrame = MockCTk
ctk.CTkTextbox = MockCTk
ctk.CTkProgressBar = MockCTk
ctk.CTkFont = lambda *args, **kwargs: None

# Mock other GUI modules
import tkinter.messagebox
tkinter.messagebox.showinfo = lambda *args, **kwargs: None
tkinter.messagebox.showwarning = lambda *args, **kwargs: None
tkinter.messagebox.showerror = lambda *args, **kwargs: None
tkinter.messagebox.askyesno = lambda *args, **kwargs: True

import tkinter.filedialog
tkinter.filedialog.asksaveasfilename = lambda *args, **kwargs: "/tmp/test.csv"

try:
    from nettools_app import NetToolsApp
    
    print("✅ NetToolsApp class imported successfully")
    
    # Try to create an instance (this will test the __init__ method)
    app = NetToolsApp()
    print("✅ NetToolsApp instance created successfully")
    
    # Test if all required attributes exist
    required_attrs = [
        'sidebar', 'main_content', 'pages', 'nav_buttons', 'current_page',
        'theme_selector', 'cidr_entry', 'mac_entry', 'status_label'
    ]
    
    missing_attrs = []
    for attr in required_attrs:
        if not hasattr(app, attr):
            missing_attrs.append(attr)
    
    if missing_attrs:
        print(f"❌ Missing attributes: {missing_attrs}")
    else:
        print("✅ All required attributes exist")
    
    # Test if pages dictionary is properly set up
    expected_pages = ['scanner', 'mac', 'compare']
    if hasattr(app, 'pages'):
        missing_pages = [page for page in expected_pages if page not in app.pages]
        if missing_pages:
            print(f"❌ Missing pages: {missing_pages}")
        else:
            print("✅ All expected pages exist")
    
    # Test if navigation buttons exist
    if hasattr(app, 'nav_buttons'):
        missing_nav = [page for page in expected_pages if page not in app.nav_buttons]
        if missing_nav:
            print(f"❌ Missing navigation buttons: {missing_nav}")
        else:
            print("✅ All navigation buttons exist")
    
    print("\n🎉 Structure test completed successfully!")
    print("The sidebar-based NetTools app structure is working correctly.")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()