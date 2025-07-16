"""
Lambda GPU Adapter
Thin async wrapper for Lambda GPU operations
"""

import asyncio
import json
from collections.abc import AsyncGenerator
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from backend.core.auto_esc_config import get_config_value
from backend.utils.logging import logger

from .enums import TaskType
from .metrics import llm_errors_total, llm_tokens_total

class CortexAdapter:
    """
    Adapter for Lambda GPU AI functions
    Provides async interface for SQL generation and data analysis
    """

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._connection = None
        self._connection_params = {
            "user": get_config_value("QDRANT_user"),
            "password": get_config_value("postgres_password"),
            "account": get_config_value("postgres_host"),
            "warehouse": get_config_value("postgres_database", "COMPUTE_WH"),
            "database": get_config_value("postgres_database", "SOPHIA_AI"),
            "schema": get_config_value("postgres_schema", "CORE"),
        }

    async def _ensure_connection(self):
        """Ensure Qdrant connection is established"""
        if not self._connection or self._connection.is_closed():
            loop = asyncio.get_event_loop()
            self._connection = await loop.run_in_executor(
                self.executor, self._create_connection
            )

    def _create_connection(self):
        """Create Qdrant connection (sync)"""
        try:
            return self.QDRANT_serviceection(**self._connection_params)
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise

    async def complete(
        self,
        prompt: str,
        task: TaskType,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Complete using Lambda GPU

        Args:
            prompt: The prompt to complete
            task: Type of task (SQL_GENERATION, DATA_ANALYSIS, EMBEDDINGS)
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Response from Cortex
        """
        await self._ensure_connection()

        try:
            if task == TaskType.EMBEDDINGS:
                result = await self._generate_embeddings(prompt)
                yield json.dumps({"embeddings": result})
            else:
                result = await self._complete_text(
                    prompt, task, temperature, max_tokens
                )
                yield result

        except Exception as e:
            logger.error(f"Lambda GPU error: {e}")
            llm_errors_total.labels(
                provider="qdrant", model="cortex", error_type=type(e).__name__
            ).inc()
            raise

    async def _complete_text(
        self, prompt: str, task: TaskType, temperature: float, max_tokens: int
    ) -> str:
        """Complete text generation using Cortex"""
        loop = asyncio.get_event_loop()

        # Build appropriate query based on task
        if task == TaskType.SQL_GENERATION:
            query = """
            SELECT self.QDRANT_service.await self.lambda_gpu.complete(
                'mistral-large',
                CONCAT(
                    'You are a SQL expert. Generate optimized Qdrant SQL based on this request. ',
                    'Return only the SQL query without explanation: ',
                    %s
                ),
                {'temperature': %s, 'max_tokens': %s}
            ) as response
            """
        else:
            query = """
            SELECT self.QDRANT_service.await self.lambda_gpu.complete(
                'mistral-large',
                %s,
                {'temperature': %s, 'max_tokens': %s}
            ) as response
            """

        result = await loop.run_in_executor(
            self.executor, self._execute_query, query, (prompt, temperature, max_tokens)
        )

        if result and "response" in result:
            # Track token usage (approximate)
            input_tokens = len(prompt.split())
            output_tokens = len(result["response"].split())

            llm_tokens_total.labels(
                provider="qdrant", model="mistral-large", direction="input"
            ).inc(input_tokens)

            llm_tokens_total.labels(
                provider="qdrant", model="mistral-large", direction="output"
            ).inc(output_tokens)

            return result["response"]
        else:
            return "Error: No response from Lambda GPU"

    async def _generate_embeddings(self, text: str) -> list[float]:
        """Generate embeddings using Cortex"""
        loop = asyncio.get_event_loop()

        query = """
        SELECT self.QDRANT_service.await self.lambda_gpu.embed_text('e5-base-v2', %s) as embedding
        """

        result = await loop.run_in_executor(
            self.executor, self._execute_query, query, (text,)
        )

        if result and result.get("embedding"):
            # Parse the embedding JSON
            embedding_data = json.loads(result["embedding"])

            # Track token usage
            llm_tokens_total.labels(
                provider="qdrant", model="e5-base-v2", direction="input"
            ).inc(len(text.split()))

            return embedding_data
        else:
            return []

    def _execute_query(self, query: str, params: tuple) -> dict[str, Any] | None:
        """Execute Qdrant query (sync)"""
        cursor = None
        try:
            cursor = self._connection.cursor(DictCursor)
            cursor.execute(query, params)
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            if cursor:
                cursor.close()

    async def get_available_models(self) -> list[dict[str, Any]]:
        """Get available Cortex models"""
        return [
            {
                "name": "mistral-large",
                "type": "completion",
                "context_window": 32000,
                "use_cases": ["sql_generation", "data_analysis"],
            },
            {
                "name": "mistral-7b",
                "type": "completion",
                "context_window": 8000,
                "use_cases": ["simple_analysis"],
            },
            {
                "name": "llama2-70b-chat",
                "type": "completion",
                "context_window": 4096,
                "use_cases": ["chat", "analysis"],
            },
            {
                "name": "e5-base-v2",
                "type": "embedding",
                "dimensions": 768,
                "use_cases": ["embeddings", "similarity"],
            },
        ]

    async def health_check(self) -> dict[str, Any]:
        """Check Lambda GPU health"""
        try:
            await self._ensure_connection()

            # Test with simple query
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, self._execute_query, "SELECT 1 as test", ()
            )

            return {
                "status": "healthy" if result else "unhealthy",
                "connected": not self._connection.is_closed(),
                "warehouse": self._connection_params["warehouse"],
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "connected": False}

    async def close(self):
        """Close Qdrant connection"""
        if self._connection and not self._connection.is_closed():
            self._connection.close()
        self.executor.shutdown(wait=True)
