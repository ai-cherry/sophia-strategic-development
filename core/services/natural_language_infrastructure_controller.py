"""
Natural Language Infrastructure Controller
=========================================
Provides a thin, dependency-light wrapper around existing infrastructure
services so that other components (e.g. Unified Chat) can issue natural
language commands that orchestrate both Lambda GPU and Lambda Labs
resources.

Key design principles
---------------------
1. **Reuse, don't duplicate**:  Delegates to already-existing services such
   as `optimized_cortex_service` for ModernStack operations and
   `LambdaLabsHybridRouter` for Lambda Labs LLM generation.  No new AI
   routing logic is implemented here – we simply expose a pragmatic facade
   for NL control so higher-level agents can remain agnostic.
2. **Stateless façade**:  The controller keeps no state except instantiated
   service singletons.  This avoids hidden coupling and simplifies future
   refactors.
3. **Graceful degradation**:  If either underlying service is unavailable
   we return a structured error rather than throwing, ensuring callers can
   decide how to fallback.
4. **Minimal surface area**:  Only two public async helpers are provided
   initially (`run_command` and `health`) keeping technical debt close to
   zero while we validate usefulness.
"""

from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3
from __future__ import annotations

import logging
from typing import Any

from infrastructure.services.lambda_labs_hybrid_router import (
    LambdaLabsHybridRouter,
)
from shared.utils.optimized_modern_stack_cortex_service import (
    optimized_cortex_service,
)

logger = logging.getLogger(__name__)


class NaturalLanguageInfrastructureController:  # pragma: no cover – thin façade
    """Thin wrapper that forwards NL infra requests to existing services."""

    def __init__(self) -> None:
        self._lambda_router = LambdaLabsHybridRouter()
        self._modern_stack = optimized_cortex_service  # global singleton

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------

    async def run_command(self, command: str) -> dict[str, Any]:
        """Route *command* to the right subsystem and return structured reply.

        Very simple heuristic routing for now: if the command mentions the
        word *modern_stack* we treat it as a warehouse optimisation request –
        otherwise we treat it as a Lambda-Labs LLM request.  This keeps us
        entirely additive (does not modify existing routers).
        """
        logger.info("NL-Infra-Controller received command: %s", command)

        if "modern_stack" in command.lower():
            return await self._handle_modern_stack_command(command)
        return await self._handle_lambda_command(command)

    async def health(self) -> dict[str, Any]:
        """Lightweight health probe combining underlying component checks."""
        # REMOVED: ModernStack dependency "unknown"
        try:
            # REMOVED: ModernStack dependency (
                "healthy" if await self._modern_stack.health_check() else "degraded"
            )
        except Exception as exc:  # broad except OK for health check
            logger.warning("ModernStack health check failed: %s", exc)
            # REMOVED: ModernStack dependency "unhealthy"

        lambda_status = "unknown"
        try:
            test_msgs = [{"role": "user", "content": "ping"}]
            await self._lambda_router.generate(test_msgs, max_tokens=5)
            lambda_status = "healthy"
        except Exception as exc:  # pragma: no cover – best-effort
            logger.warning("Lambda Labs health check failed: %s", exc)
            lambda_status = "unhealthy"

        return {
            "modern_stack": modern_stack_status,
            "lambda_labs": lambda_status,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _handle_modern_stack_command(self, command: str) -> dict[str, Any]:
        """Pass command to Lambda GPU for optimisation/analysis."""
        try:
            sql_prompt = (
                """Convert the following prose into an optimised ModernStack SQL
                query and briefly explain key optimisation choices:\n\n"""
                + command
            )
            result = await self._modern_stack.complete_text_with_cortex(  # type: ignore[attr-defined]
                sql_prompt,
                model="modern_stack-arctic",
                temperature=0,
                max_tokens=800,
            )
            return {
                "success": True,
                "provider": "modern_stack_cortex",
                "response": result,
            }
        except Exception as exc:  # pragma: no cover – propagate gracefully
            logger.error("ModernStack command failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def _handle_lambda_command(self, command: str) -> dict[str, Any]:
        """Forward command to Lambda-Labs via the hybrid router."""
        try:
            messages = [{"role": "user", "content": command}]
            result = await self._lambda_router.generate(messages, max_tokens=1024)
            return {
                "success": True,
                "provider": result.get("backend", "lambda_labs"),
                "response": result.get("choices", [{}])[0]
                .get("message", {})
                .get("content", ""),
                "raw": result,
            }
        except Exception as exc:
            logger.error("Lambda Labs command failed: %s", exc)
            return {"success": False, "error": str(exc)}
