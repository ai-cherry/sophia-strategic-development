"""Utilities for streaming data in real time."""

from __future__ import annotations

from typing import AsyncGenerator, Iterable


class RealTimeStreaming:
    """
Simple real-time stream generator."""

    async def stream(self, items: Iterable[str]) -> AsyncGenerator[str, None]:
        """
Yield items to consumers one by one."""

        for item in items:
            yield item
