"""
Salesforce MCP Server with Natural Language CRM Operations

Provides AI-friendly Salesforce integration through MCP interface:
- Natural language to SOQL/SOSL query conversion
- Schema introspection and metadata access
- CRUD operations with bulk support
- Apex code management
- Smart caching and rate limit handling
"""

import asyncio
import logging
import json
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, TextContent, ImageContent, EmbeddedResource,
    LogLevel, Prompt, PromptMessage, UserMessage, AssistantMessage
)

# Import dependencies
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from simple_salesforce import Salesforce, SalesforceError
    import redis
    from backend.core.config.service_configs import ServiceConfigs
except ImportError as e:
    logging.error(f"Import error: {e}")
    logging.error("Please install required packages: pip install simple-salesforce redis")
    raise

logger = logging.getLogger(__name__)


class QueryComplexity(Enum):
    """Query complexity levels for optimization"""
    SIMPLE = "simple"      # Single object, basic filters
    MODERATE = "moderate"  # Joins, aggregations
    COMPLEX = "complex"    # Multiple joins, subqueries
    BULK = "bulk"         # Large data operations


@dataclass
class SalesforceSession:
    """Salesforce authenticated session"""
    instance: Salesforce
    instance_url: str
    session_id: str
    expires_at: datetime
    org_id: str
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


