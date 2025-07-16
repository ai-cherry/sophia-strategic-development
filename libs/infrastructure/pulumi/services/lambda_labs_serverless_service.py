"""Lambda Labs serverless inference service with retry logic and cost tracking."""

import logging
import sqlite3
import time
from dataclasses import dataclass
from typing import Any

import aiohttp  # type: ignore[import-not-found]
from tenacity import (  # type: ignore[import-not-found]
    retry,
    stop_after_attempt,
    wait_exponential,
)

from backend.core.auto_esc_config import (
    get_config_value,  # type: ignore[import-not-found]
)

logger = logging.getLogger(__name__)

MODELS = {
    "llama3.1-8b-instruct": {"cost_per_million": 0.07, "context": 8192},
    "llama3.1-70b-instruct-fp8": {"cost_per_million": 0.35, "context": 8192},
    "llama-4-maverick-17b-128e-instruct-fp8": {
        "cost_per_million": 0.88,
        "context": 8192,
    },
}

@dataclass
class UsageRecord:
    """Record of API usage for cost tracking."""

    timestamp: int
    model: str
    tokens: int
    cost: float
    latency_ms: int
    user_id: str | None = None
    session_id: str | None = None

class LambdaLabsServerlessService:
    """Service for Lambda Labs serverless inference with cost tracking.

    This service provides:
    - Serverless inference via Lambda Labs API
    - Automatic retry logic with exponential backoff
    - Cost tracking in SQLite database
    - Usage statistics and reporting

    Attributes:
        api_key: Lambda Labs API key
        base_url: API endpoint base URL
        db_path: Path to SQLite database for usage tracking
    """

    def __init__(self, db_path: str = "data/lambda_usage.db"):
        """Initialize the serverless service.

        Args:
            db_path: Path to SQLite database for usage tracking
        """
        self.api_key = get_config_value("lambda_serverless_api_key")
        self.base_url = "https://api.lambdalabs.com/v1"
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database for usage tracking."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                model TEXT NOT NULL,
                tokens INTEGER NOT NULL,
                cost REAL NOT NULL,
                latency_ms INTEGER,
                user_id TEXT,
                session_id TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def generate(
        self,
        messages: list[dict[str, str]],
        model: str = "llama3.1-70b-instruct-fp8",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Generate completion with retry logic and cost tracking.

        Args:
            messages: OpenAI-format messages
            model: Model to use for generation
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            user_id: Optional user identifier
            session_id: Optional session identifier

        Returns:
            API response with completion

        Raises:
            ValueError: If model is unknown
            aiohttp.ClientError: If API request fails after retries
        """
        start_time = time.time()

        # Validate model
        if model not in MODELS:
            raise ValueError(f"Unknown model: {model}")

        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Make request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                result = await response.json()

        # Track usage
        latency_ms = int((time.time() - start_time) * 1000)
        tokens_used = result.get("usage", {}).get("total_tokens", 0)
        cost = (tokens_used / 1_000_000) * MODELS[model]["cost_per_million"]

        await self._track_usage(
            model=model,
            tokens=tokens_used,
            cost=cost,
            latency_ms=latency_ms,
            user_id=user_id,
            session_id=session_id,
        )

        return result

    async def _track_usage(
        self,
        model: str,
        tokens: int,
        cost: float,
        latency_ms: int,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> None:
        """Track usage in database.

        Args:
            model: Model used
            tokens: Number of tokens consumed
            cost: Cost in USD
            latency_ms: Request latency in milliseconds
            user_id: Optional user identifier
            session_id: Optional session identifier
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT INTO usage (timestamp, model, tokens, cost, latency_ms, user_id, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (int(time.time()), model, tokens, cost, latency_ms, user_id, session_id),
        )
        conn.commit()
        conn.close()

    def get_usage_stats(self, days: int = 30) -> dict[str, Any]:
        """Get usage statistics for the specified period.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary containing usage statistics by model
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Calculate time range
        end_time = int(time.time())
        start_time = end_time - (days * 86400)

        # Get aggregate stats
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_requests,
                SUM(tokens) as total_tokens,
                SUM(cost) as total_cost,
                AVG(latency_ms) as avg_latency,
                model,
                COUNT(DISTINCT user_id) as unique_users
            FROM usage
            WHERE timestamp >= ?
            GROUP BY model
            """,
            (start_time,),
        )

        model_stats = {}
        for row in cursor.fetchall():
            model_stats[row[4]] = {
                "requests": row[0],
                "tokens": row[1],
                "cost": row[2],
                "avg_latency_ms": row[3],
                "unique_users": row[5],
            }

        conn.close()

        return {
            "period_days": days,
            "model_stats": model_stats,
            "start_time": start_time,
            "end_time": end_time,
        }
