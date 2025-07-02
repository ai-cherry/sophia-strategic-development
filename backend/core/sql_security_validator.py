"""
SQL Security Validation Module for Sophia AI
Provides centralized validation for SQL identifiers to prevent injection attacks

This module implements enterprise-grade security patterns including:
- Whitelist-based identifier validation
- Input sanitization and length limits
- SQL injection pattern detection
- Comprehensive error handling and logging
"""

import logging
import re
from enum import Enum
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for different operations"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityError(Exception):
    """Custom exception for security violations"""

    pass


class SQLSecurityValidator:
    """Centralized SQL security validation for Sophia AI"""

    # Whitelisted SQL identifiers - PRODUCTION APPROVED
    SAFE_SCHEMAS = {
        "SOPHIA_AI_ADVANCED",
        "STG_TRANSFORMED",
        "RAW_estuary",
        "AI_MEMORY",
        "OPS_MONITORING",
        "UNIVERSAL_CHAT",
        "CEO_INTELLIGENCE",
        "NETSUITE_DATA",
        "PROPERTY_ASSETS",
        "AI_WEB_RESEARCH",
        "PAYREADY_CORE_SQL",
        "AI_ANALYTICS",
    }

    SAFE_TABLES = {
        "ENRICHED_HUBSPOT_DEALS",
        "ENRICHED_GONG_CALLS",
        "STG_GONG_CALLS",
        "STG_GONG_CALL_TRANSCRIPTS",
        "MEMORY_RECORDS",
        "AUTOMATED_INSIGHTS",
        "CUSTOMER_INTELLIGENCE_ADVANCED",
        "SALES_OPPORTUNITY_INTELLIGENCE",
        "COMMUNICATION_INTELLIGENCE_REALTIME",
        "COMPLIANCE_MONITORING_DASHBOARD",
        "MULTIMODAL_PROCESSING_LOG",
        "KNOWLEDGE_BASE_ENTRIES",
        "CONVERSATION_SESSIONS",
    }

    SAFE_WAREHOUSES = {"AI_SOPHIA_AI_WH", "SOPHIA_AI_WH", "ANALYTICS_WH", "SOPHIA_AI_WH"}

    SAFE_COLUMNS = {
        "ai_memory_embedding",
        "ai_memory_metadata",
        "ai_memory_updated_at",
        "id",
        "record_id",
        "deal_id",
        "call_id",
        "sentiment_score",
        "deal_stage",
        "primary_user_name",
        "contact_id",
        "message_id",
        "user_id",
        "session_id",
        "entry_id",
        "embedding_vector",
    }

    SAFE_MODELS = {
        "e5-base-v2",
        "multilingual-e5-large",
        "claude-3-5-sonnet",
        "llama2-70b-chat",
        "mistral-7b",
        "mixtral-8x7b",
        "snowflake-arctic-embed-m",
    }

    # SQL injection patterns to detect
    DANGEROUS_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|#|/\*|\*/)",  # SQL comments
        r"(\bUNION\b.*\bSELECT\b)",  # Union-based injection
        r"(\bOR\b.*=.*\bOR\b)",  # Boolean-based injection
        r"(;|\'\s*;\s*)",  # Statement termination
        r"(\bxp_cmdshell\b|\bsp_executesql\b)",  # Stored procedure injection
    ]

    @classmethod
    def validate_schema(
        cls, schema_name: str, security_level: SecurityLevel = SecurityLevel.HIGH
    ) -> str:
        """Validate schema name against whitelist"""
        if not schema_name:
            raise ValueError("Schema name cannot be empty")

        if not re.match(r"^[A-Z_][A-Z0-9_]*$", schema_name):
            raise ValueError(f"Invalid schema name format: {schema_name}")

        if schema_name not in cls.SAFE_SCHEMAS:
            logger.warning(f"Schema not in whitelist: {schema_name}")
            if security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                raise ValueError(f"Schema '{schema_name}' not in approved whitelist")

        cls._check_injection_patterns(schema_name, "schema")
        return schema_name

    @classmethod
    def validate_table(
        cls, table_name: str, security_level: SecurityLevel = SecurityLevel.HIGH
    ) -> str:
        """Validate table name against whitelist"""
        if not table_name:
            raise ValueError("Table name cannot be empty")

        if not re.match(r"^[A-Z_][A-Z0-9_]*$", table_name):
            raise ValueError(f"Invalid table name format: {table_name}")

        if table_name not in cls.SAFE_TABLES:
            logger.warning(f"Table not in whitelist: {table_name}")
            if security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                raise ValueError(f"Table '{table_name}' not in approved whitelist")

        cls._check_injection_patterns(table_name, "table")
        return table_name

    @classmethod
    def validate_warehouse(
        cls, warehouse_name: str, security_level: SecurityLevel = SecurityLevel.HIGH
    ) -> str:
        """Validate warehouse name against whitelist"""
        if not warehouse_name:
            raise ValueError("Warehouse name cannot be empty")

        if not re.match(r"^[A-Z_][A-Z0-9_]*$", warehouse_name):
            raise ValueError(f"Invalid warehouse name format: {warehouse_name}")

        if warehouse_name not in cls.SAFE_WAREHOUSES:
            logger.warning(f"Warehouse not in whitelist: {warehouse_name}")
            if security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                raise ValueError(
                    f"Warehouse '{warehouse_name}' not in approved whitelist"
                )

        cls._check_injection_patterns(warehouse_name, "warehouse")
        return warehouse_name

    @classmethod
    def validate_column(
        cls, column_name: str, security_level: SecurityLevel = SecurityLevel.MEDIUM
    ) -> str:
        """
        Validate column name against whitelist

        Args:
            column_name: Column name to validate
            security_level: Security level for validation strictness

        Returns:
            Validated column name

        Raises:
            ValueError: If column name is not in whitelist
            SecurityError: If dangerous patterns detected
        """
        if not column_name:
            raise ValueError("Column name cannot be empty")

        # Basic format validation
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", column_name):
            raise ValueError(f"Invalid column name format: {column_name}")

        # Whitelist validation (more lenient for columns)
        if column_name not in cls.SAFE_COLUMNS:
            logger.info(f"Column not in whitelist: {column_name}")
            if security_level == SecurityLevel.CRITICAL:
                raise ValueError(f"Column '{column_name}' not in approved whitelist")

        # SQL injection pattern detection
        cls._check_injection_patterns(column_name, "column")

        logger.debug(f"Column validation passed: {column_name}")
        return column_name

    @classmethod
    def validate_model(
        cls, model_name: str, security_level: SecurityLevel = SecurityLevel.HIGH
    ) -> str:
        """
        Validate AI model name against whitelist

        Args:
            model_name: Model name to validate
            security_level: Security level for validation strictness

        Returns:
            Validated model name

        Raises:
            ValueError: If model name is not in whitelist
            SecurityError: If dangerous patterns detected
        """
        if not model_name:
            raise ValueError("Model name cannot be empty")

        # Basic format validation
        if not re.match(r"^[a-zA-Z0-9_.-]+$", model_name):
            raise ValueError(f"Invalid model name format: {model_name}")

        # Whitelist validation
        if model_name not in cls.SAFE_MODELS:
            logger.warning(f"Model not in whitelist: {model_name}")
            if security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                raise ValueError(f"Model '{model_name}' not in approved whitelist")

        # SQL injection pattern detection
        cls._check_injection_patterns(model_name, "model")

        logger.debug(f"Model validation passed: {model_name}")
        return model_name

    @classmethod
    def sanitize_string(cls, input_string: str, max_length: int = 1000) -> str:
        """Sanitize string input for SQL safety"""
        if not input_string:
            return ""

        if len(input_string) > max_length:
            logger.warning(
                f"Input string truncated from {len(input_string)} to {max_length} characters"
            )
            input_string = input_string[:max_length]

        cls._check_injection_patterns(input_string, "string input")

        # Remove potentially dangerous characters
        sanitized = re.sub(r"[;\'\"\\]", "", input_string)
        sanitized = re.sub(r"--.*$", "", sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r"/\*.*?\*/", "", sanitized, flags=re.DOTALL)

        return sanitized.strip()

    @classmethod
    def validate_identifier(
        cls, identifier: str, identifier_type: str = "general"
    ) -> str:
        """
        Validate general SQL identifier format

        Args:
            identifier: SQL identifier to validate
            identifier_type: Type of identifier for logging

        Returns:
            Validated identifier

        Raises:
            ValueError: If identifier format is invalid
            SecurityError: If dangerous patterns detected
        """
        if not identifier:
            raise ValueError(f"{identifier_type} identifier cannot be empty")

        # Basic SQL identifier format
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
            raise ValueError(
                f"Invalid {identifier_type} identifier format: {identifier}"
            )

        # Length validation
        if len(identifier) > 128:  # Snowflake identifier limit
            raise ValueError(
                f"{identifier_type} identifier too long: {len(identifier)} > 128"
            )

        # SQL injection pattern detection
        cls._check_injection_patterns(identifier, identifier_type)

        logger.debug(f"{identifier_type} identifier validation passed: {identifier}")
        return identifier

    @classmethod
    def validate_query_parameters(
        cls, params: list[Any], max_params: int = 100
    ) -> list[Any]:
        """
        Validate query parameters for safety

        Args:
            params: List of query parameters
            max_params: Maximum number of parameters allowed

        Returns:
            Validated parameters

        Raises:
            ValueError: If parameters are invalid
        """
        if not params:
            return []

        # Parameter count validation
        if len(params) > max_params:
            raise ValueError(f"Too many parameters: {len(params)} > {max_params}")

        validated_params = []
        for _i, param in enumerate(params):
            if param is None:
                validated_params.append(None)
            elif isinstance(param, int | float | bool):
                validated_params.append(param)
            elif isinstance(param, str):
                # Sanitize string parameters
                sanitized = cls.sanitize_string(
                    param, max_length=8000
                )  # Snowflake limit
                validated_params.append(sanitized)
            else:
                # Convert other types to string and sanitize
                sanitized = cls.sanitize_string(str(param), max_length=8000)
                validated_params.append(sanitized)

        logger.debug(f"Query parameters validated: {len(validated_params)} parameters")
        return validated_params

    @classmethod
    def _check_injection_patterns(cls, input_string: str, context: str) -> None:
        """Check for SQL injection patterns in input"""
        input_upper = input_string.upper()

        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, input_upper, re.IGNORECASE):
                logger.error(
                    f"SQL injection pattern detected in {context}: {input_string}"
                )
                raise SecurityError(
                    f"Dangerous SQL pattern detected in {context}: {input_string}"
                )

    @classmethod
    def build_safe_query(
        cls, base_query: str, table_name: str, params: list[Any]
    ) -> tuple:
        """
        Build a safe parameterized query with validated identifiers

        Args:
            base_query: Base SQL query template
            table_name: Table name to validate and insert
            params: Query parameters to validate

        Returns:
            Tuple of (safe_query, validated_params)

        Raises:
            ValueError: If validation fails
            SecurityError: If dangerous patterns detected
        """
        # Validate table name
        safe_table = cls.validate_table(table_name)

        # Validate parameters
        safe_params = cls.validate_query_parameters(params)

        # Build safe query by inserting validated table name
        safe_query = base_query.replace("{table_name}", safe_table)

        # Final safety check on complete query
        cls._check_injection_patterns(safe_query, "complete query")

        logger.info(
            f"Safe query built for table {safe_table} with {len(safe_params)} parameters"
        )
        return safe_query, safe_params


