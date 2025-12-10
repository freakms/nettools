"""
DNSDumpster API Integration
Domain reconnaissance and subdomain enumeration
"""

import requests
from bs4 import BeautifulSoup
import re


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
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
            
            # Parse results
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if we got blocked or error page
            if 'blocked' in response.text.lower() or 'captcha' in response.text.lower():
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
                
                header_text = header.get_text().strip().lower()
                
                # Parse DNS Records (A records / Hosts)
                if 'dns records' in header_text or 'host records' in header_text:
                    rows = table.find_all('tr')[1:]  # Skip header
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 3:
                            host = cols[0].get_text().strip()
                            ip = cols[1].get_text().strip()
                            provider = cols[2].get_text().strip() if len(cols) > 2 else "Unknown"
                            
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
                            mx = cols[0].get_text().strip()
                            ip = cols[1].get_text().strip()
                            provider = cols[2].get_text().strip() if len(cols) > 2 else "Unknown"
                            
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
                            txt = cols[0].get_text().strip()
                            if txt:
                                results["dns_records"]["txt"].append(txt)
                
                # Parse NS Records (Name Servers)
                elif 'name servers' in header_text or 'ns records' in header_text:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            ns = cols[0].get_text().strip()
                            ip = cols[1].get_text().strip()
                            
                            if ns:
                                results["dns_records"]["ns"].append({
                                    "ns": ns,
                                    "ip": ip
                                })
            
            # Get statistics
            stats_div = soup.find('div', {'class': 'col-md-12'})
            if stats_div:
                text = stats_div.get_text()
                
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
