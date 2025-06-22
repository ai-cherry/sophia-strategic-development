"""Simple in-memory cache implementation."""

from __future__ import annotations

from typing import Any, Dict


class HierarchicalCache:
    """Hierarchical key-value cache supporting namespaces."""

    def __init__(self) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}

    async def set(self, namespace: str, key: str, value: Any) -> None:
        """Store a value under a namespace."""

        self._cache.setdefault(namespace, {})[key] = value

    async def get(self, namespace: str, key: str) -> Any | None:
        """Retrieve a cached value if present."""

        return self._cache.get(namespace, {}).get(key)