# Convenience functions
def validate_schema_name(schema_name: str) -> str:
    """Convenience function for schema validation"""
    return SQLSecurityValidator.validate_schema(schema_name)


def validate_table_name(table_name: str) -> str:
    """Convenience function for table validation"""
    return SQLSecurityValidator.validate_table(table_name)


def validate_warehouse_name(warehouse_name: str) -> str:
    """Convenience function for warehouse validation"""
    return SQLSecurityValidator.validate_warehouse(warehouse_name)


def sanitize_user_input(user_input: str) -> str:
    """Convenience function for input sanitization"""
    return SQLSecurityValidator.sanitize_string(user_input)


# Security audit logging
def log_security_event(event_type: str, details: dict[str, Any]) -> None:
    """Log security events for monitoring"""
    logger.warning(f"SECURITY EVENT: {event_type} - {details}")


# Example usage and testing
if __name__ == "__main__":
    # Test the validator
    try:
        # Valid cases
        schema = SQLSecurityValidator.validate_schema("SOPHIA_AI_ADVANCED")
        table = SQLSecurityValidator.validate_table("ENRICHED_GONG_CALLS")
        warehouse = SQLSecurityValidator.validate_warehouse("AI_SOPHIA_AI_WH")

        print("✅ All validations passed")

        # Test sanitization
        safe_input = SQLSecurityValidator.sanitize_string(
            "Hello World! This is safe input."
        )
        print(f"✅ Sanitization test: {safe_input}")

    except (ValueError, SecurityError) as e:
        print(f"❌ Validation failed: {e}")
