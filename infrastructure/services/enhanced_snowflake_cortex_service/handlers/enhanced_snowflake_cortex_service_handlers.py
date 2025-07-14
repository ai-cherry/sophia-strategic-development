"""
Enhanced Snowflake Cortex Service Handlers
Request/response handlers and API endpoints
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
import snowflake.connector
from snowflake.connector import DictCursor
from core.enhanced_cache_manager import EnhancedCacheManager
from infrastructure.security.audit_logger import AuditLogger
from infrastructure.services.cost_engineering_service import (
    TaskRequest,
    cost_engineering_service,
)
from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2

from .models.enhanced_snowflake_cortex_service_models import *

# Handler classes extracted from main file
class DataPipelineConfig:
    """Configuration for data processing pipelines"""

    pipeline_id: str
    source_tables: list[str]
    target_table: str
    processing_mode: DataProcessingMode
    ai_functions: list[AIFunctionType]
    schedule_cron: str | None = None
    batch_size: int = 1000
    quality_checks: bool = True
    cost_optimization: bool = True
