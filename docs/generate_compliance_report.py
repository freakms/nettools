#!/usr/bin/env python3
"""
NetTools Suite - Compliance Report Generator
Generates a professionally formatted PDF compliance report
"""

from fpdf import FPDF
from datetime import datetime
import os

class ComplianceReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        # Colors
        self.primary_color = (41, 128, 185)      # Blue
        self.success_color = (39, 174, 96)       # Green
        self.warning_color = (241, 196, 15)      # Yellow
        self.danger_color = (231, 76, 60)        # Red
        self.info_color = (52, 152, 219)         # Light Blue
        self.dark_color = (44, 62, 80)           # Dark gray
        self.light_gray = (245, 245, 245)        # Light gray bg
        self.border_gray = (200, 200, 200)       # Border gray
        
    def header(self):
        if self.page_no() == 1:
            return  # Skip header on title page
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*self.dark_color)
        self.cell(0, 10, 'NetTools Suite - Compliance Report', align='L')
        self.cell(0, 10, f'Page {self.page_no()}', align='R')
        self.ln(5)
        # Header line
        self.set_draw_color(*self.border_gray)
        self.line(10, 18, 200, 18)
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d")} | Confidential', align='C')

    def title_page(self):
        """Create a professional title page"""
        self.add_page()
        self.ln(40)
        
        # Main title
        self.set_font('Helvetica', 'B', 28)
        self.set_text_color(*self.primary_color)
        self.cell(0, 15, 'COMPLIANCE REPORT', align='C')
        self.ln(12)
        
        # Subtitle
        self.set_font('Helvetica', '', 18)
        self.set_text_color(*self.dark_color)
        self.cell(0, 10, 'NetTools Suite', align='C')
        self.ln(20)
        
        # Decorative line
        self.set_draw_color(*self.primary_color)
        self.set_line_width(1)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(20)
        
        # Info box
        self.set_fill_color(*self.light_gray)
        self.rect(40, self.get_y(), 130, 50, 'F')
        self.set_draw_color(*self.border_gray)
        self.rect(40, self.get_y(), 130, 50, 'D')
        
        self.set_xy(45, self.get_y() + 8)
        self.set_font('Helvetica', 'B', 11)
        self.cell(0, 8, 'Report Coverage:')
        self.set_xy(45, self.get_y() + 10)
        self.set_font('Helvetica', '', 10)
        self.cell(0, 6, '- Open Source License Compatibility')
        self.set_xy(45, self.get_y() + 6)
        self.cell(0, 6, '- Commercial Use Assessment')
        self.set_xy(45, self.get_y() + 6)
        self.cell(0, 6, '- GDPR (DSGVO) Compliance')
        self.set_xy(45, self.get_y() + 6)
        self.cell(0, 6, '- NIS2 Security Considerations')
        
        self.ln(60)
        
        # Date
        self.set_font('Helvetica', '', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Report Date: {datetime.now().strftime("%B %d, %Y")}', align='C')
        self.ln(8)
        self.cell(0, 10, 'Version: 1.0', align='C')
        
    def chapter_title(self, num, title):
        """Create a styled chapter title"""
        self.ln(5)
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(*self.primary_color)
        self.cell(0, 12, f'{num}. {title}', align='L')
        self.ln(3)
        # Underline
        self.set_draw_color(*self.primary_color)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(10)
        self.set_text_color(0, 0, 0)
        
    def section_title(self, title):
        """Create a styled section title"""
        self.ln(3)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(*self.dark_color)
        self.cell(0, 8, title, align='L')
        self.ln(8)
        self.set_text_color(0, 0, 0)
        
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
            self.cell(5, 6, chr(149), align='L')  # Bullet character
            self.multi_cell(0, 6, item)
        self.ln(2)

    def status_badge(self, status, text):
        """Create a colored status badge with text"""
        self.ln(2)
        
        # Badge colors
        if status == "APPROVED" or status == "OK":
            color = self.success_color
        elif status == "WARNING":
            color = self.warning_color
        elif status == "INFO":
            color = self.info_color
        else:
            color = self.danger_color
        
        # Draw badge
        badge_width = 25
        self.set_fill_color(*color)
        self.set_draw_color(*color)
        
        y_pos = self.get_y()
        self.rect(10, y_pos, badge_width, 7, 'F')
        
        self.set_xy(10, y_pos + 1)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(255, 255, 255)
        self.cell(badge_width, 5, status, align='C')
        
        # Text next to badge
        self.set_xy(10 + badge_width + 3, y_pos + 1)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        self.cell(0, 5, text)
        self.ln(12)

    def summary_table(self, data):
        """Create a summary table with status indicators"""
        self.set_fill_color(*self.light_gray)
        self.set_draw_color(*self.border_gray)
        
        # Header
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(*self.primary_color)
        self.set_text_color(255, 255, 255)
        self.cell(70, 8, 'Category', border=1, fill=True, align='C')
        self.cell(30, 8, 'Status', border=1, fill=True, align='C')
        self.cell(90, 8, 'Summary', border=1, fill=True, align='C')
        self.ln()
        
        # Rows
        self.set_font('Helvetica', '', 9)
        fill = False
        for row in data:
            category, status, summary = row
            
            # Status color
            if status in ["APPROVED", "OK", "PERMITTED"]:
                status_color = self.success_color
            elif status == "WARNING":
                status_color = self.warning_color
            elif status == "INFO":
                status_color = self.info_color
            else:
                status_color = self.danger_color
            
            if fill:
                self.set_fill_color(*self.light_gray)
            else:
                self.set_fill_color(255, 255, 255)
            
            self.set_text_color(60, 60, 60)
            self.cell(70, 8, category, border=1, fill=True)
            
            self.set_fill_color(*status_color)
            self.set_text_color(255, 255, 255)
            self.cell(30, 8, status, border=1, fill=True, align='C')
            
            if fill:
                self.set_fill_color(*self.light_gray)
            else:
                self.set_fill_color(255, 255, 255)
            self.set_text_color(60, 60, 60)
            self.cell(90, 8, summary, border=1, fill=True)
            self.ln()
            fill = not fill
        self.ln(5)

    def license_table(self, title, data):
        """Create a license table"""
        self.section_title(title)
        
        self.set_fill_color(*self.light_gray)
        self.set_draw_color(*self.border_gray)
        
        # Header
        self.set_font('Helvetica', 'B', 9)
        self.set_fill_color(*self.dark_color)
        self.set_text_color(255, 255, 255)
        self.cell(50, 7, 'Package', border=1, fill=True)
        self.cell(40, 7, 'License', border=1, fill=True)
        self.cell(100, 7, 'Purpose', border=1, fill=True)
        self.ln()
        
        # Rows
        self.set_font('Helvetica', '', 9)
        fill = False
        for row in data:
            name, lic, desc = row
            
            if fill:
                self.set_fill_color(*self.light_gray)
            else:
                self.set_fill_color(255, 255, 255)
            self.set_text_color(60, 60, 60)
            
            self.cell(50, 7, name, border=1, fill=True)
            self.cell(40, 7, lic, border=1, fill=True)
            self.cell(100, 7, desc, border=1, fill=True)
            self.ln()
            fill = not fill
        self.ln(5)

    def info_box(self, title, content, box_type="info"):
        """Create a colored info box"""
        if box_type == "success":
            bg_color = (232, 245, 233)
            border_color = self.success_color
            icon = chr(10004)  # Checkmark
        elif box_type == "warning":
            bg_color = (255, 249, 230)
            border_color = self.warning_color
            icon = "!"
        elif box_type == "danger":
            bg_color = (255, 235, 238)
            border_color = self.danger_color
            icon = "X"
        else:
            bg_color = (232, 244, 253)
            border_color = self.info_color
            icon = "i"
        
        self.ln(3)
        y_start = self.get_y()
        
        # Calculate height needed
        self.set_font('Helvetica', '', 10)
        
        # Draw box
        self.set_fill_color(*bg_color)
        self.set_draw_color(*border_color)
        self.set_line_width(0.5)
        
        # Left border accent
        self.set_fill_color(*border_color)
        self.rect(10, y_start, 3, 25, 'F')
        
        # Main box
        self.set_fill_color(*bg_color)
        self.rect(13, y_start, 184, 25, 'F')
        
        # Title
        self.set_xy(18, y_start + 3)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*border_color)
        self.cell(0, 6, title)
        
        # Content
        self.set_xy(18, y_start + 10)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(60, 60, 60)
        self.multi_cell(175, 5, content)
        
        self.set_y(y_start + 28)


