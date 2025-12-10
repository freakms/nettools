"""
DNSDumpster API Integration
Domain reconnaissance and subdomain enumeration
"""

import requests
from bs4 import BeautifulSoup
import re


def get_proper_encoding(response):
    """
    Determine the proper encoding for a response.
    Tries multiple methods to detect the correct encoding.
    """
    # Method 1: Check Content-Type header for charset
    content_type = response.headers.get('Content-Type', '')
    if 'charset=' in content_type:
        charset = content_type.split('charset=')[-1].split(';')[0].strip()
        if charset:
            return charset
    
    # Method 2: Check for encoding in HTML meta tags
    # Look at raw bytes for meta charset
    raw_content = response.content[:2048]  # Check first 2KB
    
    # Look for <meta charset="...">
    meta_charset = re.search(rb'<meta[^>]+charset=["\']?([^"\'\s>]+)', raw_content, re.IGNORECASE)
    if meta_charset:
        return meta_charset.group(1).decode('ascii', errors='ignore')
    
    # Look for <meta http-equiv="Content-Type" content="...charset=...">
    meta_content_type = re.search(rb'<meta[^>]+content=["\'][^"\']*charset=([^"\'\s;]+)', raw_content, re.IGNORECASE)
    if meta_content_type:
        return meta_content_type.group(1).decode('ascii', errors='ignore')
    
    # Method 3: Use requests' apparent_encoding (uses chardet internally if available)
    if response.apparent_encoding and response.apparent_encoding.lower() != 'ascii':
        return response.apparent_encoding
    
    # Method 4: Default to utf-8 (most common for modern web)
    return 'utf-8'


def decode_response(response):
    """
    Safely decode response content with proper encoding detection.
    Returns decoded text.
    """
    encoding = get_proper_encoding(response)
    
    # Try the detected encoding first
    try:
        return response.content.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        pass
    
    # Fallback encodings to try
    fallback_encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'latin-1']
    
    for enc in fallback_encodings:
        if enc.lower() != encoding.lower():
            try:
                return response.content.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue
    
    # Last resort: decode with errors='ignore' to strip problematic chars
    return response.content.decode('utf-8', errors='ignore')


