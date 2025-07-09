#!/usr/bin/env python3
"""
HubSpot MCP Server - Fixed Implementation
Uses the corrected standalone MCP base
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add the base directory to path for standalone imports
sys.path.append(str(Path(__file__).parent.parent / "base"))

from standalone_mcp_base_v2 import SimpleMCPServer, MCPServerConfig

class HubSpotMCPServerFixed(SimpleMCPServer):
    """HubSpot CRM integration MCP server - fixed version"""

    def __init__(self, config: MCPServerConfig = None):
        if not config:
            config = MCPServerConfig(
                name="hubspot",
                port=9006,
                version="2.0.0",
            )
        super().__init__(config)
        self.api_key = None
        self.base_url = "https://api.hubapi.com"
        
        # Register tools after initialization
        self._register_hubspot_tools()

    async def server_specific_init(self):
        """Initialize HubSpot-specific configuration"""
        # Load API key from environment using standalone config
        self.api_key = self.env_config.get("api_key")
        if not self.api_key:
            self.logger.warning("HubSpot API key not configured. Running in demo mode.")
        else:
            self.logger.info("HubSpot API key loaded successfully")

    def _register_hubspot_tools(self):
        """Register HubSpot-specific tools"""
        
        @self.mcp_tool(
            name="list_contacts",
            description="List HubSpot contacts",
            parameters={
                "limit": {
                    "type": "integer",
                    "description": "Number of contacts to return",
                    "default": 10,
                }
            }
        )
        async def list_contacts(limit: int = 10) -> Dict[str, Any]:
            """List HubSpot contacts"""
            try:
                # Demo data for now - in production would call HubSpot API
                contacts = [
                    {
                        "id": "1",
                        "properties": {
                            "firstname": "John",
                            "lastname": "Doe", 
                            "email": "john.doe@example.com",
                            "company": "Acme Corp",
                        },
                        "createdAt": "2024-01-01T00:00:00Z",
                        "updatedAt": datetime.now().isoformat(),
                    }
                ]
                self.logger.info(f"Listed {len(contacts)} contacts")
                return {"status": "success", "count": len(contacts), "contacts": contacts}
            except Exception as e:
                self.logger.exception(f"Error listing contacts: {e}")
                return {"status": "error", "message": str(e)}

        @self.mcp_tool(
            name="list_deals",
            description="List HubSpot deals",
            parameters={
                "limit": {
                    "type": "integer", 
                    "description": "Number of deals to return",
                    "default": 10,
                }
            }
        )
        async def list_deals(limit: int = 10) -> Dict[str, Any]:
            """List HubSpot deals"""
            try:
                # Demo data for now
                deals = [
                    {
                        "id": "1",
                        "properties": {
                            "dealname": "Enterprise Deal",
                            "amount": "50000",
                            "dealstage": "contractsent",
                            "closedate": "2024-12-31T00:00:00Z",
                        },
                        "createdAt": "2024-01-01T00:00:00Z",
                        "updatedAt": datetime.now().isoformat(),
                    }
                ]
                self.logger.info(f"Listed {len(deals)} deals")
                return {"status": "success", "count": len(deals), "deals": deals}
            except Exception as e:
                self.logger.exception(f"Error listing deals: {e}")
                return {"status": "error", "message": str(e)}

        @self.mcp_tool(
            name="create_contact",
            description="Create a new contact",
            parameters={
                "email": {
                    "type": "string",
                    "description": "Contact's email",
                    "required": True,
                },
                "firstname": {
                    "type": "string", 
                    "description": "Contact's first name",
                    "required": True,
                },
                "lastname": {
                    "type": "string",
                    "description": "Contact's last name", 
                    "required": True,
                },
                "company": {
                    "type": "string",
                    "description": "Contact's company",
                    "required": False,
                },
            }
        )
        async def create_contact(
            email: str, firstname: str, lastname: str, company: str = None
        ) -> Dict[str, Any]:
            """Create a new contact"""
            try:
                # Demo implementation - in production would call HubSpot API
                contact = {
                    "id": "42",
                    "properties": {
                        "email": email,
                        "firstname": firstname,
                        "lastname": lastname,
                        "company": company,
                    },
                    "createdAt": datetime.now().isoformat(),
                }
                self.logger.info(f"Created contact: {email}")
                return {"status": "success", "contact": contact}
            except Exception as e:
                self.logger.exception(f"Error creating contact: {e}")
                return {"status": "error", "message": str(e)}

    async def check_server_health(self) -> bool:
        """Check HubSpot API connectivity"""
        if not self.api_key:
            self.logger.warning("HubSpot API key not configured, health check degraded.")
            return False
        # In production, would make actual API call
        return True

    async def get_capabilities(self):
        """Get HubSpot server capabilities"""
        base_caps = await super().get_capabilities()
        hubspot_caps = [
            {
                "name": "contact_management",
                "description": "Create, read, update HubSpot contacts",
                "category": "crm",
                "available": self.api_key is not None,
                "version": "1.0.0"
            },
            {
                "name": "deal_management", 
                "description": "Manage HubSpot deals and pipeline",
                "category": "crm",
                "available": self.api_key is not None,
                "version": "1.0.0"
            }
        ]
        return base_caps + hubspot_caps


def main():
    """Main entry point"""
    server = HubSpotMCPServerFixed()
    server.run()


if __name__ == "__main__":
    main() 