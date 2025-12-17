#!/usr/bin/env python3
"""
NetTools Suite - Compliance Report Generator
Generates a PDF compliance report for open source distribution, GDPR, and NIS2
"""

from fpdf import FPDF
from datetime import datetime
import os

class ComplianceReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'NetTools Suite - Compliance Report', border=0, align='C')
        self.ln(5)
        self.set_font('Helvetica', '', 8)
        self.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', border=0, align='C')
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')
        
    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(41, 128, 185)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, title, fill=True, align='L')
        self.ln(12)
        self.set_text_color(0, 0, 0)
        
    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(44, 62, 80)
        self.cell(0, 8, title, align='L')
        self.ln(8)
        self.set_text_color(0, 0, 0)
        
    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 6, text)
        self.ln(4)
        
    def bullet_point(self, text, indent=10):
        self.set_font('Helvetica', '', 10)
        x_start = self.l_margin + indent
        self.set_x(x_start)
        available_width = self.w - x_start - self.r_margin
        self.multi_cell(available_width, 6, f"- {text}")
        
    def status_box(self, status, text):
        if status == "OK":
            self.set_fill_color(39, 174, 96)
        elif status == "WARNING":
            self.set_fill_color(241, 196, 15)
        elif status == "INFO":
            self.set_fill_color(52, 152, 219)
        else:
            self.set_fill_color(231, 76, 60)
            
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 9)
        self.cell(20, 7, status, fill=True, align='C')
        self.set_text_color(0, 0, 0)
        self.set_font('Helvetica', '', 10)
        self.cell(0, 7, f"  {text}")
        self.ln(10)

