#!/usr/bin/env python3
"""
NetTools Suite - Benutzerhandbuch PDF Generator
Generates a professionally formatted PDF user manual in German
"""

from fpdf import FPDF
from datetime import datetime
import os

class UserManualPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        # Colors matching the app's theme
        self.primary_color = (139, 92, 246)      # Electric Violet
        self.secondary_color = (0, 217, 255)     # Neon Cyan  
        self.success_color = (34, 197, 94)       # Green
        self.warning_color = (245, 158, 11)      # Yellow
        self.danger_color = (239, 68, 68)        # Red
        self.dark_bg = (26, 27, 38)              # App background
        self.card_bg = (36, 37, 58)              # Card background
        self.text_dark = (44, 62, 80)
        self.light_gray = (245, 245, 245)
        self.border_gray = (200, 200, 200)
        
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*self.text_dark)
        self.cell(0, 10, 'NetTools Suite - Benutzerhandbuch', align='L')
        self.cell(0, 10, f'Seite {self.page_no()}', align='R')
        self.ln(5)
        self.set_draw_color(*self.border_gray)
        self.line(10, 18, 200, 18)
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Version 2.0 | Dezember 2024', align='C')

    def title_page(self):
        """Create title page"""
        self.add_page()
        self.ln(25)
        
        # App icon simulation
        self.set_fill_color(*self.primary_color)
        self.rect(80, 30, 50, 50, 'F')
        self.set_xy(80, 42)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(255, 255, 255)
        self.cell(50, 20, 'NT', align='C')
        
        self.ln(55)
        
        # Title
        self.set_font('Helvetica', 'B', 36)
        self.set_text_color(*self.primary_color)
        self.cell(0, 18, 'BENUTZER', align='C')
        self.ln(14)
        self.cell(0, 18, 'HANDBUCH', align='C')
        self.ln(18)
        
        # Subtitle
        self.set_font('Helvetica', '', 20)
        self.set_text_color(*self.text_dark)
        self.cell(0, 12, 'NetTools Suite', align='C')
        self.ln(8)
        self.set_font('Helvetica', 'I', 14)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Netzwerk-Werkzeuge fuer Administratoren', align='C')
        
        self.ln(25)
        
        # Decorative line
        self.set_draw_color(*self.primary_color)
        self.set_line_width(1.5)
        self.line(50, self.get_y(), 160, self.get_y())
        
        self.ln(20)
        
        # Feature highlights box
        self.draw_feature_box()
        
        self.ln(25)
        
        # Version info
        self.set_font('Helvetica', '', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'Version 2.0', align='C')
        self.ln(6)
        self.cell(0, 8, f'Stand: Dezember 2024', align='C')

    def draw_feature_box(self):
        """Draw feature highlights"""
        y_start = self.get_y()
        self.set_fill_color(*self.light_gray)
        self.set_draw_color(*self.border_gray)
        self.rect(30, y_start, 150, 50, 'FD')
        
        features = [
            ("Netzwerk-Scanning", "IPv4, Ports, ARP"),
            ("Diagnose-Tools", "DNS, WHOIS, SSL, Traceroute"),
            ("Sicherheit", "Passwort-Generator, Hashes"),
            ("Testing", "API-Tester, Speedtest"),
        ]
        
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*self.text_dark)
        self.set_xy(35, y_start + 5)
        self.cell(0, 6, 'Hauptfunktionen:')
        
        self.set_font('Helvetica', '', 9)
        for i, (title, desc) in enumerate(features):
            row = i // 2
            col = i % 2
            x = 35 + (col * 70)
            y = y_start + 14 + (row * 12)
            self.set_xy(x, y)
            self.set_text_color(*self.primary_color)
            self.cell(3, 5, chr(149))
            self.set_text_color(*self.text_dark)
            self.cell(0, 5, f' {title}')
        
        self.set_y(y_start + 55)

    def chapter_title(self, title):
        """Chapter title with styling"""
        self.ln(5)
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(*self.primary_color)
        self.cell(0, 12, title, align='L')
        self.ln(3)
        self.set_draw_color(*self.primary_color)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(10)
        self.set_text_color(0, 0, 0)

    def section_title(self, title):
        """Section title"""
        self.ln(5)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(*self.text_dark)
        self.cell(0, 8, title, align='L')
        self.ln(8)

    def tool_title(self, icon, title):
        """Tool title with icon"""
        self.ln(3)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(*self.primary_color)
        self.cell(0, 8, f'{icon}  {title}', align='L')
        self.ln(8)
        self.set_text_color(*self.text_dark)

    def body_text(self, text):
        """Regular body text"""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def bullet_list(self, items):
        """Bullet list"""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        for item in items:
            self.set_x(15)
            self.set_text_color(*self.primary_color)
            self.cell(5, 6, chr(149))
            self.set_text_color(60, 60, 60)
            self.multi_cell(0, 6, item)
        self.ln(2)

    def numbered_steps(self, steps):
        """Numbered step list"""
        self.set_font('Helvetica', '', 10)
        for i, step in enumerate(steps, 1):
            self.set_fill_color(*self.primary_color)
            self.set_text_color(255, 255, 255)
            self.set_font('Helvetica', 'B', 9)
            self.cell(7, 7, str(i), fill=True, align='C')
            self.set_text_color(60, 60, 60)
            self.set_font('Helvetica', '', 10)
            self.cell(5, 7, '')
            self.multi_cell(0, 6, step)
            self.ln(1)
        self.ln(3)

    def draw_ui_mockup(self, title="NetTools Suite"):
        """Draw a simple UI mockup"""
        y_start = self.get_y()
        
        # Window frame
        self.set_draw_color(*self.border_gray)
        self.set_line_width(0.5)
        self.rect(20, y_start, 170, 80, 'D')
        
        # Title bar
        self.set_fill_color(*self.dark_bg)
        self.rect(20, y_start, 170, 12, 'F')
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(255, 255, 255)
        self.set_xy(25, y_start + 3)
        self.cell(0, 6, title)
        
        # Window buttons
        for i, color in enumerate([(239, 68, 68), (245, 158, 11), (34, 197, 94)]):
            self.set_fill_color(*color)
            self.ellipse(170 + (i * 8), y_start + 4, 5, 5, 'F')
        
        # Sidebar
        self.set_fill_color(36, 37, 58)
        self.rect(20, y_start + 12, 35, 68, 'F')
        
        # Sidebar items
        sidebar_items = [
            ("Dashboard", True),
            ("Scanner", False),
            ("DNS", False),
            ("Tools", False),
        ]
        self.set_font('Helvetica', '', 7)
        for i, (item, active) in enumerate(sidebar_items):
            y_pos = y_start + 18 + (i * 10)
            if active:
                self.set_fill_color(*self.primary_color)
                self.rect(20, y_pos - 2, 35, 9, 'F')
                self.set_text_color(255, 255, 255)
            else:
                self.set_text_color(180, 180, 180)
            self.set_xy(25, y_pos)
            self.cell(0, 6, item)
        
        # Main content area
        self.set_fill_color(250, 250, 250)
        self.rect(55, y_start + 12, 135, 68, 'F')
        
        # Content card
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(220, 220, 220)
        self.rect(65, y_start + 22, 115, 25, 'FD')
        
        # Card content
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*self.text_dark)
        self.set_xy(70, y_start + 26)
        self.cell(0, 5, 'Eingabebereich')
        
        # Input field mockup
        self.set_fill_color(245, 245, 245)
        self.rect(70, y_start + 33, 60, 8, 'F')
        
        # Button mockup
        self.set_fill_color(*self.primary_color)
        self.rect(135, y_start + 33, 25, 8, 'F')
        self.set_font('Helvetica', '', 6)
        self.set_text_color(255, 255, 255)
        self.set_xy(135, y_start + 34)
        self.cell(25, 6, 'Start', align='C')
        
        # Results area mockup
        self.set_fill_color(255, 255, 255)
        self.rect(65, y_start + 52, 115, 23, 'FD')
        self.set_font('Helvetica', '', 7)
        self.set_text_color(100, 100, 100)
        self.set_xy(70, y_start + 56)
        self.cell(0, 5, 'Ergebnisbereich')
        
        # Labels
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*self.primary_color)
        
        # Arrow and label for sidebar
        self.set_xy(12, y_start + 40)
        self.cell(0, 5, 'Navigation')
        self.line(10, y_start + 45, 18, y_start + 45)
        
        self.set_y(y_start + 90)

    def draw_tool_card(self, icon, title, description, features):
        """Draw a tool explanation card"""
        y_start = self.get_y()
        
        # Card background
        self.set_fill_color(*self.light_gray)
        self.set_draw_color(*self.border_gray)
        height = 35 + (len(features) * 6)
        self.rect(15, y_start, 180, height, 'FD')
        
        # Icon circle
        self.set_fill_color(*self.primary_color)
        self.ellipse(20, y_start + 5, 15, 15, 'F')
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(255, 255, 255)
        self.set_xy(20, y_start + 7)
        self.cell(15, 10, icon, align='C')
        
        # Title
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(*self.text_dark)
        self.set_xy(40, y_start + 8)
        self.cell(0, 6, title)
        
        # Description
        self.set_font('Helvetica', '', 9)
        self.set_text_color(80, 80, 80)
        self.set_xy(40, y_start + 16)
        self.cell(0, 5, description)
        
        # Features
        self.set_font('Helvetica', '', 9)
        for i, feature in enumerate(features):
            self.set_xy(25, y_start + 26 + (i * 6))
            self.set_text_color(*self.success_color)
            self.cell(5, 5, '>')
            self.set_text_color(60, 60, 60)
            self.cell(0, 5, feature)
        
        self.set_y(y_start + height + 8)

    def tip_box(self, title, content):
        """Draw a tip/hint box"""
        y_start = self.get_y()
        
        # Box
        self.set_fill_color(232, 245, 233)
        self.rect(15, y_start, 180, 22, 'F')
        
        # Left accent
        self.set_fill_color(*self.success_color)
        self.rect(15, y_start, 3, 22, 'F')
        
        # Icon and title
        self.set_xy(22, y_start + 3)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.success_color)
        self.cell(0, 5, f'TIPP: {title}')
        
        # Content
        self.set_xy(22, y_start + 10)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(60, 60, 60)
        self.multi_cell(168, 5, content)
        
        self.set_y(y_start + 26)

    def warning_box(self, title, content):
        """Draw a warning box"""
        y_start = self.get_y()
        
        self.set_fill_color(255, 249, 230)
        self.rect(15, y_start, 180, 22, 'F')
        
        self.set_fill_color(*self.warning_color)
        self.rect(15, y_start, 3, 22, 'F')
        
        self.set_xy(22, y_start + 3)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(*self.warning_color)
        self.cell(0, 5, f'HINWEIS: {title}')
        
        self.set_xy(22, y_start + 10)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(60, 60, 60)
        self.multi_cell(168, 5, content)
        
        self.set_y(y_start + 26)

    def keyboard_shortcut(self, shortcut, description):
        """Draw keyboard shortcut"""
        self.set_font('Courier', 'B', 9)
        self.set_fill_color(230, 230, 230)
        self.set_text_color(*self.text_dark)
        
        # Key box
        key_width = len(shortcut) * 4 + 8
        y = self.get_y()
        self.rect(15, y, key_width, 7, 'F')
        self.set_xy(15, y + 1)
        self.cell(key_width, 5, shortcut, align='C')
        
        # Description
        self.set_font('Helvetica', '', 10)
        self.set_xy(15 + key_width + 5, y + 1)
        self.cell(0, 5, description)
        self.ln(10)


