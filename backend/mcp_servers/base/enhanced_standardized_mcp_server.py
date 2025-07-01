#!/usr/bin/env python3
"""
Enhanced Standardized MCP Server Base Class
==========================================

Provides a unified, production-ready base class for all MCP servers in Sophia AI.
Implements comprehensive health checks, metrics, error handling, and Snowflake Cortex integration.
"""

import asyncio
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel

from backend.core.auto_esc_config import get_config_value
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logger = logging.getLogger(__name__)


class ServerStatus(Enum):
    """MCP Server status enumeration"""
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class HealthCheckLevel(Enum):
    """Health check detail levels"""
    BASIC = "basic"
    DETAILED = "detailed"
    DIAGNOSTIC = "diagnostic"


@dataclass
class MCPServerConfig:
    """Enhanced MCP Server configuration"""
    name: str
    port: int
    version: str = "3.0.0"
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    max_request_size_mb: int = 100
    timeout_seconds: int = 30
    enable_metrics: bool = True
    enable_cortex: bool = False
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    rate_limit_per_minute: int = 1000
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    health_check_interval: int = 60
    auto_recover: bool = True
    log_level: str = "INFO"


@dataclass
class MCPMetrics:
    """MCP Server metrics container"""
    requests_total: Counter
    requests_failed: Counter
    request_duration: Histogram
    active_connections: Gauge
    health_status: Gauge
    cache_hits: Counter
    cache_misses: Counter
    cortex_calls: Counter
    error_rate: Gauge


class HealthStatus(BaseModel):
    """Health check response model"""
    status: str
    server_name: str
    version: str
    uptime_seconds: float
    last_check: str
    capabilities: List[str]
    metrics: Optional[Dict[str, Any]] = None
    errors: List[str] = []
    warnings: List[str] = []


