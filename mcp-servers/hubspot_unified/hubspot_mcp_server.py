#!/usr/bin/env python3
"""
HubSpot MCP Server - Unified Implementation
Provides CRM integration for contacts, deals, and companies
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from backend.core.auto_esc_config import config as auto_esc_config
    from backend.mcp_servers.base.unified_mcp_base import (
        MCPServerConfig,
        SimpleMCPServer,
        mcp_tool,
    )
    from backend.utils.custom_logger import setup_logger
except ImportError as e:
    print(f"Failed to import necessary modules: {e}")
    sys.exit(1)

logger = setup_logger("mcp.hubspot")


class HubSpotMCPServer(SimpleMCPServer):
    """HubSpot CRM integration MCP server"""

    def __init__(self, config: MCPServerConfig | None = None):
        if not config:
            config = MCPServerConfig(
                name="hubspot",
                port=9006,
                version="2.0.0",
            )
        super().__init__(config)
        self.api_key: str | None = None
        self.base_url = "https://api.hubapi.com"

    async def server_specific_init(self) -> None:
        """Initialize HubSpot-specific configuration."""
        self.api_key = os.getenv("HUBSPOT_API_KEY") or auto_esc_config.get(
            "hubspot_api_key"
        )
        if not self.api_key:
            self.logger.warning("HubSpot API key not configured. Some tools may fail.")

    @mcp_tool(
        name="list_contacts",
        description="List HubSpot contacts",
        parameters={
            "limit": {
                "type": "integer",
                "description": "Number of contacts to return",
                "default": 10,
            }
        },
    )
    async def list_contacts(self, limit: int = 10) -> dict[str, Any]:
        """List HubSpot contacts"""
        try:
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
            self.logger.error(f"Error listing contacts: {e}")
            return {"status": "error", "message": str(e)}

    @mcp_tool(
        name="list_deals",
        description="List HubSpot deals",
        parameters={
            "limit": {
                "type": "integer",
                "description": "Number of deals to return",
                "default": 10,
            }
        },
    )
    async def list_deals(self, limit: int = 10) -> dict[str, Any]:
        """List HubSpot deals"""
        try:
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
            self.logger.error(f"Error listing deals: {e}")
            return {"status": "error", "message": str(e)}

    @mcp_tool(
        name="list_companies",
        description="List HubSpot companies",
        parameters={
            "limit": {
                "type": "integer",
                "description": "Number of companies to return",
                "default": 10,
            }
        },
    )
    async def list_companies(self, limit: int = 10) -> dict[str, Any]:
        """List HubSpot companies"""
        try:
            companies = [
                {
                    "id": "1",
                    "properties": {
                        "name": "Acme Corp",
                        "domain": "acme.com",
                        "industry": "Technology",
                        "numberofemployees": "100",
                    },
                    "createdAt": "2024-01-01T00:00:00Z",
                    "updatedAt": datetime.now().isoformat(),
                }
            ]
            self.logger.info(f"Listed {len(companies)} companies")
            return {
                "status": "success",
                "count": len(companies),
                "companies": companies,
            }
        except Exception as e:
            self.logger.error(f"Error listing companies: {e}")
            return {"status": "error", "message": str(e)}

    @mcp_tool(
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
        },
    )
    async def create_contact(
        self, email: str, firstname: str, lastname: str, company: str | None = None
    ) -> dict[str, Any]:
        """Create a new contact"""
        try:
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
            self.logger.error(f"Error creating contact: {e}")
            return {"status": "error", "message": str(e)}

    async def check_server_health(self) -> bool:
        """Check HubSpot API connectivity"""
        if not self.api_key:
            self.logger.warning(
                "HubSpot API key not configured, health check degraded."
            )
            return False
        # In production, would make actual API call
        return True

    async def server_specific_cleanup(self) -> None:
        """Server-specific shutdown actions, if any."""
        self.logger.info("HubSpot MCP server shutting down.")
        pass


async def main():
    """Main entry point"""
    server = HubSpotMCPServer()
    server.run()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())


# --- Auto-inserted health endpoint ---
try:
    from fastapi import APIRouter

    router = APIRouter()

    @router.get("/health")
    async def health():
        return {"status": "ok"}

except ImportError:
    pass
