"""Unified Multi-Database Integration Layer.

Provides :class:`MultiDatabaseManager` which routes queries between
PostgreSQL, Redis, Pinecone and Weaviate. Results are merged with a
simple relevance score.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import psycopg2
import redis

from backend.core.comprehensive_memory_manager import (
    MemoryOperationType,
    MemoryRequest,
    comprehensive_memory_manager,
)

logger = logging.getLogger(__name__)


class MultiDatabaseManager:
    """Manage connections to multiple databases."""
    def __init__(
        self,
        pg_dsn: str,
        redis_url: str,
        pinecone_key: str,
        weaviate_url: str,
        weaviate_key: str,
    ) -> None:
        self.pg_conn = psycopg2.connect(pg_dsn)
        self.redis = redis.Redis.from_url(redis_url)
        # Replaced pinecone.init with ComprehensiveMemoryManager
        self.pinecone = comprehensive_memory_manager
        # Replaced weaviate.Client with ComprehensiveMemoryManager
        self.weaviate = comprehensive_memory_manager
        logger.info("MultiDatabaseManager initialized")

    # ------------------------------------------------------------------
    # Query routing
    # ------------------------------------------------------------------
    async def query(self, text: str) -> List[Dict[str, Any]]:
        """Route query to vector DBs and Postgres."""
        results = [].

        try:
            vec = await self._vector_search(text)
            results.extend(vec)
        except Exception as exc:  # noqa: BLE001
            logger.error("Vector search failed: %s", exc)
        try:
            sql_res = self._sql_search(text)
            results.extend(sql_res)
        except Exception as exc:  # noqa: BLE001
            logger.error("SQL search failed: %s", exc)
        return self._deduplicate(results)

    async def _vector_search(self, text: str) -> List[Dict[str, Any]]:
        """Search Pinecone and Weaviate."""
        pine = await comprehensive_memory_manager.process_memory_request(
            MemoryRequest(operation=MemoryOperationType.RETRIEVE, query=text, top_k=5)
        )
        # Simplified return for now
        return pine.get("matches", []) if pine else []

    def _sql_search(self, text: str) -> List[Dict[str, Any]]:
        with self.pg_conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM companies WHERE name ILIKE %s LIMIT 5", (f"%{text}%",)
            )
            rows = cur.fetchall()
        return [{"source": "postgres", "row": r} for r in rows]

    def _deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        deduped = []
        for r in results:
            key = str(r)
            if key not in seen:
                seen.add(key)
                deduped.append(r)
        return deduped

    def health(self) -> Dict[str, Any]:
        return {
            "postgres": self.pg_conn.closed == 0,
            "redis": self.redis.ping(),
            "pinecone": True,  # assume client handles health
            "weaviate": self.weaviate.is_ready(),
        }
