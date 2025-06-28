"""
Security Module for Snowflake Operations
Provides query validation, SQL injection prevention, and parameterization

Features:
- SQL injection pattern detection
- Query type validation
- Parameterized query building
- Role-based access control helpers
- Data masking utilities
"""

import logging
import re
from enum import Enum
from typing import Any

import sqlparse
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import Keyword

from backend.core.snowflake_abstraction import QueryType

logger = logging.getLogger(__name__)


class SecurityThreatLevel(Enum):
    """Security threat levels"""

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SQLInjectionPatterns:
    """Common SQL injection patterns to detect"""

    # Basic injection patterns
    UNION_ATTACK = re.compile(r"\bUNION\s+(ALL\s+)?SELECT\b", re.IGNORECASE)
    COMMENT_INJECTION = re.compile(r"(--|#|/\*|\*/)", re.IGNORECASE)
    QUOTE_BREAK = re.compile(r"('\s*OR\s*'|'\s*AND\s*'|'\s*=\s*')", re.IGNORECASE)
    TAUTOLOGY = re.compile(
        r"(OR\s+1\s*=\s*1|AND\s+1\s*=\s*1|OR\s+\'1\'\s*=\s*\'1\')", re.IGNORECASE
    )

    # Advanced patterns
    STACKED_QUERIES = re.compile(
        r";\s*(DELETE|UPDATE|INSERT|DROP|CREATE|ALTER|EXEC)", re.IGNORECASE
    )
    TIME_BASED = re.compile(
        r"(WAITFOR\s+DELAY|SLEEP\s*\(|BENCHMARK\s*\()", re.IGNORECASE
    )
    OUT_OF_BAND = re.compile(
        r"(xp_cmdshell|sp_executesql|OPENROWSET|OPENDATASOURCE)", re.IGNORECASE
    )

    # Snowflake specific
    SYSTEM_FUNCTIONS = re.compile(
        r"(SYSTEM\$|ACCOUNT_USAGE\.|INFORMATION_SCHEMA\.)", re.IGNORECASE
    )

    @classmethod
    def get_all_patterns(cls) -> list[tuple[str, re.Pattern]]:
        """Get all injection patterns"""
        return [
            ("UNION_ATTACK", cls.UNION_ATTACK),
            ("COMMENT_INJECTION", cls.COMMENT_INJECTION),
            ("QUOTE_BREAK", cls.QUOTE_BREAK),
            ("TAUTOLOGY", cls.TAUTOLOGY),
            ("STACKED_QUERIES", cls.STACKED_QUERIES),
            ("TIME_BASED", cls.TIME_BASED),
            ("OUT_OF_BAND", cls.OUT_OF_BAND),
            ("SYSTEM_FUNCTIONS", cls.SYSTEM_FUNCTIONS),
        ]


class ThreatDetector:
    """Detect security threats in SQL queries"""

    def __init__(self):
        self.patterns = SQLInjectionPatterns.get_all_patterns()

    def has_injection_pattern(self, query: str) -> bool:
        """Quick check for any injection pattern"""
        for pattern_name, pattern in self.patterns:
            if pattern.search(query):
                logger.warning(f"SQL injection pattern detected: {pattern_name}")
                return True
        return False

    def analyze_threat_level(self, query: str) -> tuple[SecurityThreatLevel, list[str]]:
        """Analyze query and return threat level with detected patterns"""
        detected_patterns = []

        for pattern_name, pattern in self.patterns:
            if pattern.search(query):
                detected_patterns.append(pattern_name)

        if not detected_patterns:
            return SecurityThreatLevel.SAFE, []

        # Determine threat level based on patterns
        critical_patterns = {"STACKED_QUERIES", "OUT_OF_BAND", "SYSTEM_FUNCTIONS"}
        high_patterns = {"UNION_ATTACK", "TIME_BASED"}

        if any(p in critical_patterns for p in detected_patterns):
            return SecurityThreatLevel.CRITICAL, detected_patterns
        elif any(p in high_patterns for p in detected_patterns):
            return SecurityThreatLevel.HIGH, detected_patterns
        elif len(detected_patterns) > 2:
            return SecurityThreatLevel.MEDIUM, detected_patterns
        else:
            return SecurityThreatLevel.LOW, detected_patterns


