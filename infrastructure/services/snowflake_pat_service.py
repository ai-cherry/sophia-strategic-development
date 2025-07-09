"""
Snowflake PAT Authentication Service
Enhances existing Snowflake services with PAT (Programmatic Access Token) support
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

import snowflake.connector
from snowflake.connector import DictCursor

from backend.core.auto_esc_config import SNOWFLAKE_PAT_CONFIG, get_config_value
from core.infra.cortex_gateway import get_gateway

logger = logging.getLogger(__name__)


class SnowflakePATService:
    """
    Enhanced Snowflake service with PAT authentication
    Uses CortexGateway for Cortex operations
    """

    def __init__(self):
        """Initialize with PAT authentication"""
        self.pat_token = get_config_value("snowflake_password")
        self.connection = None
        self.last_connection_time = None
        self.connection_timeout = 3600  # 1 hour
        self.gateway = get_gateway()  # Use CortexGateway

        # Validate PAT token
        if not self._validate_pat_token():
            logger.warning("Snowflake PAT token validation failed")

    def _validate_pat_token(self) -> bool:
        """Validate PAT token format"""
        if not self.pat_token:
            logger.error("No Snowflake PAT token configured")
            return False

        # PAT tokens are JWT tokens that start with 'eyJ'
        if self.pat_token.startswith("eyJ") and len(self.pat_token) > 100:
            logger.info("Snowflake PAT token format validated")
            return True

        logger.warning("Snowflake password may not be a valid PAT token")
        return False

    async def _create_connection(self) -> snowflake.connector.SnowflakeConnection:
        """Create connection with PAT authentication"""
        try:
            # Run synchronous connection in thread pool
            loop = asyncio.get_event_loop()
            connection = await loop.run_in_executor(None, self._create_sync_connection)

            self.last_connection_time = datetime.now()
            logger.info("Snowflake PAT connection established successfully")
            return connection

        except Exception as e:
            logger.error(f"Failed to create Snowflake PAT connection: {e!s}")
            raise

    def _create_sync_connection(self) -> snowflake.connector.SnowflakeConnection:
        """Create synchronous Snowflake connection"""
        return snowflake.connector.connect(
            account=get_config_value(
                "snowflake_account", SNOWFLAKE_PAT_CONFIG["account"]
            ),
            user=get_config_value("snowflake_user", SNOWFLAKE_PAT_CONFIG["user"]),
            password=self.pat_token,  # PAT token as password
            role=get_config_value("snowflake_role", SNOWFLAKE_PAT_CONFIG["role"]),
            warehouse=get_config_value(
                "snowflake_warehouse", SNOWFLAKE_PAT_CONFIG["warehouse"]
            ),
            database=get_config_value(
                "snowflake_database", SNOWFLAKE_PAT_CONFIG["database"]
            ),
            schema=get_config_value("snowflake_schema", SNOWFLAKE_PAT_CONFIG["schema"]),
            session_parameters={
                "QUERY_TAG": "sophia_ai_pat_service",
            },
        )

    async def ensure_connection(self) -> snowflake.connector.SnowflakeConnection:
        """Ensure valid connection exists"""
        # Check if connection exists and is not stale
        if self.connection and not self.connection.is_closed():
            if self.last_connection_time:
                elapsed = (datetime.now() - self.last_connection_time).seconds
                if elapsed < self.connection_timeout:
                    return self.connection

        # Create new connection
        self.connection = await self._create_connection()
        return self.connection

    async def test_connection(self) -> dict[str, Any]:
        """Test Snowflake PAT connection and CortexGateway"""
        try:
            # Test direct connection
            conn = await self.ensure_connection()
            cursor = conn.cursor(DictCursor)

            # Test query
            cursor.execute(
                """
                SELECT
                    CURRENT_ACCOUNT() as account,
                    CURRENT_USER() as user,
                    CURRENT_ROLE() as role,
                    CURRENT_WAREHOUSE() as warehouse,
                    CURRENT_DATABASE() as database,
                    CURRENT_SCHEMA() as schema,
                    CURRENT_VERSION() as version
            """
            )

            result = cursor.fetchone()
            cursor.close()

            # Test CortexGateway
            gateway_health = await self.gateway.health_check()

            return {
                "connected": True,
                "authentication": "PAT",
                "session_info": dict(result) if result else {},
                "pat_validated": self._validate_pat_token(),
                "gateway_status": gateway_health["status"],
            }

        except Exception as e:
            logger.error(f"Connection test failed: {e!s}")
            return {
                "connected": False,
                "authentication": "PAT",
                "error": str(e),
                "pat_validated": self._validate_pat_token(),
            }

    async def execute_cortex_complete(
        self,
        prompt: str,
        model: str = "llama3.1-8b",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """Execute Cortex Complete using CortexGateway"""
        try:
            # Use CortexGateway for Cortex operations
            response = await self.gateway.complete(prompt, model)
            return response

        except Exception as e:
            logger.error(f"Cortex Complete error: {e!s}")
            raise

    async def execute_cortex_embed(
        self, text: str, model: str = "e5-base-v2"
    ) -> list[float]:
        """Generate embeddings using CortexGateway"""
        try:
            # Use CortexGateway for embeddings
            embedding = await self.gateway.embed(text, model)
            return embedding

        except Exception as e:
            logger.error(f"Cortex Embed error: {e!s}")
            raise

    async def natural_language_to_sql(
        self, query: str, schema_context: str | None = None
    ) -> dict[str, Any]:
        """Convert natural language to SQL using Cortex"""
        try:
            # Build prompt
            prompt = f"""Convert this natural language query to Snowflake SQL:

Query: {query}

Database Context:
- Database: {get_config_value("snowflake_database", "SOPHIA_AI_PROD")}
- Schema: {get_config_value("snowflake_schema", "PUBLIC")}

{f"Schema Information:{chr(10)}{schema_context}" if schema_context else ""}

Requirements:
- Use proper Snowflake syntax
- Include appropriate JOINs
- Add WHERE clauses for filtering
- Optimize for performance
- Return only the SQL query

SQL Query:"""

            # Get SQL from Cortex using gateway
            sql = await self.gateway.complete(prompt, "mistral-large")

            # Extract clean SQL
            sql_clean = self._extract_sql_from_response(sql)

            return {
                "success": True,
                "natural_language": query,
                "generated_sql": sql_clean,
                "model": "mistral-large",
                "authentication": "PAT",
            }

        except Exception as e:
            logger.error(f"Natural language to SQL failed: {e!s}")
            return {"success": False, "error": str(e), "natural_language": query}

    def _extract_sql_from_response(self, response: str) -> str:
        """Extract clean SQL from Cortex response"""
        # Remove markdown code blocks
        if "```sql" in response:
            start = response.find("```sql") + 6
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()

        # Return cleaned response
        lines = response.split("\n")
        sql_lines = []

        for line in lines:
            line = line.strip()
            if line.upper().startswith(
                ("SELECT", "WITH", "INSERT", "UPDATE", "DELETE")
            ) or (sql_lines and line and not line.startswith(("Note:", "Explanation:"))):
                sql_lines.append(line)

        return "\n".join(sql_lines).strip()

    async def close(self):
        """Close Snowflake connection"""
        if self.connection and not self.connection.is_closed():
            try:
                self.connection.close()
                logger.info("Snowflake PAT connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e!s}")
            finally:
                self.connection = None
                self.last_connection_time = None
