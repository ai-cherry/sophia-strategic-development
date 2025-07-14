"""
Unified Memory Service - Primary Implementation
Consolidated from multiple versions for Sophia AI

Features:
- Qdrant vector search (primary)
- Redis caching layer
- PostgreSQL hybrid queries
- Lambda GPU embeddings
- Multimodal support
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from backend.core.auto_esc_config import get_config_value
from backend.utils.logger import get_logger

# Import V3 as base implementation
from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3

logger = get_logger(__name__)

class UnifiedMemoryService(UnifiedMemoryServiceV3):
    """
    Primary memory service for Sophia AI
    
    Consolidated from:
    - UnifiedMemoryServiceV2 (deprecated)
    - UnifiedMemoryServiceV3 (promoted to primary)
    - EnhancedMemoryServiceV3 (merged)
    """
    
    def __init__(self):
        super().__init__()
        logger.info("✅ Unified Memory Service initialized (V3 promoted to primary)")
    
    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Unified memory search interface"""
        return await super().search_knowledge(
            query=query,
            limit=limit,
            metadata_filter=filters or {}
        )
    
    async def add_memory(
        self,
        content: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Unified memory storage interface"""
        return await super().add_knowledge(
            content=content,
            source=f"user_{user_id}",
            metadata=metadata or {}
        )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get memory service health"""
        return {
            "service_version": "v3_primary",
            "initialized": self.initialized,
            "total_memories": len(self.hypothetical_cache),
            "cache_hit_rate": self.performance_metrics.get("cache_hit_rate", 0),
            "avg_search_time_ms": self.performance_metrics.get("avg_search_time_ms", 0)
        }
