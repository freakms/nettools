"""
Hash Generator UI - Generate MD5, SHA1, SHA256, SHA512 hashes
"""

import customtkinter as ctk
import hashlib
import threading
import os
from design_constants import COLORS, SPACING, FONTS
from ui_components import StyledCard, StyledButton, StyledEntry, SubTitle
from tkinter import filedialog


class HashGeneratorUI:
    """Hash Generator Tool"""
    
    ALGORITHMS = ['MD5', 'SHA1', 'SHA256', 'SHA512', 'SHA3-256', 'BLAKE2b']
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.create_content()
    
    def create_content(self):
        """Create the Hash Generator page"""
        scrollable = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title = ctk.CTkLabel(
            scrollable,
            text="#️⃣ Hash Generator",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title.pack(anchor="w", pady=(0, SPACING['xs']))
        
        subtitle = SubTitle(scrollable, text="Generate cryptographic hashes for text and files")
        subtitle.pack(anchor="w", pady=(0, SPACING['lg']))
        
        # Mode selection
        mode_card = StyledCard(scrollable, variant="elevated")
        mode_card.pack(fill="x", pady=(0, SPACING['md']))
        
        mode_title = ctk.CTkLabel(
            mode_card, text="🎯 Input Mode",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        )
        mode_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        mode_frame = ctk.CTkFrame(mode_card, fg_color="transparent")
        mode_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.mode_var = ctk.StringVar(value="text")
        
        ctk.CTkRadioButton(
            mode_frame, text="Text Input", variable=self.mode_var, value="text",
            command=self._on_mode_change, fg_color=COLORS['electric_violet']
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkRadioButton(
            mode_frame, text="File Input", variable=self.mode_var, value="file",
            command=self._on_mode_change, fg_color=COLORS['electric_violet']
        ).pack(side="left")
        
        # Text input card
        self.text_card = StyledCard(scrollable, variant="elevated")
        self.text_card.pack(fill="x", pady=(0, SPACING['md']))
        
        text_title = ctk.CTkLabel(
            self.text_card, text="📝 Text Input",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        )
        text_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        self.text_input = ctk.CTkTextbox(
            self.text_card, height=100,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=COLORS.get('bg_card', ("gray95", "gray20"))
        )
        self.text_input.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        self.text_input.insert("1.0", "Enter text to hash...")
        self.text_input.bind('<FocusIn>', lambda e: self._clear_placeholder())
        
        # File input card (hidden by default)
        self.file_card = StyledCard(scrollable, variant="elevated")
        
        file_title = ctk.CTkLabel(
            self.file_card, text="📁 File Input",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        )
        file_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        file_frame = ctk.CTkFrame(self.file_card, fg_color="transparent")
        file_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.file_label = ctk.CTkLabel(
            file_frame, text="No file selected",
            font=ctk.CTkFont(size=12), text_color=COLORS['text_secondary']
        )
        self.file_label.pack(side="left", fill="x", expand=True)
        
        self.browse_btn = StyledButton(
            file_frame, text="📂 Browse",
            command=self.browse_file, variant="secondary"
        )
        self.browse_btn.pack(side="right")
        
        self.selected_file = None
        
        # Algorithm selection
        algo_card = StyledCard(scrollable, variant="elevated")
        algo_card.pack(fill="x", pady=(0, SPACING['md']))
        
        algo_title = ctk.CTkLabel(
            algo_card, text="🔐 Hash Algorithms",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        )
        algo_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        algo_frame = ctk.CTkFrame(algo_card, fg_color="transparent")
        algo_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.algo_vars = {}
        for i, algo in enumerate(self.ALGORITHMS):
            var = ctk.BooleanVar(value=(algo in ['MD5', 'SHA256']))
            self.algo_vars[algo] = var
            ctk.CTkCheckBox(
                algo_frame, text=algo, variable=var,
                font=ctk.CTkFont(size=12), fg_color=COLORS['electric_violet']
            ).grid(row=i//3, column=i%3, padx=10, pady=3, sticky="w")
        
        # Generate button
        btn_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        btn_frame.pack(fill="x", pady=SPACING['md'])
        
        self.generate_btn = StyledButton(
            btn_frame, text="🔄 Generate Hashes",
            command=self.generate_hashes, variant="primary", size="large"
        )
        self.generate_btn.pack()
        
        # Results
        results_card = StyledCard(scrollable, variant="elevated")
        results_card.pack(fill="both", expand=True, pady=(0, SPACING['md']))
        
        results_title = ctk.CTkLabel(
            results_card, text="📊 Hash Results",
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        )
        results_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        self.results_text = ctk.CTkTextbox(
            results_card, height=250,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS.get('bg_card', ("gray95", "gray20"))
        )
        self.results_text.pack(fill="both", expand=True, padx=SPACING['md'], pady=(0, SPACING['md']))
    
    def _on_mode_change(self):
        """Handle mode change"""
        if self.mode_var.get() == "text":
            self.file_card.pack_forget()
            self.text_card.pack(fill="x", pady=(0, SPACING['md']), after=self.text_card.master.winfo_children()[1])
        else:
            self.text_card.pack_forget()
            self.file_card.pack(fill="x", pady=(0, SPACING['md']), after=self.file_card.master.winfo_children()[1])
    
    def _clear_placeholder(self):
        """Clear placeholder text"""
        if self.text_input.get("1.0", "end-1c") == "Enter text to hash...":
            self.text_input.delete("1.0", "end")
    
    def browse_file(self):
        """Browse for file"""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            size = os.path.getsize(file_path)
            size_str = self._format_size(size)
            self.file_label.configure(text=f"{filename} ({size_str})")
    
    def _format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def generate_hashes(self):
        """Generate hashes"""
        selected_algos = [algo for algo, var in self.algo_vars.items() if var.get()]
        
        if not selected_algos:
            self.app.show_toast("Please select at least one algorithm", "warning")
            return
        
        self.generate_btn.configure(state="disabled", text="⏳ Generating...")
        
        thread = threading.Thread(target=self._do_generate, args=(selected_algos,), daemon=True)
        thread.start()
    
    def _do_generate(self, algorithms):
        """Generate hashes in background"""
        try:
            results = []
            
            if self.mode_var.get() == "text":
                text = self.text_input.get("1.0", "end-1c")
                if text == "Enter text to hash...":
                    text = ""
                data = text.encode('utf-8')
                source = f"Text ({len(data)} bytes)"
            else:
                if not self.selected_file:
                    self.app.after(0, lambda: self.app.show_toast("Please select a file", "warning"))
                    return
                with open(self.selected_file, 'rb') as f:
                    data = f.read()
                source = f"File: {os.path.basename(self.selected_file)} ({self._format_size(len(data))})"
            
            results.append("═" * 60)
            results.append(f"  HASH RESULTS - {source}")
            results.append("═" * 60)
            results.append("")
            
            for algo in algorithms:
                algo_lower = algo.lower().replace('-', '_')
                if algo_lower == 'blake2b':
                    h = hashlib.blake2b(data)
                elif algo_lower == 'sha3_256':
                    h = hashlib.sha3_256(data)
                else:
                    h = hashlib.new(algo_lower, data)
                
                hash_value = h.hexdigest()
                results.append(f"  {algo}:")
                results.append(f"  {hash_value}")
                results.append("")
            
            result_text = "\n".join(results)
            self.app.after(0, lambda: self._show_results(result_text))
            
        except Exception as e:
            self.app.after(0, lambda: self._show_results(f"Error: {str(e)}"))
        
        finally:
            self.app.after(0, lambda: self.generate_btn.configure(state="normal", text="🔄 Generate Hashes"))
    
    def _show_results(self, results):
        """Display results"""
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", results)
        self.app.show_toast("Hashes generated", "success")