class SQLParser:
    """Parse and analyze SQL queries"""

    @staticmethod
    def parse(query: str) -> sqlparse.sql.Statement:
        """Parse SQL query into AST"""
        parsed = sqlparse.parse(query)
        if not parsed:
            raise ParseError("Failed to parse SQL query")
        return parsed[0]

    @staticmethod
    def extract_tables(parsed_query: sqlparse.sql.Statement) -> list[str]:
        """Extract table names from parsed query"""
        tables = []

        def extract_from_tokens(tokens):
            idx = 0
            while idx < len(tokens):
                token = tokens[idx]

                if token.ttype is Keyword and token.value.upper() in [
                    "FROM",
                    "JOIN",
                    "INTO",
                ]:
                    idx += 1
                    while idx < len(tokens):
                        next_token = tokens[idx]
                        if isinstance(next_token, IdentifierList):
                            for identifier in next_token.get_identifiers():
                                tables.append(str(identifier))
                        elif isinstance(next_token, Identifier):
                            tables.append(str(next_token))
                        elif next_token.ttype is None:
                            tables.append(str(next_token))
                        else:
                            break
                        idx += 1
                elif hasattr(token, "tokens"):
                    extract_from_tokens(token.tokens)
                idx += 1

        extract_from_tokens(parsed_query.tokens)
        return tables

    @staticmethod
    def get_query_type(parsed_query: sqlparse.sql.Statement) -> QueryType:
        """Determine query type from parsed query"""
        first_token = parsed_query.get_type()

        if first_token == "SELECT":
            return QueryType.SELECT
        elif first_token == "INSERT":
            return QueryType.INSERT
        elif first_token == "UPDATE":
            return QueryType.UPDATE
        elif first_token == "DELETE":
            return QueryType.DELETE
        elif first_token in ["CREATE", "ALTER", "DROP"]:
            return QueryType.DDL
        elif first_token == "CALL":
            return QueryType.PROCEDURE
        elif first_token == "COPY":
            return QueryType.COPY
        elif first_token == "MERGE":
            return QueryType.MERGE
        else:
            # Check for Cortex functions
            query_upper = parsed_query.value.upper()
            if "SNOWFLAKE.CORTEX" in query_upper:
                return QueryType.CORTEX
            return QueryType.SELECT  # Default


