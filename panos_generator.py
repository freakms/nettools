# PAN-OS Command Generator
# Author: freakms
# Company: ich schwoere feierlich ich bin ein tunichtgut
# Version: 1.0.0
# Standalone application for generating PAN-OS CLI commands

import customtkinter as ctk
import re
from tkinter import filedialog, messagebox
from design_constants import COLORS, SPACING, RADIUS, FONTS, BUTTON_SIZES
from ui_components import (
    StyledCard, StyledButton, StyledEntry, SectionTitle, SubTitle,
    InfoBox
)


def validate_ip_address(ip):
    """Validate IP address or network with CIDR notation"""
    # Pattern for IP with optional CIDR
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(\/(\d{1,2}))?$'
    match = re.match(pattern, ip)
    
    if not match:
        return False
    
    # Validate each octet is 0-255
    octets = [int(match.group(i)) for i in range(1, 5)]
    if any(octet > 255 for octet in octets):
        return False
    
    # Validate CIDR prefix if present
    if match.group(5):  # Has CIDR
        cidr = int(match.group(6))
        if cidr > 32:
            return False
    
    return True


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_NAME = "PAN-OS Generator"
APP_VERSION = "1.0.0"


class PANOSGenerator(ctk.CTk):
    """PAN-OS CLI Command Generator Application"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1200x800")
        
        # Commands storage
        self.commands = []
        self.generated_names_data = []
        
        # Create UI
        self.create_header()
        self.create_tabs()
        self.create_output_panel()
        
    def create_header(self):
        """Create application header"""
        header = ctk.CTkFrame(self, height=80, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Logo and title
        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.pack(side="left", padx=SPACING['lg'], pady=SPACING['md'])
        
        title = ctk.CTkLabel(
            logo_frame,
            text="🛡️ PAN-OS Generator",
            font=ctk.CTkFont(size=FONTS['title'], weight="bold")
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            logo_frame,
            text="Command Generator for PAN-OS 11.1",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary']
        )
        subtitle.pack(anchor="w")
        
    def create_tabs(self):
        """Create main tabbed interface"""
        # Main container with two columns
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Left side - Input forms
        left_frame = ctk.CTkFrame(main_container)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, SPACING['md']))
        
        # Tab buttons
        tab_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        tab_frame.pack(fill="x", pady=(0, SPACING['md']))
        
        self.name_gen_btn = StyledButton(
            tab_frame,
            text="🎯 Name Generator",
            command=lambda: self.switch_tab("name"),
            size="medium",
            variant="primary"
        )
        self.name_gen_btn.pack(side="left", padx=(0, SPACING['xs']))
        
        self.addr_gen_btn = StyledButton(
            tab_frame,
            text="🌐 Address Objects",
            command=lambda: self.switch_tab("address"),
            size="medium",
            variant="neutral"
        )
        self.addr_gen_btn.pack(side="left")
        
        # Tab content area
        self.tab_content = ctk.CTkFrame(left_frame)
        self.tab_content.pack(fill="both", expand=True)
        
        # Create tabs
        self.create_name_generator_tab()
        self.create_address_generator_tab()
        
        # Show name generator by default
        self.current_tab = "name"
        self.name_gen_tab.pack(fill="both", expand=True)
        
    def switch_tab(self, tab_name):
        """Switch between tabs"""
        # Hide all tabs
        self.name_gen_tab.pack_forget()
        self.addr_gen_tab.pack_forget()
        
        # Update button styles
        if tab_name == "name":
            self.name_gen_btn.configure(fg_color=COLORS['primary'])
            self.addr_gen_btn.configure(fg_color=COLORS['neutral'])
            self.name_gen_tab.pack(fill="both", expand=True)
        else:
            self.name_gen_btn.configure(fg_color=COLORS['neutral'])
            self.addr_gen_btn.configure(fg_color=COLORS['primary'])
            self.addr_gen_tab.pack(fill="both", expand=True)
        
        self.current_tab = tab_name
    
    def create_name_generator_tab(self):
        """Create Name Generator tab"""
        self.name_gen_tab = ctk.CTkScrollableFrame(self.tab_content)
        
        # Card
        card = StyledCard(self.name_gen_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        # Title
        title = SectionTitle(card, text="Address Name Generator")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(
            card,
            text="Generate address object names from base names and IPs, then create CLI commands"
        )
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Step 1
        step1_label = ctk.CTkLabel(
            card,
            text="Step 1: Input Data",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold")
        )
        step1_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['sm']))
        
        # Base Names
        name_label = ctk.CTkLabel(
            card,
            text="Base Names (one per line):",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['xs']))
        
        self.gen_names = ctk.CTkTextbox(
            card,
            height=120,
            font=ctk.CTkFont(size=FONTS['body'], family="Consolas")
        )
        self.gen_names.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        self.gen_names.insert("1.0", "Server1\nServer2\nWebServer\nAppServer\nDBServer")
        
        # IP Addresses
        ip_label = ctk.CTkLabel(
            card,
            text="IP Addresses/Netmasks (one per line):",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        ip_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.gen_ips = ctk.CTkTextbox(
            card,
            height=120,
            font=ctk.CTkFont(size=FONTS['body'], family="Consolas")
        )
        self.gen_ips.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        self.gen_ips.insert("1.0", "192.168.1.10\n192.168.1.20\n10.0.0.10\n10.0.0.20\n10.0.0.30")
        
        # Options row
        options_frame = ctk.CTkFrame(card, fg_color="transparent")
        options_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Separator
        sep_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        sep_frame.pack(side="left", fill="x", expand=True, padx=(0, SPACING['sm']))
        
        sep_label = ctk.CTkLabel(sep_frame, text="Separator:", font=ctk.CTkFont(size=FONTS['body']))
        sep_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.gen_separator = ctk.CTkComboBox(
            sep_frame,
            values=["_ (Underscore)", "- (Dash)", ". (Dot)"],
            state="readonly"
        )
        self.gen_separator.set("_ (Underscore)")
        self.gen_separator.pack(fill="x")
        
        # Format
        format_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        format_frame.pack(side="left", fill="x", expand=True)
        
        format_label = ctk.CTkLabel(format_frame, text="Format:", font=ctk.CTkFont(size=FONTS['body']))
        format_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.gen_format = ctk.CTkComboBox(
            format_frame,
            values=["Name_IP", "IP_Name", "Name Only", "Custom"],
            state="readonly",
            command=self.on_format_change
        )
        self.gen_format.set("Name_IP")
        self.gen_format.pack(fill="x")
        
        # Custom format (hidden by default)
        self.custom_format_frame = ctk.CTkFrame(card, fg_color="transparent")
        
        custom_label = ctk.CTkLabel(
            self.custom_format_frame,
            text="Custom Format Pattern:",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        custom_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.gen_custom = StyledEntry(
            self.custom_format_frame,
            placeholder_text="e.g., {name}-{ip} or Host_{name}_{ip}"
        )
        self.gen_custom.pack(fill="x", pady=(0, SPACING['xs']))
        
        custom_help = SubTitle(
            self.custom_format_frame,
            text="Use {name} for base name and {ip} for IP address"
        )
        custom_help.pack(anchor="w")
        
        # Generate Names button
        gen_names_btn = StyledButton(
            card,
            text="🎯 Generate Object Names",
            command=self.generate_names,
            size="large",
            variant="primary"
        )
        gen_names_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
        
        # Preview section (hidden initially)
        self.preview_frame = ctk.CTkFrame(card, fg_color="transparent")
        
        preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Generated Names Preview:",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold")
        )
        preview_label.pack(anchor="w", pady=(0, SPACING['sm']))
        
        self.preview_text = ctk.CTkTextbox(
            self.preview_frame,
            height=150,
            font=ctk.CTkFont(size=FONTS['small'], family="Consolas")
        )
        self.preview_text.pack(fill="x", pady=(0, SPACING['md']))
        
        # Step 2 (hidden initially)
        self.step2_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        
        step2_label = ctk.CTkLabel(
            self.step2_frame,
            text="Step 2: Generate CLI Commands",
            font=ctk.CTkFont(size=FONTS['subheading'], weight="bold")
        )
        step2_label.pack(anchor="w", pady=(0, SPACING['sm']))
        
        self.gen_shared = ctk.CTkCheckBox(
            self.step2_frame,
            text="Create as Shared Objects (available to all virtual systems)",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        self.gen_shared.select()
        self.gen_shared.pack(anchor="w", pady=(0, SPACING['md']))
        
        gen_commands_btn = StyledButton(
            self.step2_frame,
            text="💻 Generate CLI Commands",
            command=self.generate_from_names,
            size="large",
            variant="success"
        )
        gen_commands_btn.pack(fill="x")
        
        # Help box
        help_box = InfoBox(
            card,
            message="💡 How it Works:\n"
                   "• Both lists must have the same number of lines\n"
                   "• Each name pairs with corresponding IP (line by line)\n"
                   "• Choose format to create object names automatically\n"
                   "• Example: 'Server1' + '192.168.1.10' → 'Server1_192_168_1_10'",
            box_type="info"
        )
        help_box.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['lg']))
    
    def create_address_generator_tab(self):
        """Create Address Object Generator tab"""
        self.addr_gen_tab = ctk.CTkScrollableFrame(self.tab_content)
        
        # Card
        card = StyledCard(self.addr_gen_tab)
        card.pack(fill="both", expand=True, padx=SPACING['xs'], pady=SPACING['xs'])
        
        # Title
        title = SectionTitle(card, text="Address Object Set Command Generator")
        title.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))
        
        desc = SubTitle(
            card,
            text="Create multiple address objects quickly from names and IPs"
        )
        desc.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        # Object Names
        name_label = ctk.CTkLabel(
            card,
            text="Object Names (one per line):",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        name_label.pack(anchor="w", padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['xs']))
        
        self.addr_names = ctk.CTkTextbox(
            card,
            height=150,
            font=ctk.CTkFont(size=FONTS['body'], family="Consolas")
        )
        self.addr_names.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        self.addr_names.insert("1.0", "Server1\nServer2\nServer3\nWebServer\nDBServer")
        
        # IP Addresses
        ip_label = ctk.CTkLabel(
            card,
            text="IP Addresses/Netmasks (one per line):",
            font=ctk.CTkFont(size=FONTS['body'], weight="bold")
        )
        ip_label.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['xs']))
        
        self.addr_ips = ctk.CTkTextbox(
            card,
            height=150,
            font=ctk.CTkFont(size=FONTS['body'], family="Consolas")
        )
        self.addr_ips.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        self.addr_ips.insert("1.0", "192.168.1.10\n192.168.1.20/32\n192.168.1.0/24\n10.0.0.10\n10.0.0.20")
        
        # Options
        self.addr_shared = ctk.CTkCheckBox(
            card,
            text="Create as Shared Objects (available to all virtual systems)",
            font=ctk.CTkFont(size=FONTS['body'])
        )
        self.addr_shared.select()
        self.addr_shared.pack(anchor="w", padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Generate button
        gen_btn = StyledButton(
            card,
            text="💻 Generate Commands",
            command=self.generate_address_objects,
            size="large",
            variant="primary"
        )
        gen_btn.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['md'], SPACING['lg']))
        
        # Help box
        help_box = InfoBox(
            card,
            message="💡 Tips:\n"
                   "• Both lists must have the same number of lines\n"
                   "• Each name pairs with the corresponding IP\n"
                   "• Supports CIDR notation (e.g., 192.168.1.0/24)\n"
                   "• Example: Line 1 name → Line 1 IP",
            box_type="info"
        )
        help_box.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
    
    def create_output_panel(self):
        """Create command output panel"""
        # Right side - Output
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.pack(side="right", fill="both", expand=False, padx=(0, SPACING['lg']), pady=SPACING['lg'])
        self.output_frame.configure(width=400)
        
        output_card = StyledCard(self.output_frame)
        output_card.pack(fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(output_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        
        title = ctk.CTkLabel(
            title_frame,
            text="💻 Command Output",
            font=ctk.CTkFont(size=FONTS['heading'], weight="bold")
        )
        title.pack(anchor="w")
        
        self.cmd_count = ctk.CTkLabel(
            title_frame,
            text="0 commands generated",
            font=ctk.CTkFont(size=FONTS['small']),
            text_color=COLORS['text_secondary']
        )
        self.cmd_count.pack(anchor="w")
        
        clear_btn = StyledButton(
            header_frame,
            text="🗑️",
            command=self.clear_commands,
            size="small",
            variant="neutral"
        )
        clear_btn.pack(side="right")
        
        # Commands list
        self.commands_list = ctk.CTkScrollableFrame(output_card, height=400)
        self.commands_list.pack(fill="both", expand=True, padx=SPACING['lg'], pady=(0, SPACING['md']))
        
        # Empty state
        self.empty_state = ctk.CTkFrame(self.commands_list, fg_color="transparent")
        self.empty_state.pack(fill="both", expand=True, pady=SPACING['xl'])
        
        empty_text = ctk.CTkLabel(
            self.empty_state,
            text="📋\n\nNo commands generated yet\n\nFill out the form to generate CLI commands",
            font=ctk.CTkFont(size=FONTS['body']),
            text_color=COLORS['text_secondary']
        )
        empty_text.pack(expand=True)
        
        # Action buttons
        self.action_frame = ctk.CTkFrame(output_card, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        self.action_frame.pack_forget()  # Hidden initially
        
        copy_btn = StyledButton(
            self.action_frame,
            text="📋 Copy All",
            command=self.copy_commands,
            size="medium",
            variant="neutral"
        )
        copy_btn.pack(fill="x", pady=(0, SPACING['xs']))
        
        download_btn = StyledButton(
            self.action_frame,
            text="⬇️ Download",
            command=self.download_commands,
            size="medium",
            variant="primary"
        )
        download_btn.pack(fill="x")
    
    def on_format_change(self, choice):
        """Show/hide custom format input"""
        if choice == "Custom":
            self.custom_format_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['md']))
        else:
            self.custom_format_frame.pack_forget()
    
    def generate_names(self):
        """Generate object names from base names and IPs"""
        names_text = self.gen_names.get("1.0", "end").strip()
        ips_text = self.gen_ips.get("1.0", "end").strip()
        
        if not names_text or not ips_text:
            messagebox.showerror("Error", "Please fill in both base names and IPs")
            return
        
        names = [n.strip() for n in names_text.split('\n') if n.strip()]
        ips = [i.strip() for i in ips_text.split('\n') if i.strip()]
        
        if len(names) != len(ips):
            messagebox.showerror("Error", f"Number of names ({len(names)}) doesn't match number of IPs ({len(ips)})")
            return
        
        # Get separator
        sep_map = {"_ (Underscore)": "_", "- (Dash)": "-", ". (Dot)": "."}
        separator = sep_map.get(self.gen_separator.get(), "_")
        
        # Get format
        format_choice = self.gen_format.get()
        
        self.generated_names_data = []
        
        for i in range(len(names)):
            name = names[i]
            ip = ips[i]
            
            # Validate IP
            if not validate_ip_address(ip):
                messagebox.showerror("Error", f"Invalid IP address or format: {ip}\nExpected format: 192.168.1.10 or 192.168.1.0/24")
                return
            
            # Generate name based on format
            if format_choice == "Name_IP":
                generated_name = f"{name}{separator}{ip.replace('.', separator).replace('/', separator)}"
            elif format_choice == "IP_Name":
                generated_name = f"{ip.replace('.', separator).replace('/', separator)}{separator}{name}"
            elif format_choice == "Name Only":
                generated_name = name
            elif format_choice == "Custom":
                custom_pattern = self.gen_custom.get().strip()
                if not custom_pattern:
                    messagebox.showerror("Error", "Please provide a custom format pattern")
                    return
                generated_name = custom_pattern.replace('{name}', name).replace('{ip}', ip.replace('.', separator).replace('/', separator))
            else:
                generated_name = f"{name}{separator}{ip.replace('.', separator).replace('/', separator)}"
            
            self.generated_names_data.append({
                'name': name,
                'ip': ip,
                'generated_name': generated_name
            })
        
        # Show preview
        preview_text = '\n'.join([f"{item['generated_name']} → {item['ip']}" for item in self.generated_names_data])
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", preview_text)
        
        # Show preview and step 2
        self.preview_frame.pack(fill="x", padx=SPACING['lg'], pady=(SPACING['lg'], 0))
        self.step2_frame.pack(fill="x", pady=(SPACING['md'], 0))
        
        messagebox.showinfo("Success", f"Generated {len(self.generated_names_data)} object names!")
    
    def generate_from_names(self):
        """Generate CLI commands from generated names"""
        if not self.generated_names_data:
            messagebox.showerror("Error", "Please generate names first")
            return
        
        is_shared = self.gen_shared.get()
        base_path = "shared" if is_shared else "vsys vsys1"
        
        commands = []
        for item in self.generated_names_data:
            cmd = f'set {base_path} address "{item["generated_name"]}" ip-netmask {item["ip"]}'
            commands.append(cmd)
        
        full_cmd = "configure\n" + '\n'.join(commands) + "\ncommit"
        self.add_command(full_cmd)
        messagebox.showinfo("Success", f"Generated {len(commands)} address object commands!")
    
    def generate_address_objects(self):
        """Generate address object commands"""
        names_text = self.addr_names.get("1.0", "end").strip()
        ips_text = self.addr_ips.get("1.0", "end").strip()
        
        if not names_text or not ips_text:
            messagebox.showerror("Error", "Please fill in both names and IPs")
            return
        
        names = [n.strip() for n in names_text.split('\n') if n.strip()]
        ips = [i.strip() for i in ips_text.split('\n') if i.strip()]
        
        if len(names) != len(ips):
            messagebox.showerror("Error", f"Number of names ({len(names)}) doesn't match number of IPs ({len(ips)})")
            return
        
        is_shared = self.addr_shared.get()
        base_path = "shared" if is_shared else "vsys vsys1"
        
        commands = []
        for i in range(len(names)):
            name = names[i]
            ip = ips[i]
            
            # Validate IP
            if not validate_ip_address(ip):
                messagebox.showerror("Error", f"Invalid IP address or format: {ip}\nExpected format: 192.168.1.10 or 192.168.1.0/24")
                return
            
            cmd = f'set {base_path} address "{name}" ip-netmask {ip}'
            commands.append(cmd)
        
        full_cmd = "configure\n" + '\n'.join(commands) + "\ncommit"
        self.add_command(full_cmd)
        messagebox.showinfo("Success", f"Generated {len(commands)} address object commands!")
    
    def add_command(self, cmd):
        """Add command to output"""
        self.commands.append(cmd)
        self.render_commands()
    
    def render_commands(self):
        """Render commands in output panel"""
        # Clear existing
        for widget in self.commands_list.winfo_children():
            widget.destroy()
        
        # Update count
        self.cmd_count.configure(text=f"{len(self.commands)} command{'s' if len(self.commands) != 1 else ''} generated")
        
        if len(self.commands) == 0:
            self.empty_state = ctk.CTkFrame(self.commands_list, fg_color="transparent")
            self.empty_state.pack(fill="both", expand=True, pady=SPACING['xl'])
            
            empty_text = ctk.CTkLabel(
                self.empty_state,
                text="📋\n\nNo commands generated yet\n\nFill out the form to generate CLI commands",
                font=ctk.CTkFont(size=FONTS['body']),
                text_color=COLORS['text_secondary']
            )
            empty_text.pack(expand=True)
            self.action_frame.pack_forget()
            return
        
        self.action_frame.pack(fill="x", padx=SPACING['lg'], pady=(0, SPACING['lg']))
        
        for i, cmd in enumerate(self.commands):
            cmd_frame = ctk.CTkFrame(self.commands_list, fg_color=COLORS['bg_secondary'])
            cmd_frame.pack(fill="x", pady=(0, SPACING['xs']))
            
            cmd_text = ctk.CTkTextbox(
                cmd_frame,
                height=100,
                font=ctk.CTkFont(size=FONTS['tiny'], family="Consolas"),
                wrap="none"
            )
            cmd_text.pack(fill="both", expand=True, padx=SPACING['sm'], pady=SPACING['sm'])
            cmd_text.insert("1.0", cmd)
            cmd_text.configure(state="disabled")
            
            # Remove button
            remove_btn = StyledButton(
                cmd_frame,
                text="✗",
                command=lambda idx=i: self.remove_command(idx),
                size="small",
                variant="danger"
            )
            remove_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-SPACING['sm'], y=SPACING['sm'])
    
    def remove_command(self, index):
        """Remove a command"""
        if 0 <= index < len(self.commands):
            self.commands.pop(index)
            self.render_commands()
    
    def clear_commands(self):
        """Clear all commands"""
        if self.commands and messagebox.askyesno("Clear Commands", "Clear all generated commands?"):
            self.commands = []
            self.render_commands()
    
    def copy_commands(self):
        """Copy all commands to clipboard"""
        if not self.commands:
            return
        
        text = '\n\n'.join(self.commands)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Success", "Commands copied to clipboard!")
    
    def download_commands(self):
        """Download commands to file"""
        if not self.commands:
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"panos-commands.txt"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(self.commands))
                messagebox.showinfo("Success", f"Commands saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")


def main():
    """Main entry point"""
    app = PANOSGenerator()
    app.mainloop()


if __name__ == "__main__":
    main()
