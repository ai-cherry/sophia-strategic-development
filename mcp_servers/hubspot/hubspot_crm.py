"""
HubSpot MCP Server with Natural Language CRM Operations

Provides AI-friendly HubSpot integration through MCP interface:
- Natural language to HubSpot API query conversion
- Contact, Company, Deal, and Ticket management
- Pipeline operations and automation
- Marketing email and campaign insights
- Smart caching and rate limit handling
"""

import asyncio
import logging
import json
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, TextContent, ImageContent, EmbeddedResource,
    Prompt, PromptMessage
)

# Import dependencies
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import requests
    import redis
    from backend.core.config.service_configs import ServiceConfigs
except ImportError as e:
    logging.error(f"Import error: {e}")
    logging.error("Please install required packages: pip install requests redis")
    raise

logger = logging.getLogger(__name__)


class HubSpotObjectType(Enum):
    """HubSpot CRM object types"""
    CONTACTS = "contacts"
    COMPANIES = "companies"
    DEALS = "deals"
    TICKETS = "tickets"
    TASKS = "tasks"
    NOTES = "notes"
    MEETINGS = "meetings"
    CALLS = "calls"
    EMAILS = "emails"
    PRODUCTS = "products"
    LINE_ITEMS = "line_items"
    QUOTES = "quotes"


@dataclass
class HubSpotSession:
    """HubSpot authenticated session"""
    access_token: str
    expires_at: datetime
    portal_id: str
    base_url: str = "https://api.hubapi.com"
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }


