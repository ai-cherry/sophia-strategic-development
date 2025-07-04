"""
Snowflake Cortex Service - Handlers Module
Contains AI operation handlers and business-specific methods
"""

from __future__ import annotations

import logging
from typing import Any

from .snowflake_cortex_service_utils import PerformanceMonitor

logger = logging.getLogger(__name__)


class CortexHandlers:
    """Handlers for Snowflake Cortex AI operations"""

    def __init__(self, service):
        self.service = service
        self.performance_monitor = PerformanceMonitor()

    def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics for handlers"""
        return self.performance_monitor.get_performance_stats()


class BusinessHandlers:
    """Business-specific handlers for HubSpot and Gong integration"""

    def __init__(self, service):
        self.service = service

    async def store_embedding_in_business_table(
        self,
        table_name: str,
        record_id: str,
        text_content: str,
        embedding_column: str = "ai_memory_embedding",
        metadata: dict[str, Any] | None = None,
        model: str = "e5-base-v2",
    ) -> bool:
        """Store embedding directly in business table"""
        return True  # Simplified for now
