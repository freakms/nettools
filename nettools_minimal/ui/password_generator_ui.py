"""
Password Generator UI - KeePassXC-style Password/Passphrase Generator
Provides secure password and passphrase generation with customizable options.
"""

import customtkinter as ctk
import secrets
import string
import math
from design_constants import COLORS, SPACING, FONTS
from ui_components import (
    StyledCard, StyledButton, StyledEntry, SubTitle, InfoBox, Tooltip
)

# Word list for passphrase generation (common English words)
WORD_LIST = [
    "apple", "banana", "cherry", "dragon", "eagle", "falcon", "guitar", "hammer",
    "island", "jungle", "kettle", "lemon", "marble", "needle", "orange", "pencil",
    "quantum", "rabbit", "silver", "thunder", "umbrella", "violet", "whisper", "xenon",
    "yellow", "zebra", "anchor", "beacon", "castle", "diamond", "engine", "forest",
    "garden", "harbor", "insect", "jacket", "kitten", "laptop", "magnet", "napkin",
    "octopus", "parrot", "quiver", "rocket", "sunset", "temple", "unique", "valley",
    "winter", "xylophone", "yogurt", "zephyr", "bridge", "camera", "desert", "eclipse",
    "flower", "glacier", "horizon", "ivory", "jasmine", "kingdom", "lantern", "meadow",
    "nebula", "ocean", "phoenix", "quarter", "rainbow", "shadow", "tornado", "utopia",
    "voyage", "warrior", "crystal", "dolphin", "emerald", "fantasy", "gravity", "harmony",
    "imagine", "journey", "kindred", "liberty", "mystery", "network", "orbital", "pioneer",
    "quality", "resolve", "silence", "triumph", "uniform", "venture", "wonder", "energy",
    "cosmic", "digital", "eternal", "freedom", "genesis", "hunter", "infinite", "justice",
    "knight", "legend", "momentum", "natural", "observe", "passion", "reflect", "spirit",
    "target", "upward", "virtual", "wisdom", "azure", "blaze", "cipher", "drift",
    "ember", "frost", "glow", "haze", "iron", "jade", "karma", "lunar", "maple",
    "nova", "onyx", "prism", "quest", "rapid", "spark", "titan", "ultra", "vivid",
    "wave", "apex", "bold", "calm", "dawn", "echo", "fable", "grace", "halo",
    "icon", "jewel", "key", "light", "mist", "north", "orbit", "pulse", "realm",
    "storm", "trace", "unity", "valor", "wind", "axiom", "brave", "cloud", "delta"
]