def generate_manual():
    pdf = UserManualPDF()
    pdf.alias_nb_pages()
    
    # ============ TITLE PAGE ============
    pdf.title_page()
    
    # ============ TABLE OF CONTENTS ============
    pdf.add_page()
    pdf.chapter_title("Inhaltsverzeichnis")
    
    toc = [
        ("1. Einfuehrung", "Was ist NetTools Suite?"),
        ("2. Oberflaeche", "Navigation und Aufbau"),
        ("3. Scanning-Tools", "IPv4, Ports, ARP, Traceroute"),
        ("4. Netzwerk-Tools", "DNS, WHOIS, SSL, Subnet"),
        ("5. Sicherheits-Tools", "Passwoerter, Hashes"),
        ("6. Test-Tools", "API-Tester, Speedtest"),
        ("7. Einstellungen", "Anpassungen"),
        ("8. Tastenkombinationen", "Schnellzugriff"),
    ]
    
    pdf.set_font('Helvetica', '', 11)
    for title, desc in toc:
        pdf.set_text_color(*pdf.text_dark)
        pdf.cell(60, 8, title)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, desc)
        pdf.ln()
    
    # ============ 1. INTRODUCTION ============
    pdf.add_page()
    pdf.chapter_title("1. Einfuehrung")
    
    pdf.body_text(
        "Die NetTools Suite ist eine umfassende Sammlung von Netzwerk-Werkzeugen "
        "fuer IT-Administratoren und Netzwerk-Techniker. Die Anwendung bietet eine "
        "moderne, benutzerfreundliche Oberflaeche fuer alltaegliche Netzwerk-Diagnose."
    )
    
    pdf.section_title("Was kann ich damit machen?")
    pdf.bullet_list([
        "Netzwerke nach aktiven Geraeten scannen",
        "Offene Ports auf Servern finden",
        "DNS-Eintraege und Domain-Infos abfragen",
        "SSL-Zertifikate pruefen",
        "Sichere Passwoerter generieren",
        "APIs testen und Internet-Geschwindigkeit messen"
    ])
    
    pdf.tip_box("Schnellstart", "Starten Sie mit dem Dashboard - dort sehen Sie Ihre Netzwerk-Infos auf einen Blick.")
    
    # ============ 2. USER INTERFACE ============
    pdf.add_page()
    pdf.chapter_title("2. Oberflaeche verstehen")
    
    pdf.section_title("Hauptfenster")
    pdf.body_text("So ist die Anwendung aufgebaut:")
    pdf.ln(5)
    pdf.draw_ui_mockup()
    
    pdf.section_title("Die drei Hauptbereiche")
    
    pdf.tool_title("1", "Navigation (Links)")
    pdf.body_text(
        "Die Seitenleiste links zeigt alle verfuegbaren Tools. "
        "Klicken Sie auf ein Tool, um es zu oeffnen. "
        "Die Leiste kann mit Strg+B ein- und ausgeklappt werden."
    )
    
    pdf.tool_title("2", "Hauptbereich (Mitte)")
    pdf.body_text(
        "Hier wird das aktive Tool angezeigt. Jedes Tool hat: "
        "einen Eingabebereich (oben), Aktions-Buttons, und einen Ergebnisbereich (unten)."
    )
    
    pdf.tool_title("3", "Statusleiste (Unten)")
    pdf.body_text(
        "Zeigt Informationen zum aktuellen Tool und den Status von Operationen."
    )
    
    pdf.tip_box("Suchfunktion", "Druecken Sie Strg+K um die Schnellsuche zu oeffnen. Tippen Sie den Tool-Namen ein.")
    
    # ============ 3. SCANNING TOOLS ============
    pdf.add_page()
    pdf.chapter_title("3. Scanning-Tools")
    
    # IPv4 Scanner
    pdf.draw_tool_card(
        "IP",
        "IPv4 Scanner",
        "Scannt ein Netzwerk nach aktiven Geraeten",
        [
            "IP-Bereich eingeben (z.B. 192.168.1.0/24)",
            "Scan-Methode waehlen: Ping, ARP oder TCP",
            "Hostname, MAC und Antwortzeit anzeigen",
            "Ergebnisse als CSV exportieren"
        ]
    )
    
    pdf.section_title("So verwenden Sie den IPv4 Scanner:")
    pdf.numbered_steps([
        "Oeffnen Sie 'IPv4 Scanner' in der Navigation",
        "Geben Sie den IP-Bereich ein (z.B. 192.168.1.0/24 oder 192.168.1.1-254)",
        "Waehlen Sie die Scan-Methode (Ping fuer Standard, ARP fuer lokal)",
        "Klicken Sie auf 'Scan starten'",
        "Warten Sie auf die Ergebnisse - aktive Hosts werden angezeigt"
    ])
    
    pdf.warning_box("Admin-Rechte", "Fuer ARP-Scans benoetigen Sie Administrator-Rechte.")
    
    # Port Scanner
    pdf.ln(5)
    pdf.draw_tool_card(
        "P",
        "Port Scanner",
        "Findet offene Ports auf einem Zielsystem",
        [
            "Ziel-IP oder Hostname eingeben",
            "Ports angeben: einzeln (80,443) oder Bereich (1-1000)",
            "Vordefinierte Port-Listen verfuegbar",
            "Service-Namen werden angezeigt"
        ]
    )
    
    # Traceroute
    pdf.add_page()
    pdf.draw_tool_card(
        "TR",
        "Traceroute",
        "Verfolgt den Netzwerkpfad zu einem Ziel",
        [
            "Zeigt jeden Router auf dem Weg",
            "Antwortzeiten pro Hop",
            "Vergleich mit frueheren Traces moeglich",
            "Pathping fuer detaillierte Statistiken"
        ]
    )
    
    pdf.section_title("So verwenden Sie Traceroute:")
    pdf.numbered_steps([
        "Geben Sie das Ziel ein (z.B. google.de oder 8.8.8.8)",
        "Waehlen Sie 'Tracert' oder 'Pathping'",
        "Klicken Sie auf 'Trace starten'",
        "Beobachten Sie die Hops - jede Zeile ist ein Router"
    ])
    
    pdf.tip_box("Vergleich", "Traceroute-Ergebnisse werden gespeichert. Spaeter koennen Sie Aenderungen im Pfad erkennen.")
    
    # ARP Viewer
    pdf.ln(5)
    pdf.draw_tool_card(
        "ARP",
        "ARP-Tabelle",
        "Zeigt die lokale ARP-Tabelle an",
        [
            "Alle bekannten Geraete im Netzwerk",
            "IP- und MAC-Adressen",
            "Filtern nach IP oder MAC",
            "Cache leeren moeglich"
        ]
    )
    
    # ============ 4. NETWORK TOOLS ============
    pdf.add_page()
    pdf.chapter_title("4. Netzwerk-Tools")
    
    # DNS Lookup
    pdf.draw_tool_card(
        "DNS",
        "DNS Lookup",
        "Fuehrt DNS-Abfragen durch",
        [
            "A, AAAA, MX, NS, TXT, CNAME Records",
            "Hostname zu IP aufloesen",
            "IP zu Hostname (Reverse DNS)",
            "Ergebnisse kopierbar"
        ]
    )
    
    pdf.section_title("DNS Record-Typen erklaert:")
    pdf.bullet_list([
        "A: IPv4-Adresse einer Domain",
        "AAAA: IPv6-Adresse einer Domain", 
        "MX: Mail-Server fuer E-Mails",
        "NS: Nameserver der Domain",
        "TXT: Text-Eintraege (z.B. SPF)",
        "CNAME: Alias auf andere Domain"
    ])
    
    # WHOIS
    pdf.ln(3)
    pdf.draw_tool_card(
        "WH",
        "WHOIS Lookup",
        "Zeigt Eigentuemer-Infos zu Domains/IPs",
        [
            "Registrar und Registrierungsdatum",
            "Ablaufdatum der Domain",
            "Nameserver-Informationen",
            "Kontaktdaten (wenn verfuegbar)"
        ]
    )
    
    # SSL Checker
    pdf.add_page()
    pdf.draw_tool_card(
        "SSL",
        "SSL Checker",
        "Prueft SSL/TLS-Zertifikate",
        [
            "Gueltigkeit und Ablaufdatum",
            "Aussteller (Certificate Authority)",
            "Verschluesselungsstaerke",
            "Farbige Warnung bei Problemen"
        ]
    )
    
    pdf.section_title("Farb-Codes verstehen:")
    
    # Color legend
    colors = [
        (pdf.success_color, "Gruen", "Zertifikat gueltig, > 30 Tage"),
        (pdf.warning_color, "Gelb", "Weniger als 30 Tage bis Ablauf"),
        (pdf.danger_color, "Rot", "Abgelaufen oder ungueltig"),
    ]
    
    for color, name, desc in colors:
        y = pdf.get_y()
        pdf.set_fill_color(*color)
        pdf.rect(15, y, 8, 8, 'F')
        pdf.set_xy(28, y + 1)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*pdf.text_dark)
        pdf.cell(20, 6, name)
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 6, desc)
        pdf.ln(12)
    
    # Subnet Calculator
    pdf.ln(3)
    pdf.draw_tool_card(
        "SN",
        "Subnet Calculator",
        "Berechnet Subnet-Informationen",
        [
            "CIDR-Notation eingeben (z.B. 192.168.1.0/24)",
            "Netzwerk- und Broadcast-Adresse",
            "Anzahl verfuegbarer Hosts",
            "Wildcard-Maske anzeigen"
        ]
    )
    
    # ============ 5. SECURITY TOOLS ============
    pdf.add_page()
    pdf.chapter_title("5. Sicherheits-Tools")
    
    # Password Generator
    pdf.draw_tool_card(
        "PW",
        "Passwort-Generator",
        "Erstellt sichere Passwoerter",
        [
            "Laenge einstellbar (8-128 Zeichen)",
            "Gross-/Kleinbuchstaben, Zahlen, Sonderzeichen",
            "Passphrasen-Modus (Wort-basiert)",
            "Staerke-Anzeige"
        ]
    )
    
    pdf.section_title("Empfehlungen fuer sichere Passwoerter:")
    pdf.bullet_list([
        "Mindestens 12 Zeichen verwenden",
        "Alle Zeichentypen aktivieren",
        "Fuer jeden Dienst ein eigenes Passwort",
        "Passphrasen sind leichter zu merken"
    ])
    
    # Hash Generator
    pdf.ln(3)
    pdf.draw_tool_card(
        "#",
        "Hash Generator",
        "Erzeugt kryptografische Hashes",
        [
            "MD5, SHA-1, SHA-256, SHA-512",
            "SHA3-256 und BLAKE2b",
            "Text oder Datei als Eingabe",
            "Zum Pruefen von Datei-Integritaet"
        ]
    )
    
    pdf.tip_box("Datei-Pruefung", "Vergleichen Sie den Hash einer heruntergeladenen Datei mit dem Original, um Manipulation auszuschliessen.")
    
    # ============ 6. TEST TOOLS ============
    pdf.add_page()
    pdf.chapter_title("6. Test-Tools")
    
    # API Tester
    pdf.draw_tool_card(
        "API",
        "API Tester",
        "Testet REST-APIs",
        [
            "GET, POST, PUT, DELETE, etc.",
            "Custom Headers setzen",
            "Request Body (JSON)",
            "Antwortzeit messen"
        ]
    )
    
    pdf.section_title("So testen Sie eine API:")
    pdf.numbered_steps([
        "URL eingeben (z.B. https://api.example.com/users)",
        "HTTP-Methode waehlen (GET fuer Abrufen, POST fuer Senden)",
        "Optional: Headers hinzufuegen (z.B. Authorization)",
        "Optional: Body eingeben (bei POST/PUT)",
        "Auf 'Senden' klicken und Antwort pruefen"
    ])
    
    # Speedtest
    pdf.ln(3)
    pdf.draw_tool_card(
        "ST",
        "Speedtest",
        "Misst Internet-Geschwindigkeit",
        [
            "Download-Geschwindigkeit",
            "Upload-Geschwindigkeit",
            "Ping/Latenz",
            "Automatische Server-Auswahl"
        ]
    )
    
    # ============ 7. SETTINGS ============
    pdf.add_page()
    pdf.chapter_title("7. Einstellungen")
    
    pdf.body_text(
        "In den Einstellungen koennen Sie die Anwendung an Ihre Beduerfnisse anpassen. "
        "Oeffnen Sie die Einstellungen ueber Navigation > Einstellungen."
    )
    
    pdf.section_title("Tool-Sichtbarkeit")
    pdf.body_text(
        "Sie koennen Tools, die Sie nicht benoetigen, ausblenden:"
    )
    pdf.numbered_steps([
        "Oeffnen Sie 'Einstellungen'",
        "Deaktivieren Sie die Checkbox neben Tools, die Sie nicht brauchen",
        "Klicken Sie auf 'Anwenden'",
        "Starten Sie die App neu"
    ])
    
    pdf.warning_box("Dashboard", "Das Dashboard kann nicht deaktiviert werden - es ist Ihre Startseite.")
    
    # ============ 8. KEYBOARD SHORTCUTS ============
    pdf.add_page()
    pdf.chapter_title("8. Tastenkombinationen")
    
    pdf.body_text("Mit diesen Tastenkombinationen arbeiten Sie schneller:")
    pdf.ln(5)
    
    shortcuts = [
        ("Strg+K", "Schnellsuche oeffnen"),
        ("Strg+B", "Seitenleiste ein-/ausklappen"),
        ("Strg+D", "Zum Dashboard wechseln"),
        ("Strg+1-9", "Schnellzugriff auf Tools"),
        ("Strg+S", "Ergebnisse speichern"),
        ("Strg+C", "Ausgewaehlten Text kopieren"),
        ("Escape", "Dialog schliessen"),
        ("F5", "Ansicht aktualisieren"),
    ]
    
    for shortcut, desc in shortcuts:
        pdf.keyboard_shortcut(shortcut, desc)
    
    # ============ TROUBLESHOOTING ============
    pdf.add_page()
    pdf.chapter_title("9. Problemloesung")
    
    pdf.section_title("Haeufige Probleme")
    
    problems = [
        ("Scan findet keine Hosts", "Firewall pruefen, als Admin starten, ARP-Scan verwenden"),
        ("DNS funktioniert nicht", "Netzwerkverbindung pruefen, Port 53 in Firewall freigeben"),
        ("SSL-Pruefung schlaegt fehl", "Port pruefen (Standard: 443), Hostname korrekt eingeben"),
        ("App startet nicht", "Python 3.10+ installiert? pip install -r requirements.txt"),
    ]
    
    for problem, solution in problems:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*pdf.danger_color)
        pdf.cell(0, 7, f'Problem: {problem}')
        pdf.ln()
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(*pdf.success_color)
        pdf.set_x(15)
        pdf.cell(0, 7, f'Loesung: {solution}')
        pdf.ln(12)
    
    pdf.tip_box("Hilfe", "Bei weiteren Problemen: Log-Dateien im Anwendungsordner pruefen oder GitHub Issues erstellen.")
    
    # ============ FINAL PAGE ============
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(*pdf.primary_color)
    pdf.cell(0, 15, 'Viel Erfolg!', align='C')
    pdf.ln(20)
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, 'NetTools Suite - Netzwerk-Werkzeuge fuer Profis', align='C')
    pdf.ln(30)
    
    # Version box
    y = pdf.get_y()
    pdf.set_fill_color(*pdf.light_gray)
    pdf.rect(60, y, 90, 30, 'F')
    pdf.set_xy(60, y + 8)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(*pdf.text_dark)
    pdf.cell(90, 6, 'Version 2.0', align='C')
    pdf.set_xy(60, y + 16)
    pdf.cell(90, 6, 'Dezember 2024', align='C')
    
    # Save PDF
    output_path = os.path.join(os.path.dirname(__file__), 'Benutzerhandbuch_DE.pdf')
    pdf.output(output_path)
    print(f"User manual generated: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_manual()
