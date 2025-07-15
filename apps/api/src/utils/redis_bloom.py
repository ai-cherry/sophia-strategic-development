from __future__ import annotations

import hashlib
from typing import Any

try:
    import redis  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    redis = None  # type: ignore

__all__ = ["DedupBloomFilter"]


class DedupBloomFilter:
    """Simple Redis-backed Bloom filter for high-volume deduplication."""

    def __init__(
        self,
        redis_url: str,
        key: str = "dedup:bloom",
        error_rate: float = 0.001,
        capacity: int = 1_000_000,
    ):
        if redis is None:
            raise ImportError("redis-py required for Bloom filter support")
        self._r = redis.Redis.from_url(redis_url)
        self.key = key
        # Create filter if not exists
        self._r.execute_command(
            "BF.RESERVE", key, error_rate, capacity, "NONSCALING", "EXPANSION", 2
        )

    @staticmethod
    def _hash(value: Any) -> str:
        return hashlib.sha256(str(value).encode()).hexdigest()

    def maybe_add(self, item: Any) -> bool:
        """Add *item* to filter.

        Returns True if the item **may have** been seen before.
        """
        hashed = self._hash(item)
        return bool(self._r.execute_command("BF.ADD", self.key, hashed))
