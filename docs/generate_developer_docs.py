#!/usr/bin/env python3
"""
NetTools Suite - Developer Documentation PDF Generator
Generates a professionally formatted PDF developer guide
"""

from fpdf import FPDF
from datetime import datetime
import os

class DeveloperDocsPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        # Colors
        self.primary_color = (139, 92, 246)      # Electric Violet
        self.secondary_color = (0, 217, 255)     # Neon Cyan
        self.success_color = (34, 197, 94)       # Green
        self.warning_color = (245, 158, 11)      # Yellow
        self.danger_color = (239, 68, 68)        # Red
        self.dark_color = (26, 27, 38)           # Dark background
        self.text_dark = (44, 62, 80)            # Dark text
        self.light_gray = (245, 245, 245)        # Light gray bg
        self.border_gray = (200, 200, 200)       # Border gray
        self.code_bg = (40, 42, 54)              # Code background
        
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*self.text_dark)
        self.cell(0, 10, 'NetTools Suite - Entwickler-Dokumentation', align='L')
        self.cell(0, 10, f'Seite {self.page_no()}', align='R')
        self.ln(5)
        self.set_draw_color(*self.border_gray)
        self.line(10, 18, 200, 18)
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Version 2.0 | Dezember 2024', align='C')

    def title_page(self):
        """Create a professional title page"""
        self.add_page()
        self.ln(30)
        
        # Logo/Icon area
        self.set_fill_color(*self.primary_color)
        self.rect(85, 35, 40, 40, 'F')
        self.set_xy(85, 45)
        self.set_font('Helvetica', 'B', 28)
        self.set_text_color(255, 255, 255)
        self.cell(40, 20, 'NT', align='C')
        
        self.ln(50)
        
        # Main title
        self.set_font('Helvetica', 'B', 32)
        self.set_text_color(*self.primary_color)
        self.cell(0, 15, 'ENTWICKLER', align='C')
        self.ln(12)
        self.cell(0, 15, 'DOKUMENTATION', align='C')
        self.ln(15)
        
        # Subtitle
        self.set_font('Helvetica', '', 18)
        self.set_text_color(*self.text_dark)
        self.cell(0, 10, 'NetTools Suite', align='C')
        self.ln(20)
        
        # Decorative line
        self.set_draw_color(*self.primary_color)
        self.set_line_width(1)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(25)
        
        # Info box
        self.set_fill_color(*self.light_gray)
        self.set_draw_color(*self.border_gray)
        self.rect(35, self.get_y(), 140, 55, 'FD')
        
        y_start = self.get_y() + 8
        self.set_xy(40, y_start)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*self.text_dark)
        self.cell(0, 7, 'Inhalt:')
        
        contents = [
            'Architektur & Projektstruktur',
            'UI-Komponenten & Design-System',
            'Backend-Module & Tools',
            'Neue Tools hinzufuegen',
            'Best Practices & Patterns'
        ]
        
        self.set_font('Helvetica', '', 10)
        for i, item in enumerate(contents):
            self.set_xy(45, y_start + 10 + (i * 7))
            self.cell(0, 6, f'- {item}')
        
        self.ln(70)
        
        # Version info
        self.set_font('Helvetica', '', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, f'Version 2.0', align='C')
        self.ln(6)
        self.cell(0, 8, f'Stand: Dezember 2024', align='C')

    def toc_page(self):
        """Table of Contents"""
        self.add_page()
        self.chapter_title("Inhaltsverzeichnis")
        
        toc_items = [
            ("1. Projektuebersicht", 3),
            ("2. Architektur", 4),
            ("3. Verzeichnisstruktur", 5),
            ("4. Technologie-Stack", 6),
            ("5. Hauptkomponenten", 7),
            ("6. UI-Module", 9),
            ("7. Tools-Module", 10),
            ("8. Design-System", 11),
            ("9. Konfiguration & Persistenz", 12),
            ("10. Neue Tools hinzufuegen", 13),
            ("11. Best Practices", 14),
            ("12. Bekannte Probleme", 15),
        ]
        
        self.set_font('Helvetica', '', 11)
        for title, page in toc_items:
            self.set_text_color(*self.text_dark)
            self.cell(150, 8, title)
            self.set_text_color(*self.primary_color)
            self.cell(0, 8, str(page), align='R')
            self.ln()
            # Dotted line
            self.set_draw_color(*self.border_gray)
            y = self.get_y() - 4
            self.set_dash_pattern(dash=1, gap=2)
            self.line(10, y, 200, y)
            self.set_dash_pattern()

    def chapter_title(self, title, numbered=False):
        """Create a styled chapter title"""
        self.ln(5)
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(*self.primary_color)
        self.cell(0, 12, title, align='L')
        self.ln(3)
        self.set_draw_color(*self.primary_color)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 90, self.get_y())
        self.ln(10)
        self.set_text_color(0, 0, 0)
        
    def section_title(self, title):
        """Create a styled section title"""
        self.ln(5)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(*self.text_dark)
        self.cell(0, 8, title, align='L')
        self.ln(8)
        self.set_text_color(0, 0, 0)
        
    def subsection_title(self, title):
        """Create a subsection title"""
        self.ln(3)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 7, title, align='L')
        self.ln(7)
        
    def body_text(self, text):
        """Regular body text"""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6, text)
        self.ln(3)
        
    def bullet_list(self, items):
        """Create a formatted bullet list"""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        for item in items:
            self.set_x(15)
            self.cell(5, 6, chr(149), align='L')
            self.multi_cell(0, 6, item)
        self.ln(2)

    def code_block(self, code, title=None):
        """Create a styled code block"""
        if title:
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(*self.primary_color)
            self.cell(0, 6, title)
            self.ln(4)
        
        # Code background
        lines = code.strip().split('\n')
        height = len(lines) * 5 + 8
        
        y_start = self.get_y()
        self.set_fill_color(45, 45, 55)
        self.rect(10, y_start, 190, min(height, 80), 'F')
        
        # Left accent bar
        self.set_fill_color(*self.primary_color)
        self.rect(10, y_start, 3, min(height, 80), 'F')
        
        # Code text
        self.set_xy(16, y_start + 4)
        self.set_font('Courier', '', 8)
        self.set_text_color(220, 220, 220)
        
        for i, line in enumerate(lines[:15]):  # Max 15 lines
            self.set_x(16)
            # Truncate long lines
            if len(line) > 85:
                line = line[:82] + '...'
            self.cell(0, 5, line)
            self.ln(5)
        
        if len(lines) > 15:
            self.set_x(16)
            self.set_text_color(*self.primary_color)
            self.cell(0, 5, f'... ({len(lines) - 15} weitere Zeilen)')
        
        self.set_y(y_start + min(height, 80) + 5)
        self.set_text_color(0, 0, 0)

    def info_table(self, headers, rows):
        """Create a formatted table"""
        self.set_fill_color(*self.primary_color)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 9)
        
        col_width = 190 / len(headers)
        
        # Header
        for header in headers:
            self.cell(col_width, 7, header, border=1, fill=True, align='C')
        self.ln()
        
        # Rows
        self.set_font('Helvetica', '', 9)
        fill = False
        for row in rows:
            if fill:
                self.set_fill_color(*self.light_gray)
            else:
                self.set_fill_color(255, 255, 255)
            self.set_text_color(60, 60, 60)
            
            for cell in row:
                self.cell(col_width, 6, str(cell)[:30], border=1, fill=True)
            self.ln()
            fill = not fill
        self.ln(5)

    def highlight_box(self, title, content, box_type="info"):
        """Create a highlighted info box"""
        if box_type == "tip":
            bg_color = (232, 245, 233)
            border_color = self.success_color
            icon = "TIPP"
        elif box_type == "warning":
            bg_color = (255, 249, 230)
            border_color = self.warning_color
            icon = "ACHTUNG"
        elif box_type == "important":
            bg_color = (255, 235, 238)
            border_color = self.danger_color
            icon = "WICHTIG"
        else:
            bg_color = (237, 233, 254)
            border_color = self.primary_color
            icon = "INFO"
        
        self.ln(3)
        y_start = self.get_y()
        
        # Left border accent
        self.set_fill_color(*border_color)
        self.rect(10, y_start, 3, 22, 'F')
        
        # Main box
        self.set_fill_color(*bg_color)
        self.rect(13, y_start, 184, 22, 'F')
        
        # Icon/Title
        self.set_xy(18, y_start + 3)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*border_color)
        self.cell(0, 5, f'{icon}: {title}')
        
        # Content
        self.set_xy(18, y_start + 10)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(60, 60, 60)
        self.multi_cell(175, 5, content)
        
        self.set_y(y_start + 26)

    def architecture_diagram(self):
        """Draw architecture diagram"""
        y_start = self.get_y()
        box_height = 18
        box_width = 150
        x_center = 30
        
        layers = [
            ("Benutzeroberflaeche (CustomTkinter)", self.primary_color),
            ("UI-Komponenten (StyledCard, StyledButton)", (100, 100, 180)),
            ("Tool-UI-Module (scanner_ui, dns_ui, ...)", (80, 80, 160)),
            ("Backend/Tools-Module (scanner.py, ...)", (60, 60, 140)),
            ("System/Netzwerk (subprocess, socket)", (40, 40, 120)),
        ]
        
        for i, (label, color) in enumerate(layers):
            y = y_start + (i * (box_height + 5))
            self.set_fill_color(*color)
            self.rect(x_center, y, box_width, box_height, 'F')
            
            self.set_xy(x_center, y + 5)
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(255, 255, 255)
            self.cell(box_width, 8, label, align='C')
            
            # Arrow
            if i < len(layers) - 1:
                arrow_y = y + box_height + 2
                self.set_draw_color(*self.text_dark)
                self.line(x_center + box_width/2, arrow_y, x_center + box_width/2, arrow_y + 3)
        
        self.set_y(y_start + len(layers) * (box_height + 5) + 10)