def generate_report():
    pdf = ComplianceReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # ============ EXECUTIVE SUMMARY ============
    pdf.chapter_title("1. Executive Summary")
    pdf.body_text(
        "This compliance report analyzes NetTools Suite for suitability as an open source project, "
        "commercial use licensing compatibility, GDPR (DSGVO) compliance, and NIS2 security requirements.\n\n"
        "OVERALL ASSESSMENT: NetTools Suite is SUITABLE for open source distribution under the MIT License."
    )
    
    pdf.status_box("OK", "Open Source License Compatibility: APPROVED")
    pdf.status_box("OK", "Commercial Use: PERMITTED (with minor considerations)")
    pdf.status_box("OK", "GDPR Compliance: LOW RISK (local-only tool)")
    pdf.status_box("INFO", "NIS2: INFORMATIONAL (user responsibility)")
    
    # ============ LICENSE ANALYSIS ============
    pdf.add_page()
    pdf.chapter_title("2. License Analysis for Open Source Distribution")
    
    pdf.section_title("2.1 Project License")
    pdf.body_text(
        "NetTools Suite is licensed under the MIT License, which is:\n"
        "- Permissive and business-friendly\n"
        "- Compatible with most open source licenses\n"
        "- Allows commercial use, modification, and distribution\n"
        "- Requires only attribution in derivative works"
    )
    
    pdf.section_title("2.2 Dependency License Summary")
    
    # License categories
    licenses_permissive = [
        ("customtkinter", "MIT", "GUI Framework"),
        ("Pillow", "MIT-CMU", "Image Processing"),
        ("pythonping", "MIT", "Network Ping"),
        ("requests", "Apache 2.0", "HTTP Client"),
        ("cryptography", "Apache 2.0 / BSD-3", "Encryption"),
        ("urllib3", "MIT", "HTTP Library"),
        ("beautifulsoup4", "MIT", "HTML Parsing"),
        ("speedtest-cli", "Apache 2.0", "Speed Testing"),
    ]
    
    licenses_copyleft = [
        ("PyInstaller", "GPLv2", "Build Tool - SPECIAL CONSIDERATION"),
    ]
    
    licenses_other = [
        ("matplotlib", "PSF", "Plotting - Python Software Foundation"),
        ("certifi", "MPL 2.0", "SSL Certificates"),
    ]
    
    pdf.body_text("PERMISSIVE LICENSES (No Restrictions):")
    for name, lic, desc in licenses_permissive:
        pdf.bullet_point(f"{name}: {lic} - {desc}")
    
    pdf.ln(5)
    pdf.body_text("COPYLEFT LICENSES (Special Considerations):")
    for name, lic, desc in licenses_copyleft:
        pdf.bullet_point(f"{name}: {lic} - {desc}")
    
    pdf.ln(5)
    pdf.body_text("OTHER PERMISSIVE LICENSES:")
    for name, lic, desc in licenses_other:
        pdf.bullet_point(f"{name}: {lic} - {desc}")
    
    pdf.section_title("2.3 PyInstaller GPL Consideration")
    pdf.body_text(
        "PyInstaller is licensed under GPLv2. However, according to PyInstaller's official FAQ:\n\n"
        "- The PyInstaller bootloader has a special exception that allows bundling proprietary code\n"
        "- Applications built with PyInstaller do NOT inherit the GPL license\n"
        "- Your application remains under its own license (MIT in this case)\n\n"
        "CONCLUSION: PyInstaller's GPL does NOT affect NetTools Suite's MIT license."
    )
    pdf.status_box("OK", "PyInstaller: Exception clause permits MIT-licensed distribution")
    
    pdf.section_title("2.4 Commercial Use Assessment")
    pdf.body_text(
        "All dependencies used by NetTools Suite permit commercial use:\n\n"
        "- MIT License: Unrestricted commercial use\n"
        "- Apache 2.0: Permits commercial use with patent grants\n"
        "- BSD: Permits commercial use with attribution\n"
        "- PSF: Python Software Foundation license permits commercial use\n"
        "- MPL 2.0: File-level copyleft only, compatible with commercial use\n\n"
        "CONCLUSION: NetTools Suite can be used commercially without licensing conflicts."
    )
    pdf.status_box("OK", "Commercial Use: FULLY PERMITTED")
    
    # ============ GDPR COMPLIANCE ============
    pdf.add_page()
    pdf.chapter_title("3. GDPR (DSGVO) Compliance Analysis")
    
    pdf.section_title("3.1 Data Processing Overview")
    pdf.body_text(
        "NetTools Suite is primarily a LOCAL network diagnostic tool. The following data handling "
        "characteristics were identified during code review:"
    )
    
    pdf.section_title("3.2 Local Data Storage")
    pdf.body_text("Data stored LOCALLY on the user's machine:")
    pdf.bullet_point("Window geometry and UI preferences (~/.nettools_config.json)")
    pdf.bullet_point("Theme settings and favorite tools")
    pdf.bullet_point("Enabled/disabled tool preferences")
    pdf.bullet_point("Scan history and comparison data (local files)")
    pdf.bullet_point("Network profiles (IP ranges, scan configurations)")
    
    pdf.status_box("OK", "Local storage only - No cloud data transmission")
    
    pdf.section_title("3.3 External Network Connections")
    pdf.body_text("The application MAY connect to external services for specific features:")
    pdf.bullet_point("speedtest-cli: Connects to Speedtest.net servers (user-initiated)")
    pdf.bullet_point("MXToolbox API: Optional DNS lookup enhancement (requires API key)")
    pdf.bullet_point("DNSDumpster: Optional domain reconnaissance (requires API key)")
    pdf.bullet_point("phpIPAM: Optional IPAM integration (user-configured server)")
    
    pdf.status_box("INFO", "External connections are user-initiated and optional")
    
    pdf.section_title("3.4 Sensitive Data Handling")
    pdf.body_text("The following sensitive data may be processed:")
    pdf.bullet_point("IP addresses: Network diagnostic purpose (no PII)")
    pdf.bullet_point("Hostnames: Network diagnostic purpose (no PII)")
    pdf.bullet_point("API Keys: Stored in local api_keys.json file")
    pdf.bullet_point("Remote credentials (PSExec - DISABLED): Username/password for remote access")
    
    pdf.status_box("WARNING", "Remote Tools module stores credentials - Currently DISABLED")
    
    pdf.section_title("3.5 GDPR Risk Assessment")
    pdf.body_text(
        "RISK LEVEL: LOW\n\n"
        "Justification:\n"
        "- No automatic collection of Personal Identifiable Information (PII)\n"
        "- No telemetry, analytics, or tracking functionality\n"
        "- No data transmission to third-party servers without user action\n"
        "- All data remains on the local machine\n"
        "- External API usage is optional and user-configured\n\n"
        "RECOMMENDATION: No GDPR compliance documentation required for the tool itself. "
        "Organizations using the tool should assess their own data handling policies."
    )
    pdf.status_box("OK", "GDPR Compliance: LOW RISK - Local tool, no PII collection")
    
    # ============ NIS2 COMPLIANCE ============
    pdf.add_page()
    pdf.chapter_title("4. NIS2 Security Considerations")
    
    pdf.section_title("4.1 NIS2 Overview")
    pdf.body_text(
        "The NIS2 Directive (Network and Information Security Directive 2) is an EU regulation "
        "for improving cybersecurity. As a network diagnostic TOOL, NetTools Suite itself is not "
        "directly subject to NIS2. However, organizations using it may be.\n\n"
        "This section provides security considerations for organizations deploying the tool."
    )
    
    pdf.section_title("4.2 Security Features")
    pdf.body_text("Positive security characteristics:")
    pdf.bullet_point("Open source: Full code transparency and auditability")
    pdf.bullet_point("Local execution: No cloud dependencies reduce attack surface")
    pdf.bullet_point("No network listeners: Tool does not open server ports (except iPerf when used)")
    pdf.bullet_point("Configurable features: Sensitive tools can be disabled via settings")
    
    pdf.section_title("4.3 Security Considerations")
    pdf.body_text("Areas requiring user attention:")
    pdf.bullet_point("API Keys: Store api_keys.json securely, consider encryption")
    pdf.bullet_point("Remote Tools (DISABLED): Module handles credentials - keep disabled unless needed")
    pdf.bullet_point("phpIPAM Integration: Uses network credentials - ensure SSL/TLS")
    pdf.bullet_point("Scan Results: May contain sensitive network topology - protect exports")
    
    pdf.section_title("4.4 Recommendations for Enterprise Use")
    pdf.body_text("For NIS2-compliant organizations:")
    pdf.bullet_point("Deploy via approved software channels only")
    pdf.bullet_point("Restrict access to authorized network administrators")
    pdf.bullet_point("Enable logging if using in regulated environments")
    pdf.bullet_point("Review and approve external API integrations before use")
    pdf.bullet_point("Keep Remote Tools disabled unless specific need exists")
    pdf.bullet_point("Encrypt or protect exported scan results")
    
    pdf.status_box("INFO", "NIS2: Tool compliance depends on organizational policies")
    
    # ============ RECOMMENDATIONS ============
    pdf.add_page()
    pdf.chapter_title("5. Recommendations for Open Source Release")
    
    pdf.section_title("5.1 Required Actions")
    pdf.bullet_point("Include LICENSE.txt (MIT) in all distributions - DONE")
    pdf.bullet_point("Add attribution notices for third-party libraries in documentation")
    pdf.bullet_point("Document external API dependencies clearly")
    
    pdf.section_title("5.2 Recommended Actions")
    pdf.bullet_point("Add SECURITY.md file for vulnerability reporting")
    pdf.bullet_point("Create CONTRIBUTING.md for contributor guidelines")
    pdf.bullet_point("Add CHANGELOG.md for version history")
    pdf.bullet_point("Consider removing api_keys.json from repository (add to .gitignore)")
    pdf.bullet_point("Add example configuration file (api_keys.example.json)")
    
    pdf.section_title("5.3 Optional Enhancements")
    pdf.bullet_point("Add code signing for distributed executables")
    pdf.bullet_point("Create privacy policy document for enterprise users")
    pdf.bullet_point("Implement optional audit logging feature")
    
    # ============ CONCLUSION ============
    pdf.add_page()
    pdf.chapter_title("6. Conclusion")
    
    pdf.body_text(
        "NetTools Suite has been analyzed for compliance with open source licensing, "
        "GDPR regulations, and NIS2 security requirements.\n\n"
        "KEY FINDINGS:\n\n"
        "1. OPEN SOURCE: The tool is FULLY COMPATIBLE with open source distribution under MIT License. "
        "All dependencies use permissive licenses that allow commercial and open source use.\n\n"
        "2. COMMERCIAL USE: The tool CAN be used commercially without licensing restrictions. "
        "PyInstaller's GPL exception explicitly permits this.\n\n"
        "3. GDPR: The tool presents LOW RISK for GDPR compliance as it is a local-only tool "
        "that does not collect, process, or transmit Personal Identifiable Information.\n\n"
        "4. NIS2: As a diagnostic tool, NIS2 compliance depends on organizational deployment policies. "
        "The tool itself has good security characteristics suitable for enterprise use.\n\n"
        "OVERALL RECOMMENDATION: NetTools Suite is APPROVED for open source release and "
        "commercial deployment with the minor recommendations noted in Section 5."
    )
    
    pdf.ln(10)
    pdf.status_box("OK", "APPROVED FOR OPEN SOURCE DISTRIBUTION")
    
    # ============ APPENDIX ============
    pdf.add_page()
    pdf.chapter_title("Appendix A: Complete License List")
    
    all_licenses = [
        ("altgraph", "MIT"),
        ("annotated-types", "MIT"),
        ("anyio", "MIT"),
        ("bcrypt", "Apache 2.0"),
        ("beautifulsoup4", "MIT"),
        ("certifi", "MPL 2.0"),
        ("cffi", "MIT"),
        ("charset-normalizer", "MIT"),
        ("click", "BSD-3-Clause"),
        ("contourpy", "BSD"),
        ("cryptography", "Apache 2.0 / BSD-3"),
        ("customtkinter", "MIT"),
        ("cycler", "BSD"),
        ("darkdetect", "BSD"),
        ("dnspython", "ISC"),
        ("fonttools", "MIT"),
        ("idna", "BSD-3-Clause"),
        ("kiwisolver", "BSD"),
        ("matplotlib", "PSF"),
        ("numpy", "BSD"),
        ("packaging", "Apache 2.0 / BSD"),
        ("Pillow", "MIT-CMU"),
        ("pycparser", "BSD"),
        ("PyInstaller", "GPLv2 (Exception)"),
        ("pyparsing", "MIT"),
        ("pythonping", "MIT"),
        ("requests", "Apache 2.0"),
        ("speedtest-cli", "Apache 2.0"),
        ("urllib3", "MIT"),
    ]
    
    pdf.set_font('Helvetica', '', 9)
    for name, lic in all_licenses:
        pdf.cell(60, 6, name)
        pdf.cell(0, 6, lic)
        pdf.ln()
    
    # Save PDF
    output_path = os.path.join(os.path.dirname(__file__), 'NetTools_Compliance_Report.pdf')
    pdf.output(output_path)
    print(f"Compliance report generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_report()
