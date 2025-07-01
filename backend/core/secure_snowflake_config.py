"""
Secure Snowflake Configuration for Sophia AI
Implements programmatic authentication using service user and secure token
Replaces hardcoded credentials with ESC-managed secure configuration
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


@dataclass
class SnowflakeCredentials:
    """Secure Snowflake credentials using programmatic authentication"""
    account: str
    user: str
    password: str
    role: str
    warehouse: str
    database: str
    schema: str


class SecureSnowflakeConfig:
    """
    Secure Snowflake configuration manager
    Uses programmatic service user authentication with secure token
    """
    
    def __init__(self):
        self._credentials: Optional[SnowflakeCredentials] = None
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate that required environment variables are available"""
        required_vars = [
            "snowflake_account",
            "sophia_ai_token"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not get_config_value(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            raise ValueError(f"Missing required Snowflake configuration: {missing_vars}")
    
    @property
    def credentials(self) -> SnowflakeCredentials:
        """Get secure Snowflake credentials"""
        if self._credentials is None:
            self._credentials = SnowflakeCredentials(
                account=get_config_value("snowflake_account"),
                user="PROGRAMMATIC_SERVICE_USER",  # From knowledge base
                password=get_config_value("sophia_ai_token"),  # Secure token
                role=get_config_value("snowflake_role", "SYSADMIN"),
                warehouse=get_config_value("snowflake_warehouse", "COMPUTE_WH"),
                database=get_config_value("snowflake_database", "SOPHIA_AI"),
                schema=get_config_value("snowflake_schema", "PUBLIC")
            )
        return self._credentials
    
    def get_connection_params(self) -> dict:
        """Get connection parameters for Snowflake connector"""
        creds = self.credentials
        return {
            "account": creds.account,
            "user": creds.user,
            "password": creds.password,
            "role": creds.role,
            "warehouse": creds.warehouse,
            "database": creds.database,
            "schema": creds.schema
        }
    
    def get_connection_string(self) -> str:
        """Get connection string for SQLAlchemy or similar"""
        creds = self.credentials
        return (
            f"snowflake://{creds.user}:{creds.password}@{creds.account}/"
            f"{creds.database}/{creds.schema}?warehouse={creds.warehouse}&role={creds.role}"
        )
    
    def validate_connection(self) -> bool:
        """Validate that connection can be established"""
        try:
            import snowflake.connector
            
            conn = snowflake.connector.connect(**self.get_connection_params())
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            logger.info(f"Snowflake connection validated successfully. Version: {result[0]}")
            return True
            
        except Exception as e:
            logger.error(f"Snowflake connection validation failed: {e}")
            return False


# Global instance for application use
secure_snowflake_config = SecureSnowflakeConfig()


def get_secure_snowflake_connection():
    """
    Get a secure Snowflake connection using programmatic authentication
    
    Returns:
        snowflake.connector.SnowflakeConnection: Authenticated connection
    """
    try:
        import snowflake.connector
        return snowflake.connector.connect(**secure_snowflake_config.get_connection_params())
    except ImportError:
        logger.error("snowflake-connector-python not installed")
        raise
    except Exception as e:
        logger.error(f"Failed to create Snowflake connection: {e}")
        raise


def get_secure_connection_string() -> str:
    """
    Get secure Snowflake connection string for SQLAlchemy
    
    Returns:
        str: SQLAlchemy-compatible connection string
    """
    return secure_snowflake_config.get_connection_string()

