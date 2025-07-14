"""
# REMOVED: ModernStack dependencyuration for Sophia AI
Implements programmatic authentication using service user and secure token
Replaces hardcoded credentials with ESC-managed secure configuration
"""

import logging
from dataclasses import dataclass

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


@dataclass
class ModernStackCredentials:
    """Secure ModernStack credentials using programmatic authentication"""

    account: str
    user: str
    password: str
    role: str
    warehouse: str
    database: str
    schema: str


# REMOVED: ModernStack dependency:
    """
# REMOVED: ModernStack dependencyuration manager
    Uses programmatic service user authentication with secure token
    """

    def __init__(self):
        self._credentials: ModernStackCredentials | None = None
        self._validate_environment()

    def _validate_environment(self):
        """Validate that required environment variables are available"""
        required_vars = ["postgres_host", "sophia_ai_token"]

        missing_vars = []
        for var in required_vars:
            if not get_config_value(var):
                missing_vars.append(var)

        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            raise ValueError(
# REMOVED: ModernStack dependencyuration: {missing_vars}"
            )

    @property
    def credentials(self) -> ModernStackCredentials:
        """Get secure ModernStack credentials"""
        if self._credentials is None:
            self._credentials = ModernStackCredentials(
                account=get_config_value("postgres_host"),
                user="SCOOBYJAVA15",  # From knowledge base
                password=get_config_value("sophia_ai_token"),  # Secure token
                role=get_config_value("modern_stack_role", "SYSADMIN"),
                warehouse=get_config_value("postgres_database", "SOPHIA_AI_WH"),
                database=get_config_value("postgres_database", "SOPHIA_AI"),
                schema=get_config_value("postgres_schema", "PUBLIC"),
            )
        return self._credentials

    def get_connection_params(self) -> dict:
        """Get connection parameters for ModernStack connector"""
        creds = self.credentials
        return {
            "account": creds.account,
            "user": creds.user,
            "password": creds.password,
            "role": creds.role,
            "warehouse": creds.warehouse,
            "database": creds.database,
            "schema": creds.schema,
        }

    def get_connection_string(self) -> str:
        """Get connection string for SQLAlchemy or similar"""
        creds = self.credentials
        return (
            f"modern_stack://{creds.user}:{creds.password}@{creds.account}/"
            f"{creds.database}/{creds.schema}?warehouse={creds.warehouse}&role={creds.role}"
        )

    def validate_connection(self) -> bool:
        """Validate that connection can be established"""
        try:
            # REMOVED: ModernStack dependency - use UnifiedMemoryServiceV3

            conn = self.modern_stack_connection(**self.get_connection_params())
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            logger.info(
                f"ModernStack connection validated successfully. Version: {result[0]}"
            )
            return True

        except Exception as e:
            logger.exception(f"ModernStack connection validation failed: {e}")
            return False


# Global instance for application use - using lazy initialization
_secure_# REMOVED: ModernStack dependency None


# REMOVED: ModernStack dependency:
# REMOVED: ModernStack dependencyuration instance with lazy initialization"""
# REMOVED: ModernStack dependency
# REMOVED: ModernStack dependency is None:
# REMOVED: ModernStack dependency()
# REMOVED: ModernStack dependency


# Backward compatibility - create a module-level callable that acts like a property
# REMOVED: ModernStack dependency:
# REMOVED: ModernStack dependency"""
# REMOVED: ModernStack dependency()


def get_secure_modern_stack_connection():
    """
    Get a secure ModernStack connection using programmatic authentication

    Returns:
        modern_stack.connector.ModernStackConnection: Authenticated connection
    """
    try:
        # REMOVED: ModernStack dependency - use UnifiedMemoryServiceV3

# REMOVED: ModernStack dependency()
        return self.modern_stack_connection(**config.get_connection_params())
    except ImportError:
        logger.exception("modern_stack-connector-python not installed")
        raise
    except Exception as e:
        logger.exception(f"Failed to create ModernStack connection: {e}")
        raise


def get_secure_connection_string() -> str:
    """
    Get secure ModernStack connection string for SQLAlchemy

    Returns:
        str: SQLAlchemy-compatible connection string
    """
# REMOVED: ModernStack dependency()
    return config.get_connection_string()