def sanitize_text(text):
    """
    Clean text by removing or replacing problematic characters.
    Ensures the output is clean displayable text.
    """
    if not text:
        return text
    
    # Replace common problematic characters
    replacements = {
        '\ufffd': '',  # Unicode replacement character
        '\x00': '',    # Null character
        '\r': '',      # Carriage return (normalize to just \n)
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove any remaining non-printable characters except newlines and tabs
    cleaned = ''.join(
        char for char in text 
        if char.isprintable() or char in '\n\t'
    )
    
    # Normalize whitespace
    cleaned = ' '.join(cleaned.split())
    
    return cleaned.strip()


class DNSDumpster:
    """DNSDumpster API for domain reconnaissance"""
    
    BASE_URL = "https://dnsdumpster.com/"
    
    @staticmethod
    def lookup(domain):
        """
        Perform DNSDumpster lookup for a domain
        
        Args:
            domain (str): Domain name to lookup (e.g., example.com)
            
        Returns:
            dict: DNSDumpster results including subdomains, DNS records, etc.
        """
        try:
            # Create session with proper headers
            session = requests.Session()
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Get initial page to retrieve CSRF token
            response = session.get(DNSDumpster.BASE_URL, headers=headers, timeout=30)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to load DNSDumpster page (HTTP {response.status_code})",
                    "domain": domain
                }
            
            # Decode response with proper encoding detection
            html_text = decode_response(response)
            
            # Parse HTML
            soup = BeautifulSoup(html_text, 'html.parser')
            
            # Try multiple methods to find CSRF token
            csrf_token = None
            
            # Method 1: Look for input field
            csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
            
            # Method 2: Look in cookies
            if not csrf_token:
                if 'csrftoken' in session.cookies:
                    csrf_token = session.cookies['csrftoken']
            
            # Method 3: Look for any hidden input with csrf
            if not csrf_token:
                for input_tag in soup.find_all('input', {'type': 'hidden'}):
                    if 'csrf' in input_tag.get('name', '').lower():
                        csrf_token = input_tag.get('value')
                        break
            
            if not csrf_token:
                # Provide more helpful error
                return {
                    "success": False,
                    "error": "DNSDumpster might be blocking automated requests or has changed its structure.\n\n" +
                            "Alternative: Visit https://dnsdumpster.com directly in your browser.",
                    "domain": domain,
                    "debug": "CSRF token not found in page or cookies"
                }
            
            # Prepare POST data
            data = {
                'csrfmiddlewaretoken': csrf_token,
                'targetip': domain,
                'user': 'free'
            }
            
            # Update headers for POST
            headers.update({
                'Referer': DNSDumpster.BASE_URL,
                'Origin': 'https://dnsdumpster.com',
                'Content-Type': 'application/x-www-form-urlencoded'
            })
            
            # Add CSRF token to cookies if not present
            if 'csrftoken' not in session.cookies:
                session.cookies.set('csrftoken', csrf_token)
            
            # Make POST request
            response = session.post(
                DNSDumpster.BASE_URL,
                data=data,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"DNSDumpster returned HTTP {response.status_code}",
                    "domain": domain
                }
            
            # Decode response with proper encoding detection
            html_text = decode_response(response)
            
            # Parse results
            soup = BeautifulSoup(html_text, 'html.parser')
            
            # Check if we got blocked or error page
            if 'blocked' in html_text.lower() or 'captcha' in html_text.lower():
                return {
                    "success": False,
                    "error": "DNSDumpster has blocked this request (rate limiting or bot detection).\n\n" +
                            "Please try again in a few minutes or visit the website directly.",
                    "domain": domain
                }
            
            results = DNSDumpster._parse_results(soup, domain)
            results["success"] = True
            results["domain"] = domain
            
            return results
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out. DNSDumpster might be slow or unreachable.",
                "domain": domain
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "domain": domain
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "domain": domain
            }
    
    @staticmethod
    def _parse_results(soup, domain):
        """Parse DNSDumpster HTML results"""
        results = {
            "dns_records": {
                "host": [],
                "mx": [],
                "txt": [],
                "ns": []
            },
            "subdomains": [],
            "statistics": {}
        }
        
        try:
            # Find all tables
            tables = soup.find_all('table', {'class': 'table'})
            
            for table in tables:
                # Check table header to determine type
                header = table.find('th')
                if not header:
                    continue
                
                header_text = sanitize_text(header.get_text()).lower()
                
                # Parse DNS Records (A records / Hosts)
                if 'dns records' in header_text or 'host records' in header_text:
                    rows = table.find_all('tr')[1:]  # Skip header
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 3:
                            host = sanitize_text(cols[0].get_text())
                            ip = sanitize_text(cols[1].get_text())
                            provider = sanitize_text(cols[2].get_text()) if len(cols) > 2 else "Unknown"
                            
                            if host and ip:
                                results["dns_records"]["host"].append({
                                    "host": host,
                                    "ip": ip,
                                    "provider": provider
                                })
                                
                                # Also add to subdomains if it's a subdomain
                                if host != domain and domain in host:
                                    results["subdomains"].append(host)
                
                # Parse MX Records
                elif 'mx records' in header_text:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 3:
                            mx = sanitize_text(cols[0].get_text())
                            ip = sanitize_text(cols[1].get_text())
                            provider = sanitize_text(cols[2].get_text()) if len(cols) > 2 else "Unknown"
                            
                            if mx:
                                results["dns_records"]["mx"].append({
                                    "mx": mx,
                                    "ip": ip,
                                    "provider": provider
                                })
                
                # Parse TXT Records
                elif 'txt records' in header_text:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if cols:
                            txt = sanitize_text(cols[0].get_text())
                            if txt:
                                results["dns_records"]["txt"].append(txt)
                
                # Parse NS Records (Name Servers)
                elif 'name servers' in header_text or 'ns records' in header_text:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            ns = sanitize_text(cols[0].get_text())
                            ip = sanitize_text(cols[1].get_text())
                            
                            if ns:
                                results["dns_records"]["ns"].append({
                                    "ns": ns,
                                    "ip": ip
                                })
            
            # Get statistics
            stats_div = soup.find('div', {'class': 'col-md-12'})
            if stats_div:
                text = sanitize_text(stats_div.get_text())
                
                # Try to extract counts
                host_match = re.search(r'(\d+)\s+host', text, re.IGNORECASE)
                if host_match:
                    results["statistics"]["total_hosts"] = int(host_match.group(1))
                
                subdomain_match = re.search(r'(\d+)\s+subdomain', text, re.IGNORECASE)
                if subdomain_match:
                    results["statistics"]["total_subdomains"] = int(subdomain_match.group(1))
            
            # Remove duplicates from subdomains
            results["subdomains"] = list(set(results["subdomains"]))
            results["subdomains"].sort()
            
        except Exception as e:
            results["parse_error"] = str(e)
        
        return results
    
    @staticmethod
    def is_available():
        """Check if DNSDumpster is accessible"""
        try:
            response = requests.get(DNSDumpster.BASE_URL, timeout=5)
            return response.status_code == 200
        except:
            return False
