"""Snowflake configuration utilities for Sophia AI"""

from backend.core.auto_esc_config import get_config_value


class SnowflakeConfig:
    """Centralized Snowflake configuration management"""

    @staticmethod
    def get_connection_params() -> dict[str, str]:
        """Get Snowflake connection parameters from Pulumi ESC"""
        return {
            "account": get_config_value("snowflake_account"),
            "user": get_config_value("snowflake_user"),
            "password": get_config_value("snowflake_password"),
            "warehouse": get_config_value(
                "snowflake_warehouse", "SOPHIA_AI_ANALYTICS_WH"
            ),
            "database": get_config_value("snowflake_database", "SOPHIA_AI"),
            "schema": get_config_value("snowflake_schema", "FOUNDATIONAL_KNOWLEDGE"),
            "role": get_config_value("snowflake_role", "SOPHIA_AI_APPLICATION"),
        }

    @staticmethod
    def get_warehouse_for_workload(workload_type: str) -> str:
        """Get appropriate warehouse based on workload type"""
        warehouse_mapping = {
            "analytics": "SOPHIA_AI_ANALYTICS_WH",
            "etl": "SOPHIA_AI_ETL_WH",
            "ml": "SOPHIA_AI_ML_WH",
            "embedding": "SOPHIA_AI_ML_WH",
            "default": "SOPHIA_AI_ANALYTICS_WH",
        }
        return warehouse_mapping.get(workload_type, warehouse_mapping["default"])

    @staticmethod
    def get_embedding_model() -> str:
        """Get the embedding model to use"""
        return get_config_value("snowflake_embedding_model", "e5-base-v2")

    @staticmethod
    def get_vector_dimension() -> int:
        """Get the vector dimension for embeddings"""
        return int(get_config_value("snowflake_vector_dimension", "768"))
