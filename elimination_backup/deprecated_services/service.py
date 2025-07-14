"""Main Lambda GPU service with dual-mode support."""

from backend.services.unified_memory_service_primary import UnifiedMemoryService
import os
from contextlib import asynccontextmanager
from typing import Any, Union

from prometheus_client import Counter, Histogram

from backend.core.auto_esc_config import get_config_value

from .cache import CortexCache
from .core import DirectCortexCore
from .enums import CortexModel, MCPMode, TaskType
from .errors import CortexAuthenticationError, CortexError
from .mcp_client import QdrantMCPClient
from .pool import AsyncConnectionPool

# Metrics
CORTEX_REQUESTS = Counter(
    "cortex_requests_total", "Total Cortex requests", ["mode", "task_type", "model"]
)
CORTEX_ERRORS = Counter(
    "cortex_errors_total", "Total Cortex errors", ["mode", "task_type", "error_type"]
)
CORTEX_LATENCY = Histogram(
    "cortex_latency_seconds", "Cortex request latency", ["mode", "task_type"]
)
CORTEX_CACHE_HITS = Counter("cortex_cache_hits_total", "Cache hits", ["task_type"])


class QdrantUnifiedMemoryService:
    """Unified Lambda GPU service with dual-mode support."""

    def __init__(
        self,
        mode: Union[MCPMode, str] = MCPMode.AUTO,
        enable_cache: bool = True,
        pool_size: int = 8,
    ):
        """Initialize Cortex service.

        Args:
            mode: Operation mode (DIRECT, MCP, or AUTO)
            enable_cache: Whether to enable result caching
            pool_size: Connection pool size for direct mode
        """
        self.mode = MCPMode(mode) if isinstance(mode, str) else mode
        self._enable_cache = enable_cache

        # Initialize components
        self._direct: DirectCortexCore | None = None
        self._mcp: QdrantMCPClient | None = None
        self._pool: AsyncConnectionPool | None = None
        self._cache: CortexCache | None = None

        # Load configuration
        self._load_config()

        # Determine actual mode if AUTO
        if self.mode == MCPMode.AUTO:
            self._determine_mode()

    def _load_config(self) -> None:
        """Load configuration from Pulumi ESC."""
        # Direct mode credentials
        self._
            "user": get_config_value("qdrant_user"),
            "password": get_config_value("postgres_password"),
            "account": get_config_value("postgres_host"),
            "warehouse": get_config_value("postgres_database"),
            "database": get_config_value("postgres_database"),
            "schema": get_config_value("postgres_schema"),
            "role": get_config_value("qdrant_role", "SYSADMIN"),
        }

        # MCP mode configuration
        self._mcp_config = {
            "pat_token": get_config_value("qdrant_mcp_pat"),
            "mcp_url": get_config_value("qdrant_mcp_url"),
        }

        # Context for direct mode




    def _determine_mode(self) -> None:
        """Auto-determine the best mode based on available credentials."""
        # Check environment override first
        env_mode = os.getenv("CORTEX_MODE")
        if env_mode:
            try:
                self.mode = MCPMode(env_mode.lower())
                return
            except ValueError:
                pass

        # Prefer MCP if PAT is available
        if self._mcp_config.get("pat_token"):
            self.mode = MCPMode.MCP

            "password"
        ):
            self.mode = MCPMode.DIRECT
        else:
            raise CortexAuthenticationError(
                "No valid credentials found for Cortex operations",
                details={
                    "pat_available": bool(self._mcp_config.get("pat_token")),
                    "user_pwd_available": bool(


                    ),
                },
            )

    async def initialize(self) -> None:
        """Initialize the service components."""
        # Initialize cache if enabled
        if self._enable_cache and not self._cache:
            self._cache = CortexCache()
            await self._cache.connect()

        # Initialize based on mode
        if self.mode == MCPMode.MCP:
            if not self._mcp:
                self._mcp = QdrantMCPClient(
                    base_url=self._mcp_config.get("mcp_url"),
                    pat_token=self._mcp_config.get("pat_token"),
                )
        else:  # DIRECT mode
            if not self._pool:
                self._pool = AsyncConnectionPool(
                    maxsize=8,
                    minsize=2,

                )
                await self._pool.initialize()

            if not self._direct:
                self._direct = DirectCortexCore(self._pool)
                self._direct.set_context(
                    warehouse=self._warehouse,
                    database=self._database,
                    schema=self._schema,
                )

    async def close(self) -> None:
        """Close all connections and resources."""
        if self._cache:
            await self._cache.close()

        if self._mcp:
            await self._mcp.close()

        if self._pool:
            await self._pool.close()

    @asynccontextmanager
    async def session(self):
        """Context manager for service lifecycle."""
        await self.initialize()
        try:
            yield self
        finally:
            await self.close()

    async def generate_embedding(
        self, text: str, model: str = "e5-base-v2"
    ) -> list[float]:
        """Generate embeddings for text.

        Args:
            text: Text to embed
            model: Embedding model to use

        Returns:
            Embedding vector
        """
        # Check cache
        if self._cache:
            cache_key = self._cache._generate_key(
                TaskType.EMBEDDING.value, text, model=model
            )
            cached = await self._cache.get(cache_key)
            if cached:
                CORTEX_CACHE_HITS.labels(task_type=TaskType.EMBEDDING.value).inc()
                return cached

        # Track metrics
        CORTEX_REQUESTS.labels(
            mode=self.mode.value, task_type=TaskType.EMBEDDING.value, model=model
        ).inc()

        with CORTEX_LATENCY.labels(
            mode=self.mode.value, task_type=TaskType.EMBEDDING.value
        ).time():
            try:
                if self.mode == MCPMode.MCP:
                    if not self._mcp:
                        await self.initialize()
                    result = await self._mcp.embed_text(text, model)
                else:
                    if not self._direct:
                        await self.initialize()
                    result = await self._direct.generate_embedding(text, model)

                # Cache result
                if self._cache and cache_key:
                    await self._cache.set(cache_key, result)

                return result

            except Exception as e:
                CORTEX_ERRORS.labels(
                    mode=self.mode.value,
                    task_type=TaskType.EMBEDDING.value,
                    error_type=type(e).__name__,
                ).inc()
                raise

    async def complete_text_with_cortex(
        self,
        prompt: str,
        model: Union[CortexModel, str] = CortexModel.MISTRAL_7B,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> str:
        """Generate text completion.

        Args:
            prompt: Input prompt
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        # Ensure model is CortexModel enum
        if isinstance(model, str):
            model = CortexModel(model)

        # Check cache
        if self._cache:
            cache_key = self._cache._generate_key(
                TaskType.COMPLETION.value,
                prompt,
                model=model.value,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            cached = await self._cache.get(cache_key)
            if cached:
                CORTEX_CACHE_HITS.labels(task_type=TaskType.COMPLETION.value).inc()
                return cached

        # Track metrics
        CORTEX_REQUESTS.labels(
            mode=self.mode.value, task_type=TaskType.COMPLETION.value, model=model.value
        ).inc()

        with CORTEX_LATENCY.labels(
            mode=self.mode.value, task_type=TaskType.COMPLETION.value
        ).time():
            try:
                if self.mode == MCPMode.MCP:
                    if not self._mcp:
                        await self.initialize()
                    result = await self._mcp.complete(
                        prompt, model, temperature, max_tokens, **kwargs
                    )
                else:
                    if not self._direct:
                        await self.initialize()
                    result = await self._direct.complete_text(
                        prompt, model, temperature, max_tokens, **kwargs
                    )

                # Cache result
                if self._cache and cache_key:
                    await self._cache.set(cache_key, result)

                return result

            except Exception as e:
                CORTEX_ERRORS.labels(
                    mode=self.mode.value,
                    task_type=TaskType.COMPLETION.value,
                    error_type=type(e).__name__,
                ).inc()
                raise

    async def analyze_sentiment(self, text: str) -> dict[str, Any]:
        """Analyze sentiment of text."""
        # Only available in direct mode currently
        if self.mode == MCPMode.MCP:
            # Fall back to direct mode for this operation
            if not self._direct:
                await self.initialize()
            return await self._direct.analyze_sentiment(text)
        else:
            if not self._direct:
                await self.initialize()
            return await self._direct.analyze_sentiment(text)

    async def summarize_text(self, text: str, max_length: int = 500) -> str:
        """Summarize text."""
        # Only available in direct mode currently
        if self.mode == MCPMode.MCP:
            # Use completion for summarization
            prompt = f"Summarize the following text in {max_length} characters or less:\n\n{text}"
            return await self.complete_text_with_cortex(
                prompt, model=CortexModel.MISTRAL_7B, max_tokens=max_length
            )
        else:
            if not self._direct:
                await self.initialize()
            return await self._direct.summarize_text(text, max_length)

    async def search(
        self,
        query: str,
        service: str,
        columns: list[str],
        limit: int = 10,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Execute Cortex Search (MCP mode only)."""
        if self.mode != MCPMode.MCP:
            raise CortexError(
                "Cortex Search is only available in MCP mode",
                details={"current_mode": self.mode.value},
            )

        if not self._mcp:
            await self.initialize()

        return await self._mcp.search(query, service, columns, limit, **kwargs)

    async def analyze(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Execute Cortex Analyst query (MCP mode only)."""
        if self.mode != MCPMode.MCP:
            raise CortexError(
                "Cortex Analyst is only available in MCP mode",
                details={"current_mode": self.mode.value},
            )

        if not self._mcp:
            await self.initialize()

        return await self._mcp.analyze(query, context, **kwargs)

    @property
    def current_mode(self) -> str:
        """Get current operation mode."""
        return self.mode.value

    @property
    def is_initialized(self) -> bool:
        """Check if service is initialized."""
        if self.mode == MCPMode.MCP:
            return self._mcp is not None
        else:
            return self._direct is not None and self._pool is not None