class QueryValidator:
    """Validate queries for security threats"""

    def __init__(self):
        self.sql_parser = SQLParser()
        self.threat_detector = ThreatDetector()
        self.allowed_schemas = {
            "SOPHIA_AI_DEV",
            "SOPHIA_AI_PROD",
            "SOPHIA_AI_ADVANCED",
            "RAW_MULTIMODAL",
            "PROCESSED_AI",
            "REAL_TIME_ANALYTICS",
        }

    async def is_safe(self, query: str, query_type: QueryType) -> bool:
        """Validate query safety"""
        try:
            # Quick injection check
            if self.threat_detector.has_injection_pattern(query):
                return False

            # Parse query
            parsed = self.sql_parser.parse(query)

            # Validate based on query type
            if query_type == QueryType.SELECT:
                return await self._validate_select(parsed)
            elif query_type == QueryType.INSERT:
                return await self._validate_insert(parsed)
            elif query_type == QueryType.UPDATE:
                return await self._validate_update(parsed)
            elif query_type == QueryType.DELETE:
                return await self._validate_delete(parsed)
            elif query_type == QueryType.DDL:
                return await self._validate_ddl(parsed)
            elif query_type == QueryType.PROCEDURE:
                return await self._validate_procedure(parsed)
            elif query_type == QueryType.CORTEX:
                return await self._validate_cortex(parsed)
            else:
                return True

        except Exception as e:
            logger.error(f"Query validation error: {e}")
            return False

    async def _validate_select(self, parsed: sqlparse.sql.Statement) -> bool:
        """Validate SELECT query"""
        # Check for dangerous functions
        query_text = str(parsed).upper()
        dangerous_functions = ["SYSTEM$", "ACCOUNT_USAGE", "SNOWFLAKE.ACCOUNT_USAGE"]

        for func in dangerous_functions:
            if func in query_text:
                logger.warning(f"Dangerous function in SELECT: {func}")
                return False

        return True

    async def _validate_insert(self, parsed: sqlparse.sql.Statement) -> bool:
        """Validate INSERT query"""
        # Ensure no system tables
        tables = self.sql_parser.extract_tables(parsed)
        for table in tables:
            if self._is_system_table(table):
                return False
        return True

    async def _validate_update(self, parsed: sqlparse.sql.Statement) -> bool:
        """Validate UPDATE query"""
        # Must have WHERE clause
        query_text = str(parsed).upper()
        if "WHERE" not in query_text:
            logger.warning("UPDATE without WHERE clause detected")
            return False

        # Check tables
        tables = self.sql_parser.extract_tables(parsed)
        for table in tables:
            if self._is_system_table(table):
                return False
        return True

    async def _validate_delete(self, parsed: sqlparse.sql.Statement) -> bool:
        """Validate DELETE query"""
        # Must have WHERE clause
        query_text = str(parsed).upper()
        if "WHERE" not in query_text:
            logger.warning("DELETE without WHERE clause detected")
            return False

        # Check tables
        tables = self.sql_parser.extract_tables(parsed)
        for table in tables:
            if self._is_system_table(table):
                return False
        return True

    async def _validate_ddl(self, parsed: sqlparse.sql.Statement) -> bool:
        """Validate DDL query"""
        # Only allow in approved schemas
        query_text = str(parsed)

        # Extract schema/database references
        for schema in self.allowed_schemas:
            if schema in query_text.upper():
                return True

        logger.warning("DDL operation in non-approved schema")
        return False

    async def _validate_procedure(self, parsed: sqlparse.sql.Statement) -> bool:
        """Validate PROCEDURE call"""
        # Check for dangerous procedures
        query_text = str(parsed).upper()
        dangerous_procs = ["SYSTEM$", "TASK_", "PIPE_"]

        for proc in dangerous_procs:
            if proc in query_text:
                logger.warning(f"Dangerous procedure call: {proc}")
                return False

        return True

    async def _validate_cortex(self, parsed: sqlparse.sql.Statement) -> bool:
        """Validate Cortex function call"""
        # Cortex functions are generally safe but validate parameters
        query_text = str(parsed)

        # Check for parameter injection
        if "--" in query_text or "/*" in query_text:
            return False

        return True

    def _is_system_table(self, table_name: str) -> bool:
        """Check if table is a system table"""
        system_prefixes = ["INFORMATION_SCHEMA", "ACCOUNT_USAGE", "SNOWFLAKE."]

        table_upper = table_name.upper()
        return any(table_upper.startswith(prefix) for prefix in system_prefixes)


