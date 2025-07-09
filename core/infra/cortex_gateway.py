"""
CortexGateway: unified async entry-point for all Snowflake Cortex and SQL operations.

– Guarantees ONE pooled connection via OptimizedConnectionManager
– Adds hooks for Prometheus metrics & credit-limit guardrails
– Public async API:
    complete(), embed(), batch_embed(), search(), sentiment(), execute_sql(), health_check()

Downstream services & agents should call:
    from core.infra.cortex_gateway import get_gateway
    gateway = get_gateway()
    await gateway.complete("Hello")
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from infrastructure.core.optimized_connection_manager import (
    ConnectionType,
    OptimizedConnectionManager,
)

logger = logging.getLogger(__name__)


def _prom_metrics(func):  # placeholder – connect to real Prom client later
    async def wrapper(self, *args, **kwargs):  # type: ignore[override]
        start = datetime.utcnow()
        result = await func(self, *args, **kwargs)
        duration = (datetime.utcnow() - start).total_seconds()
        logger.debug("CortexGateway.%s executed in %.3fs", func.__name__, duration)

        # Log usage to Snowflake table (fire-and-forget)
        try:
            await self._log_usage(func.__name__, duration)
        except Exception as log_exc:  # pragma: no cover
            logger.debug("Usage log failed: %s", log_exc)
        return result

    return wrapper


class CreditLimitExceeded(Exception):
    """Raised when daily credit / token budget is exceeded."""


def _credit_limit(max_credits_day: int = 100, max_tokens: int = 10_000):
    """Decorator stub – real implementation will consult cost table once available."""

    def decorator(func):  # type: ignore[override]
        async def wrapper(self, *args, **kwargs):
            # TODO: pull rolling totals from monitoring table and raise if limits exceeded
            return await func(self, *args, **kwargs)

        return wrapper

    return decorator


class CortexGateway:
    """Async singleton that routes every Snowflake call through one pooled connection."""

    _instance: CortexGateway | None = None
    _lock = asyncio.Lock()

    def __init__(self) -> None:
        self._initialized = False
        self.connection_manager = OptimizedConnectionManager()

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------
    async def initialize(self) -> None:
        if self._initialized:
            return
        await self.connection_manager.initialize()
        self._initialized = True
        logger.info("✅ CortexGateway initialised with OptimizedConnectionManager")

    async def _execute(self, sql: str, params: tuple | None = None):
        """Low-level helper for parameterised queries."""
        await self.initialize()
        return await self.connection_manager.execute_query(
            sql,
            params=params,
            connection_type=ConnectionType.SNOWFLAKE,
        )

    # ------------------------------------------------------------------
    # Public API wrappers
    # ------------------------------------------------------------------
    @_prom_metrics
    @_credit_limit()
    async def complete(self, prompt: str, model: str = "mixtral-8x7b") -> str:
        sql = "SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, %s) AS COMPLETION"
        rows = await self._execute(sql, (model, prompt))
        return rows[0]["COMPLETION"] if rows else ""

    @_prom_metrics
    async def sentiment(self, text: str) -> str:
        sql = "SELECT SNOWFLAKE.CORTEX.SENTIMENT(%s) AS SENTIMENT"
        rows = await self._execute(sql, (text,))
        return rows[0]["SENTIMENT"] if rows else ""

    @_prom_metrics
    async def embed(self, text: str, model: str = "e5-base-v2") -> list[float]:
        sql = "SELECT SNOWFLAKE.CORTEX.EMBED_TEXT(%s, %s) AS EMBED"
        rows = await self._execute(sql, (model, text))
        if not rows:
            return []
        emb = rows[0]["EMBED"]
        return json.loads(emb) if isinstance(emb, str) else emb

    @_prom_metrics
    async def batch_embed(
        self, texts: list[str], model: str = "e5-base-v2"
    ) -> list[list[float]]:
        # Uses array flatten trick to embed many rows in one query
        sql = "SELECT SNOWFLAKE.CORTEX.EMBED_TEXT(%s, value) AS EMBED FROM TABLE(FLATTEN(INPUT=>%s))"
        rows = await self._execute(sql, (model, json.dumps(texts)))
        embeds: list[list[float]] = []
        for r in rows:
            v = r["EMBED"]
            embeds.append(json.loads(v) if isinstance(v, str) else v)
        return embeds

    @_prom_metrics
    async def search(self, service: str, query: str, limit: int = 10):
        sql = f"SELECT * FROM TABLE(SNOWFLAKE.CORTEX.SEARCH_PREVIEW('{service}', %s, {limit}))"
        return await self._execute(sql, (query,))

    async def execute_sql(self, sql: str):
        """Run arbitrary SQL (used sparingly)"""
        return await self._execute(sql)

    async def health_check(self) -> dict[str, Any]:
        try:
            rows = await self._execute(
                "SELECT CURRENT_REGION() AS REGION, CURRENT_VERSION() AS VERSION"
            )
            return {"status": "healthy", "details": rows[0] if rows else {}}
        except Exception as exc:  # pragma: no cover
            return {"status": "unhealthy", "error": str(exc)}

    async def _log_usage(self, function_name: str, duration_s: float):
        """Insert usage record into CORTEX_USAGE_LOG. Creates table if missing."""
        # Tokens and credits are unknown here; we can approximate via duration
        sql_create = """
        CREATE TABLE IF NOT EXISTS CORTEX_USAGE_LOG (
            ts TIMESTAMP_NTZ,
            function STRING,
            duration_s FLOAT,
            user STRING DEFAULT CURRENT_USER(),
            warehouse STRING DEFAULT CURRENT_WAREHOUSE(),
            session_id NUMBER DEFAULT CURRENT_SESSION() )
        """
        sql_insert = "INSERT INTO CORTEX_USAGE_LOG(ts, function, duration_s) VALUES(CURRENT_TIMESTAMP(), %s, %s)"

        # Run in background without blocking caller
        await self._execute(sql_create)
        await self._execute(sql_insert, (function_name, duration_s))


# ------------------------------------------------------------------
# Singleton accessor
# ------------------------------------------------------------------
_gateway: CortexGateway | None = None


def get_gateway() -> CortexGateway:
    global _gateway
    if _gateway is None:
        _gateway = CortexGateway()
    return _gateway