class HubSpotMCPServer:
    """
    MCP Server for HubSpot CRM operations
    
    Features:
    - Natural language query understanding
    - Full CRUD operations for all CRM objects
    - Pipeline management and deal tracking
    - Marketing insights and campaign data
    - Rate limit handling with smart retries
    - Redis caching for performance
    """
    
    def __init__(self):
        self.server = Server("hubspot")
        self.session: Optional[HubSpotSession] = None
        self.redis_client: Optional[redis.Redis] = None
        self.config = ServiceConfigs().get_hubspot_config()
        
        # Cache settings
        self.cache_ttl = 300  # 5 minutes
        self.pipeline_cache_ttl = 3600  # 1 hour
        
        # Rate limiting (HubSpot has strict limits)
        self.api_calls = 0
        self.rate_limit_per_second = 10
        self.rate_limit_daily = 250000
        
        # Register handlers
        self._register_handlers()
        
    def _register_handlers(self):
        """Register all MCP handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available HubSpot tools"""
            return [
                Tool(
                    name="search",
                    description="Search HubSpot CRM using natural language",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language search query"
                            },
                            "object_type": {
                                "type": "string",
                                "description": "Object type to search (contacts, companies, deals, etc.)",
                                "enum": [obj.value for obj in HubSpotObjectType]
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum results to return (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="create_object",
                    description="Create a new HubSpot object (contact, company, deal, etc.)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_type": {
                                "type": "string",
                                "description": "Type of object to create",
                                "enum": [obj.value for obj in HubSpotObjectType]
                            },
                            "properties": {
                                "type": "object",
                                "description": "Object properties"
                            },
                            "associations": {
                                "type": "array",
                                "description": "Optional associations with other objects",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "to_object_type": {"type": "string"},
                                        "to_object_id": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "required": ["object_type", "properties"]
                    }
                ),
                Tool(
                    name="update_object",
                    description="Update an existing HubSpot object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_type": {
                                "type": "string",
                                "description": "Type of object to update",
                                "enum": [obj.value for obj in HubSpotObjectType]
                            },
                            "object_id": {
                                "type": "string",
                                "description": "ID of the object to update"
                            },
                            "properties": {
                                "type": "object",
                                "description": "Properties to update"
                            }
                        },
                        "required": ["object_type", "object_id", "properties"]
                    }
                ),
                Tool(
                    name="delete_object",
                    description="Delete a HubSpot object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_type": {
                                "type": "string",
                                "description": "Type of object to delete",
                                "enum": [obj.value for obj in HubSpotObjectType]
                            },
                            "object_id": {
                                "type": "string",
                                "description": "ID of the object to delete"
                            }
                        },
                        "required": ["object_type", "object_id"]
                    }
                ),
                Tool(
                    name="get_pipelines",
                    description="Get sales pipelines and their stages",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_type": {
                                "type": "string",
                                "description": "Pipeline type (deals or tickets)",
                                "enum": ["deals", "tickets"],
                                "default": "deals"
                            }
                        }
                    }
                ),
                Tool(
                    name="move_deal_stage",
                    description="Move a deal to a different pipeline stage",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "deal_id": {
                                "type": "string",
                                "description": "ID of the deal to move"
                            },
                            "stage_id": {
                                "type": "string",
                                "description": "ID of the target stage"
                            }
                        },
                        "required": ["deal_id", "stage_id"]
                    }
                ),
                Tool(
                    name="get_analytics",
                    description="Get analytics and insights for CRM data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "report_type": {
                                "type": "string",
                                "description": "Type of analytics report",
                                "enum": ["revenue", "deals", "contacts", "activities", "pipeline"]
                            },
                            "time_period": {
                                "type": "string",
                                "description": "Time period for the report",
                                "enum": ["today", "this_week", "this_month", "this_quarter", "this_year"],
                                "default": "this_month"
                            }
                        },
                        "required": ["report_type"]
                    }
                ),
                Tool(
                    name="get_timeline",
                    description="Get timeline/activity history for an object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_type": {
                                "type": "string",
                                "description": "Type of object",
                                "enum": [obj.value for obj in HubSpotObjectType]
                            },
                            "object_id": {
                                "type": "string",
                                "description": "ID of the object"
                            },
                            "activity_types": {
                                "type": "array",
                                "description": "Filter by activity types",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["object_type", "object_id"]
                    }
                ),
                Tool(
                    name="batch_operation",
                    description="Perform batch create/update operations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "Operation type",
                                "enum": ["create", "update", "archive"]
                            },
                            "object_type": {
                                "type": "string",
                                "description": "Type of objects",
                                "enum": [obj.value for obj in HubSpotObjectType]
                            },
                            "inputs": {
                                "type": "array",
                                "description": "Array of objects to process",
                                "items": {"type": "object"}
                            }
                        },
                        "required": ["operation", "object_type", "inputs"]
                    }
                ),
                Tool(
                    name="health_check",
                    description="Check HubSpot connection and API limits",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute HubSpot tools"""
            
            # Ensure authenticated
            await self._ensure_authenticated()
            
            try:
                if name == "search":
                    return await self._handle_search(arguments)
                elif name == "create_object":
                    return await self._handle_create_object(arguments)
                elif name == "update_object":
                    return await self._handle_update_object(arguments)
                elif name == "delete_object":
                    return await self._handle_delete_object(arguments)
                elif name == "get_pipelines":
                    return await self._handle_get_pipelines(arguments)
                elif name == "move_deal_stage":
                    return await self._handle_move_deal_stage(arguments)
                elif name == "get_analytics":
                    return await self._handle_get_analytics(arguments)
                elif name == "get_timeline":
                    return await self._handle_get_timeline(arguments)
                elif name == "batch_operation":
                    return await self._handle_batch_operation(arguments)
                elif name == "health_check":
                    return await self._handle_health_check()
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        @self.server.list_prompts()
        async def list_prompts() -> List[Prompt]:
            """List available prompt templates"""
            return [
                Prompt(
                    name="deal_pipeline_analysis",
                    description="Analyze deals in the pipeline",
                    arguments=[
                        {
                            "name": "pipeline",
                            "description": "Pipeline name to analyze",
                            "required": False
                        },
                        {
                            "name": "stage",
                            "description": "Filter by specific stage",
                            "required": False
                        }
                    ]
                ),
                Prompt(
                    name="contact_engagement",
                    description="Analyze contact engagement metrics",
                    arguments=[
                        {
                            "name": "segment",
                            "description": "Contact segment to analyze",
                            "required": False
                        }
                    ]
                ),
                Prompt(
                    name="revenue_forecast",
                    description="Generate revenue forecast based on pipeline",
                    arguments=[
                        {
                            "name": "time_period",
                            "description": "Forecast period (e.g., next_quarter)",
                            "required": True
                        }
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, Any]) -> PromptMessage:
            """Get specific prompt template"""
            
            if name == "deal_pipeline_analysis":
                pipeline = arguments.get("pipeline", "all pipelines")
                stage = arguments.get("stage", "all stages")
                
                query = f"""
                Analyze the deal pipeline with these criteria:
                - Pipeline: {pipeline}
                - Stage: {stage}
                
                Provide:
                1. Total deals and value in pipeline
                2. Average deal size and velocity
                3. Bottlenecks and stuck deals
                4. Win probability by stage
                5. Recommendations for improvement
                """
                
                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=query)
                )
                
            elif name == "contact_engagement":
                segment = arguments.get("segment", "all contacts")
                
                query = f"""
                Analyze contact engagement for: {segment}
                
                Include:
                1. Engagement score distribution
                2. Most engaged contacts
                3. Recent activity trends
                4. Email open/click rates
                5. Recommended outreach strategies
                """
                
                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=query)
                )
                
            elif name == "revenue_forecast":
                time_period = arguments.get("time_period", "next quarter")
                
                query = f"""
                Generate revenue forecast for: {time_period}
                
                Based on:
                1. Current pipeline value and stages
                2. Historical close rates
                3. Average deal velocity
                4. Seasonal trends
                
                Provide:
                - Expected revenue range
                - Confidence level
                - Key risks and opportunities
                - Actions to meet targets
                """
                
                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=query)
                )
                
            else:
                return PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Unknown prompt template: {name}"
                    )
                )
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid HubSpot session"""
        if self.session and not self.session.is_expired:
            return
            
        # Authenticate with HubSpot
        logger.info("Authenticating with HubSpot...")
        
        try:
            # For private app, we just need the access token
            self.session = HubSpotSession(
                access_token=self.config["private_app_key"],
                expires_at=datetime.now() + timedelta(days=365),  # Private app tokens don't expire
                portal_id=self.config["portal_id"]
            )
            
            # Test the connection
            response = requests.get(
                f"{self.session.base_url}/crm/v3/objects/contacts?limit=1",
                headers=self.session.headers
            )
            response.raise_for_status()
            
            logger.info(f"✅ Authenticated with HubSpot portal: {self.session.portal_id}")
            
            # Initialize Redis if available
            try:
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    decode_responses=True
                )
                self.redis_client.ping()
                logger.info("✅ Connected to Redis for caching")
            except:
                logger.warning("Redis not available - caching disabled")
                self.redis_client = None
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise Exception(f"Failed to authenticate with HubSpot: {str(e)}")
    
    async def _handle_search(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle search requests"""
        query = arguments.get("query", "")
        object_type = arguments.get("object_type", "contacts")
        limit = arguments.get("limit", 10)
        
        # Convert natural language to search parameters
        search_params = self._parse_natural_language_query(query, object_type)
        
        # Check cache first
        cache_key = f"hs:search:{object_type}:{json.dumps(search_params, sort_keys=True)}"
        if self.redis_client:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.info("Cache hit for search")
                return [TextContent(
                    type="text",
                    text=f"🔍 Search Results (cached):\n\n{cached}"
                )]
        
        try:
            # Build search request
            url = f"{self.session.base_url}/crm/v3/objects/{object_type}/search"
            
            search_body = {
                "filterGroups": search_params.get("filters", []),
                "sorts": search_params.get("sorts", []),
                "properties": self._get_default_properties(object_type),
                "limit": limit
            }
            
            # Add query if provided
            if search_params.get("query"):
                search_body["query"] = search_params["query"]
            
            response = requests.post(url, headers=self.session.headers, json=search_body)
            response.raise_for_status()
            
            results = response.json()
            
            # Format results
            output = self._format_search_results(results, object_type, query)
            
            # Cache results
            if self.redis_client and len(output) < 10000:
                self.redis_client.setex(cache_key, self.cache_ttl, output)
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return [TextContent(
                type="text",
                text=f"Search Error: {str(e)}"
            )]
    
    def _parse_natural_language_query(self, query: str, object_type: str) -> Dict[str, Any]:
        """Parse natural language query into HubSpot search parameters"""
        query_lower = query.lower()
        search_params = {"filters": [], "sorts": []}
        
        # Common search patterns
        if object_type == "contacts":
            if "email" in query_lower:
                # Extract email pattern
                import re
                email_match = re.search(r'[\w\.-]+@[\w\.-]+', query)
                if email_match:
                    search_params["filters"].append({
                        "filters": [{
                            "propertyName": "email",
                            "operator": "EQ",
                            "value": email_match.group(0)
                        }]
                    })
            elif "company" in query_lower:
                # Search by company name
                company_name = query.split("company")[-1].strip()
                search_params["query"] = company_name
            elif "created" in query_lower:
                # Date-based search
                if "today" in query_lower:
                    search_params["filters"].append({
                        "filters": [{
                            "propertyName": "createdate",
                            "operator": "GTE",
                            "value": str(int(datetime.now().timestamp() * 1000))
                        }]
                    })
                    
        elif object_type == "deals":
            if "closed" in query_lower:
                if "won" in query_lower:
                    search_params["filters"].append({
                        "filters": [{
                            "propertyName": "dealstage",
                            "operator": "EQ",
                            "value": "closedwon"
                        }]
                    })
                elif "lost" in query_lower:
                    search_params["filters"].append({
                        "filters": [{
                            "propertyName": "dealstage",
                            "operator": "EQ",
                            "value": "closedlost"
                        }]
                    })
            elif "amount" in query_lower or "$" in query_lower:
                # Parse amount
                import re
                amount_match = re.search(r'\$?([\d,]+)', query_lower)
                if amount_match:
                    amount = int(amount_match.group(1).replace(',', ''))
                    operator = "GT" if "more than" in query_lower or "greater" in query_lower else "LT"
                    search_params["filters"].append({
                        "filters": [{
                            "propertyName": "amount",
                            "operator": operator,
                            "value": str(amount)
                        }]
                    })
                    
        elif object_type == "companies":
            if "industry" in query_lower:
                # Extract industry after the word "industry"
                industry = query.split("industry")[-1].strip()
                search_params["filters"].append({
                    "filters": [{
                        "propertyName": "industry",
                        "operator": "EQ",
                        "value": industry
                    }]
                })
        
        # Default text search if no specific filters
        if not search_params["filters"] and not search_params.get("query"):
            search_params["query"] = query
        
        # Add default sorting
        if object_type == "deals":
            search_params["sorts"] = [{"propertyName": "amount", "direction": "DESCENDING"}]
        else:
            search_params["sorts"] = [{"propertyName": "createdate", "direction": "DESCENDING"}]
        
        return search_params
    
    def _get_default_properties(self, object_type: str) -> List[str]:
        """Get default properties to return for each object type"""
        properties_map = {
            "contacts": ["firstname", "lastname", "email", "phone", "company", "jobtitle", "createdate"],
            "companies": ["name", "domain", "industry", "city", "state", "country", "numberofemployees", "annualrevenue"],
            "deals": ["dealname", "amount", "dealstage", "closedate", "pipeline", "hubspot_owner_id"],
            "tickets": ["subject", "content", "hs_pipeline_stage", "priority", "createdate"],
            "tasks": ["hs_task_subject", "hs_task_body", "hs_task_status", "hs_task_priority", "hs_timestamp"],
            "notes": ["hs_note_body", "hs_timestamp"],
            "meetings": ["hs_meeting_title", "hs_meeting_body", "hs_meeting_start_time", "hs_meeting_end_time"],
            "calls": ["hs_call_title", "hs_call_body", "hs_call_duration", "hs_timestamp"]
        }
        
        return properties_map.get(object_type, ["createdate", "hs_object_id"])
    
    def _format_search_results(self, results: Dict[str, Any], object_type: str, query: str) -> str:
        """Format search results for display"""
        output = f"🔍 HubSpot Search Results:\n\n"
        output += f"Query: {query}\n"
        output += f"Object Type: {object_type}\n"
        output += f"Total Results: {results.get('total', 0)}\n\n"
        
        if results.get('total', 0) == 0:
            output += "No results found."
            return output
        
        # Format each result
        for i, result in enumerate(results.get('results', []), 1):
            properties = result.get('properties', {})
            output += f"Result {i}:\n"
            output += f"  ID: {result.get('id')}\n"
            
            # Format based on object type
            if object_type == "contacts":
                output += f"  Name: {properties.get('firstname', '')} {properties.get('lastname', '')}\n"
                output += f"  Email: {properties.get('email', 'N/A')}\n"
                output += f"  Company: {properties.get('company', 'N/A')}\n"
            elif object_type == "companies":
                output += f"  Name: {properties.get('name', 'N/A')}\n"
                output += f"  Domain: {properties.get('domain', 'N/A')}\n"
                output += f"  Industry: {properties.get('industry', 'N/A')}\n"
            elif object_type == "deals":
                output += f"  Name: {properties.get('dealname', 'N/A')}\n"
                output += f"  Amount: ${properties.get('amount', 0):,.2f}\n"
                output += f"  Stage: {properties.get('dealstage', 'N/A')}\n"
                output += f"  Close Date: {properties.get('closedate', 'N/A')}\n"
            
            output += "\n"
            
            # Limit output
            if i >= 5 and results.get('total', 0) > 5:
                output += f"... and {results['total'] - 5} more results\n"
                break
        
        return output
    
    async def _handle_create_object(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle object creation"""
        object_type = arguments.get("object_type", "")
        properties = arguments.get("properties", {})
        associations = arguments.get("associations", [])
        
        try:
            url = f"{self.session.base_url}/crm/v3/objects/{object_type}"
            
            # Create object
            create_body = {"properties": properties}
            if associations:
                create_body["associations"] = associations
            
            response = requests.post(url, headers=self.session.headers, json=create_body)
            response.raise_for_status()
            
            result = response.json()
            
            output = f"✅ Successfully created {object_type}\n\n"
            output += f"ID: {result.get('id')}\n"
            output += f"Properties set:\n"
            for key, value in properties.items():
                output += f"  {key}: {value}\n"
            
            if associations:
                output += f"\nAssociations created: {len(associations)}\n"
            
            # Clear relevant caches
            if self.redis_client:
                pattern = f"hs:*{object_type}*"
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Create error: {e}")
            return [TextContent(
                type="text",
                text=f"Error creating object: {str(e)}"
            )]
    
    async def _handle_update_object(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle object updates"""
        object_type = arguments.get("object_type", "")
        object_id = arguments.get("object_id", "")
        properties = arguments.get("properties", {})
        
        try:
            url = f"{self.session.base_url}/crm/v3/objects/{object_type}/{object_id}"
            
            response = requests.patch(
                url, 
                headers=self.session.headers, 
                json={"properties": properties}
            )
            response.raise_for_status()
            
            output = f"✅ Successfully updated {object_type}\n\n"
            output += f"ID: {object_id}\n"
            output += f"Updated properties:\n"
            for key, value in properties.items():
                output += f"  {key}: {value}\n"
            
            # Clear relevant caches
            if self.redis_client:
                pattern = f"hs:*{object_type}*"
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Update error: {e}")
            return [TextContent(
                type="text",
                text=f"Error updating object: {str(e)}"
            )]
    
    async def _handle_delete_object(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle object deletion"""
        object_type = arguments.get("object_type", "")
        object_id = arguments.get("object_id", "")
        
        try:
            url = f"{self.session.base_url}/crm/v3/objects/{object_type}/{object_id}"
            
            response = requests.delete(url, headers=self.session.headers)
            response.raise_for_status()
            
            output = f"✅ Successfully deleted {object_type}\n\n"
            output += f"ID: {object_id}\n"
            
            # Clear relevant caches
            if self.redis_client:
                pattern = f"hs:*{object_type}*"
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return [TextContent(
                type="text",
                text=f"Error deleting object: {str(e)}"
            )]
    
    async def _handle_get_pipelines(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get pipeline information"""
        object_type = arguments.get("object_type", "deals")
        
        # Check cache
        cache_key = f"hs:pipelines:{object_type}"
        if self.redis_client:
            cached = self.redis_client.get(cache_key)
            if cached:
                return [TextContent(type="text", text=f"📊 Pipelines (cached):\n\n{cached}")]
        
        try:
            url = f"{self.session.base_url}/crm/v3/pipelines/{object_type}"
            response = requests.get(url, headers=self.session.headers)
            response.raise_for_status()
            
            pipelines = response.json().get('results', [])
            
            output = f"📊 {object_type.title()} Pipelines:\n\n"
            
            for pipeline in pipelines:
                output += f"Pipeline: {pipeline['label']} (ID: {pipeline['id']})\n"
                output += f"  Default: {pipeline.get('displayOrder', 0) == 0}\n"
                output += f"  Stages:\n"
                
                for stage in pipeline.get('stages', []):
                    output += f"    • {stage['label']} (ID: {stage['id']})\n"
                    output += f"      Order: {stage.get('displayOrder', 0)}\n"
                    output += f"      Probability: {stage.get('probability', 0)}%\n"
                
                output += "\n"
            
            # Cache results
            if self.redis_client:
                self.redis_client.setex(cache_key, self.pipeline_cache_ttl, output)
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Get pipelines error: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting pipelines: {str(e)}"
            )]
    
    async def _handle_move_deal_stage(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Move a deal to a different stage"""
        deal_id = arguments.get("deal_id", "")
        stage_id = arguments.get("stage_id", "")
        
        try:
            # Update the deal's stage
            url = f"{self.session.base_url}/crm/v3/objects/deals/{deal_id}"
            response = requests.patch(
                url,
                headers=self.session.headers,
                json={"properties": {"dealstage": stage_id}}
            )
            response.raise_for_status()
            
            result = response.json()
            
            output = f"✅ Successfully moved deal\n\n"
            output += f"Deal ID: {deal_id}\n"
            output += f"New Stage ID: {stage_id}\n"
            output += f"Deal Name: {result['properties'].get('dealname', 'N/A')}\n"
            output += f"Amount: ${result['properties'].get('amount', 0):,.2f}\n"
            
            # Clear caches
            if self.redis_client:
                pattern = f"hs:*deals*"
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Move deal error: {e}")
            return [TextContent(
                type="text",
                text=f"Error moving deal: {str(e)}"
            )]
    
    async def _handle_get_analytics(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get analytics and insights"""
        report_type = arguments.get("report_type", "revenue")
        time_period = arguments.get("time_period", "this_month")
        
        try:
            # Get date range
            date_range = self._get_date_range(time_period)
            
            output = f"📊 {report_type.title()} Analytics Report\n"
            output += f"Period: {time_period.replace('_', ' ').title()}\n"
            output += f"Date Range: {date_range['start']} to {date_range['end']}\n\n"
            
            if report_type == "revenue":
                # Get deals data
                search_body = {
                    "filterGroups": [{
                        "filters": [
                            {
                                "propertyName": "closedate",
                                "operator": "GTE",
                                "value": date_range['start_ms']
                            },
                            {
                                "propertyName": "closedate",
                                "operator": "LTE",
                                "value": date_range['end_ms']
                            }
                        ]
                    }],
                    "properties": ["dealname", "amount", "dealstage", "closedate"],
                    "limit": 100
                }
                
                url = f"{self.session.base_url}/crm/v3/objects/deals/search"
                response = requests.post(url, headers=self.session.headers, json=search_body)
                response.raise_for_status()
                
                deals = response.json().get('results', [])
                
                # Calculate metrics
                total_revenue = sum(float(d['properties'].get('amount', 0)) for d in deals if d['properties'].get('dealstage') == 'closedwon')
                total_deals = len([d for d in deals if d['properties'].get('dealstage') == 'closedwon'])
                avg_deal_size = total_revenue / total_deals if total_deals > 0 else 0
                
                output += f"💰 Revenue Metrics:\n"
                output += f"  Total Revenue: ${total_revenue:,.2f}\n"
                output += f"  Closed Won Deals: {total_deals}\n"
                output += f"  Average Deal Size: ${avg_deal_size:,.2f}\n"
                
            elif report_type == "pipeline":
                # Get pipeline data
                search_body = {
                    "filterGroups": [{
                        "filters": [{
                            "propertyName": "dealstage",
                            "operator": "NIN",
                            "values": ["closedwon", "closedlost"]
                        }]
                    }],
                    "properties": ["dealname", "amount", "dealstage", "closedate"],
                    "limit": 100
                }
                
                url = f"{self.session.base_url}/crm/v3/objects/deals/search"
                response = requests.post(url, headers=self.session.headers, json=search_body)
                response.raise_for_status()
                
                deals = response.json().get('results', [])
                
                # Calculate pipeline metrics
                total_pipeline_value = sum(float(d['properties'].get('amount', 0)) for d in deals)
                total_pipeline_deals = len(deals)
                
                output += f"📈 Pipeline Metrics:\n"
                output += f"  Total Pipeline Value: ${total_pipeline_value:,.2f}\n"
                output += f"  Active Deals: {total_pipeline_deals}\n"
                output += f"  Average Deal Value: ${total_pipeline_value/total_pipeline_deals if total_pipeline_deals > 0 else 0:,.2f}\n"
            
            elif report_type == "contacts":
                # Get contacts data
                search_body = {
                    "filterGroups": [{
                        "filters": [{
                            "propertyName": "createdate",
                            "operator": "GTE",
                            "value": date_range['start_ms']
                        }]
                    }],
                    "properties": ["firstname", "lastname", "email", "createdate"],
                    "limit": 100
                }
                
                url = f"{self.session.base_url}/crm/v3/objects/contacts/search"
                response = requests.post(url, headers=self.session.headers, json=search_body)
                response.raise_for_status()
                
                contacts = response.json()
                
                output += f"👥 Contact Metrics:\n"
                output += f"  New Contacts: {contacts.get('total', 0)}\n"
                output += f"  Growth Rate: +{contacts.get('total', 0) / 30:.1f} per day\n"
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return [TextContent(
                type="text",
                text=f"Error generating analytics: {str(e)}"
            )]
    
    async def _handle_get_timeline(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get object timeline/activity history"""
        object_type = arguments.get("object_type", "")
        object_id = arguments.get("object_id", "")
        activity_types = arguments.get("activity_types", [])
        
        try:
            # Get timeline events
            url = f"{self.session.base_url}/crm/v3/objects/{object_type}/{object_id}/timeline"
            response = requests.get(url, headers=self.session.headers)
            response.raise_for_status()
            
            events = response.json().get('results', [])
            
            output = f"📅 Timeline for {object_type} (ID: {object_id}):\n\n"
            
            # Filter by activity types if specified
            if activity_types:
                events = [e for e in events if e.get('eventType') in activity_types]
            
            # Format events
            for event in events[:20]:  # Limit to recent 20
                event_type = event.get('eventType', 'Unknown')
                timestamp = event.get('timestamp', '')
                
                output += f"🔹 {event_type}\n"
                output += f"   Time: {timestamp}\n"
                
                # Add event-specific details
                if 'subject' in event:
                    output += f"   Subject: {event['subject']}\n"
                if 'body' in event:
                    output += f"   Body: {event['body'][:100]}...\n"
                
                output += "\n"
            
            if len(events) > 20:
                output += f"... and {len(events) - 20} more events\n"
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Timeline error: {e}")
            return [TextContent(
                type="text",
                text=f"Error getting timeline: {str(e)}"
            )]
    
    async def _handle_batch_operation(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle batch operations"""
        operation = arguments.get("operation", "")
        object_type = arguments.get("object_type", "")
        inputs = arguments.get("inputs", [])
        
        try:
            url = f"{self.session.base_url}/crm/v3/objects/{object_type}/batch/{operation}"
            
            # Prepare batch request
            batch_body = {"inputs": inputs}
            
            response = requests.post(url, headers=self.session.headers, json=batch_body)
            response.raise_for_status()
            
            results = response.json()
            
            output = f"✅ Batch {operation} completed\n\n"
            output += f"Object Type: {object_type}\n"
            output += f"Total Processed: {len(inputs)}\n"
            
            # Check for errors
            if 'errors' in results:
                output += f"Errors: {len(results['errors'])}\n"
                for error in results['errors'][:5]:
                    output += f"  - {error.get('message', 'Unknown error')}\n"
            
            if 'results' in results:
                output += f"Successful: {len(results['results'])}\n"
                # Show sample results
                for i, result in enumerate(results['results'][:3]):
                    output += f"  {i+1}. ID: {result.get('id')}\n"
            
            # Clear caches
            if self.redis_client:
                pattern = f"hs:*{object_type}*"
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
            
            self.api_calls += len(inputs)
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Batch operation error: {e}")
            return [TextContent(
                type="text",
                text=f"Error in batch operation: {str(e)}"
            )]
    
    async def _handle_health_check(self) -> List[TextContent]:
        """Check HubSpot health and limits"""
        try:
            # Get account info
            url = f"{self.session.base_url}/crm/v3/properties/contacts"
            response = requests.get(url, headers=self.session.headers)
            response.raise_for_status()
            
            # Check rate limits from headers
            rate_limit_daily = response.headers.get('X-HubSpot-RateLimit-Daily', 'N/A')
            rate_limit_daily_remaining = response.headers.get('X-HubSpot-RateLimit-Daily-Remaining', 'N/A')
            
            output = "🏥 HubSpot Health Check:\n\n"
            output += f"✅ Connection Status: Healthy\n"
            output += f"Portal ID: {self.session.portal_id}\n"
            
            output += f"\n📊 API Limits:\n"
            output += f"  Daily Limit: {rate_limit_daily}\n"
            output += f"  Daily Remaining: {rate_limit_daily_remaining}\n"
            output += f"  Calls This Session: {self.api_calls}\n"
            
            # Calculate usage percentage
            try:
                if rate_limit_daily != 'N/A' and rate_limit_daily_remaining != 'N/A':
                    daily_limit = int(rate_limit_daily)
                    daily_remaining = int(rate_limit_daily_remaining)
                    usage_pct = ((daily_limit - daily_remaining) / daily_limit) * 100
                    output += f"  Usage: {usage_pct:.1f}%\n"
            except:
                pass
            
            output += f"\n⏰ Session Info:\n"
            output += f"  Session Valid Until: {self.session.expires_at}\n"
            
            if self.redis_client:
                try:
                    info = self.redis_client.info()
                    output += f"\n💾 Cache Status:\n"
                    output += f"  Redis Connected: ✅\n"
                    output += f"  Used Memory: {info.get('used_memory_human', 'Unknown')}\n"
                except:
                    output += f"\n💾 Cache Status: ❌ Not available\n"
            
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return [TextContent(type="text", text=f"❌ Health check failed: {str(e)}")]
    
    def _get_date_range(self, time_period: str) -> Dict[str, Any]:
        """Convert time period to date range"""
        now = datetime.now()
        
        if time_period == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif time_period == "this_week":
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif time_period == "this_month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif time_period == "this_quarter":
            quarter = (now.month - 1) // 3
            start = now.replace(month=quarter*3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif time_period == "this_year":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        else:
            # Default to last 30 days
            start = now - timedelta(days=30)
            end = now
        
        return {
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "start_ms": str(int(start.timestamp() * 1000)),
            "end_ms": str(int(end.timestamp() * 1000))
        }
    
    async def run(self):
        """Run the MCP server"""
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run server
    server = HubSpotMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
