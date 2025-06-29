"""
Enhanced API Authentication for MCP Servers
Provides secure authentication for all external services
"""

import os
import logging
from typing import Dict, Optional
from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

class MCPAuthenticator:
    """Centralized authentication for MCP servers"""
    
    def __init__(self):
        self.credentials = self._load_credentials()
    
    def _load_credentials(self) -> Dict[str, str]:
        """Load all API credentials from Pulumi ESC"""
        
        credentials = {
            # Snowflake
            'snowflake_password': get_config_value('snowflake.password', ''),
            
            # HubSpot
            'hubspot_api_key': get_config_value('hubspot.api_key', ''),
            
            # Slack
            'slack_bot_token': get_config_value('slack.bot_token', ''),
            'slack_app_token': get_config_value('slack.app_token', ''),
            
            # GitHub
            'github_access_token': get_config_value('github.access_token', ''),
            
            # Notion
            'notion_api_token': get_config_value('notion.api_token', ''),
            
            # OpenAI (for AI features)
            'openai_api_key': get_config_value('openai.api_key', ''),
            
            # Pinecone (for vector search)
            'pinecone_api_key': get_config_value('pinecone.api_key', ''),
        }
        
        # Log which credentials are available (without exposing values)
        for key, value in credentials.items():
            status = "✅ Available" if value else "❌ Missing"
            logger.info(f"   {key}: {status}")
        
        return credentials
    
    def get_credential(self, service: str, credential_type: str = 'api_key') -> Optional[str]:
        """Get credential for a specific service"""
        key = f"{service}_{credential_type}"
        return self.credentials.get(key)
    
    def is_service_configured(self, service: str) -> bool:
        """Check if a service has required credentials"""
        
        required_creds = {
            'snowflake': ['password'],
            'hubspot': ['api_key'],
            'slack': ['bot_token'],
            'github': ['access_token'],
            'notion': ['api_token']
        }
        
        if service not in required_creds:
            return False
        
        for cred_type in required_creds[service]:
            if not self.get_credential(service, cred_type):
                return False
        
        return True
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get configuration status for all services"""
        services = ['snowflake', 'hubspot', 'slack', 'github', 'notion']
        return {service: self.is_service_configured(service) for service in services}

# Global authenticator instance
mcp_auth = MCPAuthenticator()
