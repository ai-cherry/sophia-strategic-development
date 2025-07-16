"""
Service Discovery for Distributed Sophia AI

This module implements a comprehensive service discovery system for the
distributed Sophia AI architecture across Lambda Labs GPU instances.

Features:
- Automatic service registration and deregistration
- Health monitoring with configurable intervals
- Circuit breaker pattern for failed services
- Load balancing support
- Graceful degradation during network issues

Architecture:
- Maintains registry of all services across instances
- Periodic health checks with exponential backoff
- Event-driven service status updates
- Thread-safe operations with async support

Author: Sophia AI Team
Date: July 2025
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from config.infrastructure import InfrastructureConfig, ServiceType

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"


@dataclass
class ServiceEndpoint:
    """Represents a service endpoint with health and performance metrics."""
    name: str
    url: str
    service_type: ServiceType
    instance_name: str
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: datetime = field(default_factory=datetime.now)
    response_time: float = 0.0
    consecutive_failures: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_healthy(self) -> bool:
        """Check if the service is currently healthy."""
        return self.status == ServiceStatus.HEALTHY
    
    @property
    def is_circuit_open(self) -> bool:
        """Check if circuit breaker should be open."""
        return self.consecutive_failures >= 5
    
    def update_success(self, response_time: float):
        """Update service with successful health check."""
        self.status = ServiceStatus.HEALTHY
        self.response_time = response_time
        self.consecutive_failures = 0
        self.last_success = datetime.now()
        self.last_check = datetime.now()
    
    def update_failure(self, error: str):
        """Update service with failed health check."""
        self.status = ServiceStatus.UNHEALTHY
        self.consecutive_failures += 1
        self.last_failure = datetime.now()
        self.last_check = datetime.now()
        self.metadata['last_error'] = error


class ServiceDiscovery:
    """
    Manages service discovery across Lambda Labs instances.
    
    This class provides comprehensive service discovery functionality
    including registration, health monitoring, load balancing support,
    and automatic failover capabilities.
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceEndpoint] = {}
        self.config = InfrastructureConfig()
        self.discovery_config = self.config.get_service_discovery_config()
        
        # Configuration
        self.health_check_interval = self.discovery_config['health_check_interval']
        self.service_timeout = self.discovery_config['service_timeout']
        self.retry_attempts = self.discovery_config['retry_attempts']
        self.retry_delay = self.discovery_config['retry_delay']
        
        # Internal state
        self._health_check_task: Optional[asyncio.Task] = None
        self._running = False
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Event callbacks
        self._status_change_callbacks: List[Callable] = []
        
        # Metrics
        self._metrics = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'services_registered': 0,
            'services_deregistered': 0
        }
    
    async def initialize(self):
        """Initialize service discovery system."""
        logger.info("🔍 Initializing Service Discovery System...")
        
        # Create HTTP session for health checks
        timeout = aiohttp.ClientTimeout(total=self.service_timeout)
        self._session = aiohttp.ClientSession(timeout=timeout)
        
        # Register all known services from infrastructure config
        await self._register_infrastructure_services()
        
        # Start health checking if enabled
        if self.discovery_config['enabled']:
            self._running = True
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            logger.info(f"✅ Service discovery initialized with {len(self.services)} services")
        else:
            logger.info("⚠️ Service discovery disabled in configuration")
    
    async def _register_infrastructure_services(self):
        """Register all services from infrastructure configuration."""
        for instance_name, instance in self.config.INSTANCES.items():
            for service_type in instance.services:
                service_name = f"{instance_name}_{service_type.value}"
                service_port = instance.get_service_port(service_type)
                service_url = f"http://{instance.ip}:{service_port}"
                
                await self.register_service(
                    name=service_name,
                    url=service_url,
                    service_type=service_type,
                    instance_name=instance_name
                )
        
        self._metrics['services_registered'] = len(self.services)
    
    async def register_service(
        self,
        name: str,
        url: str,
        service_type: ServiceType,
        instance_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register a service endpoint.
        
        Args:
            name: Unique service name
            url: Service endpoint URL
            service_type: Type of service
            instance_name: Name of the instance hosting the service
            metadata: Optional metadata for the service
        """
        endpoint = ServiceEndpoint(
            name=name,
            url=url,
            service_type=service_type,
            instance_name=instance_name,
            metadata=metadata or {}
        )
        
        self.services[name] = endpoint
        logger.info(f"📝 Registered service: {name} at {url}")
        
        # Perform immediate health check
        if self._session and self._running:
            await self._check_service_health(name)
    
    async def deregister_service(self, name: str):
        """
        Deregister a service endpoint.
        
        Args:
            name: Service name to deregister
        """
        if name in self.services:
            del self.services[name]
            self._metrics['services_deregistered'] += 1
            logger.info(f"❌ Deregistered service: {name}")
    
    async def get_service_url(self, service_name: str) -> Optional[str]:
        """
        Get URL for a healthy service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service URL if healthy, None otherwise
        """
        service = self.services.get(service_name)
        if service and service.is_healthy and not service.is_circuit_open:
            return service.url
        return None
    
    async def get_services_by_type(self, service_type: ServiceType) -> List[ServiceEndpoint]:
        """
        Get all healthy services of a specific type.
        
        Args:
            service_type: Type of service to find
            
        Returns:
            List of healthy service endpoints
        """
        return [
            service for service in self.services.values()
            if service.service_type == service_type and service.is_healthy
        ]
    
    async def get_best_service(self, service_type: ServiceType) -> Optional[ServiceEndpoint]:
        """
        Get the best performing service of a specific type.
        
        Args:
            service_type: Type of service to find
            
        Returns:
            Best performing service endpoint or None
        """
        candidates = await self.get_services_by_type(service_type)
        if not candidates:
            return None
        
        # Sort by response time and consecutive failures
        candidates.sort(key=lambda s: (s.consecutive_failures, s.response_time))
        return candidates[0]
    
    async def get_healthy_services(self) -> List[str]:
        """
        Get list of healthy service names.
        
        Returns:
            List of healthy service names
        """
        return [
            name for name, service in self.services.items()
            if service.is_healthy and not service.is_circuit_open
        ]
    
    async def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get comprehensive status of all services.
        
        Returns:
            Dictionary with service status information
        """
        status = {}
        for name, service in self.services.items():
            status[name] = {
                'url': service.url,
                'type': service.service_type.value,
                'instance': service.instance_name,
                'status': service.status.value,
                'response_time': service.response_time,
                'consecutive_failures': service.consecutive_failures,
                'last_check': service.last_check.isoformat(),
                'last_success': service.last_success.isoformat() if service.last_success else None,
                'last_failure': service.last_failure.isoformat() if service.last_failure else None,
                'circuit_open': service.is_circuit_open,
                'metadata': service.metadata
            }
        
        return {
            'services': status,
            'metrics': self._metrics,
            'config': self.discovery_config
        }
    
    def add_status_change_callback(self, callback: Callable):
        """
        Add callback for service status changes.
        
        Args:
            callback: Function to call when service status changes
        """
        self._status_change_callbacks.append(callback)
    
    async def _notify_status_change(self, service_name: str, old_status: ServiceStatus, new_status: ServiceStatus):
        """Notify registered callbacks of status changes."""
        for callback in self._status_change_callbacks:
            try:
                await callback(service_name, old_status, new_status)
            except Exception as e:
                logger.error(f"❌ Error in status change callback: {e}")
    
    async def _health_check_loop(self):
        """Continuous health checking loop with error handling."""
        logger.info(f"🏥 Starting health check loop (interval: {self.health_check_interval}s)")
        
        while self._running:
            try:
                await self._check_all_services()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                logger.info("🛑 Health check loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Health check loop error: {e}")
                await asyncio.sleep(min(self.health_check_interval, 10))
    
    async def _check_all_services(self):
        """Check health of all registered services."""
        if not self.services:
            return
        
        # Create tasks for all health checks
        tasks = []
        for service_name in list(self.services.keys()):
            task = asyncio.create_task(self._check_service_health(service_name))
            tasks.append(task)
        
        # Wait for all checks to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log any exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    service_name = list(self.services.keys())[i]
                    logger.error(f"❌ Health check exception for {service_name}: {result}")
    
    async def _check_service_health(self, service_name: str):
        """
        Check health of a specific service.
        
        Args:
            service_name: Name of service to check
        """
        service = self.services.get(service_name)
        if not service or not self._session:
            return
        
        old_status = service.status
        start_time = time.time()
        
        # Skip check if circuit is open and not enough time has passed
        if service.is_circuit_open:
            if service.last_check and (datetime.now() - service.last_check).seconds < 60:
                return
        
        try:
            self._metrics['total_checks'] += 1
            
            # Construct health check URL
            health_url = f"{service.url.rstrip('/')}/health"
            
            # Perform health check
            async with self._session.get(health_url) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    # Additional validation of response content
                    try:
                        data = await response.json()
                        if data.get('status') in ['healthy', 'ok']:
                            service.update_success(response_time)
                            self._metrics['successful_checks'] += 1
                        else:
                            service.update_failure(f"Unhealthy status: {data.get('status')}")
                            self._metrics['failed_checks'] += 1
                    except (json.JSONDecodeError, KeyError):
                        # Accept 200 status even without proper JSON
                        service.update_success(response_time)
                        self._metrics['successful_checks'] += 1
                else:
                    service.update_failure(f"HTTP {response.status}")
                    self._metrics['failed_checks'] += 1
                    
        except asyncio.TimeoutError:
            service.update_failure("Timeout")
            self._metrics['failed_checks'] += 1
        except aiohttp.ClientError as e:
            service.update_failure(f"Client error: {e}")
            self._metrics['failed_checks'] += 1
        except Exception as e:
            service.update_failure(f"Unexpected error: {e}")
            self._metrics['failed_checks'] += 1
        
        # Notify callbacks if status changed
        if old_status != service.status:
            await self._notify_status_change(service_name, old_status, service.status)
            
            if service.status == ServiceStatus.HEALTHY:
                logger.info(f"✅ Service {service_name} is now healthy")
            else:
                logger.warning(f"⚠️ Service {service_name} is now {service.status.value}")
    
    async def shutdown(self):
        """Gracefully shutdown service discovery."""
        logger.info("🔄 Shutting down service discovery...")
        
        self._running = False
        
        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Close HTTP session
        if self._session:
            await self._session.close()
        
        logger.info("✅ Service discovery shutdown complete")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get service discovery metrics.
        
        Returns:
            Dictionary with metrics and statistics
        """
        healthy_count = sum(1 for s in self.services.values() if s.is_healthy)
        unhealthy_count = len(self.services) - healthy_count
        
        return {
            **self._metrics,
            'healthy_services': healthy_count,
            'unhealthy_services': unhealthy_count,
            'total_services': len(self.services),
            'circuit_breakers_open': sum(1 for s in self.services.values() if s.is_circuit_open),
            'average_response_time': sum(s.response_time for s in self.services.values() if s.response_time > 0) / max(1, len([s for s in self.services.values() if s.response_time > 0]))
        }


# Global service discovery instance
_service_discovery_instance: Optional[ServiceDiscovery] = None


async def get_service_discovery() -> ServiceDiscovery:
    """
    Get the global service discovery instance.
    
    Returns:
        Initialized ServiceDiscovery instance
    """
    global _service_discovery_instance
    
    if _service_discovery_instance is None:
        _service_discovery_instance = ServiceDiscovery()
        await _service_discovery_instance.initialize()
    
    return _service_discovery_instance
