"""
Aligned Snowflake Configuration for Sophia AI
Uses the actual Snowflake setup created during alignment process
Implements secure authentication with the provided PAT token
"""

import contextlib
import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SnowflakeCredentials:
    """Aligned Snowflake credentials from actual setup"""

    account: str = "ZNB04675.us-east-1"
    user: str = "SCOOBYJAVA15"
    password: str = "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A"
    role: str = "ACCOUNTADMIN"
    warehouse: str = "SOPHIA_AI_WH"
    database: str = "SOPHIA_AI_DB"
    schema: str = "ESTUARY_FLOW"


@dataclass
class SnowflakeSchemas:
    """Aligned schema configuration from actual setup"""

    raw_data: str = "RAW_DATA"
    staging: str = "STAGING"
    analytics: str = "ANALYTICS"
    estuary_flow: str = "ESTUARY_FLOW"
    cortex_ai: str = "CORTEX_AI"
    vector_search: str = "VECTOR_SEARCH"
    monitoring: str = "MONITORING"


class AlignedSnowflakeConfig:
    """
    Aligned Snowflake configuration manager
    Uses the actual Snowflake setup created during alignment
    Provides secure access to all configured schemas and tables
    """

    def __init__(self):
        self._credentials = SnowflakeCredentials()
        self._schemas = SnowflakeSchemas()
        self._connection_params: dict | None = None
        self._validate_setup()

    def _validate_setup(self):
        """Validate the Snowflake setup alignment"""
        try:
            # Check if connection info file exists
            connection_info_path = (
                "/home/ubuntu/sophia-project/snowflake_connection_info.json"
            )
            if os.path.exists(connection_info_path):
                import json

                with open(connection_info_path) as f:
                    connection_info = json.load(f)

                # Validate alignment
                if connection_info.get("account") == self._credentials.account:
                    logger.info("✅ Snowflake configuration aligned with actual setup")
                else:
                    logger.warning("⚠️ Configuration mismatch detected")
            else:
                logger.info(
                    "ℹ️ Connection info file not found, using default configuration"
                )

        except Exception as e:
            logger.warning(f"⚠️ Setup validation failed: {e}")

    def get_connection_params(self) -> dict:
        """Get connection parameters for Snowflake"""
        if not self._connection_params:
            self._connection_params = {
                "account": self._credentials.account,
                "user": self._credentials.user,
                "password": self._credentials.password,
                "role": self._credentials.role,
                "warehouse": self._credentials.warehouse,
                "database": self._credentials.database,
                "schema": self._credentials.schema,
            }

        return self._connection_params.copy()

    def get_connection_params_for_schema(self, schema_name: str) -> dict:
        """Get connection parameters for a specific schema"""
        params = self.get_connection_params()

        # Map schema names to actual schema names
        schema_mapping = {
            "raw_data": self._schemas.raw_data,
            "staging": self._schemas.staging,
            "analytics": self._schemas.analytics,
            "estuary_flow": self._schemas.estuary_flow,
            "cortex_ai": self._schemas.cortex_ai,
            "vector_search": self._schemas.vector_search,
            "monitoring": self._schemas.monitoring,
        }

        if schema_name in schema_mapping:
            params["schema"] = schema_mapping[schema_name]
        else:
            # Assume it's already a valid schema name
            params["schema"] = schema_name

        return params

    def get_table_reference(self, table_name: str, schema: str = "estuary_flow") -> str:
        """Get fully qualified table reference"""
        schema_name = getattr(self._schemas, schema, schema)
        return f"{self._credentials.database}.{schema_name}.{table_name}"

    def get_estuary_flow_tables(self) -> dict[str, str]:
        """Get all Estuary Flow table references"""
        return {
            "hubspot_contacts": self.get_table_reference("HUBSPOT_CONTACTS"),
            "hubspot_deals": self.get_table_reference("HUBSPOT_DEALS"),
            "gong_calls": self.get_table_reference("GONG_CALLS"),
            "slack_messages": self.get_table_reference("SLACK_MESSAGES"),
            "unified_contacts": self.get_table_reference("UNIFIED_CONTACTS"),
            "deal_intelligence": self.get_table_reference("DEAL_INTELLIGENCE"),
        }

    def get_analytics_views(self) -> dict[str, str]:
        """Get all analytics view references"""
        return {
            "contact_analytics": self.get_table_reference(
                "CONTACT_ANALYTICS", "analytics"
            ),
            "deal_pipeline_analytics": self.get_table_reference(
                "DEAL_PIPELINE_ANALYTICS", "analytics"
            ),
            "call_analytics": self.get_table_reference("CALL_ANALYTICS", "analytics"),
        }

    def get_monitoring_tables(self) -> dict[str, str]:
        """Get all monitoring table references"""
        return {
            "pipeline_metrics": self.get_table_reference(
                "PIPELINE_METRICS", "monitoring"
            ),
            "data_quality_metrics": self.get_table_reference(
                "DATA_QUALITY_METRICS", "monitoring"
            ),
        }

    def get_cortex_ai_config(self) -> dict:
        """Get Cortex AI configuration"""
        return {
            "schema": self._schemas.cortex_ai,
            "functions": {
                "complete": "SNOWFLAKE.CORTEX.COMPLETE",
                "sentiment": "SNOWFLAKE.CORTEX.SENTIMENT",
                "extract_answer": "SNOWFLAKE.CORTEX.EXTRACT_ANSWER",
                "summarize": "SNOWFLAKE.CORTEX.SUMMARIZE",
                "translate": "SNOWFLAKE.CORTEX.TRANSLATE",
            },
            "models": {
                "default": "mistral-7b",
                "alternatives": ["llama2-70b-chat", "mixtral-8x7b", "gemma-7b"],
            },
        }

    def get_vector_search_config(self) -> dict:
        """Get vector search configuration"""
        return {
            "schema": self._schemas.vector_search,
            "embedding_dimensions": 1536,  # OpenAI ada-002 dimensions
            "similarity_function": "COSINE",
            "index_type": "VECTOR",
        }

    def validate_connection(self) -> bool:
        """Validate Snowflake connection"""
        try:
            import snowflake.connector

            conn = snowflake.connector.connect(**self.get_connection_params())
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            logger.info(f"✅ Snowflake connection validated. Version: {version}")
            return True

        except Exception as e:
            logger.exception(f"❌ Snowflake connection validation failed: {e}")
            return False

    def get_estuary_materialization_config(self) -> dict:
        """Get Estuary Flow materialization configuration for Snowflake"""
        return {
            "connector_image": "ghcr.io/estuary/materialize-snowflake:dev",
            "config": {
                "account": self._credentials.account,
                "user": self._credentials.user,
                "password": self._credentials.password,
                "role": self._credentials.role,
                "warehouse": self._credentials.warehouse,
                "database": self._credentials.database,
                "schema": self._schemas.estuary_flow,
            },
            "bindings": [
                {
                    "source": "sophia_ai/hubspot_contacts",
                    "resource": {"table": "HUBSPOT_CONTACTS"},
                },
                {
                    "source": "sophia_ai/hubspot_deals",
                    "resource": {"table": "HUBSPOT_DEALS"},
                },
                {"source": "sophia_ai/gong_calls", "resource": {"table": "GONG_CALLS"}},
                {
                    "source": "sophia_ai/slack_messages",
                    "resource": {"table": "SLACK_MESSAGES"},
                },
                {
                    "source": "sophia_ai/unified_contacts",
                    "resource": {"table": "UNIFIED_CONTACTS"},
                },
                {
                    "source": "sophia_ai/deal_intelligence",
                    "resource": {"table": "DEAL_INTELLIGENCE"},
                },
            ],
        }


