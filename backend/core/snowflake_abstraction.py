"""
Snowflake Abstraction Layer for Sophia AI
Provides secure, scalable interface to Snowflake with proper abstraction

This module implements:
- Abstract base classes for Snowflake operations
- Secure query execution with parameterization
- Connection pooling integration
- Performance monitoring
- Error handling and retry logic
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries for validation and optimization"""

    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    DDL = "DDL"
    PROCEDURE = "PROCEDURE"
    CORTEX = "CORTEX"
    COPY = "COPY"
    MERGE = "MERGE"


@dataclass
class QueryResult:
    """Standardized result for all query operations"""

    success: bool
    data: list[dict[str, Any]] | None = None
    error: str | None = None
    execution_time_ms: float = 0.0
    rows_affected: int = 0
    query_id: str | None = None
    warnings: list[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class SnowflakeAbstraction(ABC):
    """Abstract base for all Snowflake operations"""

    @abstractmethod
    async def execute_query(
        self,
        query: str,
        params: list[Any] | dict[str, Any] | None = None,
        query_type: QueryType = QueryType.SELECT,
        timeout: int | None = None,
    ) -> QueryResult:
        """Execute a single query with optional parameters"""
        pass

    @abstractmethod
    async def execute_batch(
        self,
        queries: list[tuple[str, list[Any] | dict[str, Any] | None]],
        transaction: bool = True,
        stop_on_error: bool = True,
    ) -> list[QueryResult]:
        """Execute multiple queries, optionally in a transaction"""
        pass

    @abstractmethod
    async def call_procedure(
        self,
        procedure_name: str,
        args: list[Any],
        database: str | None = None,
        schema: str | None = None,
    ) -> QueryResult:
        """Call a stored procedure"""
        pass

    @abstractmethod
    async def stream_query(
        self,
        query: str,
        params: list[Any] | dict[str, Any] | None = None,
        chunk_size: int = 1000,
    ):
        """Stream large query results"""
        pass

    @abstractmethod
    async def get_query_status(self, query_id: str) -> dict[str, Any]:
        """Get status of a running or completed query"""
        pass

    @abstractmethod
    async def cancel_query(self, query_id: str) -> bool:
        """Cancel a running query"""
        pass


class SecureSnowflakeExecutor(SnowflakeAbstraction):
    """Secure implementation with parameterized queries and monitoring"""

    def __init__(
        self,
        connection_pool,  # Will be ConnectionPool type
        query_validator=None,  # Will be QueryValidator type
        monitor=None,  # Will be PerformanceMonitor type
    ):
        self.pool = connection_pool
        self.query_validator = query_validator
        self.monitor = monitor
        self.retry_config = {
            "max_retries": 3,
            "backoff_factor": 2,
            "retriable_errors": ["NETWORK_ERROR", "TIMEOUT", "RESOURCE_BUSY"],
        }

    async def execute_query(
        self,
        query: str,
        params: list[Any] | dict[str, Any] | None = None,
        query_type: QueryType = QueryType.SELECT,
        timeout: int | None = None,
    ) -> QueryResult:
        """Execute query with full validation and monitoring"""
        start_time = time.time()

        # Validate query if validator available
        if self.query_validator and not await self.query_validator.is_safe(
            query, query_type
        ):
            return QueryResult(
                success=False,
                error="Query failed security validation",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        # Execute with retry logic
        last_error = None
        for attempt in range(self.retry_config["max_retries"]):
            try:
                result = await self._execute_with_monitoring(
                    query, params, query_type, timeout
                )

                # Record metrics if monitor available
                if self.monitor:
                    await self.monitor.record_query(
                        query_type=query_type,
                        execution_time_ms=result.execution_time_ms,
                        success=result.success,
                        rows_affected=result.rows_affected,
                    )

                return result

            except Exception as e:
                last_error = e
                if not self._is_retriable_error(e):
                    break

                # Exponential backoff
                if attempt < self.retry_config["max_retries"] - 1:
                    wait_time = self.retry_config["backoff_factor"] ** attempt
                    await asyncio.sleep(wait_time)

        # All retries failed
        return QueryResult(
            success=False,
            error=f"Query failed after {self.retry_config['max_retries']} attempts: {str(last_error)}",
            execution_time_ms=(time.time() - start_time) * 1000,
        )

    async def _execute_with_monitoring(
        self,
        query: str,
        params: list[Any] | dict[str, Any] | None,
        query_type: QueryType,
        timeout: int | None,
    ) -> QueryResult:
        """Execute query with connection from pool"""
        execution_start = time.time()

        async with self.pool.get_connection() as conn:
            cursor = conn.cursor()

            try:
                # Set query timeout if specified
                if timeout:
                    cursor.execute(
                        f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = {timeout}"
                    )

                # Execute query with parameters
                if params:
                    if isinstance(params, dict):
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Get query ID for tracking
                query_id = cursor.sfqid if hasattr(cursor, "sfqid") else None

                # Fetch results based on query type
                if query_type in [QueryType.SELECT, QueryType.CORTEX]:
                    # Fetch all results
                    columns = (
                        [desc[0] for desc in cursor.description]
                        if cursor.description
                        else []
                    )
                    rows = cursor.fetchall()

                    # Convert to list of dicts
                    data = []
                    for row in rows:
                        data.append(dict(zip(columns, row, strict=False)))

                    return QueryResult(
                        success=True,
                        data=data,
                        execution_time_ms=(time.time() - execution_start) * 1000,
                        rows_affected=len(data),
                        query_id=query_id,
                    )
                else:
                    # DML/DDL operations
                    rows_affected = (
                        cursor.rowcount if hasattr(cursor, "rowcount") else 0
                    )

                    return QueryResult(
                        success=True,
                        execution_time_ms=(time.time() - execution_start) * 1000,
                        rows_affected=rows_affected,
                        query_id=query_id,
                    )

            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                return QueryResult(
                    success=False,
                    error=str(e),
                    execution_time_ms=(time.time() - execution_start) * 1000,
                    query_id=query_id if "query_id" in locals() else None,
                )
            finally:
                cursor.close()

    async def execute_batch(
        self,
        queries: list[tuple[str, list[Any] | dict[str, Any] | None]],
        transaction: bool = True,
        stop_on_error: bool = True,
    ) -> list[QueryResult]:
        """Execute multiple queries with transaction support"""
        results = []

        async with self.pool.get_connection() as conn:
            cursor = conn.cursor()

            try:
                if transaction:
                    cursor.execute("BEGIN TRANSACTION")

                for query, params in queries:
                    try:
                        if params:
                            cursor.execute(query, params)
                        else:
                            cursor.execute(query)

                        results.append(
                            QueryResult(
                                success=True,
                                rows_affected=(
                                    cursor.rowcount
                                    if hasattr(cursor, "rowcount")
                                    else 0
                                ),
                            )
                        )

                    except Exception as e:
                        results.append(QueryResult(success=False, error=str(e)))

                        if stop_on_error:
                            if transaction:
                                cursor.execute("ROLLBACK")
                            raise

                if transaction:
                    cursor.execute("COMMIT")

            except Exception:
                if transaction:
                    try:
                        cursor.execute("ROLLBACK")
                    except:
                        pass

                # Fill remaining results with errors
                while len(results) < len(queries):
                    results.append(
                        QueryResult(success=False, error="Batch execution aborted")
                    )

            finally:
                cursor.close()

        return results

    async def call_procedure(
        self,
        procedure_name: str,
        args: list[Any],
        database: str | None = None,
        schema: str | None = None,
    ) -> QueryResult:
        """Call stored procedure with proper escaping"""
        # Build procedure call
        full_name = procedure_name
        if database and schema:
            full_name = f"{database}.{schema}.{procedure_name}"
        elif schema:
            full_name = f"{schema}.{procedure_name}"

        # Build parameter placeholders
        placeholders = ", ".join(["%s"] * len(args))
        query = f"CALL {full_name}({placeholders})"

        return await self.execute_query(
            query, params=args, query_type=QueryType.PROCEDURE
        )

    async def stream_query(
        self,
        query: str,
        params: list[Any] | dict[str, Any] | None = None,
        chunk_size: int = 1000,
    ):
        """Stream large query results in chunks"""
        async with self.pool.get_connection() as conn:
            cursor = conn.cursor()

            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                columns = (
                    [desc[0] for desc in cursor.description]
                    if cursor.description
                    else []
                )

                while True:
                    rows = cursor.fetchmany(chunk_size)
                    if not rows:
                        break

                    # Convert chunk to list of dicts
                    chunk_data = []
                    for row in rows:
                        chunk_data.append(dict(zip(columns, row, strict=False)))

                    yield chunk_data

            finally:
                cursor.close()

    async def get_query_status(self, query_id: str) -> dict[str, Any]:
        """Get query execution status"""
        query = """
        SELECT
            QUERY_ID,
            QUERY_TEXT,
            DATABASE_NAME,
            SCHEMA_NAME,
            QUERY_TYPE,
            SESSION_ID,
            USER_NAME,
            ROLE_NAME,
            WAREHOUSE_NAME,
            WAREHOUSE_SIZE,
            EXECUTION_STATUS,
            ERROR_CODE,
            ERROR_MESSAGE,
            START_TIME,
            END_TIME,
            TOTAL_ELAPSED_TIME,
            BYTES_SCANNED,
            ROWS_PRODUCED,
            COMPILATION_TIME,
            EXECUTION_TIME,
            QUEUED_PROVISIONING_TIME,
            QUEUED_REPAIR_TIME,
            QUEUED_OVERLOAD_TIME
        FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
        WHERE QUERY_ID = %s
        """

        result = await self.execute_query(query, params=[query_id])

        if result.success and result.data:
            return result.data[0]
        else:
            return {"error": "Query not found or access denied"}

    async def cancel_query(self, query_id: str) -> bool:
        """Cancel a running query"""
        try:
            result = await self.execute_query(
                f"SELECT SYSTEM$CANCEL_QUERY('{query_id}')", query_type=QueryType.SELECT
            )
            return result.success
        except Exception as e:
            logger.error(f"Failed to cancel query {query_id}: {e}")
            return False

    def _is_retriable_error(self, error: Exception) -> bool:
        """Check if error is retriable"""
        error_msg = str(error).upper()
        return any(
            retriable in error_msg
            for retriable in self.retry_config["retriable_errors"]
        )


class QueryBuilder:
    """Build safe, parameterized queries"""

    @staticmethod
    def build_insert(
        table: str,
        data: dict[str, Any],
        database: str | None = None,
        schema: str | None = None,
    ) -> tuple[str, list[Any]]:
        """Build parameterized INSERT query"""
        # Build fully qualified table name
        table_name = QueryBuilder._build_table_name(table, database, schema)

        # Extract columns and values
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ["%s"] * len(columns)

        query = f"""
        INSERT INTO {table_name} ({", ".join(columns)})
        VALUES ({", ".join(placeholders)})
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
        table_name = QueryBuilder._build_table_name(table, database, schema)

        # Build SET clause
        set_items = []
        values = []
        for column, value in data.items():
            set_items.append(f"{column} = %s")
            values.append(value)

        # Add WHERE parameters
        values.extend(where_params)

        query = f"""
        UPDATE {table_name}
        SET {", ".join(set_items)}
        WHERE {where_clause}
        """

        return query.strip(), values

    @staticmethod
    def build_merge(
        target_table: str,
        source_data: list[dict[str, Any]],
        merge_keys: list[str],
        update_columns: list[str],
        database: str | None = None,
        schema: str | None = None,
    ) -> tuple[str, list[Any]]:
        """Build MERGE statement for upsert operations"""
        table_name = QueryBuilder._build_table_name(target_table, database, schema)

        # Build source values
        all_columns = list(source_data[0].keys()) if source_data else []
        values = []
        value_rows = []

        for row in source_data:
            row_placeholders = []
            for col in all_columns:
                values.append(row.get(col))
                row_placeholders.append("%s")
            value_rows.append(f"({', '.join(row_placeholders)})")

        # Build MERGE statement
        merge_conditions = " AND ".join(
            [f"target.{key} = source.{key}" for key in merge_keys]
        )

        update_sets = ", ".join(
            [f"target.{col} = source.{col}" for col in update_columns]
        )

        insert_columns = ", ".join(all_columns)
        insert_values = ", ".join([f"source.{col}" for col in all_columns])

        query = f"""
        MERGE INTO {table_name} AS target
        USING (
            SELECT {", ".join([f"column{i + 1} AS {col}" for i, col in enumerate(all_columns)])}
            FROM VALUES {", ".join(value_rows)}
        ) AS source
        ON {merge_conditions}
        WHEN MATCHED THEN
            UPDATE SET {update_sets}
        WHEN NOT MATCHED THEN
            INSERT ({insert_columns})
            VALUES ({insert_values})
        """

        return query.strip(), values

    @staticmethod
    def _build_table_name(
        table: str, database: str | None = None, schema: str | None = None
    ) -> str:
        """Build fully qualified table name"""
        parts = []
        if database:
            parts.append(database)
        if schema:
            parts.append(schema)
        parts.append(table)

        return ".".join(parts)
