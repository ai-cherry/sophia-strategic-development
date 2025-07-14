#!/usr/bin/env python3
"""

# Modern stack imports
from backend.services.unified_memory_service_primary import UnifiedMemoryService
from backend.services.lambda_labs_serverless_service import LambdaLabsServerlessService
import redis.asyncio as redis
import asyncpg

Sophia AI HubSpot Unified MCP Server
Provides CRM operations and business intelligence
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

import httpx
from base.unified_standardized_base import (
    ServerConfig,
)
from base.unified_standardized_base import (
    UnifiedStandardizedMCPServer as StandardizedMCPServer,
)
from mcp.types import TextContent, Tool

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


class HubSpotUnifiedMCPServer(StandardizedMCPServer):
    """HubSpot Unified MCP Server for CRM operations"""

    def __init__(self):
        config = ServerConfig(
            name="hubspot_unified",
            version="1.0.0",
            description="CRM operations and business intelligence",
        )
        super().__init__(config)

        # HubSpot configuration
        self.api_key = get_config_value("hubspot_api_key")
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }


        # Initialize modern stack services
        self.memory_service = UnifiedMemoryService()
        self.lambda_gpu = LambdaLabsServerlessService()
        self.redis = redis.Redis(host='localhost', port=6379)

    async def get_custom_tools(self) -> list[Tool]:
        """Define custom tools for HubSpot operations"""
        return [
            Tool(
                name="list_contacts",
                description="List contacts with filters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of contacts to return",
                            "default": 10,
                        },
                        "properties": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Properties to include",
                        },
                    },
                },
            ),
            Tool(
                name="get_contact",
                description="Get contact details by ID or email",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "contact_id": {
                            "type": "string",
                            "description": "Contact ID or email",
                        }
                    },
                    "required": ["contact_id"],
                },
            ),
            Tool(
                name="search_contacts",
                description="Search contacts by query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "filters": {
                            "type": "object",
                            "description": "Additional filters",
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="list_deals",
                description="List deals with filters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pipeline": {"type": "string", "description": "Pipeline ID"},
                        "stage": {"type": "string", "description": "Deal stage"},
                        "limit": {
                            "type": "integer",
                            "description": "Number of deals",
                            "default": 10,
                        },
                    },
                },
            ),
            Tool(
                name="get_deal",
                description="Get deal details",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "deal_id": {"type": "string", "description": "Deal ID"}
                    },
                    "required": ["deal_id"],
                },
            ),
            Tool(
                name="get_company",
                description="Get company details",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "company_id": {
                            "type": "string",
                            "description": "Company ID or domain",
                        }
                    },
                    "required": ["company_id"],
                },
            ),
            Tool(
                name="get_analytics",
                description="Get CRM analytics and metrics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "metric_type": {
                            "type": "string",
                            "description": "Type of metric (deals, contacts, revenue)",
                            "enum": ["deals", "contacts", "revenue", "pipeline"],
                        },
                        "time_period": {
                            "type": "string",
                            "description": "Time period (today, week, month, quarter)",
                            "default": "month",
                        },
                    },
                    "required": ["metric_type"],
                },
            ),
        ]

    async def handle_custom_tool(self, name: str, arguments: dict) -> list[TextContent]:
        """Handle custom tool calls"""
        try:
            if name == "list_contacts":
                return await self._list_contacts(arguments)
            elif name == "get_contact":
                return await self._get_contact(arguments["contact_id"])
            elif name == "search_contacts":
                return await self._search_contacts(arguments)
            elif name == "list_deals":
                return await self._list_deals(arguments)
            elif name == "get_deal":
                return await self._get_deal(arguments["deal_id"])
            elif name == "get_company":
                return await self._get_company(arguments["company_id"])
            elif name == "get_analytics":
                return await self._get_analytics(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Error handling tool {name}: {e}")
            return [TextContent(type="text", text=f"Error: {e!s}")]

    async def _list_contacts(self, params: dict) -> list[TextContent]:
        """List contacts"""
        try:
            limit = params.get("limit", 10)
            properties = params.get(
                "properties", ["email", "firstname", "lastname", "company"]
            )

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/crm/v3/objects/contacts",
                    headers=self.headers,
                    params={"limit": limit, "properties": ",".join(properties)},
                )
                response.raise_for_status()

            data = response.json()
            contacts = data.get("results", [])

            result = f"Found {len(contacts)} contacts:\n\n"
            for contact in contacts:
                props = contact.get("properties", {})
                result += (
                    f"- {props.get('firstname', '')} {props.get('lastname', '')}\n"
                )
                result += f"  Email: {props.get('email', 'N/A')}\n"
                result += f"  Company: {props.get('company', 'N/A')}\n"
                result += f"  ID: {contact.get('id')}\n\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error listing contacts: {e}")
            return [TextContent(type="text", text=f"Error listing contacts: {e!s}")]

    async def _get_contact(self, contact_id: str) -> list[TextContent]:
        """Get contact details"""
        try:
            # Determine if it's an email or ID
            endpoint = f"{self.base_url}/crm/v3/objects/contacts/"
            if "@" in contact_id:
                endpoint += f"email:{contact_id}"
            else:
                endpoint += contact_id

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers,
                    params={
                        "properties": "email,firstname,lastname,company,phone,lifecyclestage"
                    },
                )
                response.raise_for_status()

            contact = response.json()
            props = contact.get("properties", {})

            result = "Contact Details:\n\n"
            result += (
                f"Name: {props.get('firstname', '')} {props.get('lastname', '')}\n"
            )
            result += f"Email: {props.get('email', 'N/A')}\n"
            result += f"Company: {props.get('company', 'N/A')}\n"
            result += f"Phone: {props.get('phone', 'N/A')}\n"
            result += f"Lifecycle Stage: {props.get('lifecyclestage', 'N/A')}\n"
            result += f"ID: {contact.get('id')}\n"
            result += f"Created: {contact.get('createdAt', 'N/A')}\n"
            result += f"Updated: {contact.get('updatedAt', 'N/A')}\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error getting contact: {e}")
            return [TextContent(type="text", text=f"Error getting contact: {e!s}")]

    async def _search_contacts(self, params: dict) -> list[TextContent]:
        """Search contacts"""
        try:
            query = params["query"]
            filters = params.get("filters", {})

            search_request = {
                "query": query,
                "limit": 10,
                "properties": ["email", "firstname", "lastname", "company"],
            }

            if filters:
                search_request["filterGroups"] = [{"filters": filters}]

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/crm/v3/objects/contacts/search",
                    headers=self.headers,
                    json=search_request,
                )
                response.raise_for_status()

            data = response.json()
            contacts = data.get("results", [])

            result = f"Found {data.get('total', 0)} contacts matching '{query}':\n\n"
            for contact in contacts:
                props = contact.get("properties", {})
                result += (
                    f"- {props.get('firstname', '')} {props.get('lastname', '')}\n"
                )
                result += f"  Email: {props.get('email', 'N/A')}\n"
                result += f"  Company: {props.get('company', 'N/A')}\n\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error searching contacts: {e}")
            return [TextContent(type="text", text=f"Error searching contacts: {e!s}")]

    async def _list_deals(self, params: dict) -> list[TextContent]:
        """List deals"""
        try:
            limit = params.get("limit", 10)

            query_params = {
                "limit": limit,
                "properties": "dealname,amount,dealstage,closedate,pipeline",
            }

            # Add filters if provided
            filters = []
            if "pipeline" in params:
                filters.append(
                    {
                        "propertyName": "pipeline",
                        "operator": "EQ",
                        "value": params["pipeline"],
                    }
                )
            if "stage" in params:
                filters.append(
                    {
                        "propertyName": "dealstage",
                        "operator": "EQ",
                        "value": params["stage"],
                    }
                )

            async with httpx.AsyncClient() as client:
                if filters:
                    # Use search endpoint for filtering
                    response = await client.post(
                        f"{self.base_url}/crm/v3/objects/deals/search",
                        headers=self.headers,
                        json={
                            "filterGroups": [{"filters": filters}],
                            "limit": limit,
                            "properties": [
                                "dealname",
                                "amount",
                                "dealstage",
                                "closedate",
                                "pipeline",
                            ],
                        },
                    )
                else:
                    # Use list endpoint
                    response = await client.get(
                        f"{self.base_url}/crm/v3/objects/deals",
                        headers=self.headers,
                        params=query_params,
                    )
                response.raise_for_status()

            data = response.json()
            deals = data.get("results", [])

            result = f"Found {len(deals)} deals:\n\n"
            for deal in deals:
                props = deal.get("properties", {})
                result += f"- {props.get('dealname', 'Unnamed Deal')}\n"
                result += f"  Amount: ${props.get('amount', '0')}\n"
                result += f"  Stage: {props.get('dealstage', 'N/A')}\n"
                result += f"  Close Date: {props.get('closedate', 'N/A')}\n"
                result += f"  ID: {deal.get('id')}\n\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error listing deals: {e}")
            return [TextContent(type="text", text=f"Error listing deals: {e!s}")]

    async def _get_deal(self, deal_id: str) -> list[TextContent]:
        """Get deal details"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/crm/v3/objects/deals/{deal_id}",
                    headers=self.headers,
                    params={
                        "properties": "dealname,amount,dealstage,closedate,pipeline,hs_object_id"
                    },
                )
                response.raise_for_status()

            deal = response.json()
            props = deal.get("properties", {})

            result = "Deal Details:\n\n"
            result += f"Name: {props.get('dealname', 'Unnamed Deal')}\n"
            result += f"Amount: ${props.get('amount', '0')}\n"
            result += f"Stage: {props.get('dealstage', 'N/A')}\n"
            result += f"Pipeline: {props.get('pipeline', 'N/A')}\n"
            result += f"Close Date: {props.get('closedate', 'N/A')}\n"
            result += f"ID: {deal.get('id')}\n"
            result += f"Created: {deal.get('createdAt', 'N/A')}\n"
            result += f"Updated: {deal.get('updatedAt', 'N/A')}\n"

            # Get associated contacts
            try:
                assoc_response = await client.get(
                    f"{self.base_url}/crm/v3/objects/deals/{deal_id}/associations/contacts",
                    headers=self.headers,
                )
                if assoc_response.status_code == 200:
                    associations = assoc_response.json().get("results", [])
                    if associations:
                        result += f"\nAssociated Contacts: {len(associations)}\n"
            except:
                pass

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error getting deal: {e}")
            return [TextContent(type="text", text=f"Error getting deal: {e!s}")]

    async def _get_company(self, company_id: str) -> list[TextContent]:
        """Get company details"""
        try:
            # Determine if it's a domain or ID
            endpoint = f"{self.base_url}/crm/v3/objects/companies/"
            if "." in company_id and "@" not in company_id:
                # Likely a domain
                endpoint += f"domain:{company_id}"
            else:
                endpoint += company_id

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers,
                    params={
                        "properties": "name,domain,industry,numberofemployees,annualrevenue,city,state,country"
                    },
                )
                response.raise_for_status()

            company = response.json()
            props = company.get("properties", {})

            result = "Company Details:\n\n"
            result += f"Name: {props.get('name', 'N/A')}\n"
            result += f"Domain: {props.get('domain', 'N/A')}\n"
            result += f"Industry: {props.get('industry', 'N/A')}\n"
            result += f"Employees: {props.get('numberofemployees', 'N/A')}\n"
            result += f"Annual Revenue: ${props.get('annualrevenue', 'N/A')}\n"
            result += f"Location: {props.get('city', '')}, {props.get('state', '')} {props.get('country', '')}\n"
            result += f"ID: {company.get('id')}\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error getting company: {e}")
            return [TextContent(type="text", text=f"Error getting company: {e!s}")]

    async def _get_analytics(self, params: dict) -> list[TextContent]:
        """Get CRM analytics"""
        try:
            metric_type = params["metric_type"]
            time_period = params.get("time_period", "month")

            # Calculate date range
            end_date = datetime.now()
            if time_period == "today":
                start_date = end_date.replace(hour=0, minute=0, second=0)
            elif time_period == "week":
                start_date = end_date - timedelta(days=7)
            elif time_period == "month":
                start_date = end_date - timedelta(days=30)
            elif time_period == "quarter":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)

            result = f"CRM Analytics - {metric_type.title()} ({time_period}):\n\n"

            async with httpx.AsyncClient() as client:
                if metric_type == "deals":
                    # Get deal metrics
                    response = await client.post(
                        f"{self.base_url}/crm/v3/objects/deals/search",
                        headers=self.headers,
                        json={
                            "filterGroups": [
                                {
                                    "filters": [
                                        {
                                            "propertyName": "createdate",
                                            "operator": "GTE",
                                            "value": int(start_date.timestamp() * 1000),
                                        }
                                    ]
                                }
                            ],
                            "properties": ["amount", "dealstage", "closedate"],
                            "limit": 100,
                        },
                    )
                    response.raise_for_status()

                    deals = response.json().get("results", [])
                    total_value = sum(
                        float(d.get("properties", {}).get("amount", 0) or 0)
                        for d in deals
                    )
                    stages = {}
                    for deal in deals:
                        stage = deal.get("properties", {}).get("dealstage", "Unknown")
                        stages[stage] = stages.get(stage, 0) + 1

                    result += f"Total Deals: {len(deals)}\n"
                    result += f"Total Value: ${total_value:,.2f}\n"
                    result += f"Average Deal Size: ${total_value/len(deals):,.2f}\n\n"
                    result += "Deals by Stage:\n"
                    for stage, count in sorted(
                        stages.items(), key=lambda x: x[1], reverse=True
                    ):
                        result += f"  {stage}: {count}\n"

                elif metric_type == "contacts":
                    # Get contact metrics
                    response = await client.post(
                        f"{self.base_url}/crm/v3/objects/contacts/search",
                        headers=self.headers,
                        json={
                            "filterGroups": [
                                {
                                    "filters": [
                                        {
                                            "propertyName": "createdate",
                                            "operator": "GTE",
                                            "value": int(start_date.timestamp() * 1000),
                                        }
                                    ]
                                }
                            ],
                            "properties": ["lifecyclestage"],
                            "limit": 100,
                        },
                    )
                    response.raise_for_status()

                    contacts = response.json().get("results", [])
                    stages = {}
                    for contact in contacts:
                        stage = contact.get("properties", {}).get(
                            "lifecyclestage", "Unknown"
                        )
                        stages[stage] = stages.get(stage, 0) + 1

                    result += f"New Contacts: {len(contacts)}\n\n"
                    result += "Contacts by Lifecycle Stage:\n"
                    for stage, count in sorted(
                        stages.items(), key=lambda x: x[1], reverse=True
                    ):
                        result += f"  {stage}: {count}\n"

                elif metric_type == "revenue":
                    # Get revenue metrics
                    result += "Revenue metrics would require custom properties or integration with deals data.\n"
                    result += "This is a placeholder for revenue analytics.\n"

                elif metric_type == "pipeline":
                    # Get pipeline metrics
                    response = await client.get(
                        f"{self.base_url}/crm/v3/pipelines/deals", headers=self.headers
                    )
                    response.raise_for_status()

                    pipelines = response.json().get("results", [])
                    result += f"Total Pipelines: {len(pipelines)}\n\n"
                    for pipeline in pipelines:
                        result += f"Pipeline: {pipeline.get('label')}\n"
                        stages = pipeline.get("stages", [])
                        result += f"  Stages: {len(stages)}\n"
                        for stage in stages[:5]:  # Show first 5 stages
                            result += f"    - {stage.get('label')}\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return [TextContent(type="text", text=f"Error getting analytics: {e!s}")]


# Main entry point
async def main():
    """Main entry point"""
    server = HubSpotUnifiedMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