# Global instance for easy access
aligned_snowflake_config = AlignedSnowflakeConfig()


# Convenience functions
def get_snowflake_connection():
    """Get Snowflake connection using aligned configuration"""
    import snowflake.connector

    return snowflake.connector.connect(
        **aligned_snowflake_config.get_connection_params()
    )


def get_snowflake_connection_for_schema(schema_name: str):
    """Get Snowflake connection for specific schema"""
    import snowflake.connector

    return snowflake.connector.connect(
        **aligned_snowflake_config.get_connection_params_for_schema(schema_name)
    )


def execute_snowflake_query(query: str, schema: str = "estuary_flow"):
    """Execute query in Snowflake with aligned configuration"""
    from snowflake.connector import DictCursor

    conn = get_snowflake_connection_for_schema(schema)
    try:
        cursor = conn.cursor(DictCursor)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    finally:
        conn.close()


def test_snowflake_cortex(prompt: str, model: str = "mistral-7b"):
    """Test Snowflake Cortex AI function"""
    query = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{prompt}') as AI_RESPONSE
    """
    result = execute_snowflake_query(query, "cortex_ai")
    return result[0]["AI_RESPONSE"] if result else None


if __name__ == "__main__":
    # Test the configuration
    config = AlignedSnowflakeConfig()

    # Test connection
    if config.validate_connection():
        # Show configuration details

        for _schema_key, _schema_name in config._schemas.__dict__.items():
            pass

        for _table_key, _table_ref in config.get_estuary_flow_tables().items():
            pass

        # Test Cortex AI
        with contextlib.suppress(Exception):
            response = test_snowflake_cortex("What is Estuary Flow?")

    else:
        pass