class ParameterizedQueryBuilder:
    """Build safe parameterized queries"""

    @staticmethod
    def build_insert(
        table: str,
        data: dict[str, Any],
        database: str | None = None,
        schema: str | None = None,
    ) -> tuple[str, list[Any]]:
        """Build parameterized INSERT query"""
        # Validate table name
        if not ParameterizedQueryBuilder._is_valid_identifier(table):
            raise ValueError(f"Invalid table name: {table}")

        # Build fully qualified table name
        table_name = ParameterizedQueryBuilder._build_table_name(
            table, database, schema
        )

        # Extract columns and values
        columns = list(data.keys())
        values = list(data.values())

        # Validate column names
        for col in columns:
            if not ParameterizedQueryBuilder._is_valid_identifier(col):
                raise ValueError(f"Invalid column name: {col}")

        placeholders = ["%s"] * len(columns)

        query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """

        return query.strip(), values

    @staticmethod
    def build_update(
        table: str,
        data: dict[str, Any],
        where_clause: str,
        where_params: list[Any],
        database: str | None = None,
        schema: str | None = None,
    ) -> tuple[str, list[Any]]:
        """Build parameterized UPDATE query"""
        # Validate inputs
        if not ParameterizedQueryBuilder._is_valid_identifier(table):
            raise ValueError(f"Invalid table name: {table}")

        table_name = ParameterizedQueryBuilder._build_table_name(
            table, database, schema
        )

        # Build SET clause
        set_items = []
        values = []
        for column, value in data.items():
            if not ParameterizedQueryBuilder._is_valid_identifier(column):
                raise ValueError(f"Invalid column name: {column}")
            set_items.append(f"{column} = %s")
            values.append(value)

        # Validate WHERE clause doesn't contain obvious injection
        if "--" in where_clause or "/*" in where_clause:
            raise ValueError("Suspicious WHERE clause detected")

        # Add WHERE parameters
        values.extend(where_params)

        query = f"""
        UPDATE {table_name}
        SET {', '.join(set_items)}
        WHERE {where_clause}
        """

        return query.strip(), values

    @staticmethod
    def build_delete(
        table: str,
        where_clause: str,
        where_params: list[Any],
        database: str | None = None,
        schema: str | None = None,
    ) -> tuple[str, list[Any]]:
        """Build parameterized DELETE query"""
        if not ParameterizedQueryBuilder._is_valid_identifier(table):
            raise ValueError(f"Invalid table name: {table}")

        table_name = ParameterizedQueryBuilder._build_table_name(
            table, database, schema
        )

        # Validate WHERE clause
        if not where_clause or where_clause.strip() == "":
            raise ValueError("DELETE requires WHERE clause")

        if "--" in where_clause or "/*" in where_clause:
            raise ValueError("Suspicious WHERE clause detected")

        query = f"""
        DELETE FROM {table_name}
        WHERE {where_clause}
        """

        return query.strip(), where_params

    @staticmethod
    def _build_table_name(
        table: str, database: str | None = None, schema: str | None = None
    ) -> str:
        """Build fully qualified table name"""
        parts = []

        if database:
            if not ParameterizedQueryBuilder._is_valid_identifier(database):
                raise ValueError(f"Invalid database name: {database}")
            parts.append(database)

        if schema:
            if not ParameterizedQueryBuilder._is_valid_identifier(schema):
                raise ValueError(f"Invalid schema name: {schema}")
            parts.append(schema)

        parts.append(table)

        return ".".join(parts)

    @staticmethod
    def _is_valid_identifier(identifier: str) -> bool:
        """Check if identifier is valid (alphanumeric + underscore)"""
        # Snowflake identifiers can contain letters, numbers, underscores
        # and dollar signs, but shouldn't contain quotes or semicolons
        invalid_chars = [";", "--", "/*", "*/", '"', "'", "\\"]

        if not identifier:
            return False

        for char in invalid_chars:
            if char in identifier:
                return False

        # Basic alphanumeric + underscore check
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_$]*$", identifier):
            # Could be quoted identifier, check if properly quoted
            if identifier.startswith('"') and identifier.endswith('"'):
                # Remove quotes and check inner content
                inner = identifier[1:-1]
                # Inner content shouldn't contain unescaped quotes
                if '"' in inner.replace('""', ""):
                    return False
                return True
            return False

        return True


class DataMasking:
    """Data masking utilities for sensitive information"""

    @staticmethod
    def create_masking_policy(
        policy_name: str, column_type: str, masking_expression: str
    ) -> str:
        """Create a dynamic data masking policy"""
        return f"""
        CREATE OR REPLACE MASKING POLICY {policy_name} AS (val {column_type})
        RETURNS {column_type} ->
        CASE
            WHEN CURRENT_ROLE() IN ('SOPHIA_AI_ADMIN', 'ACCOUNTADMIN') THEN val
            ELSE {masking_expression}
        END
        """

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address"""
        if "@" not in email:
            return "***@***.***"

        local, domain = email.split("@", 1)
        if len(local) <= 3:
            masked_local = "*" * len(local)
        else:
            masked_local = local[:2] + "*" * (len(local) - 3) + local[-1]

        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number"""
        # Keep only last 4 digits
        cleaned = re.sub(r"\D", "", phone)
        if len(cleaned) < 4:
            return "*" * len(phone)
        return "*" * (len(phone) - 4) + cleaned[-4:]

    @staticmethod
    def mask_ssn(ssn: str) -> str:
        """Mask SSN"""
        cleaned = re.sub(r"\D", "", ssn)
        if len(cleaned) != 9:
            return "*" * len(ssn)
        return f"***-**-{cleaned[-4:]}"


class ParseError(Exception):
    """SQL parsing error"""

    pass


# Create global instances for reuse
query_validator = QueryValidator()
threat_detector = ThreatDetector()
query_builder = ParameterizedQueryBuilder()