class SalesforceMCPServer:
    """
    MCP Server for Salesforce CRM operations
    
    Features:
    - Natural language query understanding
    - Automatic SOQL generation
    - Schema discovery and introspection
    - CRUD operations with validation
    - Apex code management
    - Rate limit handling
    - Redis caching for performance
    """
    
    def __init__(self):
        self.server = Server("salesforce")
        self.session: Optional[SalesforceSession] = None
        self.redis_client: Optional[redis.Redis] = None
        self.config = ServiceConfigs().get_salesforce_config()
        
        # Cache settings
        self.cache_ttl = 300  # 5 minutes
        self.schema_cache_ttl = 3600  # 1 hour
        
        # Rate limiting
        self.api_calls = 0
        self.api_limit = 100000  # Daily limit
        self.bulk_api_limit = 10000  # Bulk API limit
        
        # Register handlers
        self._register_handlers()
        
    def _register_handlers(self):
        """Register all MCP handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available Salesforce tools"""
            return [
                Tool(
                    name="query",
                    description="Query Salesforce using natural language or SOQL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query or SOQL statement"
                            },
                            "use_sosl": {
                                "type": "boolean",
                                "description": "Use SOSL for text search (default: false)",
                                "default": False
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum records to return (default: 100)",
                                "default": 100
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="create_record",
                    description="Create a new Salesforce record",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_type": {
                                "type": "string",
                                "description": "Salesforce object type (e.g., Account, Contact)"
                            },
                            "fields": {
                                "type": "object",
                                "description": "Field values for the new record"
                            }
                        },
                        "required": ["object_type", "fields"]
                    }
                ),
                Tool(
                    name="update_record",
                    description="Update an existing Salesforce record",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_type": {
                                "type": "string",
                                "description": "Salesforce object type"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "Salesforce record ID"
                            },
                            "fields": {
                                "type": "object",
                                "description": "Fields to update"
                            }
                        },
                        "required": ["object_type", "record_id", "fields"]
                    }
                ),
                Tool(
                    name="delete_record",
                    description="Delete a Salesforce record",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_type": {
                                "type": "string",
                                "description": "Salesforce object type"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "Salesforce record ID"
                            }
                        },
                        "required": ["object_type", "record_id"]
                    }
                ),
                Tool(
                    name="bulk_operation",
                    description="Perform bulk create/update/delete operations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "Operation type",
                                "enum": ["insert", "update", "upsert", "delete"]
                            },
                            "object_type": {
                                "type": "string",
                                "description": "Salesforce object type"
                            },
                            "records": {
                                "type": "array",
                                "description": "Array of records to process",
                                "items": {"type": "object"}
                            },
                            "external_id_field": {
                                "type": "string",
                                "description": "External ID field for upsert operations"
                            }
                        },
                        "required": ["operation", "object_type", "records"]
                    }
                ),
                Tool(
                    name="describe_object",
                    description="Get schema information for a Salesforce object",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "object_type": {
                                "type": "string",
                                "description": "Salesforce object type to describe"
                            },
                            "include_fields": {
                                "type": "boolean",
                                "description": "Include field details (default: true)",
                                "default": True
                            },
                            "include_relationships": {
                                "type": "boolean",
                                "description": "Include relationship details (default: true)",
                                "default": True
                            }
                        },
                        "required": ["object_type"]
                    }
                ),
                Tool(
                    name="list_objects",
                    description="List all available Salesforce objects",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_custom": {
                                "type": "boolean",
                                "description": "Include custom objects (default: true)",
                                "default": True
                            },
                            "filter_pattern": {
                                "type": "string",
                                "description": "Filter objects by name pattern"
                            }
                        }
                    }
                ),
                Tool(
                    name="execute_apex",
                    description="Execute anonymous Apex code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Apex code to execute"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_apex_class",
                    description="Retrieve Apex class source code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "class_name": {
                                "type": "string",
                                "description": "Name of the Apex class"
                            }
                        },
                        "required": ["class_name"]
                    }
                ),
                Tool(
                    name="health_check",
                    description="Check Salesforce connection and API limits",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute Salesforce tools"""
            
            # Ensure authenticated
            await self._ensure_authenticated()
            
            try:
                if name == "query":
                    return await self._handle_query(arguments)
                elif name == "create_record":
                    return await self._handle_create_record(arguments)
                elif name == "update_record":
                    return await self._handle_update_record(arguments)
                elif name == "delete_record":
                    return await self._handle_delete_record(arguments)
                elif name == "bulk_operation":
                    return await self._handle_bulk_operation(arguments)
                elif name == "describe_object":
                    return await self._handle_describe_object(arguments)
                elif name == "list_objects":
                    return await self._handle_list_objects(arguments)
                elif name == "execute_apex":
                    return await self._handle_execute_apex(arguments)
                elif name == "get_apex_class":
                    return await self._handle_get_apex_class(arguments)
                elif name == "health_check":
                    return await self._handle_health_check()
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except SalesforceError as e:
                logger.error(f"Salesforce API error: {e}")
                return [TextContent(
                    type="text",
                    text=f"Salesforce Error: {str(e)}"
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
                    name="opportunity_analysis",
                    description="Analyze opportunities in the pipeline",
                    arguments=[
                        {
                            "name": "stage",
                            "description": "Filter by opportunity stage",
                            "required": False
                        },
                        {
                            "name": "owner",
                            "description": "Filter by owner name",
                            "required": False
                        }
                    ]
                ),
                Prompt(
                    name="account_summary",
                    description="Get comprehensive account summary",
                    arguments=[
                        {
                            "name": "account_name",
                            "description": "Account name to summarize",
                            "required": True
                        }
                    ]
                ),
                Prompt(
                    name="lead_scoring",
                    description="Score and prioritize leads",
                    arguments=[
                        {
                            "name": "criteria",
                            "description": "Scoring criteria (e.g., industry, size)",
                            "required": False
                        }
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, Any]) -> PromptMessage:
            """Get specific prompt template"""
            
            if name == "opportunity_analysis":
                stage = arguments.get("stage", "all stages")
                owner = arguments.get("owner", "all owners")
                
                query = f"""
                Analyze opportunities with the following criteria:
                - Stage: {stage}
                - Owner: {owner}
                
                Please provide:
                1. Total pipeline value
                2. Average deal size
                3. Win probability by stage
                4. Key risks and recommendations
                """
                
                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=query)
                )
                
            elif name == "account_summary":
                account_name = arguments.get("account_name", "")
                
                query = f"""
                Provide a comprehensive summary for account: {account_name}
                
                Include:
                1. Basic account information
                2. Recent activities and interactions
                3. Open opportunities
                4. Key contacts
                5. Support cases
                6. Overall account health score
                """
                
                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=query)
                )
                
            elif name == "lead_scoring":
                criteria = arguments.get("criteria", "standard criteria")
                
                query = f"""
                Score and prioritize current leads using: {criteria}
                
                For each lead, provide:
                1. Lead score (0-100)
                2. Key positive factors
                3. Risk factors
                4. Recommended next action
                5. Conversion probability
                
                Sort by highest priority first.
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
        """Ensure we have a valid Salesforce session"""
        if self.session and not self.session.is_expired:
            return
            
        # Authenticate with Salesforce
        logger.info("Authenticating with Salesforce...")
        
        try:
            # Use password flow authentication
            sf = Salesforce(
                username=self.config["username"],
                password=self.config["password"],
                security_token=self.config["security_token"],
                client_id=self.config["client_id"],
                client_secret=self.config["client_secret"],
                domain='test' if self.config["sandbox"] else 'login'
            )
            
            # Create session
            self.session = SalesforceSession(
                instance=sf,
                instance_url=sf.base_url,
                session_id=sf.session_id,
                expires_at=datetime.now() + timedelta(hours=2),
                org_id=sf.sf_instance
            )
            
            logger.info(f"✅ Authenticated with Salesforce org: {self.session.org_id}")
            
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
            raise Exception(f"Failed to authenticate with Salesforce: {str(e)}")
    
    async def _handle_query(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle query requests"""
        query = arguments.get("query", "")
        use_sosl = arguments.get("use_sosl", False)
        limit = arguments.get("limit", 100)
        
        # Check if it's already SOQL/SOSL
        if self._is_soql_query(query):
            soql = query
        else:
            # Convert natural language to SOQL
            soql = self._natural_language_to_soql(query, limit)
        
        # Check cache first
        cache_key = f"sf:query:{soql}"
        if self.redis_client:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.info("Cache hit for query")
                return [TextContent(
                    type="text",
                    text=f"📊 Query Results (cached):\n\n{cached}"
                )]
        
        # Execute query
        try:
            if use_sosl:
                results = self.session.instance.search(soql)
            else:
                results = self.session.instance.query_all(soql)
            
            # Format results
            output = self._format_query_results(results, soql)
            
            # Cache results
            if self.redis_client and len(output) < 10000:  # Don't cache huge results
                self.redis_client.setex(cache_key, self.cache_ttl, output)
            
            # Track API usage
            self.api_calls += 1
            
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Query error: {e}")
            return [TextContent(
                type="text",
                text=f"Query Error: {str(e)}\n\nQuery: {soql}"
            )]
    
    def _is_soql_query(self, query: str) -> bool:
        """Check if the query is already SOQL"""
        soql_keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY', 'LIMIT']
        query_upper = query.upper()
        return any(keyword in query_upper for keyword in soql_keywords)
    
    def _natural_language_to_soql(self, nl_query: str, limit: int) -> str:
        """Convert natural language to SOQL"""
        nl_lower = nl_query.lower()
        
        # Common patterns
        patterns = {
            # Accounts
            r"(all |list )?(accounts|companies)": 
                f"SELECT Id, Name, Type, Industry, AnnualRevenue, NumberOfEmployees FROM Account LIMIT {limit}",
            
            r"accounts? (named?|called?) (['\"]?)(\w+)":
                lambda m: f"SELECT Id, Name, Type, Industry, Website FROM Account WHERE Name LIKE '%{m.group(3)}%' LIMIT {limit}",
            
            # Contacts
            r"(all |list )?contacts":
                f"SELECT Id, FirstName, LastName, Email, Phone, Account.Name FROM Contact LIMIT {limit}",
            
            r"contacts? (at|from|for) (['\"]?)(\w+)":
                lambda m: f"SELECT Id, FirstName, LastName, Email, Title FROM Contact WHERE Account.Name LIKE '%{m.group(3)}%' LIMIT {limit}",
            
            # Opportunities
            r"(all |list |open )?opportunities":
                f"SELECT Id, Name, StageName, Amount, CloseDate, Account.Name FROM Opportunity WHERE IsClosed = false LIMIT {limit}",
            
            r"opportunities (worth )?more than \$?([\d,]+)":
                lambda m: f"SELECT Id, Name, Amount, StageName FROM Opportunity WHERE Amount > {m.group(2).replace(',', '')} LIMIT {limit}",
            
            r"opportunities closing (this|next) (month|quarter|year)":
                lambda m: self._build_date_filter_query('Opportunity', m.group(1), m.group(2), limit),
            
            # Leads
            r"(all |list |new )?leads":
                f"SELECT Id, FirstName, LastName, Company, Status, LeadSource FROM Lead WHERE IsConverted = false LIMIT {limit}",
            
            r"hot leads|high priority leads":
                f"SELECT Id, Name, Company, Email, Rating FROM Lead WHERE Rating = 'Hot' AND IsConverted = false LIMIT {limit}",
            
            # Cases
            r"(all |list |open )?cases":
                f"SELECT Id, CaseNumber, Subject, Status, Priority, Account.Name FROM Case WHERE IsClosed = false LIMIT {limit}",
            
            r"(high priority|urgent) cases":
                f"SELECT Id, CaseNumber, Subject, Status, CreatedDate FROM Case WHERE Priority = 'High' AND IsClosed = false LIMIT {limit}"
        }
        
        # Try to match patterns
        for pattern, query_template in patterns.items():
            match = re.search(pattern, nl_lower)
            if match:
                if callable(query_template):
                    return query_template(match)
                return query_template
        
        # Default: search for the query text in common objects
        search_term = nl_query.replace("'", "\\'")
        return f"""
        SELECT Id, Name FROM Account WHERE Name LIKE '%{search_term}%'
        UNION
        SELECT Id, Name FROM Contact WHERE Name LIKE '%{search_term}%' 
        UNION  
        SELECT Id, Name FROM Opportunity WHERE Name LIKE '%{search_term}%'
        LIMIT {limit}
        """
    
    def _build_date_filter_query(self, object_type: str, period: str, unit: str, limit: int) -> str:
        """Build SOQL query with date filters"""
        if period == "this":
            if unit == "month":
                date_filter = "THIS_MONTH"
            elif unit == "quarter":
                date_filter = "THIS_QUARTER"
            else:
                date_filter = "THIS_YEAR"
        else:  # next
            if unit == "month":
                date_filter = "NEXT_MONTH"
            elif unit == "quarter":
                date_filter = "NEXT_QUARTER"
            else:
                date_filter = "NEXT_YEAR"
        
        if object_type == "Opportunity":
            return f"SELECT Id, Name, Amount, CloseDate, StageName FROM Opportunity WHERE CloseDate = {date_filter} LIMIT {limit}"
        
        return f"SELECT Id, Name FROM {object_type} WHERE CreatedDate = {date_filter} LIMIT {limit}"
    
    def _format_query_results(self, results: Dict[str, Any], query: str) -> str:
        """Format query results for display"""
        output = f"📊 Query Results:\n\n"
        output += f"Query: {query}\n"
        output += f"Total Records: {results['totalSize']}\n\n"
        
        if results['totalSize'] == 0:
            output += "No records found."
            return output
        
        # Format records
        for i, record in enumerate(results['records'], 1):
            output += f"Record {i}:\n"
            
            # Skip attributes
            for key, value in record.items():
                if key != 'attributes':
                    # Handle nested objects
                    if isinstance(value, dict) and 'Name' in value:
                        output += f"  {key}: {value['Name']}\n"
                    elif value is not None:
                        output += f"  {key}: {value}\n"
            
            output += "\n"
            
            # Limit output size
            if i >= 10 and results['totalSize'] > 10:
                output += f"... and {results['totalSize'] - 10} more records\n"
                break
        
        return output
    
    async def _handle_create_record(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle record creation"""
        object_type = arguments.get("object_type", "")
        fields = arguments.get("fields", {})
        
        try:
            # Create record
            result = getattr(self.session.instance, object_type).create(fields)
            
            if result['success']:
                output = f"✅ Successfully created {object_type} record\n\n"
                output += f"Record ID: {result['id']}\n"
                output += f"Fields set:\n"
                for key, value in fields.items():
                    output += f"  {key}: {value}\n"
                
                # Clear relevant caches
                if self.redis_client:
                    pattern = f"sf:query:*{object_type}*"
                    for key in self.redis_client.scan_iter(match=pattern):
                        self.redis_client.delete(key)
                
                self.api_calls += 1
                return [TextContent(type="text", text=output)]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Failed to create record: {result.get('errors', 'Unknown error')}"
                )]
                
        except Exception as e:
            logger.error(f"Create error: {e}")
            return [TextContent(
                type="text",
                text=f"Error creating record: {str(e)}"
            )]
    
    async def _handle_update_record(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle record updates"""
        object_type = arguments.get("object_type", "")
        record_id = arguments.get("record_id", "")
        fields = arguments.get("fields", {})
        
        try:
            # Update record
            getattr(self.session.instance, object_type).update(record_id, fields)
            
            output = f"✅ Successfully updated {object_type} record\n\n"
            output += f"Record ID: {record_id}\n"
            output += f"Updated fields:\n"
            for key, value in fields.items():
                output += f"  {key}: {value}\n"
            
            # Clear relevant caches
            if self.redis_client:
                pattern = f"sf:query:*{object_type}*"
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Update error: {e}")
            return [TextContent(
                type="text",
                text=f"Error updating record: {str(e)}"
            )]
    
    async def _handle_delete_record(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle record deletion"""
        object_type = arguments.get("object_type", "")
        record_id = arguments.get("record_id", "")
        
        try:
            # Delete record
            getattr(self.session.instance, object_type).delete(record_id)
            
            output = f"✅ Successfully deleted {object_type} record\n\n"
            output += f"Record ID: {record_id}\n"
            
            # Clear relevant caches
            if self.redis_client:
                pattern = f"sf:query:*{object_type}*"
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return [TextContent(
                type="text",
                text=f"Error deleting record: {str(e)}"
            )]
    
    async def _handle_bulk_operation(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle bulk operations"""
        operation = arguments.get("operation", "")
        object_type = arguments.get("object_type", "")
        records = arguments.get("records", [])
        external_id_field = arguments.get("external_id_field")
        
        try:
            bulk_api = self.session.instance.bulk
            job_id = None
            
            # Create bulk job
            if operation == "insert":
                job_id = bulk_api.create_insert_job(object_type)
            elif operation == "update":
                job_id = bulk_api.create_update_job(object_type)
            elif operation == "upsert" and external_id_field:
                job_id = bulk_api.create_upsert_job(object_type, external_id_field)
            elif operation == "delete":
                job_id = bulk_api.create_delete_job(object_type)
            else:
                return [TextContent(
                    type="text",
                    text=f"Invalid bulk operation: {operation}"
                )]
            
            # Add batch
            batch_id = bulk_api.post_batch(job_id, records)
            
            # Wait for completion (simplified - in production use async polling)
            import time
            max_wait = 60  # seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                batch_status = bulk_api.batch_status(batch_id, job_id)
                if batch_status['state'] in ['Completed', 'Failed']:
                    break
                await asyncio.sleep(2)
            
            # Get results
            if batch_status['state'] == 'Completed':
                results = bulk_api.get_batch_results(batch_id, job_id)
                
                output = f"✅ Bulk {operation} completed\n\n"
                output += f"Object Type: {object_type}\n"
                output += f"Records Processed: {batch_status['numberRecordsProcessed']}\n"
                output += f"Records Failed: {batch_status['numberRecordsFailed']}\n"
                
                # Show sample results
                if results and len(results) > 0:
                    output += f"\nSample Results (first 5):\n"
                    for i, result in enumerate(results[:5]):
                        output += f"  Record {i+1}: {result}\n"
            else:
                output = f"❌ Bulk operation failed\n"
                output += f"State: {batch_status['state']}\n"
                output += f"State Message: {batch_status.get('stateMessage', 'No message')}\n"
            
            # Clear caches
            if self.redis_client:
                pattern = f"sf:*{object_type}*"
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
            
            self.api_calls += len(records)
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Bulk operation error: {e}")
            return [TextContent(
                type="text",
                text=f"Error in bulk operation: {str(e)}"
            )]
    
    async def _handle_describe_object(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle object schema description"""
        object_type = arguments.get("object_type", "")
        include_fields = arguments.get("include_fields", True)
        include_relationships = arguments.get("include_relationships", True)
        
        # Check cache
        cache_key = f"sf:schema:{object_type}"
        if self.redis_client:
            cached = self.redis_client.get(cache_key)
            if cached:
                return [TextContent(type="text", text=f"📋 Object Schema (cached):\n\n{cached}")]
        
        try:
            # Get object description
            description = getattr(self.session.instance, object_type).describe()
            
            output = f"📋 {object_type} Object Schema:\n\n"
            output += f"Label: {description['label']}\n"
            output += f"API Name: {description['name']}\n"
            output += f"Queryable: {description['queryable']}\n"
            output += f"Createable: {description['createable']}\n"
            output += f"Updateable: {description['updateable']}\n"
            output += f"Deleteable: {description['deletable']}\n\n"
            
            if include_fields and 'fields' in description:
                output += "Fields:\n"
                for field in description['fields'][:20]:  # Limit to first 20 fields
                    output += f"  • {field['name']} ({field['type']})"
                    if field['label'] != field['name']:
                        output += f" - {field['label']}"
                    output += "\n"
                
                if len(description['fields']) > 20:
                    output += f"  ... and {len(description['fields']) - 20} more fields\n"
            
            if include_relationships and 'childRelationships' in description:
                output += "\nChild Relationships:\n"
                for rel in description['childRelationships'][:10]:
                    if rel['relationshipName']:
                        output += f"  • {rel['relationshipName']} → {rel['childSObject']}\n"
                
                if len(description['childRelationships']) > 10:
                    output += f"  ... and {len(description['childRelationships']) - 10} more relationships\n"
            
            # Cache result
            if self.redis_client:
                self.redis_client.setex(cache_key, self.schema_cache_ttl, output)
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Describe error: {e}")
            return [TextContent(type="text", text=f"Error describing object: {str(e)}")]
    
    async def _handle_list_objects(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """List available Salesforce objects"""
        include_custom = arguments.get("include_custom", True)
        filter_pattern = arguments.get("filter_pattern", "")
        
        # Check cache
        cache_key = "sf:objects:list"
        if self.redis_client:
            cached = self.redis_client.get(cache_key)
            if cached and not filter_pattern:
                return [TextContent(type="text", text=f"📚 Available Objects (cached):\n\n{cached}")]
        
        try:
            # Get global describe
            all_objects = self.session.instance.describe()["sobjects"]
            
            # Filter objects
            filtered_objects = []
            for obj in all_objects:
                # Skip if custom objects excluded
                if not include_custom and obj['custom']:
                    continue
                
                # Apply pattern filter
                if filter_pattern and filter_pattern.lower() not in obj['name'].lower():
                    continue
                
                filtered_objects.append(obj)
            
            # Format output
            output = f"📚 Available Salesforce Objects:\n\n"
            output += f"Total: {len(filtered_objects)} objects\n\n"
            
            # Group by type
            standard_objects = [o for o in filtered_objects if not o['custom']]
            custom_objects = [o for o in filtered_objects if o['custom']]
            
            if standard_objects:
                output += "Standard Objects:\n"
                for obj in standard_objects[:20]:
                    output += f"  • {obj['name']}"
                    if obj['label'] != obj['name']:
                        output += f" ({obj['label']})"
                    output += "\n"
                
                if len(standard_objects) > 20:
                    output += f"  ... and {len(standard_objects) - 20} more standard objects\n"
            
            if custom_objects:
                output += "\nCustom Objects:\n"
                for obj in custom_objects[:20]:
                    output += f"  • {obj['name']}"
                    if obj['label'] != obj['name']:
                        output += f" ({obj['label']})"
                    output += "\n"
                
                if len(custom_objects) > 20:
                    output += f"  ... and {len(custom_objects) - 20} more custom objects\n"
            
            # Cache if no filter
            if self.redis_client and not filter_pattern:
                self.redis_client.setex(cache_key, self.schema_cache_ttl, output)
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"List objects error: {e}")
            return [TextContent(type="text", text=f"Error listing objects: {str(e)}")]
    
    async def _handle_execute_apex(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute anonymous Apex code"""
        code = arguments.get("code", "")
        
        try:
            # Execute Apex
            result = self.session.instance.restful('tooling/executeAnonymous', {
                'anonymousBody': code
            })
            
            output = "⚡ Apex Execution Result:\n\n"
            
            if result['success']:
                output += "✅ Execution successful\n\n"
                if result.get('compiled'):
                    output += "Compilation: Success\n"
                if result.get('executed'):
                    output += "Execution: Success\n"
                
                # Show debug log if available
                if 'debugLog' in result:
                    output += f"\nDebug Log:\n{result['debugLog'][:500]}"
                    if len(result['debugLog']) > 500:
                        output += "\n... (truncated)"
            else:
                output += "❌ Execution failed\n\n"
                if 'compileProblem' in result:
                    output += f"Compile Error: {result['compileProblem']}\n"
                    output += f"Line: {result.get('line', 'Unknown')}, Column: {result.get('column', 'Unknown')}\n"
                if 'exceptionMessage' in result:
                    output += f"Exception: {result['exceptionMessage']}\n"
                    output += f"Stack Trace: {result.get('exceptionStackTrace', 'N/A')}\n"
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Apex execution error: {e}")
            return [TextContent(type="text", text=f"Error executing Apex: {str(e)}")]
    
    async def _handle_get_apex_class(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get Apex class source code"""
        class_name = arguments.get("class_name", "")
        
        try:
            # Query for Apex class
            query = f"SELECT Id, Name, Body, Status, ApiVersion FROM ApexClass WHERE Name = '{class_name}'"
            result = self.session.instance.query(query)
            
            if result['totalSize'] == 0:
                return [TextContent(type="text", text=f"❌ Apex class '{class_name}' not found")]
            
            apex_class = result['records'][0]
            
            output = f"📄 Apex Class: {apex_class['Name']}\n\n"
            output += f"Status: {apex_class['Status']}\n"
            output += f"API Version: {apex_class['ApiVersion']}\n\n"
            output += "Source Code:\n"
            output += "```apex\n"
            output += apex_class['Body']
            output += "\n```"
            
            self.api_calls += 1
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Get Apex class error: {e}")
            return [TextContent(type="text", text=f"Error retrieving Apex class: {str(e)}")]
    
    async def _handle_health_check(self) -> List[TextContent]:
        """Check Salesforce health and limits"""
        try:
            # Get organization info
            org_info = self.session.instance.query("SELECT Name, OrganizationType, TrialExpirationDate FROM Organization")
            org = org_info['records'][0] if org_info['totalSize'] > 0 else {}
            
            # Get API limits
            limits = self.session.instance.limits()
            
            output = "🏥 Salesforce Health Check:\n\n"
            output += f"✅ Connection Status: Healthy\n"
            output += f"Organization: {org.get('Name', 'Unknown')}\n"
            output += f"Type: {org.get('OrganizationType', 'Unknown')}\n"
            
            if org.get('TrialExpirationDate'):
                output += f"Trial Expires: {org['TrialExpirationDate']}\n"
            
            output += f"\n📊 API Limits:\n"
            
            # Show key limits
            key_limits = ['DailyApiRequests', 'DailyBulkApiRequests', 'DailyAsyncApexExecutions']
            for limit_name in key_limits:
                if limit_name in limits:
                    limit_info = limits[limit_name]
                    used = limit_info.get('used', 0)
                    max_val = limit_info.get('max', 0)
                    if max_val > 0:
                        percentage = (used / max_val) * 100
                        output += f"  • {limit_name}: {used:,}/{max_val:,} ({percentage:.1f}%)\n"
            
            output += f"\n📈 Session Stats:\n"
            output += f"  • API Calls This Session: {self.api_calls}\n"
            output += f"  • Session Started: {datetime.now() - (self.session.expires_at - timedelta(hours=2))}\n"
            output += f"  • Session Expires: {self.session.expires_at}\n"
            
            if self.redis_client:
                try:
                    info = self.redis_client.info()
                    output += f"\n💾 Cache Status:\n"
                    output += f"  • Redis Connected: ✅\n"
                    output += f"  • Used Memory: {info.get('used_memory_human', 'Unknown')}\n"
                except:
                    output += f"\n💾 Cache Status: ❌ Not available\n"
            
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return [TextContent(type="text", text=f"❌ Health check failed: {str(e)}")]
    
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
    server = SalesforceMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
