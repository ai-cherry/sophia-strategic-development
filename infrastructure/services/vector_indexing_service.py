# File: backend/services/vector_indexing_service.py

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any

from core.config_manager import get_config_value
from infrastructure.integrations.gong_api_client import GongAPIClient
from infrastructure.services.semantic_layer_service import SemanticLayerService
from backend.services.unified_memory_service_primary import UnifiedMemoryService

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """Qdrant vector database"""
        # For now, this just checks the semantic service health.
        # A more complete implementation would check for index existence, etc.
        semantic_health = await self.semantic_service.health_check()
        if semantic_health["status"] == "healthy":
            return {"status": "healthy", "message": "Dependent services are healthy."}
        else:
            return {
                "status": "unhealthy",
                "message": "SemanticLayerService is unhealthy.",
            }