class PasswordGeneratorUI:
    """
    UI for Password/Passphrase Generator - KeePassXC style
    """
    
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.generated_password = ""
        self.create_content()
    
    def create_content(self):
        """Create the Password Generator page content"""
        # Scrollable content
        scrollable = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        title_label = ctk.CTkLabel(
            scrollable,
            text="🔐 Password Generator",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['electric_violet']
        )
        title_label.pack(anchor="w", pady=(0, SPACING['xs']))
        
        subtitle = SubTitle(
            scrollable,
            text="Generate secure passwords and passphrases with customizable options"
        )
        subtitle.pack(anchor="w", pady=(0, SPACING['lg']))
        
        # Main content - two columns
        main_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        
        # Left column - Options
        left_col = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, SPACING['md']))
        
        # Right column - Output
        right_col = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True)
        
        # === LEFT COLUMN: Options ===
        
        # Type Selection Card
        type_card = StyledCard(left_col, variant="elevated")
        type_card.pack(fill="x", pady=(0, SPACING['md']))
        
        type_title = ctk.CTkLabel(
            type_card,
            text="🎯 Generation Type",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        type_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        # Radio buttons for type
        self.gen_type_var = ctk.StringVar(value="password")
        
        type_frame = ctk.CTkFrame(type_card, fg_color="transparent")
        type_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.password_radio = ctk.CTkRadioButton(
            type_frame,
            text="Password (Random Characters)",
            variable=self.gen_type_var,
            value="password",
            command=self._on_type_change,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS['electric_violet'],
            hover_color=COLORS['electric_violet_hover']
        )
        self.password_radio.pack(anchor="w", pady=3)
        
        self.passphrase_radio = ctk.CTkRadioButton(
            type_frame,
            text="Passphrase (Random Words)",
            variable=self.gen_type_var,
            value="passphrase",
            command=self._on_type_change,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS['electric_violet'],
            hover_color=COLORS['electric_violet_hover']
        )
        self.passphrase_radio.pack(anchor="w", pady=3)
        
        # === PASSWORD OPTIONS ===
        self.password_options_card = StyledCard(left_col, variant="elevated")
        self.password_options_card.pack(fill="x", pady=(0, SPACING['md']))
        
        pw_title = ctk.CTkLabel(
            self.password_options_card,
            text="🔤 Character Options",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        pw_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        # Character type checkboxes
        char_frame = ctk.CTkFrame(self.password_options_card, fg_color="transparent")
        char_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
        
        self.use_uppercase = ctk.BooleanVar(value=True)
        self.use_lowercase = ctk.BooleanVar(value=True)
        self.use_numbers = ctk.BooleanVar(value=True)
        self.use_special = ctk.BooleanVar(value=True)
        self.use_extended = ctk.BooleanVar(value=False)
        self.exclude_ambiguous = ctk.BooleanVar(value=True)
        
        # Row 1
        row1 = ctk.CTkFrame(char_frame, fg_color="transparent")
        row1.pack(fill="x", pady=2)
        
        ctk.CTkCheckBox(
            row1, text="A-Z (Uppercase)", variable=self.use_uppercase,
            font=ctk.CTkFont(size=12), fg_color=COLORS['electric_violet'],
            command=self._update_preview
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkCheckBox(
            row1, text="a-z (Lowercase)", variable=self.use_lowercase,
            font=ctk.CTkFont(size=12), fg_color=COLORS['electric_violet'],
            command=self._update_preview
        ).pack(side="left")
        
        # Row 2
        row2 = ctk.CTkFrame(char_frame, fg_color="transparent")
        row2.pack(fill="x", pady=2)
        
        ctk.CTkCheckBox(
            row2, text="0-9 (Numbers)", variable=self.use_numbers,
            font=ctk.CTkFont(size=12), fg_color=COLORS['electric_violet'],
            command=self._update_preview
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkCheckBox(
            row2, text="!@#$ (Special)", variable=self.use_special,
            font=ctk.CTkFont(size=12), fg_color=COLORS['electric_violet'],
            command=self._update_preview
        ).pack(side="left")
        
        # Row 3
        row3 = ctk.CTkFrame(char_frame, fg_color="transparent")
        row3.pack(fill="x", pady=2)
        
        ctk.CTkCheckBox(
            row3, text="Extended ASCII (äöü)", variable=self.use_extended,
            font=ctk.CTkFont(size=12), fg_color=COLORS['electric_violet'],
            command=self._update_preview
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkCheckBox(
            row3, text="Exclude Ambiguous (0O1lI)", variable=self.exclude_ambiguous,
            font=ctk.CTkFont(size=12), fg_color=COLORS['electric_violet'],
            command=self._update_preview
        ).pack(side="left")
        
        # Custom characters
        custom_frame = ctk.CTkFrame(self.password_options_card, fg_color="transparent")
        custom_frame.pack(fill="x", padx=SPACING['md'], pady=(SPACING['sm'], SPACING['sm']))
        
        ctk.CTkLabel(
            custom_frame, text="Custom Characters:", 
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 10))
        
        self.custom_chars_entry = StyledEntry(custom_frame, placeholder_text="Add extra characters...")
        self.custom_chars_entry.pack(side="left", fill="x", expand=True)
        
        # Password length slider
        length_frame = ctk.CTkFrame(self.password_options_card, fg_color="transparent")
        length_frame.pack(fill="x", padx=SPACING['md'], pady=(SPACING['sm'], SPACING['md']))
        
        length_label_frame = ctk.CTkFrame(length_frame, fg_color="transparent")
        length_label_frame.pack(fill="x")
        
        ctk.CTkLabel(
            length_label_frame, text="Password Length:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left")
        
        self.pw_length_label = ctk.CTkLabel(
            length_label_frame, text="20",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['neon_cyan']
        )
        self.pw_length_label.pack(side="right")
        
        self.pw_length_slider = ctk.CTkSlider(
            length_frame,
            from_=4, to=128,
            number_of_steps=124,
            command=self._on_pw_length_change,
            fg_color=COLORS.get('bg_card', ("gray80", "gray30")),
            progress_color=COLORS['electric_violet'],
            button_color=COLORS['neon_cyan']
        )
        self.pw_length_slider.set(20)
        self.pw_length_slider.pack(fill="x", pady=(5, 0))
        
        # === PASSPHRASE OPTIONS ===
        self.passphrase_options_card = StyledCard(left_col, variant="elevated")
        # Initially hidden
        
        pp_title = ctk.CTkLabel(
            self.passphrase_options_card,
            text="📝 Passphrase Options",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        pp_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        # Word count slider
        word_frame = ctk.CTkFrame(self.passphrase_options_card, fg_color="transparent")
        word_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
        
        word_label_frame = ctk.CTkFrame(word_frame, fg_color="transparent")
        word_label_frame.pack(fill="x")
        
        ctk.CTkLabel(
            word_label_frame, text="Number of Words:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left")
        
        self.word_count_label = ctk.CTkLabel(
            word_label_frame, text="5",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['neon_cyan']
        )
        self.word_count_label.pack(side="right")
        
        self.word_count_slider = ctk.CTkSlider(
            word_frame,
            from_=3, to=12,
            number_of_steps=9,
            command=self._on_word_count_change,
            fg_color=COLORS.get('bg_card', ("gray80", "gray30")),
            progress_color=COLORS['electric_violet'],
            button_color=COLORS['neon_cyan']
        )
        self.word_count_slider.set(5)
        self.word_count_slider.pack(fill="x", pady=(5, 0))
        
        # Word separator
        sep_frame = ctk.CTkFrame(self.passphrase_options_card, fg_color="transparent")
        sep_frame.pack(fill="x", padx=SPACING['md'], pady=(SPACING['sm'], SPACING['sm']))
        
        ctk.CTkLabel(
            sep_frame, text="Word Separator:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.separator_var = ctk.StringVar(value="-")
        
        sep_buttons_frame = ctk.CTkFrame(sep_frame, fg_color="transparent")
        sep_buttons_frame.pack(fill="x")
        
        separators = [
            ("-", "Dash (-)"),
            ("_", "Underscore (_)"),
            (" ", "Space ( )"),
            (".", "Dot (.)"),
            ("", "None"),
            ("custom", "Custom")
        ]
        
        for i, (sep_val, sep_label) in enumerate(separators):
            btn = ctk.CTkRadioButton(
                sep_buttons_frame,
                text=sep_label,
                variable=self.separator_var,
                value=sep_val,
                font=ctk.CTkFont(size=11),
                fg_color=COLORS['electric_violet'],
                command=self._on_separator_change
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=2, sticky="w")
        
        # Custom separator entry
        self.custom_sep_frame = ctk.CTkFrame(sep_frame, fg_color="transparent")
        self.custom_sep_frame.pack(fill="x", pady=(5, 0))
        
        ctk.CTkLabel(
            self.custom_sep_frame, text="Custom:",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=(0, 5))
        
        self.custom_sep_entry = StyledEntry(self.custom_sep_frame, placeholder_text="Enter separator")
        self.custom_sep_entry.configure(width=100)
        self.custom_sep_entry.pack(side="left")
        self.custom_sep_frame.pack_forget()  # Hide initially
        
        # Passphrase options
        pp_options_frame = ctk.CTkFrame(self.passphrase_options_card, fg_color="transparent")
        pp_options_frame.pack(fill="x", padx=SPACING['md'], pady=(SPACING['sm'], SPACING['md']))
        
        self.capitalize_words = ctk.BooleanVar(value=True)
        self.include_number = ctk.BooleanVar(value=False)
        
        ctk.CTkCheckBox(
            pp_options_frame, text="Capitalize Words", variable=self.capitalize_words,
            font=ctk.CTkFont(size=12), fg_color=COLORS['electric_violet']
        ).pack(anchor="w", pady=2)
        
        ctk.CTkCheckBox(
            pp_options_frame, text="Include Number", variable=self.include_number,
            font=ctk.CTkFont(size=12), fg_color=COLORS['electric_violet']
        ).pack(anchor="w", pady=2)
        
        # === RIGHT COLUMN: Output ===
        
        # Generated password display
        output_card = StyledCard(right_col, variant="elevated")
        output_card.pack(fill="x", pady=(0, SPACING['md']))
        
        output_title = ctk.CTkLabel(
            output_card,
            text="🔑 Generated Password",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        output_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        # Password display with copy button
        pw_display_frame = ctk.CTkFrame(output_card, fg_color="transparent")
        pw_display_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['sm']))
        
        self.password_display = ctk.CTkTextbox(
            pw_display_frame,
            height=80,
            font=ctk.CTkFont(family="Consolas", size=14),
            fg_color=COLORS.get('bg_card', ("gray95", "gray20")),
            wrap="char"
        )
        self.password_display.pack(fill="x")
        self.password_display.insert("1.0", "Click 'Generate' to create a password")
        self.password_display.configure(state="disabled")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(output_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        self.generate_btn = StyledButton(
            btn_frame,
            text="🎲 Generate",
            command=self.generate_password,
            size="medium",
            variant="primary"
        )
        self.generate_btn.pack(side="left", padx=(0, 10))
        
        self.copy_btn = StyledButton(
            btn_frame,
            text="📋 Copy",
            command=self.copy_to_clipboard,
            size="medium",
            variant="secondary"
        )
        self.copy_btn.pack(side="left", padx=(0, 10))
        
        self.regenerate_btn = StyledButton(
            btn_frame,
            text="🔄 Regenerate",
            command=self.generate_password,
            size="medium",
            variant="ghost"
        )
        self.regenerate_btn.pack(side="left")
        
        # Strength indicator
        strength_card = StyledCard(right_col, variant="elevated")
        strength_card.pack(fill="x", pady=(0, SPACING['md']))
        
        strength_title = ctk.CTkLabel(
            strength_card,
            text="💪 Password Strength",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        strength_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        self.strength_bar = ctk.CTkProgressBar(
            strength_card,
            height=12,
            corner_radius=6,
            fg_color=COLORS.get('bg_card', ("gray80", "gray30")),
            progress_color=COLORS['success']
        )
        self.strength_bar.pack(fill="x", padx=SPACING['md'], pady=(0, 5))
        self.strength_bar.set(0)
        
        self.strength_label = ctk.CTkLabel(
            strength_card,
            text="No password generated",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        self.strength_label.pack(padx=SPACING['md'], pady=(0, SPACING['sm']))
        
        self.entropy_label = ctk.CTkLabel(
            strength_card,
            text="Entropy: -- bits",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        )
        self.entropy_label.pack(padx=SPACING['md'], pady=(0, SPACING['md']))
        
        # Character set preview
        preview_card = StyledCard(right_col, variant="subtle")
        preview_card.pack(fill="x", pady=(0, SPACING['md']))
        
        preview_title = ctk.CTkLabel(
            preview_card,
            text="📊 Character Set",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        preview_title.pack(fill="x", padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        self.charset_label = ctk.CTkLabel(
            preview_card,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary'],
            wraplength=300,
            justify="left",
            anchor="w"
        )
        self.charset_label.pack(fill="x", padx=SPACING['md'], pady=(0, SPACING['md']))
        
        # Initialize UI state
        self._on_type_change()
        self._update_preview()
    
    def _on_type_change(self):
        """Handle generation type change"""
        gen_type = self.gen_type_var.get()
        
        if gen_type == "password":
            self.password_options_card.pack(fill="x", pady=(0, SPACING['md']), after=self.password_options_card.master.winfo_children()[0])
            self.passphrase_options_card.pack_forget()
        else:
            self.password_options_card.pack_forget()
            self.passphrase_options_card.pack(fill="x", pady=(0, SPACING['md']))
        
        self._update_preview()
    
    def _on_pw_length_change(self, value):
        """Handle password length slider change"""
        length = int(value)
        self.pw_length_label.configure(text=str(length))
        self._update_preview()
    
    def _on_word_count_change(self, value):
        """Handle word count slider change"""
        count = int(value)
        self.word_count_label.configure(text=str(count))
    
    def _on_separator_change(self):
        """Handle separator selection change"""
        if self.separator_var.get() == "custom":
            self.custom_sep_frame.pack(fill="x", pady=(5, 0))
        else:
            self.custom_sep_frame.pack_forget()
    
    def _update_preview(self):
        """Update character set preview"""
        charset = self._get_charset()
        if charset:
            preview = charset[:50] + ("..." if len(charset) > 50 else "")
            self.charset_label.configure(text=f"Using {len(charset)} characters: {preview}")
        else:
            self.charset_label.configure(text="⚠️ No characters selected!")
    
    def _get_charset(self):
        """Build character set based on selected options"""
        charset = ""
        
        if self.use_uppercase.get():
            charset += string.ascii_uppercase
        if self.use_lowercase.get():
            charset += string.ascii_lowercase
        if self.use_numbers.get():
            charset += string.digits
        if self.use_special.get():
            charset += "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        if self.use_extended.get():
            charset += "äöüÄÖÜßàáâãåæçèéêëìíîïñòóôõøùúûýÿ"
        
        # Add custom characters
        custom = self.custom_chars_entry.get()
        if custom:
            charset += custom
        
        # Remove ambiguous characters if option selected
        if self.exclude_ambiguous.get():
            ambiguous = "0O1lI|"
            charset = "".join(c for c in charset if c not in ambiguous)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_charset = ""
        for c in charset:
            if c not in seen:
                seen.add(c)
                unique_charset += c
        
        return unique_charset
    
    def _get_separator(self):
        """Get the selected word separator"""
        sep = self.separator_var.get()
        if sep == "custom":
            return self.custom_sep_entry.get() or "-"
        return sep
    
    def generate_password(self):
        """Generate password or passphrase based on selected options"""
        gen_type = self.gen_type_var.get()
        
        if gen_type == "password":
            self.generated_password = self._generate_random_password()
        else:
            self.generated_password = self._generate_passphrase()
        
        # Update display
        self.password_display.configure(state="normal")
        self.password_display.delete("1.0", "end")
        self.password_display.insert("1.0", self.generated_password)
        self.password_display.configure(state="disabled")
        
        # Update strength
        self._update_strength()
        
        self.app.show_toast("Password generated!", "success")
    
    def _generate_random_password(self):
        """Generate a random password"""
        charset = self._get_charset()
        if not charset:
            return "Error: No characters selected"
        
        length = int(self.pw_length_slider.get())
        
        # Use secrets module for cryptographically secure randomness
        password = ''.join(secrets.choice(charset) for _ in range(length))
        
        return password
    
    def _generate_passphrase(self):
        """Generate a passphrase"""
        word_count = int(self.word_count_slider.get())
        separator = self._get_separator()
        capitalize = self.capitalize_words.get()
        include_num = self.include_number.get()
        
        # Select random words
        words = [secrets.choice(WORD_LIST) for _ in range(word_count)]
        
        # Capitalize if selected
        if capitalize:
            words = [w.capitalize() for w in words]
        
        # Join with separator
        passphrase = separator.join(words)
        
        # Add number if selected
        if include_num:
            num = secrets.randbelow(100)
            passphrase += separator + str(num)
        
        return passphrase
    
    def _update_strength(self):
        """Update password strength indicator"""
        password = self.generated_password
        
        if not password or password.startswith("Error"):
            self.strength_bar.set(0)
            self.strength_label.configure(text="No password generated", text_color=COLORS['text_secondary'])
            self.entropy_label.configure(text="Entropy: -- bits")
            return
        
        # Calculate entropy
        gen_type = self.gen_type_var.get()
        
        if gen_type == "password":
            charset_size = len(self._get_charset())
            entropy = len(password) * math.log2(charset_size) if charset_size > 0 else 0
        else:
            # Passphrase entropy
            word_count = int(self.word_count_slider.get())
            entropy = word_count * math.log2(len(WORD_LIST))
            if self.include_number.get():
                entropy += math.log2(100)
        
        # Determine strength level
        if entropy >= 128:
            strength = 1.0
            label = "Excellent - Virtually Uncrackable"
            color = "#22C55E"  # Green
        elif entropy >= 80:
            strength = 0.8
            label = "Very Strong - Highly Secure"
            color = "#84CC16"  # Lime
        elif entropy >= 60:
            strength = 0.6
            label = "Strong - Good Security"
            color = "#EAB308"  # Yellow
        elif entropy >= 40:
            strength = 0.4
            label = "Moderate - Acceptable"
            color = "#F97316"  # Orange
        elif entropy >= 28:
            strength = 0.25
            label = "Weak - Improve It"
            color = "#EF4444"  # Red
        else:
            strength = 0.1
            label = "Very Weak - Unsafe"
            color = "#DC2626"  # Dark red
        
        self.strength_bar.configure(progress_color=color)
        self.strength_bar.set(strength)
        self.strength_label.configure(text=label, text_color=color)
        self.entropy_label.configure(text=f"Entropy: {entropy:.1f} bits")
    
    def copy_to_clipboard(self):
        """Copy generated password to clipboard"""
        if not self.generated_password or self.generated_password.startswith("Error"):
            self.app.show_toast("No password to copy", "warning")
            return
        
        try:
            self.app.clipboard_clear()
            self.app.clipboard_append(self.generated_password)
            self.app.show_toast("Password copied to clipboard!", "success")
        except Exception as e:
            self.app.show_toast(f"Copy failed: {str(e)}", "error")