def generate_report():
    pdf = ComplianceReportPDF()
    pdf.alias_nb_pages()
    
    # ============ TITLE PAGE ============
    pdf.title_page()
    
    # ============ EXECUTIVE SUMMARY ============
    pdf.add_page()
    pdf.chapter_title(1, "Executive Summary")
    
    pdf.body_text(
        "This compliance report analyzes NetTools Suite for suitability as an open source project, "
        "commercial use licensing compatibility, GDPR (DSGVO) compliance, and NIS2 security requirements."
    )
    
    pdf.ln(5)
    pdf.summary_table([
        ("Open Source License", "APPROVED", "MIT License - fully compatible"),
        ("Commercial Use", "PERMITTED", "All dependencies allow commercial use"),
        ("GDPR Compliance", "OK", "Local-only tool, no PII collection"),
        ("NIS2 Security", "INFO", "Depends on organizational policies"),
    ])
    
    pdf.info_box(
        "Overall Assessment",
        "NetTools Suite is SUITABLE for open source distribution under the MIT License. "
        "All dependencies use permissive licenses compatible with commercial use.",
        "success"
    )
    
    # ============ LICENSE ANALYSIS ============
    pdf.add_page()
    pdf.chapter_title(2, "License Analysis")
    
    pdf.section_title("2.1 Project License")
    pdf.body_text(
        "NetTools Suite is licensed under the MIT License, which is permissive and business-friendly. "
        "It allows commercial use, modification, and distribution with only attribution required."
    )
    
    pdf.license_table("2.2 Permissive Licenses (No Restrictions)", [
        ("customtkinter", "MIT", "GUI Framework"),
        ("Pillow", "MIT-CMU", "Image Processing"),
        ("pythonping", "MIT", "Network Ping Operations"),
        ("requests", "Apache 2.0", "HTTP Client Library"),
        ("cryptography", "Apache 2.0 / BSD-3", "Encryption Functions"),
        ("urllib3", "MIT", "HTTP Library"),
        ("beautifulsoup4", "MIT", "HTML Parsing"),
        ("speedtest-cli", "Apache 2.0", "Internet Speed Testing"),
        ("matplotlib", "PSF", "Data Visualization"),
        ("numpy", "BSD", "Numerical Computing"),
    ])
    
    pdf.section_title("2.3 PyInstaller GPL Consideration")
    pdf.info_box(
        "Important: PyInstaller Exception",
        "PyInstaller is licensed under GPLv2, but has a special bootloader exception that allows "
        "bundling proprietary/MIT code. Applications built with PyInstaller do NOT inherit the GPL license. "
        "Your application remains under its own license (MIT).",
        "info"
    )
    
    pdf.status_badge("APPROVED", "PyInstaller exception clause permits MIT-licensed distribution")
    
    # ============ GDPR COMPLIANCE ============
    pdf.add_page()
    pdf.chapter_title(3, "GDPR (DSGVO) Compliance")
    
    pdf.section_title("3.1 Data Processing Overview")
    pdf.body_text(
        "NetTools Suite is primarily a LOCAL network diagnostic tool. The following data handling "
        "characteristics were identified during code review:"
    )
    
    pdf.section_title("3.2 Local Data Storage")
    pdf.bullet_list([
        "Window geometry and UI preferences stored in ~/.nettools_config.json",
        "Theme settings and favorite tools (user preferences only)",
        "Enabled/disabled tool preferences",
        "Scan history and comparison data (local files only)",
        "Network profiles containing IP ranges and scan configurations"
    ])
    
    pdf.status_badge("OK", "All data stored locally - No cloud transmission")
    
    pdf.section_title("3.3 External Network Connections")
    pdf.body_text("The application MAY connect to external services for specific features (all user-initiated):")
    pdf.bullet_list([
        "speedtest-cli: Connects to Speedtest.net servers for speed tests",
        "MXToolbox API: Optional DNS lookup enhancement (requires user API key)",
        "DNSDumpster: Optional domain reconnaissance (requires user API key)",
        "phpIPAM: Optional IPAM integration (user-configured server)"
    ])
    
    pdf.info_box(
        "GDPR Risk Assessment: LOW",
        "No automatic collection of Personal Identifiable Information (PII). No telemetry, analytics, "
        "or tracking. No data transmission without explicit user action. All data remains local.",
        "success"
    )
    
    # ============ NIS2 SECURITY ============
    pdf.add_page()
    pdf.chapter_title(4, "NIS2 Security Considerations")
    
    pdf.section_title("4.1 Overview")
    pdf.body_text(
        "The NIS2 Directive is an EU regulation for improving cybersecurity. As a diagnostic tool, "
        "NetTools Suite itself is not directly subject to NIS2. However, organizations using it may be."
    )
    
    pdf.section_title("4.2 Security Features")
    pdf.bullet_list([
        "Open source: Full code transparency and auditability",
        "Local execution: No cloud dependencies, reduced attack surface",
        "No network listeners (except iPerf server mode when explicitly used)",
        "Configurable features: Sensitive tools can be disabled via settings",
        "Remote Tools module: Currently DISABLED by default"
    ])
    
    pdf.section_title("4.3 Recommendations for Enterprise Use")
    pdf.bullet_list([
        "Deploy via approved software channels only",
        "Restrict access to authorized network administrators",
        "Enable logging if using in regulated environments",
        "Review and approve external API integrations before use",
        "Keep Remote Tools disabled unless specific need exists",
        "Encrypt or protect exported scan results"
    ])
    
    pdf.info_box(
        "NIS2 Compliance Note",
        "Tool compliance depends on organizational deployment policies. The tool itself has "
        "good security characteristics suitable for enterprise use.",
        "info"
    )
    
    # ============ RECOMMENDATIONS ============
    pdf.add_page()
    pdf.chapter_title(5, "Recommendations")
    
    pdf.section_title("5.1 Required for Open Source Release")
    pdf.bullet_list([
        "Include LICENSE.txt (MIT) in all distributions [DONE]",
        "Add attribution notices for third-party libraries",
        "Document external API dependencies clearly"
    ])
    
    pdf.section_title("5.2 Recommended Improvements")
    pdf.bullet_list([
        "Add SECURITY.md file for vulnerability reporting",
        "Create CONTRIBUTING.md for contributor guidelines",
        "Add api_keys.json to .gitignore (sensitive data)",
        "Provide api_keys.example.json template [DONE]",
        "Consider code signing for distributed executables"
    ])
    
    # ============ CONCLUSION ============
    pdf.add_page()
    pdf.chapter_title(6, "Conclusion")
    
    pdf.body_text(
        "NetTools Suite has been thoroughly analyzed for compliance with open source licensing, "
        "GDPR regulations, and NIS2 security requirements."
    )
    
    pdf.ln(5)
    pdf.info_box(
        "Final Verdict: APPROVED FOR OPEN SOURCE DISTRIBUTION",
        "1. OPEN SOURCE: Fully compatible with MIT License distribution.\n"
        "2. COMMERCIAL USE: Permitted without licensing restrictions.\n"
        "3. GDPR: Low risk - local tool with no PII collection.\n"
        "4. NIS2: Good security posture suitable for enterprise deployment.",
        "success"
    )
    
    # ============ APPENDIX ============
    pdf.add_page()
    pdf.chapter_title("A", "Appendix: Complete License List")
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(*pdf.dark_color)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 7, 'Package', border=1, fill=True)
    pdf.cell(60, 7, 'License', border=1, fill=True)
    pdf.cell(70, 7, 'Compatibility', border=1, fill=True)
    pdf.ln()
    
    all_licenses = [
        ("altgraph", "MIT", "Permissive"),
        ("bcrypt", "Apache 2.0", "Permissive"),
        ("beautifulsoup4", "MIT", "Permissive"),
        ("certifi", "MPL 2.0", "File-level copyleft"),
        ("cryptography", "Apache 2.0 / BSD-3", "Permissive"),
        ("customtkinter", "MIT", "Permissive"),
        ("dnspython", "ISC", "Permissive"),
        ("matplotlib", "PSF", "Permissive"),
        ("numpy", "BSD", "Permissive"),
        ("Pillow", "MIT-CMU", "Permissive"),
        ("PyInstaller", "GPLv2 (Exception)", "Bootloader exception"),
        ("pythonping", "MIT", "Permissive"),
        ("requests", "Apache 2.0", "Permissive"),
        ("speedtest-cli", "Apache 2.0", "Permissive"),
        ("urllib3", "MIT", "Permissive"),
    ]
    
    pdf.set_font('Helvetica', '', 9)
    fill = False
    for name, lic, compat in all_licenses:
        if fill:
            pdf.set_fill_color(*pdf.light_gray)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(60, 60, 60)
        
        pdf.cell(60, 6, name, border=1, fill=True)
        pdf.cell(60, 6, lic, border=1, fill=True)
        pdf.cell(70, 6, compat, border=1, fill=True)
        pdf.ln()
        fill = not fill
    
    # Save PDF
    output_path = os.path.join(os.path.dirname(__file__), 'NetTools_Compliance_Report.pdf')
    pdf.output(output_path)
    print(f"Compliance report generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_report()