class EnhancedStandardizedMCPServer(ABC):
    """
    Enhanced base class for all Sophia AI MCP servers.
    Provides comprehensive functionality for production-ready MCP servers.
    """
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.app = FastAPI(
            title=f"{config.name} MCP Server",
            description=config.description or f"MCP Server for {config.name}",
            version=config.version
        )
        
        # Server state
        self.start_time = datetime.now(timezone.utc)
        self.health_status = ServerStatus.INITIALIZING
        self.last_health_check = None
        self.error_count = 0
        self.warning_count = 0
        
        # Services
        self.cortex_service: Optional[SnowflakeCortexService] = None
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, float] = {}
        
        # Metrics
        self.metrics = self._initialize_metrics() if config.enable_metrics else None
        
        # Setup
        self._setup_middleware()
        self._setup_routes()
        self._setup_error_handlers()
        
        # Background tasks
        self.background_tasks = []
        
    def _initialize_metrics(self) -> MCPMetrics:
        """Initialize Prometheus metrics"""
        return MCPMetrics(
            requests_total=Counter(
                f'{self.config.name}_requests_total',
                f'Total requests to {self.config.name} MCP server'
            ),
            requests_failed=Counter(
                f'{self.config.name}_requests_failed',
                f'Failed requests to {self.config.name} MCP server'
            ),
            request_duration=Histogram(
                f'{self.config.name}_request_duration_seconds',
                f'Request duration for {self.config.name} MCP server'
            ),
            active_connections=Gauge(
                f'{self.config.name}_active_connections',
                f'Active connections to {self.config.name} MCP server'
            ),
            health_status=Gauge(
                f'{self.config.name}_health_status',
                f'Health status of {self.config.name} MCP server (1=healthy, 0=unhealthy)'
            ),
            cache_hits=Counter(
                f'{self.config.name}_cache_hits',
                f'Cache hits for {self.config.name} MCP server'
            ),
            cache_misses=Counter(
                f'{self.config.name}_cache_misses',
                f'Cache misses for {self.config.name} MCP server'
            ),
            cortex_calls=Counter(
                f'{self.config.name}_cortex_calls',
                f'Snowflake Cortex calls from {self.config.name} MCP server'
            ),
            error_rate=Gauge(
                f'{self.config.name}_error_rate',
                f'Error rate for {self.config.name} MCP server'
            )
        )
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Request tracking middleware
        @self.app.middleware("http")
        async def track_requests(request, call_next):
            start_time = time.time()
            
            if self.metrics:
                self.metrics.requests_total.inc()
                self.metrics.active_connections.inc()
            
            try:
                response = await call_next(request)
                
                if self.metrics:
                    duration = time.time() - start_time
                    self.metrics.request_duration.observe(duration)
                    
                    if response.status_code >= 400:
                        self.metrics.requests_failed.inc()
                
                return response
                
            except Exception as e:
                if self.metrics:
                    self.metrics.requests_failed.inc()
                raise
            finally:
                if self.metrics:
                    self.metrics.active_connections.dec()
    
    def _setup_routes(self):
        """Setup standard routes"""
        @self.app.get("/health", response_model=HealthStatus)
        async def health_check(level: HealthCheckLevel = HealthCheckLevel.BASIC):
            return await self.get_health_status(level)
        
        @self.app.get("/metrics")
        async def metrics():
            if not self.config.enable_metrics:
                raise HTTPException(status_code=404, detail="Metrics not enabled")
            return generate_latest()
        
        @self.app.get("/capabilities")
        async def capabilities():
            return {
                "server": self.config.name,
                "version": self.config.version,
                "capabilities": self.config.capabilities,
                "cortex_enabled": self.config.enable_cortex,
                "caching_enabled": self.config.enable_caching,
                "rate_limit": self.config.rate_limit_per_minute
            }
        
        # Add server-specific routes
        self._setup_server_routes()
    
    def _setup_error_handlers(self):
        """Setup global error handlers"""
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request, exc):
            self.error_count += 1
            logger.error(f"Unhandled exception in {self.config.name}: {exc}")
            
            if self.metrics:
                self.metrics.error_rate.set(
                    self.error_count / max(1, self.metrics.requests_total._value.get())
                )
            
            return {
                "error": "Internal server error",
                "message": str(exc) if logger.level <= logging.DEBUG else "An error occurred",
                "server": self.config.name,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def initialize(self):
        """Initialize the MCP server"""
        logger.info(f"🚀 Initializing {self.config.name} MCP Server...")
        
        try:
            # Load port from centralized config
            self._load_port_from_config()
            
            # Initialize Snowflake Cortex if enabled
            if self.config.enable_cortex:
                await self._initialize_cortex_service()
            
            # Server-specific initialization
            await self.server_specific_init()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Update health status
            self.health_status = ServerStatus.HEALTHY
            if self.metrics:
                self.metrics.health_status.set(1)
            
            logger.info(f"✅ {self.config.name} MCP Server initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.config.name}: {e}")
            self.health_status = ServerStatus.UNHEALTHY
            if self.metrics:
                self.metrics.health_status.set(0)
            raise
    
    def _load_port_from_config(self):
        """Load port from centralized configuration"""
        try:
            config_path = "config/consolidated_mcp_ports.json"
            if os.path.exists(config_path):
                with open(config_path) as f:
                    ports_config = json.load(f)
                    
                active_servers = ports_config.get("active_servers", {})
                if self.config.name in active_servers:
                    self.config.port = active_servers[self.config.name]
                    logger.info(f"Loaded port {self.config.port} for {self.config.name}")
        except Exception as e:
            logger.warning(f"Failed to load port config: {e}, using default port {self.config.port}")
    
    async def _initialize_cortex_service(self):
        """Initialize Snowflake Cortex service"""
        try:
            self.cortex_service = SnowflakeCortexService()
            await self.cortex_service.initialize()
            logger.info(f"✅ Snowflake Cortex initialized for {self.config.name}")
        except Exception as e:
            logger.error(f"Failed to initialize Cortex service: {e}")
            self.warning_count += 1
    
    async def _start_background_tasks(self):
        """Start background tasks"""
        # Health check task
        async def health_check_loop():
            while True:
                try:
                    await asyncio.sleep(self.config.health_check_interval)
                    await self._perform_health_check()
                except Exception as e:
                    logger.error(f"Health check error: {e}")
        
        # Cache cleanup task
        async def cache_cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(60)  # Check every minute
                    await self._cleanup_cache()
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")
        
        self.background_tasks.append(asyncio.create_task(health_check_loop()))
        
        if self.config.enable_caching:
            self.background_tasks.append(asyncio.create_task(cache_cleanup_loop()))
    
    async def _perform_health_check(self):
        """Perform internal health check"""
        try:
            # Check server-specific health
            is_healthy = await self.check_server_health()
            
            # Update status
            if is_healthy:
                self.health_status = ServerStatus.HEALTHY
                if self.metrics:
                    self.metrics.health_status.set(1)
            else:
                self.health_status = ServerStatus.DEGRADED
                if self.metrics:
                    self.metrics.health_status.set(0.5)
            
            self.last_health_check = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.health_status = ServerStatus.UNHEALTHY
            if self.metrics:
                self.metrics.health_status.set(0)
    
    async def _cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self.cache_timestamps.items()
            if current_time - timestamp > self.config.cache_ttl_seconds
        ]
        
        for key in expired_keys:
            del self.cache[key]
            del self.cache_timestamps[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    async def get_health_status(self, level: HealthCheckLevel = HealthCheckLevel.BASIC) -> HealthStatus:
        """Get comprehensive health status"""
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        status = HealthStatus(
            status=self.health_status.value,
            server_name=self.config.name,
            version=self.config.version,
            uptime_seconds=uptime,
            last_check=self.last_health_check.isoformat() if self.last_health_check else "never",
            capabilities=self.config.capabilities
        )
        
        if level in [HealthCheckLevel.DETAILED, HealthCheckLevel.DIAGNOSTIC]:
            # Add metrics
            if self.metrics:
                status.metrics = {
                    "requests_total": self.metrics.requests_total._value.get(),
                    "requests_failed": self.metrics.requests_failed._value.get(),
                    "error_rate": self.metrics.error_rate._value.get(),
                    "cache_hit_rate": self._calculate_cache_hit_rate(),
                    "active_connections": self.metrics.active_connections._value.get()
                }
        
        if level == HealthCheckLevel.DIAGNOSTIC:
            # Add diagnostic information
            if self.error_count > 0:
                status.errors.append(f"Total errors: {self.error_count}")
            if self.warning_count > 0:
                status.warnings.append(f"Total warnings: {self.warning_count}")
            
            # Check Cortex service
            if self.config.enable_cortex and not self.cortex_service:
                status.warnings.append("Cortex service not initialized")
        
        return status
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if not self.metrics:
            return 0.0
        
        hits = self.metrics.cache_hits._value.get()
        misses = self.metrics.cache_misses._value.get()
        total = hits + misses
        
        return (hits / total * 100) if total > 0 else 0.0
    
    async def get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.config.enable_caching:
            return None
        
        if key in self.cache:
            current_time = time.time()
            if current_time - self.cache_timestamps[key] <= self.config.cache_ttl_seconds:
                if self.metrics:
                    self.metrics.cache_hits.inc()
                return self.cache[key]
            else:
                # Expired
                del self.cache[key]
                del self.cache_timestamps[key]
        
        if self.metrics:
            self.metrics.cache_misses.inc()
        return None
    
    async def set_cache(self, key: str, value: Any):
        """Set value in cache"""
        if self.config.enable_caching:
            self.cache[key] = value
            self.cache_timestamps[key] = time.time()
    
    async def call_cortex(self, function: str, *args, **kwargs) -> Any:
        """Call Snowflake Cortex function"""
        if not self.cortex_service:
            raise RuntimeError("Cortex service not initialized")
        
        if self.metrics:
            self.metrics.cortex_calls.inc()
        
        return await self.cortex_service.call_function(function, *args, **kwargs)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info(f"Shutting down {self.config.name} MCP Server...")
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Server-specific shutdown
        await self.server_specific_shutdown()
        
        # Close Cortex service
        if self.cortex_service:
            await self.cortex_service.close()
        
        logger.info(f"✅ {self.config.name} MCP Server shut down successfully")
    
    # Abstract methods for server-specific implementation
    
    @abstractmethod
    async def server_specific_init(self):
        """Server-specific initialization logic"""
        pass
    
    @abstractmethod
    def _setup_server_routes(self):
        """Setup server-specific routes"""
        pass
    
    @abstractmethod
    async def check_server_health(self) -> bool:
        """Check server-specific health status"""
        pass
    
    @abstractmethod
    async def server_specific_shutdown(self):
        """Server-specific shutdown logic"""
        pass 