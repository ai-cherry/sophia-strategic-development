"""
Sophia AI Integration Registry

Minimal stub for integration registry in Sophia AI backend
"""

from __future__ import annotations

from typing import Any, Dict


class IntegrationRegistry:
    """
    In-memory registry for service integrations."""

    def __init__(self) -> None:
        self._registry: Dict[str, Any] = {}

    async def register(self, name: str, integration: Any) -> None:
        """
        Register a new integration."""

        self._registry[name] = integration

    async def get(self, name: str) -> Any:
        """
        Retrieve a registered integration by name."""

        if name not in self._registry:
            raise KeyError(f"Integration '{name}' not found")
        return self._registry[name]

    async def all(self) -> Dict[str, Any]:
        """Return all registered integrations."""

        return dict(self._registry)
