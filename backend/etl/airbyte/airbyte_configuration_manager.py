#!/usr/bin/env python3
"""
Enhanced Airbyte Configuration Manager for Sophia AI Platform

Production-ready Airbyte management with comprehensive error handling,
retry logic, data quality validation, and performance monitoring.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import structlog

from backend.core.auto_esc_config import get_config_value
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logger = structlog.get_logger(__name__)


class ErrorType(Enum):
    """Categorized error types for enhanced error handling"""
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "authentication_error"
    CONFIGURATION_ERROR = "configuration_error"
    DATA_QUALITY_ERROR = "data_quality_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    TIMEOUT_ERROR = "timeout_error"
    VALIDATION_ERROR = "validation_error"
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    INFRASTRUCTURE_ERROR = "infrastructure_error"
    UNKNOWN_ERROR = "unknown_error"


class AirbyteOperationStatus(Enum):
    """Status indicators for Airbyte operations"""
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"
    TIMEOUT = "timeout"
    VALIDATION_FAILED = "validation_failed"
    RATE_LIMITED = "rate_limited"


@dataclass
class RetryConfig:
    """Configuration for retry mechanisms"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class DataQualityMetrics:
    """Data quality metrics for ingested data"""
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    missing_required_fields: int = 0
    data_type_violations: int = 0
    business_rule_violations: int = 0
    quality_score: float = 0.0
    validation_timestamp: Optional[datetime] = None
    issues: List[str] = field(default_factory=list)


@dataclass
class AirbyteOperationResult:
    """Result of an Airbyte operation with comprehensive metadata"""
    status: AirbyteOperationStatus
    operation_type: str
    resource_id: Optional[str] = None
    execution_time: Optional[float] = None
    error_type: Optional[ErrorType] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    data_quality: Optional[DataQualityMetrics] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class EnhancedAirbyteManager:
    """Enhanced Airbyte Configuration Manager with production-ready features"""

    def __init__(self, environment: str = "dev"):
        self.environment = environment
        self.session: Optional[aiohttp.ClientSession] = None
        self.cortex_service: Optional[SnowflakeCortexService] = None
        
        # Configuration
        self.airbyte_config = self._load_airbyte_config()
        self.gong_config = self._load_gong_config()
        self.snowflake_config = self._load_snowflake_config()
        
        # Retry configuration
        self.retry_config = RetryConfig()
        
        # Operation tracking
        self.operation_history: List[AirbyteOperationResult] = []
        self.health_status = {"last_check": None, "status": "unknown"}

    def _load_airbyte_config(self) -> Dict[str, Any]:
        """Load Airbyte configuration from Pulumi ESC"""
        return {
            "base_url": get_config_value("airbyte_server_url", "http://localhost:8000"),
            "username": get_config_value("airbyte_username", "airbyte"),
            "password": get_config_value("airbyte_password", "password"),
            "workspace_id": get_config_value("airbyte_workspace_id", "default")
        }

    def _load_gong_config(self) -> Dict[str, Any]:
        """Load Gong configuration from Pulumi ESC"""
        return {
            "access_key": get_config_value("gong_access_key"),
            "access_key_secret": get_config_value("gong_client_secret"),
            "start_date": get_config_value("gong_sync_start_date", "2024-01-01T00:00:00Z"),
            "include_transcripts": get_config_value("gong_include_transcripts", True),
            "call_types": get_config_value("gong_call_types", ["inbound", "outbound"])
        }

    def _load_snowflake_config(self) -> Dict[str, Any]:
        """Load Snowflake configuration from Pulumi ESC"""
        return {
            "host": f"{get_config_value('snowflake_account')}.snowflakecomputing.com",
            "username": get_config_value("snowflake_user", "SCOOBYJAVA15"),
            "password": get_config_value("snowflake_password"),
            "warehouse": get_config_value("snowflake_warehouse", "WH_SOPHIA_ETL_TRANSFORM"),
            "database": get_config_value("snowflake_database", f"SOPHIA_AI_{self.environment.upper()}"),
            "role": get_config_value("snowflake_role", "ROLE_SOPHIA_AIRBYTE_INGEST"),
            "raw_schema": "RAW_AIRBYTE"
        }

    async def initialize(self) -> AirbyteOperationResult:
        """Initialize the Airbyte manager with enhanced error handling"""
        try:
            timeout = aiohttp.ClientTimeout(total=300, connect=30)
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Sophia-AI-Airbyte-Manager/1.0"
            }
            
            auth = aiohttp.BasicAuth(
                self.airbyte_config["username"],
                self.airbyte_config["password"]
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
                auth=auth
            )
            
            self.cortex_service = SnowflakeCortexService()
            await self.cortex_service.initialize()
            
            logger.info("✅ Enhanced Airbyte Manager initialized successfully")
            
            return AirbyteOperationResult(
                status=AirbyteOperationStatus.SUCCESS,
                operation_type="initialization",
                execution_time=0.0,
                metadata={"environment": self.environment}
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize Airbyte manager: {e}")
            
            return AirbyteOperationResult(
                status=AirbyteOperationStatus.FAILED,
                operation_type="initialization",
                error_message=str(e)
            )

    async def cleanup(self) -> None:
        """Clean up resources"""
        if self.session:
            await self.session.close()
        if self.cortex_service:
            await self.cortex_service.close()
