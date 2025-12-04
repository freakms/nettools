"""
phpIPAM Tool Module
Simplified interface for phpIPAM integration
"""

import sys
import os

# Add parent directory to path to import phpipam_client
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phpipam_client import PHPIPAMClient
from phpipam_config import PHPIPAMConfig


class PHPIPAMTool:
    """Simplified phpIPAM tool interface"""
    
    def __init__(self):
        """Initialize phpIPAM tool"""
        self.config = PHPIPAMConfig()
        self.client = None
    
    def get_client(self):
        """Get or create phpIPAM client instance"""
        if self.client is None:
            self.client = PHPIPAMClient(self.config)
        return self.client
    
    def is_configured(self):
        """
        Check if phpIPAM is configured
        
        Returns:
            bool: True if configured, False otherwise
        """
        return self.config.is_enabled() and self.config.get_phpipam_url() and self.config.get_app_id()
    
    def test_connection(self):
        """
        Test connection to phpIPAM
        
        Returns:
            tuple: (success, message)
        """
        if not self.is_configured():
            return False, "phpIPAM not configured. Please configure phpIPAM settings first."
        
        client = self.get_client()
        return client.test_connection()
    
    def authenticate(self, username, password):
        """
        Authenticate with phpIPAM
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            tuple: (success, message)
        """
        if not self.is_configured():
            return False, "phpIPAM not configured"
        
        client = self.get_client()
        return client.authenticate(username, password)
    
    def search_ip(self, ip_address):
        """
        Search for IP address in phpIPAM
        
        Args:
            ip_address (str): IP address to search
            
        Returns:
            tuple: (success, data)
        """
        if not self.is_configured():
            return False, "phpIPAM not configured"
        
        client = self.get_client()
        
        if not client.token:
            return False, "Not authenticated. Please login first."
        
        return client.search_address(ip_address)
    
    def get_subnets(self):
        """
        Get all subnets from phpIPAM
        
        Returns:
            tuple: (success, data)
        """
        if not self.is_configured():
            return False, "phpIPAM not configured"
        
        client = self.get_client()
        
        if not client.token:
            return False, "Not authenticated. Please login first."
        
        return client.get_subnets()
    
    def get_subnet_addresses(self, subnet_id):
        """
        Get addresses for a specific subnet
        
        Args:
            subnet_id (int): Subnet ID
            
        Returns:
            tuple: (success, data)
        """
        if not self.is_configured():
            return False, "phpIPAM not configured"
        
        client = self.get_client()
        
        if not client.token:
            return False, "Not authenticated. Please login first."
        
        return client.get_subnet_addresses(subnet_id)
    
    def is_authenticated(self):
        """
        Check if currently authenticated
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        if not self.client:
            return False
        return bool(self.client.token)
    
    def get_config(self):
        """
        Get phpIPAM configuration
        
        Returns:
            PHPIPAMConfig: Configuration object
        """
        return self.config
    
    def update_config(self, url=None, app_id=None, api_key=None, ssl_verify=None):
        """
        Update phpIPAM configuration
        
        Args:
            url (str): phpIPAM URL
            app_id (str): App ID
            api_key (str): API key
            ssl_verify (bool): SSL verification
            
        Returns:
            bool: True if updated successfully
        """
        try:
            if url:
                self.config.set_phpipam_url(url)
            if app_id:
                self.config.set_app_id(app_id)
            if api_key:
                self.config.set_api_key(api_key)
            if ssl_verify is not None:
                self.config.set_ssl_verify(ssl_verify)
            
            # Reset client to pick up new config
            self.client = None
            
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def validate_ip(ip_address):
        """
        Validate IP address format
        
        Args:
            ip_address (str): IP address to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        import ipaddress
        try:
            ipaddress.ip_address(ip_address)
            return True
        except:
            return False
