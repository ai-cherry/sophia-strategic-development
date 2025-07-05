"""
Salesforce MCP Server for Sophia AI
Provides comprehensive Salesforce data extraction and migration capabilities
Designed for enterprise-grade CRM migration projects
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import requests
from mcp import server

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


class SalesforceMCPServer:
    """Production-ready Salesforce MCP Server for data migration"""

    def __init__(self, port: int = 9006):
        self.port = port
        self.name = "salesforce"
        self.version = "1.0.0"

        # Initialize MCP server
        self.mcp_server = server(self.name, self.version)

        # Load Salesforce credentials from Pulumi ESC
        self.client_id = get_config_value("salesforce_client_id", "")
        self.client_secret = get_config_value("salesforce_client_secret", "")
        self.username = get_config_value("salesforce_username", "")
        self.password = get_config_value("salesforce_password", "")
        self.security_token = get_config_value("salesforce_security_token", "")
        self.instance_url = get_config_value(
            "salesforce_instance_url", "https://login.salesforce.com"
        )

        # OAuth and session management
        self.access_token = None
        self.instance_url_actual = None
        self.session_expires = None

        # Register tools and resources
        self._register_tools()
        self._register_resources()

    def _register_tools(self):
        """Register Salesforce MCP tools"""

        @self.mcp_server.tool("health_check")
        async def health_check() -> dict[str, Any]:
            """Check Salesforce API connection health"""
            try:
                # Test authentication
                auth_result = await self._authenticate()

                if auth_result["success"]:
                    # Test a simple API call
                    limits = await self._get_api_limits()

                    return {
                        "healthy": True,
                        "authenticated": True,
                        "instance_url": self.instance_url_actual,
                        "api_limits": limits,
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    return {
                        "healthy": False,
                        "authenticated": False,
                        "error": auth_result.get("error", "Authentication failed"),
                        "timestamp": datetime.now().isoformat(),
                    }

            except Exception as e:
                logger.error(f"Salesforce health check failed: {e}")
                return {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        @self.mcp_server.tool("authenticate")
        async def authenticate() -> dict[str, Any]:
            """Authenticate with Salesforce using OAuth2"""
            try:
                # OAuth2 Username-Password flow
                auth_url = f"{self.instance_url}/services/oauth2/token"

                data = {
                    "grant_type": "password",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "username": self.username,
                    "password": f"{self.password}{self.security_token}",
                }

                response = requests.post(auth_url, data=data)

                if response.status_code == 200:
                    auth_data = response.json()
                    self.access_token = auth_data["access_token"]
                    self.instance_url_actual = auth_data["instance_url"]

                    # Set expiration (default 2 hours)
                    self.session_expires = datetime.now() + timedelta(hours=2)

                    return {
                        "success": True,
                        "access_token": self.access_token[:20] + "...",  # Masked
                        "instance_url": self.instance_url_actual,
                        "expires_at": self.session_expires.isoformat(),
                    }
                else:
                    error_msg = f"Authentication failed: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {"success": False, "error": error_msg}

            except Exception as e:
                logger.error(f"Authentication error: {e}")
                return {"success": False, "error": str(e)}

        @self.mcp_server.tool("query_objects")
        async def query_objects(
            object_type: str,
            fields: str = "*",
            where_clause: str = "",
            limit: int = 1000,
        ) -> dict[str, Any]:
            """Query Salesforce objects with SOQL"""
            try:
                if not await self._ensure_authenticated():
                    return {"error": "Authentication required"}

                # Build SOQL query
                if fields == "*":
                    # Get common fields for the object
                    describe_result = await self._describe_object(object_type)
                    if describe_result["success"]:
                        common_fields = [
                            field["name"]
                            for field in describe_result["fields"]
                            if field.get("queryable", True)
                            and field["name"]
                            not in [
                                "CreatedById",
                                "LastModifiedById",  # Skip complex relationships
                            ]
                        ][
                            :20
                        ]  # Limit to first 20 fields to avoid query complexity
                        fields = ", ".join(common_fields)
                    else:
                        fields = "Id, Name"  # Fallback

                soql = f"SELECT {fields} FROM {object_type}"
                if where_clause:
                    soql += f" WHERE {where_clause}"
                soql += f" LIMIT {limit}"

                # Execute query
                query_url = f"{self.instance_url_actual}/services/data/v57.0/query/"
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                }

                response = requests.get(query_url, headers=headers, params={"q": soql})

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "total_size": result["totalSize"],
                        "done": result["done"],
                        "records": result["records"],
                        "soql": soql,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Query failed: {response.status_code} - {response.text}",
                        "soql": soql,
                    }

            except Exception as e:
                logger.error(f"Query objects error: {e}")
                return {"success": False, "error": str(e)}

        @self.mcp_server.tool("get_migration_data")
        async def get_migration_data() -> dict[str, Any]:
            """Get comprehensive data for HubSpot/Intercom migration"""
            try:
                if not await self._ensure_authenticated():
                    return {"error": "Authentication required"}

                migration_data = {}

                # Define key objects and their migration mappings
                migration_objects = {
                    "Account": {
                        "hubspot_target": "Company",
                        "key_fields": [
                            "Id",
                            "Name",
                            "Website",
                            "Phone",
                            "BillingAddress",
                            "Industry",
                            "AnnualRevenue",
                        ],
                        "where_clause": "IsDeleted = FALSE",
                    },
                    "Contact": {
                        "hubspot_target": "Contact",
                        "key_fields": [
                            "Id",
                            "FirstName",
                            "LastName",
                            "Email",
                            "Phone",
                            "AccountId",
                            "Title",
                        ],
                        "where_clause": "IsDeleted = FALSE AND Email != NULL",
                    },
                    "Lead": {
                        "hubspot_target": "Contact",
                        "key_fields": [
                            "Id",
                            "FirstName",
                            "LastName",
                            "Email",
                            "Phone",
                            "Company",
                            "Status",
                        ],
                        "where_clause": "IsDeleted = FALSE AND IsConverted = FALSE",
                    },
                    "Opportunity": {
                        "hubspot_target": "Deal",
                        "key_fields": [
                            "Id",
                            "Name",
                            "AccountId",
                            "Amount",
                            "CloseDate",
                            "StageName",
                            "Probability",
                        ],
                        "where_clause": "IsDeleted = FALSE",
                    },
                    "Case": {
                        "intercom_target": "Conversation",
                        "key_fields": [
                            "Id",
                            "Subject",
                            "Description",
                            "Status",
                            "Priority",
                            "ContactId",
                        ],
                        "where_clause": "IsDeleted = FALSE",
                    },
                }

                for obj_name, config in migration_objects.items():
                    logger.info(f"Extracting {obj_name} data for migration...")

                    result = await query_objects(
                        object_type=obj_name,
                        fields=", ".join(config["key_fields"]),
                        where_clause=config["where_clause"],
                        limit=5000,  # Increased limit for migration
                    )

                    if result["success"]:
                        migration_data[obj_name] = {
                            "records": result["records"],
                            "total_size": result["total_size"],
                            "target_system": config.get("hubspot_target")
                            or config.get("intercom_target"),
                            "migration_mapping": config,
                        }
                    else:
                        migration_data[obj_name] = {
                            "error": result["error"],
                            "target_system": config.get("hubspot_target")
                            or config.get("intercom_target"),
                        }

                # Calculate migration statistics
                total_records = sum(
                    data.get("total_size", 0)
                    for data in migration_data.values()
                    if isinstance(data, dict) and "total_size" in data
                )

                return {
                    "success": True,
                    "migration_data": migration_data,
                    "summary": {
                        "total_objects": len(migration_objects),
                        "total_records": total_records,
                        "extraction_timestamp": datetime.now().isoformat(),
                        "hubspot_objects": [
                            obj
                            for obj, config in migration_objects.items()
                            if "hubspot_target" in config
                        ],
                        "intercom_objects": [
                            obj
                            for obj, config in migration_objects.items()
                            if "intercom_target" in config
                        ],
                    },
                }

            except Exception as e:
                logger.error(f"Migration data extraction error: {e}")
                return {"success": False, "error": str(e)}

        @self.mcp_server.tool("describe_object")
        async def describe_object(object_type: str) -> dict[str, Any]:
            """Get detailed object schema information"""
            return await self._describe_object(object_type)

        @self.mcp_server.tool("get_api_limits")
        async def get_api_limits() -> dict[str, Any]:
            """Get current API usage and limits"""
            try:
                limits = await self._get_api_limits()
                return {"success": True, "limits": limits}
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def _authenticate(self) -> dict[str, Any]:
        """Internal authentication method"""
        return await self.mcp_server.call_tool("authenticate", {})

    async def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid authentication"""
        if not self.access_token or (
            self.session_expires and datetime.now() > self.session_expires
        ):
            auth_result = await self._authenticate()
            return auth_result.get("success", False)
        return True

    async def _describe_object(self, object_type: str) -> dict[str, Any]:
        """Internal method to describe Salesforce object"""
        try:
            if not await self._ensure_authenticated():
                return {"success": False, "error": "Authentication required"}

            describe_url = f"{self.instance_url_actual}/services/data/v57.0/sobjects/{object_type}/describe/"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            response = requests.get(describe_url, headers=headers)

            if response.status_code == 200:
                describe_data = response.json()
                return {
                    "success": True,
                    "name": describe_data["name"],
                    "label": describe_data["label"],
                    "fields": describe_data["fields"],
                    "queryable": describe_data.get("queryable", True),
                    "createable": describe_data.get("createable", False),
                    "updateable": describe_data.get("updateable", False),
                }
            else:
                return {
                    "success": False,
                    "error": f"Describe failed: {response.status_code} - {response.text}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_api_limits(self) -> dict[str, Any]:
        """Get API usage limits"""
        try:
            if not await self._ensure_authenticated():
                return {"error": "Authentication required"}

            limits_url = f"{self.instance_url_actual}/services/data/v57.0/limits/"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            response = requests.get(limits_url, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get limits: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _register_resources(self):
        """Register Salesforce MCP resources"""

        @self.mcp_server.resource("objects")
        async def get_objects() -> list[dict[str, Any]]:
            """Get list of available Salesforce objects"""
            try:
                if not await self._ensure_authenticated():
                    return []

                sobjects_url = (
                    f"{self.instance_url_actual}/services/data/v57.0/sobjects/"
                )
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                }

                response = requests.get(sobjects_url, headers=headers)

                if response.status_code == 200:
                    sobjects_data = response.json()
                    return [
                        {
                            "name": obj["name"],
                            "label": obj["label"],
                            "queryable": obj.get("queryable", False),
                            "createable": obj.get("createable", False),
                        }
                        for obj in sobjects_data["sobjects"]
                        if obj.get("queryable", False)  # Only return queryable objects
                    ]
                else:
                    logger.error(f"Failed to get objects: {response.status_code}")
                    return []

            except Exception as e:
                logger.error(f"Error getting objects: {e}")
                return []

    async def start(self):
        """Start the Salesforce MCP server"""
        logger.info(f"🚀 Starting Salesforce MCP Server on port {self.port}")

        # Test connection
        health = await self.mcp_server.call_tool("health_check", {})
        logger.info(f"   Health check: {health}")

        if health.get("healthy"):
            logger.info("✅ Salesforce MCP Server started successfully")
            logger.info("   🔗 API connection established")
            logger.info("   📊 Migration data extraction ready")
            logger.info("   🎯 HubSpot/Intercom migration capabilities enabled")
        else:
            logger.warning(
                "⚠️ Salesforce MCP Server started with limited functionality"
            )

    async def stop(self):
        """Stop the Salesforce MCP server"""
        logger.info("🛑 Stopping Salesforce MCP Server")


# Create server instance
salesforce_server = SalesforceMCPserver()

if __name__ == "__main__":
    asyncio.run(salesforce_server.start())


# --- Auto-inserted health endpoint ---
try:
    from fastapi import APIRouter

    router = APIRouter()

    @router.get("/health")
    async def health():
        return {
            "status": "ok",
            "version": "1.0.0",
            "features": [
                "data_extraction",
                "migration_preparation",
                "oauth_authentication",
            ],
        }

except ImportError:
    pass
