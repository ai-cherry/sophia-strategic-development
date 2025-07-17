"""
Base Infrastructure Agent

Provides common functionality for all infrastructure monitoring agents
including configuration loading, metric export, and alert management.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum

from prometheus_client import Counter, Gauge, Histogram, Info
from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AgentStatus(Enum):
    """Agent operational status"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class BaseInfrastructureAgent(ABC):
    """
    Base class for infrastructure monitoring agents
    
    Provides:
    - Configuration management via Pulumi ESC
    - Prometheus metrics export
    - Alert management
    - Async monitoring loop
    - Error handling and retry logic
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize base infrastructure agent
        
        Args:
            name: Agent name (e.g., 'lambda_labs_monitor')
            description: Human-readable description
        """
        self.name = name
        self.description = description
        self.status = AgentStatus.STARTING
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Configuration
        self.monitoring_interval = int(get_config_value(
            f"{name.upper()}_MONITOR_INTERVAL", "300"  # 5 minutes default
        ) or "300")
        self.max_retries = int(get_config_value(
            f"{name.upper()}_MAX_RETRIES", "3"
        ) or "3")
        self.retry_delay = int(get_config_value(
            f"{name.upper()}_RETRY_DELAY", "30"
        ) or "30")
        
        # Initialize Prometheus metrics
        self._init_metrics()
        
        logger.info(f"Initialized {self.name} agent: {self.description}")
    
    def _init_metrics(self):
        """Initialize Prometheus metrics for the agent"""
        # Agent info
        self.agent_info = Info(
            f"{self.name}_info",
            f"Information about {self.name} agent"
        )
        self.agent_info.info({
            'version': '1.0.0',
            'description': self.description
        })
        
        # Status metrics
        self.status_gauge = Gauge(
            f"{self.name}_status",
            f"Current status of {self.name} (0=stopped, 1=running, 2=error)"
        )
        
        # Monitoring metrics
        self.monitoring_runs = Counter(
            f"{self.name}_monitoring_runs_total",
            f"Total monitoring runs by {self.name}"
        )
        self.monitoring_errors = Counter(
            f"{self.name}_monitoring_errors_total",
            f"Total monitoring errors in {self.name}"
        )
        self.monitoring_duration = Histogram(
            f"{self.name}_monitoring_duration_seconds",
            f"Duration of monitoring runs in {self.name}"
        )
        
        # Alert metrics
        self.alerts_sent = Counter(
            f"{self.name}_alerts_sent_total",
            f"Total alerts sent by {self.name}",
            ['severity', 'type']
        )
    
    async def start(self):
        """Start the monitoring agent"""
        try:
            logger.info(f"Starting {self.name} agent...")
            self.status = AgentStatus.RUNNING
            self._running = True
            self.status_gauge.set(1)
            
            # Start monitoring loop
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Initialize agent-specific resources
            await self.initialize()
            
            logger.info(f"{self.name} agent started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start {self.name} agent: {e}")
            self.status = AgentStatus.ERROR
            self.status_gauge.set(2)
            raise
    
    async def stop(self):
        """Stop the monitoring agent gracefully"""
        try:
            logger.info(f"Stopping {self.name} agent...")
            self.status = AgentStatus.STOPPING
            self._running = False
            
            # Cancel monitoring task
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Cleanup agent-specific resources
            await self.cleanup()
            
            self.status = AgentStatus.STOPPED
            self.status_gauge.set(0)
            logger.info(f"{self.name} agent stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping {self.name} agent: {e}")
            self.status = AgentStatus.ERROR
            self.status_gauge.set(2)
    
    async def _monitoring_loop(self):
        """Main monitoring loop with error handling"""
        while self._running:
            try:
                # Record monitoring start
                start_time = datetime.utcnow()
                self.monitoring_runs.inc()
                
                # Perform monitoring with duration tracking
                with self.monitoring_duration.time():
                    await self.monitor()
                
                # Log successful run
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.debug(f"{self.name} monitoring completed in {duration:.2f}s")
                
            except Exception as e:
                self.monitoring_errors.inc()
                logger.error(f"Error in {self.name} monitoring loop: {e}")
                await self.handle_monitoring_error(e)
            
            # Wait for next monitoring interval
            await asyncio.sleep(self.monitoring_interval)
    
    async def handle_monitoring_error(self, error: Exception):
        """
        Handle errors in monitoring loop
        
        Args:
            error: The exception that occurred
        """
        # Default implementation - can be overridden by subclasses
        logger.error(f"Monitoring error in {self.name}: {error}")
        
        # Send critical alert if too many errors
        error_rate = self.monitoring_errors._value.get() / max(1, self.monitoring_runs._value.get())
        if error_rate > 0.5:  # More than 50% error rate
            await self.send_alert(
                AlertSeverity.CRITICAL,
                f"High error rate in {self.name}",
                {"error_rate": f"{error_rate:.2%}", "latest_error": str(error)}
            )
    
    async def send_alert(self, severity: AlertSeverity, message: str, 
                        details: Optional[Dict[str, Any]] = None):
        """
        Send an alert (to be implemented by subclasses)
        
        Args:
            severity: Alert severity level
            message: Alert message
            details: Additional alert details
        """
        self.alerts_sent.labels(severity=severity.value, type='generic').inc()
        logger.warning(f"[{severity.value.upper()}] {self.name}: {message}")
        if details:
            logger.warning(f"Alert details: {details}")
    
    async def retry_operation(self, operation, *args, **kwargs):
        """
        Retry an operation with exponential backoff
        
        Args:
            operation: Async function to retry
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Operation failed (attempt {attempt + 1}/{self.max_retries}), "
                        f"retrying in {delay}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Operation failed after {self.max_retries} attempts: {e}")
        
        if last_error:
            raise last_error
        else:
            raise RuntimeError(f"Operation failed after {self.max_retries} attempts")
    
    @abstractmethod
    async def initialize(self):
        """Initialize agent-specific resources"""
        pass
    
    @abstractmethod
    async def monitor(self):
        """Perform monitoring tasks (to be implemented by subclasses)"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup agent-specific resources"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status
        
        Returns:
            Dictionary with agent status information
        """
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "monitoring_interval": self.monitoring_interval,
            "monitoring_runs": self.monitoring_runs._value.get(),
            "monitoring_errors": self.monitoring_errors._value.get(),
            "uptime": self._get_uptime()
        }
    
    def _get_uptime(self) -> Optional[float]:
        """Get agent uptime in seconds"""
        # This would need to track start time
        # Simplified for now
        return None if self.status != AgentStatus.RUNNING else 0.0
