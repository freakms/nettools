"""
MAC Formatter UI Module
Contains the MAC address formatter tool page implementation
"""

import customtkinter as ctk
from tkinter import messagebox
import re

from design_constants import COLORS, SPACING, RADIUS, FONTS
from ui_components import StyledCard, StyledButton, StyledEntry, SectionTitle
from tools.mac_formatter import MACFormatter


class MACFormatterUI:
    """MAC Formatter page UI implementation"""
    
    def __init__(self, app):
        """
        Initialize MAC Formatter UI
        
        Args:
            app: Reference to main NetToolsApp instance
        """
        self.app = app

    def create_content(self, parent):
        """Create MAC Formatter page content"""
        # Input section with styled card
        input_card = StyledCard(parent)
        input_card.pack(fill="x", padx=SPACING['lg'], pady=SPACING['lg'])
        
        mac_label = ctk.CTkLabel(
            input_card,
            text="Enter MAC Address:",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        mac_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        # Frame for MAC entry and history button
        mac_entry_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        mac_entry_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        self.mac_entry = StyledEntry(
            mac_entry_frame,
            placeholder_text="e.g., AA:BB:CC:DD:EE:FF or AABBCCDDEEFF"
        )
        self.mac_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING['xs']))
        self.mac_entry.bind('<KeyRelease>', self.update_mac_formats)
        
        # History button for MAC
        self.mac_history_btn = StyledButton(
            mac_entry_frame,
            text="⏱",
            size="small",
            variant="neutral",
            command=self.app.show_mac_history
        )
        self.mac_history_btn.pack(side="left")
        
        self.mac_warning_label = ctk.CTkLabel(
            input_card,
            text="",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['danger']
        )
        self.mac_warning_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        # Vendor information display
        self.vendor_label = ctk.CTkLabel(
            input_card,
            text="",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold"),
            text_color=COLORS['success']
        )
        self.vendor_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Scrollable content area for formats and commands
        self.mac_scrollable = ctk.CTkScrollableFrame(parent)
        self.mac_scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # MAC Formats section with styled card
        self.formats_frame = StyledCard(self.mac_scrollable)
        self.formats_frame.pack(fill="x", padx=SPACING['xs'], pady=(SPACING['md'], SPACING['lg']))
        
        formats_title = SectionTitle(
            self.formats_frame,
            text="Standard MAC Formats"
        )
        formats_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        format_labels = [
            "Format 1 (Plain):",
            "Format 2 (Colon):",
            "Format 3 (Dash-4):",
            "Format 4 (Dash-2):"
        ]
        
        self.app.format_entries = []
        for label_text in format_labels:
            row_frame = ctk.CTkFrame(self.formats_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
            
            label = ctk.CTkLabel(
                row_frame,
                text=label_text,
                width=150,
                anchor="w",
                font=ctk.CTkFont(size=FONTS['body'])
            )
            label.pack(side="left", padx=(0, SPACING['md']))
            
            entry = StyledEntry(row_frame)
            entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING['md']))
            entry.configure(state="readonly")
            self.app.format_entries.append(entry)
            
            copy_btn = StyledButton(
                row_frame,
                text="Copy",
                size="small",
                variant="neutral",
                command=lambda e=entry: self.copy_to_clipboard(e)
            )
            copy_btn.pack(side="left")
        
        # Switch Commands section with styled card
        self.commands_frame = StyledCard(self.mac_scrollable)
        self.commands_frame.pack(fill="x", padx=SPACING['xs'], pady=(0, SPACING['lg']))
        
        commands_title = SectionTitle(
            self.commands_frame,
            text="Switch Commands"
        )
        commands_title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        command_labels = [
            "EXTREME CLI:",
            "Huawei CLI:",
            "Huawei Access-User CLI:",
            "Dell CLI:"
        ]
        
        self.command_textboxes = []
        for label_text in command_labels:
            row_frame = ctk.CTkFrame(self.commands_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=SPACING['lg'], pady=SPACING['xs'])
            
            label = ctk.CTkLabel(
                row_frame,
                text=label_text,
                width=200,
                anchor="w",
                font=ctk.CTkFont(size=FONTS['body'])
            )
            label.pack(side="left", padx=(0, SPACING['md']))
            
            textbox = ctk.CTkTextbox(
                row_frame,
                height=35,
                wrap="word",
                font=ctk.CTkFont(size=FONTS['body']),
                corner_radius=RADIUS['medium']
            )
            textbox.pack(side="left", fill="x", expand=True, padx=(0, SPACING['md']))
            textbox.configure(state="disabled")
            self.command_textboxes.append(textbox)
            
            copy_btn = StyledButton(
                row_frame,
                text="Copy",
                size="small",
                variant="neutral",
                command=lambda tb=textbox: self.copy_textbox_to_clipboard(tb)
            )
            copy_btn.pack(side="left")
        
        # Add bottom padding
        padding_frame = ctk.CTkFrame(self.commands_frame, fg_color="transparent", height=SPACING['md'])
        padding_frame.pack()
        
        self.commands_visible = True
    
    def update_mac_formats(self, event=None):
        """Update MAC address formats"""
        mac_input = self.mac_entry.get()
        
        if not mac_input:
            self.mac_warning_label.configure(text="")
            self.vendor_label.configure(text="")
            for entry in self.app.format_entries:
                entry.configure(state="normal")
                entry.delete(0, 'end')
                entry.configure(state="readonly")
            for textbox in self.command_textboxes:
                textbox.configure(state="normal")
                textbox.delete("1.0", 'end')
                textbox.configure(state="disabled")
            return
        
        hex_mac, error = MACFormatter.validate_mac(mac_input)
        
        if error:
            self.mac_warning_label.configure(text=error)
            self.vendor_label.configure(text="")
            for entry in self.app.format_entries:
                entry.configure(state="normal")
                entry.delete(0, 'end')
                entry.configure(state="readonly")
            for textbox in self.command_textboxes:
                textbox.configure(state="normal")
                textbox.delete("1.0", 'end')
                textbox.configure(state="disabled")
            return
        
        self.mac_warning_label.configure(text="")
        
        # Lookup and display vendor
        vendor = self.app.lookup_vendor(hex_mac)
        if vendor and vendor != "Unknown Vendor":
            self.vendor_label.configure(text=f"🏢 Vendor: {vendor}")
        else:
            self.vendor_label.configure(text="🏢 Vendor: Unknown")
        
        # Save to history (only when valid)
        self.app.history.add_mac(hex_mac)
        
        # Update formats
        formats = MACFormatter.format_mac(hex_mac)
        format_values = [
            formats['plain'],
            formats['colon'],
            formats['dash_4'],
            formats['dash_2']
        ]
        
        for entry, value in zip(self.app.format_entries, format_values):
            entry.configure(state="normal")
            entry.delete(0, 'end')
            entry.insert(0, value)
            entry.configure(state="readonly")
        
        # Update commands
        commands = MACFormatter.generate_switch_commands(formats)
        command_values = [
            commands['EXTREME'],
            commands['Huawei'],
            commands['Huawei Access-User'],
            commands['Dell']
        ]
        
        for textbox, value in zip(self.command_textboxes, command_values):
            textbox.configure(state="normal")
            textbox.delete("1.0", 'end')
            textbox.insert("1.0", value)
            
            # Auto-adjust height based on content lines
            # Count newlines in text to determine height needed
            lines = value.count('\n') + 1
            if lines > 1:
                new_height = min(35 + (lines - 1) * 20, 80)  # Max 80px height
                textbox.configure(height=new_height)
            else:
                textbox.configure(height=35)  # Single line height
            
            textbox.configure(state="disabled")
    
    def copy_to_clipboard(self, entry):
        """Copy entry content to clipboard"""
        text = entry.get()
        if text:
            self.app.clipboard_clear()
            self.app.clipboard_append(text)
            self.status_label.configure(text="Copied to clipboard!")
            self.app.after(2000, lambda: self.status_label.configure(text="Ready."))
