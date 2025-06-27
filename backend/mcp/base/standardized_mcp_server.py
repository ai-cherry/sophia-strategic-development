"""
Sophia AI - Standardized MCP Server Base Class
Provides enterprise-grade foundation for all MCP servers with unified AI processing
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import logging
import aiohttp
import time
import traceback
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from prometheus_client import Counter, Histogram, Gauge, Info
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logger = logging.getLogger(__name__)

class SyncPriority(Enum):
    """Data synchronization priority levels."""
    REAL_TIME = "real_time"    # <1 minute
    HIGH = "high"              # <5 minutes  
    MEDIUM = "medium"          # <30 minutes
    LOW = "low"                # <24 hours

class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

@dataclass
class MCPServerConfig:
    """Configuration for MCP servers."""
    server_name: str
    port: int
    sync_priority: SyncPriority = SyncPriority.MEDIUM
    sync_interval_minutes: int = 30
    batch_size: int = 100
    retry_attempts: int = 3
    timeout_seconds: int = 300
    enable_ai_processing: bool = True
    enable_metrics: bool = True
    health_check_interval: int = 60

@dataclass
class HealthCheckResult:
    """Health check result data structure."""
    component: str
    status: HealthStatus
    response_time_ms: float
    error_message: Optional[str] = None
    last_success: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class StandardizedMCPServer(ABC):
    """
    Base class for all Sophia AI MCP servers with enterprise-grade capabilities.
    
    Provides:
    - Snowflake Cortex AI integration
    - Prometheus metrics collection
    - Health monitoring and checks
    - Standardized error handling
    - Cross-platform sync coordination
    - AI-powered data processing
    """
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        
        # Load port from centralized config
        self._load_port_from_config()

        self.server_name = config.server_name
        self.cortex_service: Optional[SnowflakeCortexService] = None
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Health tracking
        self.last_health_check = datetime.utcnow()
        self.health_results: Dict[str, HealthCheckResult] = {}
        self.is_healthy = False
        
        # Performance tracking
        self.last_sync_time: Optional[datetime] = None
        self.sync_success_count = 0
        self.sync_error_count = 0
        
        # Initialize metrics if enabled
        if config.enable_metrics:
            self._initialize_metrics()
    
    def _initialize_metrics(self) -> None:
        """Initialize Prometheus metrics for monitoring."""
        try:
            # Request metrics
            self.request_counter = Counter(
                f'mcp_{self.server_name}_requests_total',
                'Total requests to MCP server',
                ['method', 'status', 'endpoint']
            )
            
            self.request_duration = Histogram(
                f'mcp_{self.server_name}_request_duration_seconds',
                'Request duration in seconds',
                ['method', 'endpoint']
            )
            
            # Health metrics
            self.health_gauge = Gauge(
                f'mcp_{self.server_name}_health_status',
                'Health status of MCP server (1=healthy, 0=unhealthy)'
            )
            
            # Sync metrics
            self.sync_success_rate = Gauge(
                f'mcp_{self.server_name}_sync_success_rate',
                'Success rate of data synchronization'
            )
            
            self.data_freshness = Gauge(
                f'mcp_{self.server_name}_data_freshness_seconds',
                'Age of the most recent data in seconds'
            )
            
            self.records_processed = Counter(
                f'mcp_{self.server_name}_records_processed_total',
                'Total records processed',
                ['operation', 'status']
            )
            
            # AI processing metrics
            self.ai_processing_duration = Histogram(
                f'mcp_{self.server_name}_ai_processing_duration_seconds',
                'Duration of AI processing operations',
                ['operation']
            )
            
            self.ai_accuracy_score = Gauge(
                f'mcp_{self.server_name}_ai_accuracy_score',
                'AI processing accuracy score'
            )
            
            # Server info
            self.server_info = Info(
                f'mcp_{self.server_name}_info',
                'MCP server information'
            )
            
            # Set server info
            self.server_info.info({
                'version': '2.0.0',
                'server_name': self.server_name,
                'sync_priority': self.config.sync_priority.value,
                'ai_enabled': str(self.config.enable_ai_processing)
            })
            
            logger.info(f"✅ Metrics initialized for {self.server_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize metrics for {self.server_name}: {e}")

    async def initialize(self) -> None:
        """Initialize MCP server with all dependencies."""
        try:
            logger.info(f"🚀 Initializing {self.server_name} MCP server...")
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            )
            
            # Initialize Snowflake Cortex service
            if self.config.enable_ai_processing:
                self.cortex_service = SnowflakeCortexService()
                await self.cortex_service.initialize()
                logger.info(f"✅ Snowflake Cortex initialized for {self.server_name}")
            
            # Server-specific initialization
            await self.server_specific_init()
            
            # Perform initial health check
            await self.comprehensive_health_check()
            
            # Update health status
            if self.config.enable_metrics:
                self.health_gauge.set(1 if self.is_healthy else 0)
            
            logger.info(f"✅ {self.server_name} MCP server initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.server_name}: {e}")
            if self.config.enable_metrics:
                self.health_gauge.set(0)
            raise

    async def shutdown(self) -> None:
        """Clean shutdown of MCP server."""
        try:
            logger.info(f"🔄 Shutting down {self.server_name} MCP server...")
            
            # Server-specific cleanup
            await self.server_specific_cleanup()
            
            # Close HTTP session
            if self.session:
                await self.session.close()
            
            # Close Cortex service
            if self.cortex_service:
                await self.cortex_service.close()
            
            logger.info(f"✅ {self.server_name} MCP server shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during {self.server_name} shutdown: {e}")

    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all components."""
        try:
            health_results = {}
            overall_healthy = True
            
            # Check external API connectivity
            api_result = await self._check_external_api_health()
            health_results['external_api'] = api_result
            if api_result.status != HealthStatus.HEALTHY:
                overall_healthy = False
            
            # Check Snowflake Cortex connectivity
            if self.cortex_service:
                cortex_result = await self._check_cortex_health()
                health_results['snowflake_cortex'] = cortex_result
                if cortex_result.status != HealthStatus.HEALTHY:
                    overall_healthy = False
            
            # Check data freshness
            freshness_result = await self._check_data_freshness()
            health_results['data_freshness'] = freshness_result
            if freshness_result.status != HealthStatus.HEALTHY:
                overall_healthy = False
            
            # Server-specific health checks
            server_result = await self.server_specific_health_check()
            health_results['server_specific'] = server_result
            if server_result.status != HealthStatus.HEALTHY:
                overall_healthy = False
            
            # Update health status
            self.is_healthy = overall_healthy
            self.last_health_check = datetime.utcnow()
            self.health_results = health_results
            
            # Update metrics
            if self.config.enable_metrics:
                self.health_gauge.set(1 if overall_healthy else 0)
            
            return {
                "server": self.server_name,
                "status": "healthy" if overall_healthy else "unhealthy",
                "timestamp": self.last_health_check.isoformat(),
                "components": {k: {
                    'status': v.status.value,
                    'response_time_ms': v.response_time_ms,
                    'error_message': v.error_message,
                    'metadata': v.metadata
                } for k, v in health_results.items()}
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed for {self.server_name}: {e}")
            self.is_healthy = False
            if self.config.enable_metrics:
                self.health_gauge.set(0)
            
            return {
                "server": self.server_name,
                "status": "critical",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _check_external_api_health(self) -> HealthCheckResult:
        """Check external API health with timing."""
        start_time = time.time()
        try:
            is_healthy = await self.check_external_api()
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                component="external_api",
                status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                last_success=datetime.utcnow() if is_healthy else None
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="external_api",
                status=HealthStatus.CRITICAL,
                response_time_ms=response_time,
                error_message=str(e)
            )

    async def _check_cortex_health(self) -> HealthCheckResult:
        """Check Snowflake Cortex health."""
        start_time = time.time()
        try:
            # Test basic Cortex functionality
            test_query = "SELECT CURRENT_TIMESTAMP() as health_check"
            result = await self.cortex_service.execute_query(test_query)
            response_time = (time.time() - start_time) * 1000
            
            if result:
                return HealthCheckResult(
                    component="snowflake_cortex",
                    status=HealthStatus.HEALTHY,
                    response_time_ms=response_time,
                    last_success=datetime.utcnow(),
                    metadata={"query_result_count": len(result)}
                )
            else:
                return HealthCheckResult(
                    component="snowflake_cortex",
                    status=HealthStatus.DEGRADED,
                    response_time_ms=response_time,
                    error_message="No result returned from health check query"
                )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component="snowflake_cortex",
                status=HealthStatus.CRITICAL,
                response_time_ms=response_time,
                error_message=str(e)
            )

    async def _check_data_freshness(self) -> HealthCheckResult:
        """Check data freshness to ensure sync is working."""
        try:
            freshness_seconds = await self.get_data_age_seconds()
            
            # Determine status based on sync priority
            if self.config.sync_priority == SyncPriority.REAL_TIME:
                threshold = 300  # 5 minutes
            elif self.config.sync_priority == SyncPriority.HIGH:
                threshold = 1800  # 30 minutes
            elif self.config.sync_priority == SyncPriority.MEDIUM:
                threshold = 7200  # 2 hours
            else:  # LOW
                threshold = 86400  # 24 hours
            
            if freshness_seconds <= threshold:
                status = HealthStatus.HEALTHY
            elif freshness_seconds <= threshold * 2:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            # Update metrics
            if self.config.enable_metrics:
                self.data_freshness.set(freshness_seconds)
            
            return HealthCheckResult(
                component="data_freshness",
                status=status,
                response_time_ms=0,  # Not applicable
                metadata={
                    "data_age_seconds": freshness_seconds,
                    "threshold_seconds": threshold,
                    "sync_priority": self.config.sync_priority.value
                }
            )
        except Exception as e:
            return HealthCheckResult(
                component="data_freshness",
                status=HealthStatus.CRITICAL,
                response_time_ms=0,
                error_message=str(e)
            )

    async def sync_and_process_data(self) -> Dict[str, Any]:
        """Main method to sync and process data with AI."""
        start_time = time.time()
        sync_result = {
            "server": self.server_name,
            "status": "started",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Sync data from external platform
            logger.info(f"🔄 Starting data sync for {self.server_name}")
            raw_data = await self.sync_data()
            
            sync_result.update({
                "sync_status": "success",
                "records_synced": len(raw_data) if isinstance(raw_data, list) else 1,
                "sync_duration": time.time() - start_time
            })
            
            # Process with AI if enabled
            if self.config.enable_ai_processing and self.cortex_service:
                ai_start = time.time()
                ai_result = await self.process_with_ai(raw_data)
                ai_duration = time.time() - ai_start
                
                sync_result.update({
                    "ai_processing_status": "success",
                    "ai_duration": ai_duration,
                    "ai_insights": ai_result.get("insights", []),
                    "ai_metadata": ai_result.get("metadata", {})
                })
                
                # Update AI metrics
                if self.config.enable_metrics:
                    self.ai_processing_duration.labels(operation="sync_processing").observe(ai_duration)
                    if "accuracy_score" in ai_result:
                        self.ai_accuracy_score.set(ai_result["accuracy_score"])
            
            # Update success metrics
            self.sync_success_count += 1
            self.last_sync_time = datetime.utcnow()
            
            if self.config.enable_metrics:
                success_rate = self.sync_success_count / (self.sync_success_count + self.sync_error_count)
                self.sync_success_rate.set(success_rate)
                self.records_processed.labels(operation="sync", status="success").inc(
                    sync_result.get("records_synced", 0)
                )
            
            sync_result.update({
                "status": "completed",
                "total_duration": time.time() - start_time
            })
            
            logger.info(f"✅ Data sync completed for {self.server_name}: {sync_result['records_synced']} records")
            return sync_result
            
        except Exception as e:
            self.sync_error_count += 1
            error_msg = str(e)
            logger.error(f"❌ Data sync failed for {self.server_name}: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Update error metrics
            if self.config.enable_metrics:
                success_rate = self.sync_success_count / (self.sync_success_count + self.sync_error_count)
                self.sync_success_rate.set(success_rate)
                self.records_processed.labels(operation="sync", status="error").inc(1)
            
            sync_result.update({
                "status": "failed",
                "error": error_msg,
                "total_duration": time.time() - start_time
            })
            
            return sync_result

    def track_request(self, method: str, endpoint: str):
        """Decorator to track request metrics."""
        def decorator(func: Callable):
            async def wrapper(*args, **kwargs):
                if not self.config.enable_metrics:
                    return await func(*args, **kwargs)
                
                start_time = time.time()
                status = "success"
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    self.request_counter.labels(
                        method=method, 
                        status=status, 
                        endpoint=endpoint
                    ).inc()
                    self.request_duration.labels(
                        method=method, 
                        endpoint=endpoint
                    ).observe(duration)
            
            return wrapper
        return decorator

    # Abstract methods that must be implemented by concrete servers
    @abstractmethod
    async def server_specific_init(self) -> None:
        """Server-specific initialization logic."""
        pass
    
    @abstractmethod
    async def server_specific_cleanup(self) -> None:
        """Server-specific cleanup logic."""
        pass
    
    @abstractmethod
    async def sync_data(self) -> Dict[str, Any]:
        """Sync data from external platform."""
        pass
    
    @abstractmethod
    async def process_with_ai(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data with Snowflake Cortex AI."""
        pass
    
    @abstractmethod
    async def check_external_api(self) -> bool:
        """Check connectivity to external API."""
        pass
    
    @abstractmethod
    async def server_specific_health_check(self) -> HealthCheckResult:
        """Server-specific health checks."""
        pass
    
    @abstractmethod
    async def get_data_age_seconds(self) -> int:
        """Get the age of the most recent data in seconds."""
        pass

    # Utility methods
    async def make_api_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling and metrics."""
        if not self.session:
            raise RuntimeError("HTTP session not initialized")
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                if response.content_type == 'application/json':
                    return await response.json()
                else:
                    return {"text": await response.text()}
        except Exception as e:
            logger.error(f"API request failed: {method} {url} - {str(e)}")
            raise

    async def store_in_snowflake(self, table_name: str, data: List[Dict[str, Any]]) -> bool:
        """Store data in Snowflake with error handling."""
        if not self.cortex_service:
            logger.warning(f"Cortex service not available for storing data in {table_name}")
            return False
        
        try:
            # Implementation would depend on specific table schema
            # This is a placeholder for the actual implementation
            logger.info(f"Storing {len(data)} records in {table_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to store data in {table_name}: {e}")
            return False

    def _load_port_from_config(self) -> None:
        """Loads the server's port from the centralized mcp_ports.json file."""
        ports_config_path = Path.cwd() / "config" / "mcp_ports.json"
        if not ports_config_path.exists():
            logger.warning("mcp_ports.json not found. Using default port from config.")
            return

        with open(ports_config_path, 'r') as f:
            ports_config = json.load(f)
        
        server_port = ports_config.get("servers", {}).get(self.config.server_name)
        if server_port:
            self.config.port = server_port
            logger.info(f"Loaded port {server_port} for {self.config.server_name} from config.")
        else:
            logger.warning(f"Port for {self.config.server_name} not found in mcp_ports.json. Using default.") 