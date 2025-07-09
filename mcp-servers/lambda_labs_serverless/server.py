#!/usr/bin/env python3
"""
Lambda Labs Serverless MCP Server (Phase 2)
-----------------------------------------
A **minimal but production-safe** MCP server that exposes a single
`serverless_inference` tool.  It will evolve in Phase 3, but this version
is deliberately light-weight so the new server slot can be wired into the
MCP gateway, CI can start, and subsequent phases can iterate safely.

Design notes
• Depends only on standard library + `aiohttp` (already in repo stack).
• Reads `LAMBDA_LABS_API_KEY` from environment – **no other secrets**.
• Uses FastAPI under the hood via the existing StandardisedMCPServer base
  so it inherits health-check, metrics, and graceful-shutdown behaviour.
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from typing import Any

import aiohttp

# Import the enhanced base class.  Primary location after recent refactor is
# infrastructure.mcp_servers.base.  Keep a fallback to any legacy path to avoid
# runtime breakage while migration PRs merge.

try:
    from infrastructure.mcp_servers.base.enhanced_standardized_mcp_server import (
        EnhancedStandardizedMCPServer,
        MCPServerConfig,
    )
    from infrastructure.mcp_servers.base.standardized_mcp_server import ServerCapability
except ModuleNotFoundError:
    from backend.mcp_servers.base.enhanced_standardized_mcp_server import (  # type: ignore
        EnhancedStandardizedMCPServer,
        MCPServerConfig,
    )
    from backend.mcp_servers.base.standardized_mcp_server import (
        ServerCapability,  # type: ignore
    )

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants & helpers
# ---------------------------------------------------------------------------

DEFAULT_INFERENCE_ENDPOINT = "https://api.lambda.ai/v1/chat/completions"
DEFAULT_MODEL = "llama3.1-8b-instruct"


# type: ignore[misc] – base comes from dynamic import depending on path
class LambdaLabsServerlessMCP(EnhancedStandardizedMCPServer):  # type: ignore
    """Light-weight serverless inference server."""

    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self._api_key: str | None = os.getenv("LAMBDA_LABS_API_KEY")
        self._session: aiohttp.ClientSession | None = None

    # ------------- lifecycle -------------------------------------------------

    async def server_specific_init(self) -> None:
        """Initialise client session and sanity-check API key."""

        if not self._api_key:
            raise RuntimeError("LAMBDA_LABS_API_KEY not set in environment")

        timeout = aiohttp.ClientTimeout(total=30)
        self._session = aiohttp.ClientSession(timeout=timeout)
        logger.info("✅ λ Labs Serverless MCP initialised (model=%s)", DEFAULT_MODEL)

    async def server_specific_cleanup(self) -> None:
        if self._session:
            await self._session.close()

    # ------------- health ----------------------------------------------------

    async def server_specific_health_check(self):
        """Ping Lambda Labs with a 0-token dry-run to ensure key valid."""
        if not self._session:
            return self._crit("aiohttp session not initialised")
        try:
            payload = {
                "model": DEFAULT_MODEL,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 1,
                "temperature": 0,
            }
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            start = datetime.utcnow()
            async with self._session.post(
                DEFAULT_INFERENCE_ENDPOINT, headers=headers, json=payload
            ) as resp:
                latency_ms = (datetime.utcnow() - start).total_seconds() * 1000
                if resp.status == 200:
                    return self._ok(latency_ms)
                return self._unhealthy(latency_ms, f"HTTP {resp.status}")
        except Exception as exc:
            return self._crit(str(exc))

    # ------------- capabilities & sync --------------------------------------

    async def get_server_capabilities(self) -> list[ServerCapability]:
        return [
            ServerCapability(
                name="serverless_inference",
                description="Chat completions via Lambda Labs serverless API",
                category="ai_inference",
                available=True,
                version="0.1.0",
            )
        ]

    async def sync_data(self) -> dict[str, Any]:
        """No data to sync yet – return trivial success."""
        return {"synced": True, "ts": datetime.utcnow().isoformat()}

    # ------------- MCP tools -------------------------------------------------

    async def serverless_inference(
        self, prompt: str, max_tokens: int = 256, temperature: float = 0.7
    ) -> str:
        """Expose simple inference as an MCP tool (decorated dynamically)."""
        if not self._session:
            raise RuntimeError("Session not initialised")
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        async with self._session.post(
            DEFAULT_INFERENCE_ENDPOINT, headers=headers, json=payload
        ) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise RuntimeError(f"Lambda Labs error {resp.status}: {data}")
            return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Entrypoint helper
# ---------------------------------------------------------------------------


async def main() -> None:
    config = MCPServerConfig(
        name="lambda_labs_serverless",
        port=9025,
        enable_metrics=True,
    )

    server = LambdaLabsServerlessMCP(config)

    # Dynamically register tool after instantiation so decorator not required.
    server.register_tool(server.serverless_inference)

    await server.start()


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