def generate_docs():
    pdf = DeveloperDocsPDF()
    pdf.alias_nb_pages()
    
    # ============ TITLE PAGE ============
    pdf.title_page()
    
    # ============ TABLE OF CONTENTS ============
    pdf.toc_page()
    
    # ============ 1. PROJECT OVERVIEW ============
    pdf.add_page()
    pdf.chapter_title("1. Projektuebersicht")
    
    pdf.body_text(
        "Die NetTools Suite ist eine Desktop-Anwendung fuer Netzwerk-Administration, "
        "entwickelt mit Python und CustomTkinter. Die Anwendung folgt einer modularen "
        "Architektur, die einfache Erweiterung und Wartung ermoeglicht."
    )
    
    pdf.section_title("Kernziele")
    pdf.bullet_list([
        "Moderne, benutzerfreundliche GUI mit Dark Theme",
        "Modulare Tool-Architektur fuer einfache Erweiterung",
        "Plattformuebergreifend (primaer Windows)",
        "Einfache Erweiterbarkeit durch klare Strukturen"
    ])
    
    # ============ 2. ARCHITECTURE ============
    pdf.add_page()
    pdf.chapter_title("2. Architektur")
    
    pdf.section_title("Schichtenmodell")
    pdf.body_text("Die Anwendung folgt einem klaren Schichtenmodell:")
    pdf.ln(5)
    pdf.architecture_diagram()
    
    pdf.section_title("Kommunikationsfluss")
    pdf.bullet_list([
        "Benutzer-Aktion -> UI-Modul (z.B. scanner_ui.py)",
        "Validierung der Eingabe im UI-Modul",
        "Backend-Modul fuehrt Operation aus (Threading)",
        "System-Aufruf (ping, tracert, etc.)",
        "Ergebnis-Callback zurueck zum UI",
        "UI-Update im Haupt-Thread via app.after()"
    ])
    
    pdf.highlight_box(
        "Threading-Regel",
        "Lange Operationen IMMER in separatem Thread ausfuehren. UI-Updates NUR ueber self.app.after(0, callback)!",
        "important"
    )
    
    # ============ 3. DIRECTORY STRUCTURE ============
    pdf.add_page()
    pdf.chapter_title("3. Verzeichnisstruktur")
    
    pdf.code_block("""nettools/
|-- nettools_app.py          # Hauptanwendung & Entry Point
|-- design_constants.py      # Farben, Schriften, Abstaende
|-- ui_components.py         # Wiederverwendbare UI-Komponenten
|-- requirements.txt         # Python-Abhaengigkeiten
|
|-- ui/                      # UI-Module fuer jeden Tool
|   |-- dashboard_ui.py      # Dashboard-Ansicht
|   |-- scanner_ui.py        # IPv4-Scanner UI
|   |-- dns_ui.py            # DNS-Lookup UI
|   |-- traceroute_ui.py     # Traceroute UI
|   |-- settings_ui.py       # Einstellungen
|   +-- ...
|
|-- tools/                   # Backend-Logik
|   |-- scanner.py           # IPv4-Scanner Logik
|   |-- traceroute.py        # Traceroute Logik
|   |-- traceroute_manager.py # Verlaufs-Manager
|   +-- ...
|
+-- docs/                    # Dokumentation""")
    
    # ============ 4. TECHNOLOGY STACK ============
    pdf.add_page()
    pdf.chapter_title("4. Technologie-Stack")
    
    pdf.section_title("Hauptabhaengigkeiten")
    pdf.info_table(
        ["Bibliothek", "Version", "Verwendung"],
        [
            ("customtkinter", ">= 5.2.0", "Moderne GUI-Komponenten"),
            ("tkinter", "(builtin)", "Basis-GUI-Framework"),
            ("requests", ">= 2.31.0", "HTTP-Anfragen"),
            ("dnspython", ">= 2.4.0", "DNS-Abfragen"),
            ("beautifulsoup4", ">= 4.12.0", "HTML-Parsing"),
            ("pyinstaller", ">= 6.0.0", "Executable-Erstellung"),
            ("matplotlib", ">= 3.7.0", "Visualisierungen"),
        ]
    )
    
    pdf.section_title("System-Tools (extern)")
    pdf.bullet_list([
        "ping / tracert / pathping - Windows-Netzwerktools",
        "arp - ARP-Tabelle auslesen",
        "nslookup - DNS-Abfragen (Fallback)",
        "iperf3 - Bandbreiten-Tests (optional)"
    ])
    
    # ============ 5. MAIN COMPONENTS ============
    pdf.add_page()
    pdf.chapter_title("5. Hauptkomponenten")
    
    pdf.section_title("5.1 nettools_app.py - Hauptanwendung")
    pdf.body_text("Dies ist der zentrale Entry Point und enthaelt die NetToolsApp Klasse:")
    
    pdf.code_block("""class NetToolsApp(ctk.CTk):
    def __init__(self):
        # Fenster-Initialisierung
        # Konfiguration laden
        # UI aufbauen
        
    def create_sidebar(self):
        # Erstellt die Navigation
        
    def switch_page(self, page_id):
        # Wechselt zwischen Tools
        
    def show_toast(self, message, type):
        # Zeigt Benachrichtigungen""")
    
    pdf.section_title("Wichtige Methoden")
    pdf.info_table(
        ["Methode", "Beschreibung"],
        [
            ("__init__()", "Initialisiert App, laedt Config"),
            ("create_sidebar()", "Erstellt Navigation"),
            ("switch_page(id)", "Wechselt zu einem Tool"),
            ("show_toast(msg, type)", "Zeigt Benachrichtigung"),
            ("get_enabled_tools()", "Laedt aktivierte Tools"),
            ("is_admin()", "Prueft Admin-Rechte"),
        ]
    )
    
    pdf.section_title("5.2 design_constants.py")
    pdf.body_text("Zentrale Definition aller visuellen Konstanten:")
    
    pdf.code_block("""COLORS = {
    "bg_primary": ("#1A1B26", "#1A1B26"),
    "electric_violet": ("#8B5CF6", "#A78BFA"),
    "neon_cyan": ("#00D9FF", "#67E8F9"),
    "success": ("#22C55E", "#4ADE80"),
    "danger": ("#EF4444", "#F87171"),
}

SPACING = {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32}
FONT_SIZES = {"title": 24, "heading": 18, "body": 12}""")
    
    # ============ 6. UI MODULES ============
    pdf.add_page()
    pdf.chapter_title("6. UI-Module")
    
    pdf.section_title("Struktur eines UI-Moduls")
    pdf.code_block("""class ToolNameUI:
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.create_ui()
    
    def create_ui(self):
        main_frame = ctk.CTkScrollableFrame(self.parent)
        main_frame.pack(fill="both", expand=True)
        
        # Titel
        title = ctk.CTkLabel(main_frame, text="Tool Name")
        title.pack(anchor="w")
        
        # Eingabebereich mit StyledCard
        input_card = StyledCard(main_frame, variant="elevated")
        input_card.pack(fill="x", pady=15)
    
    def _do_action(self):
        # Threading fuer lange Operationen
        pass""")
    
    pdf.highlight_box(
        "UI-Konsistenz",
        "Immer COLORS und SPACING aus design_constants verwenden. StyledCard fuer Container, StyledButton fuer Aktionen.",
        "tip"
    )
    
    # ============ 7. TOOLS MODULES ============
    pdf.add_page()
    pdf.chapter_title("7. Tools-Module")
    
    pdf.section_title("Struktur eines Backend-Moduls")
    pdf.code_block("""class ToolName:
    @staticmethod
    def run(target: str, options: dict = None) -> Dict:
        try:
            if not target:
                return {"success": False, "error": "Kein Ziel"}
            
            result = subprocess.run(
                ["tool", target],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}""")
    
    # ============ 8. DESIGN SYSTEM ============
    pdf.add_page()
    pdf.chapter_title("8. Design-System")
    
    pdf.section_title("Farbschema")
    pdf.info_table(
        ["Farbe", "Hex", "Verwendung"],
        [
            ("Electric Violet", "#8B5CF6", "Primaerfarbe, aktive Elemente"),
            ("Neon Cyan", "#00D9FF", "Akzente, Links"),
            ("Success Green", "#22C55E", "Erfolg, positive Werte"),
            ("Danger Red", "#EF4444", "Fehler, negative Werte"),
            ("Warning Yellow", "#F59E0B", "Warnungen"),
            ("Background", "#1A1B26", "Haupt-Hintergrund"),
        ]
    )
    
    pdf.section_title("Abstands-System")
    pdf.info_table(
        ["Name", "Wert", "Verwendung"],
        [
            ("xs", "4px", "Minimal (zwischen Icons)"),
            ("sm", "8px", "Klein (verwandte Elemente)"),
            ("md", "16px", "Standard (Padding in Cards)"),
            ("lg", "24px", "Gross (zwischen Sektionen)"),
            ("xl", "32px", "Extra gross (Seiten-Raender)"),
        ]
    )
    
    # ============ 9. CONFIGURATION ============
    pdf.add_page()
    pdf.chapter_title("9. Konfiguration & Persistenz")
    
    pdf.section_title("Konfigurations-Datei")
    pdf.body_text("Speicherort: ~/.nettools/config.json")
    
    pdf.code_block("""{
    "favorite_tools": ["scanner", "dns", "traceroute"],
    "enabled_tools": ["dashboard", "scanner", "dns"],
    "window": {
        "width": 1400,
        "height": 900
    },
    "scan_profiles": {
        "office": {
            "ip_range": "192.168.1.0/24",
            "ports": "22,80,443"
        }
    }
}""")
    
    pdf.section_title("Verlaufs-Speicherung")
    pdf.code_block("""~/.nettools/
|-- config.json          # Haupt-Konfiguration
|-- scans.json           # Scan-Verlauf
|-- traceroutes.json     # Traceroute-Verlauf
|-- dns_lookups.json     # DNS-Verlauf
+-- port_scans.json      # Port-Scan-Verlauf""")
    
    # ============ 10. ADDING NEW TOOLS ============
    pdf.add_page()
    pdf.chapter_title("10. Neue Tools hinzufuegen")
    
    pdf.section_title("Schritt 1: Backend-Modul erstellen")
    pdf.body_text("Erstelle tools/neues_tool.py:")
    pdf.code_block("""class NeuesTool:
    @staticmethod
    def run(target: str) -> dict:
        # Implementierung
        return {"success": True, "output": "..."}""")
    
    pdf.section_title("Schritt 2: UI-Modul erstellen")
    pdf.body_text("Erstelle ui/neues_tool_ui.py:")
    pdf.code_block("""from ui_components import StyledCard, StyledButton

class NeuesToolUI:
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.create_ui()
    
    def create_ui(self):
        # UI-Code hier
        pass""")
    
    pdf.section_title("Schritt 3: In nettools_app.py registrieren")
    pdf.bullet_list([
        "Import hinzufuegen: from ui.neues_tool_ui import NeuesToolUI",
        "In nav_categories einfuegen: ('neues_tool', 'Icon', 'Name', 'Tooltip')",
        "In switch_page Handler hinzufuegen",
        "In get_enabled_tools Default hinzufuegen"
    ])
    
    # ============ 11. BEST PRACTICES ============
    pdf.add_page()
    pdf.chapter_title("11. Best Practices")
    
    pdf.section_title("Threading")
    pdf.highlight_box(
        "Wichtig",
        "IMMER lange Operationen in separatem Thread. UI-Updates NUR ueber self.app.after(0, callback). daemon=True setzen!",
        "important"
    )
    
    pdf.section_title("Error Handling")
    pdf.code_block("""try:
    result = dangerous_operation()
except SpecificError as e:
    self.app.show_toast(f"Fehler: {e}", "error")
except Exception as e:
    print(f"Unerwarteter Fehler: {e}")
    self.app.show_toast("Ein Fehler ist aufgetreten", "error")""")
    
    pdf.section_title("Encoding (Windows)")
    pdf.code_block("""# Bei subprocess:
result = subprocess.run(cmd, capture_output=True)
# NICHT text=True bei moeglichen Sonderzeichen!
# Manuell dekodieren:
output = result.stdout.decode('utf-8', errors='replace')""")
    
    # ============ 12. KNOWN ISSUES ============
    pdf.add_page()
    pdf.chapter_title("12. Bekannte Probleme")
    
    pdf.info_table(
        ["Problem", "Loesung"],
        [
            ("Emoji-Breite variiert", "Fixe Breite mit width Parameter"),
            ("Windows-Encoding", "Bytes-Modus + manuelle Dekodierung"),
            ("Admin-Rechte noetig", "is_admin() pruefen, restart_as_admin()"),
            ("PSExec Cross-Domain", "Feature temporaer deaktiviert"),
        ]
    )
    
    pdf.ln(10)
    pdf.highlight_box(
        "Weiterentwicklung",
        "Geplant: Netzwerk-Topologie-Visualisierung, PDF-Export, Plugin-System, Dark/Light Mode Toggle",
        "info"
    )
    
    # Save PDF
    output_path = os.path.join(os.path.dirname(__file__), 'Entwickler_Dokumentation_DE.pdf')
    pdf.output(output_path)
    print(f"Developer documentation generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_docs()
