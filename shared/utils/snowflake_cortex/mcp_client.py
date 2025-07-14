"""MCP client wrapper for Lambda GPU operations."""

import os
from typing import Any

import httpx

from .enums import CortexModel
from .errors import CortexAuthenticationError, MCPServerError


class ModernStackMCPClient:
    """Client for interacting with ModernStack MCP server."""

    def __init__(
        self,
        base_url: str | None = None,
        pat_token: str | None = None,
        timeout: float = 30.0,
    ):
        """Initialize MCP client.

        Args:
            base_url: Base URL for MCP server
            pat_token: Programmatic Access Token
            timeout: Request timeout in seconds
        """
        self._base_url = base_url or os.getenv(
            "SNOWFLAKE_MCP_URL", "http://modern_stack-mcp:9130"
        )
        self._token = pat_token or os.getenv("SNOWFLAKE_MCP_PAT")

        if not self._token:
            raise CortexAuthenticationError(
                "No PAT token provided for MCP authentication",
                details={"env_var": "SNOWFLAKE_MCP_PAT"},
            )

        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def health_check(self) -> dict[str, Any]:
        """Check MCP server health."""
        try:
            response = await self._client.get("/health")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise MCPServerError(f"Health check failed: {e}", details={"error": str(e)})

    async def embed_text(self, text: str, model: str = "e5-base-v2") -> list[float]:
        """Generate embeddings for text.

        Args:
            text: Text to embed
            model: Embedding model to use

        Returns:
            Embedding vector
        """
        try:
            response = await self._client.post(
                "/tools/embed", json={"model": model, "text": text}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("vector", result.get("embedding", []))
        except httpx.HTTPError as e:
            raise MCPServerError(
                f"Embedding generation failed: {e}",
                details={"model": model, "error": str(e)},
            )

    async def complete(
        self,
        prompt: str,
        model: CortexModel,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> str:
        """Generate text completion.

        Args:
            prompt: Input prompt
            model: Cortex model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model parameters

        Returns:
            Generated text
        """
        try:
            response = await self._client.post(
                "/tools/complete",
                json={
                    "model": model.value,
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    **kwargs,
                },
            )
            response.raise_for_status()
            result = response.json()
            return result.get("completion", result.get("text", ""))
        except httpx.HTTPError as e:
            raise MCPServerError(
                f"Completion generation failed: {e}",
                details={"model": model.value, "error": str(e)},
            )

    async def search(
        self,
        query: str,
        service: str,
        columns: list[str],
        limit: int = 10,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Execute Cortex Search.

        Args:
            query: Search query
            service: Cortex Search service name
            columns: Columns to search
            limit: Maximum results
            **kwargs: Additional search parameters

        Returns:
            Search results
        """
        try:
            response = await self._client.post(
                "/tools/search",
                json={
                    "query": query,
                    "service": service,
                    "columns": columns,
                    "limit": limit,
                    **kwargs,
                },
            )
            response.raise_for_status()
            result = response.json()
            return result.get("results", [])
        except httpx.HTTPError as e:
            raise MCPServerError(
                f"Search failed: {e}", details={"service": service, "error": str(e)}
            )

    async def analyze(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Execute Cortex Analyst query.

        Args:
            query: Natural language query
            context: Query context
            **kwargs: Additional parameters

        Returns:
            Analysis results
        """
        try:
            response = await self._client.post(
                "/tools/analyze",
                json={"query": query, "context": context or {}, **kwargs},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise MCPServerError(
                f"Analysis failed: {e}", details={"query": query, "error": str(e)}
            )

    async def list_capabilities(self) -> dict[str, Any]:
        """List available MCP server capabilities."""
        try:
            response = await self._client.get("/capabilities")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise MCPServerError(
                f"Failed to list capabilities: {e}", details={"error": str(e)}
            )
