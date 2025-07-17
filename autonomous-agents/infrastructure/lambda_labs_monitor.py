"""
Lambda Labs GPU Monitoring Agent

Autonomous agent that monitors Lambda Labs GPU instances for:
- GPU utilization
- Memory usage
- Temperature
- Power consumption
- Cost optimization opportunities
"""

import asyncio
import logging
import aiohttp
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from prometheus_client import Gauge
from backend.core.auto_esc_config import get_lambda_labs_config
from .base_infrastructure_agent import BaseInfrastructureAgent, AlertSeverity

logger = logging.getLogger(__name__)


@dataclass
class GPUMetrics:
    """GPU metrics from Lambda Labs instance"""
    instance_id: str
    instance_name: str
    instance_type: str
    gpu_utilization: float  # 0-100%
    gpu_memory_used: float  # GB
    gpu_memory_total: float  # GB
    gpu_temperature: float  # Celsius
    gpu_power_draw: float  # Watts
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def gpu_memory_utilization(self) -> float:
        """Calculate memory utilization percentage"""
        if self.gpu_memory_total == 0:
            return 0.0
        return (self.gpu_memory_used / self.gpu_memory_total) * 100


@dataclass
class InstanceCost:
    """Cost information for Lambda Labs instance"""
    instance_id: str
    instance_type: str
    hourly_rate: float
    daily_cost: float
    monthly_cost: float
    current_usage_hours: float
    current_cost: float


class LambdaLabsMonitorAgent(BaseInfrastructureAgent):
    """
    Monitors Lambda Labs GPU instances for performance and cost optimization
    
    Features:
    - Real-time GPU utilization monitoring
    - Memory usage tracking
    - Temperature and power monitoring
    - Cost optimization recommendations
    - Anomaly detection and alerting
    """
    
    def __init__(self):
        super().__init__(
            name="lambda_labs_monitor",
            description="Monitors Lambda Labs GPU instances for performance and cost optimization"
        )
        
        # Configuration
        self.api_config = get_lambda_labs_config()
        self.api_key = self.api_config.get("api_key")
        self.base_url = self.api_config.get("api_url", "https://cloud.lambdalabs.com/api/v1")
        
        # Thresholds (configurable via environment)
        self.high_gpu_threshold = float(self.api_config.get("high_gpu_threshold", "80"))
        self.low_gpu_threshold = float(self.api_config.get("low_gpu_threshold", "20"))
        self.high_temp_threshold = float(self.api_config.get("high_temp_threshold", "85"))
        self.high_memory_threshold = float(self.api_config.get("high_memory_threshold", "90"))
        
        # Duration thresholds (in minutes)
        self.high_usage_duration = int(self.api_config.get("high_usage_duration_mins", "15"))
        self.low_usage_duration = int(self.api_config.get("low_usage_duration_mins", "30"))
        
        # Tracking
        self.instances: Dict[str, Dict[str, Any]] = {}
        self.metrics_history: Dict[str, List[GPUMetrics]] = {}
        self.anomaly_state: Dict[str, Dict[str, Any]] = {}
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Additional Prometheus metrics
        self._init_lambda_metrics()
    
    def _init_lambda_metrics(self):
        """Initialize Lambda Labs specific Prometheus metrics"""
        # GPU metrics per instance
        self.gpu_utilization_gauge = Gauge(
            'lambda_labs_gpu_utilization_percent',
            'GPU utilization percentage',
            ['instance_id', 'instance_name', 'instance_type']
        )
        self.gpu_memory_gauge = Gauge(
            'lambda_labs_gpu_memory_percent',
            'GPU memory utilization percentage',
            ['instance_id', 'instance_name', 'instance_type']
        )
        self.gpu_temperature_gauge = Gauge(
            'lambda_labs_gpu_temperature_celsius',
            'GPU temperature in Celsius',
            ['instance_id', 'instance_name', 'instance_type']
        )
        self.gpu_power_gauge = Gauge(
            'lambda_labs_gpu_power_watts',
            'GPU power consumption in watts',
            ['instance_id', 'instance_name', 'instance_type']
        )
        
        # Cost metrics
        self.instance_cost_gauge = Gauge(
            'lambda_labs_instance_cost_dollars',
            'Current instance cost in dollars',
            ['instance_id', 'instance_type', 'period']
        )
        
        # Anomaly metrics
        self.anomaly_gauge = Gauge(
            'lambda_labs_anomaly_detected',
            'Anomaly detection status (1=detected, 0=normal)',
            ['instance_id', 'anomaly_type']
        )
    
    async def initialize(self):
        """Initialize Lambda Labs monitoring resources"""
        # Create HTTP session
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        # Get initial instance list
        await self.refresh_instances()
        
        logger.info(f"Lambda Labs monitor initialized with {len(self.instances)} instances")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def refresh_instances(self):
        """Refresh the list of Lambda Labs instances"""
        try:
            instances = await self.retry_operation(self._get_instances)
            
            # Update instance tracking
            for instance in instances:
                instance_id = instance["id"]
                self.instances[instance_id] = instance
                
                # Initialize tracking structures
                if instance_id not in self.metrics_history:
                    self.metrics_history[instance_id] = []
                if instance_id not in self.anomaly_state:
                    self.anomaly_state[instance_id] = {
                        "high_gpu_start": None,
                        "low_gpu_start": None,
                        "high_temp_start": None,
                        "high_memory_start": None
                    }
            
            logger.info(f"Refreshed {len(instances)} Lambda Labs instances")
            
        except Exception as e:
            logger.error(f"Failed to refresh instances: {e}")
            await self.send_alert(
                AlertSeverity.ERROR,
                "Failed to refresh Lambda Labs instances",
                {"error": str(e)}
            )
    
    async def _get_instances(self) -> List[Dict[str, Any]]:
        """Get list of instances from Lambda Labs API"""
        if not self.session:
            raise RuntimeError("HTTP session not initialized")
        async with self.session.get(f"{self.base_url}/instances") as response:
            response.raise_for_status()
            data = await response.json()
            if not isinstance(data, dict):
                return []
            return data.get("data", [])
    
    async def _get_instance_metrics(self, instance_id: str) -> Optional[GPUMetrics]:
        """
        Get GPU metrics for a specific instance
        
        Note: In production, this would use SSH or Lambda Labs monitoring API
        For now, simulating with realistic values
        """
        instance = self.instances.get(instance_id)
        if not instance:
            return None
        
        # TODO: Implement actual metric collection via SSH or API
        # For now, using simulated metrics for demonstration
        import random
        
        # Simulate different patterns based on instance type
        instance_type = instance.get("instance_type", {}).get("name", "unknown")
        
        if "GH200" in instance_type:
            # GH200 instances typically have higher utilization
            base_util = 70
            memory_total = 96  # GB
        elif "A100" in instance_type:
            base_util = 60
            memory_total = 80  # GB
        else:
            base_util = 50
            memory_total = 48  # GB
        
        # Add some variation
        gpu_util = max(0, min(100, base_util + random.uniform(-20, 20)))
        memory_used = (gpu_util / 100) * memory_total * random.uniform(0.8, 1.2)
        
        return GPUMetrics(
            instance_id=instance_id,
            instance_name=instance.get("name", ""),
            instance_type=instance_type,
            gpu_utilization=gpu_util,
            gpu_memory_used=min(memory_used, memory_total),
            gpu_memory_total=memory_total,
            gpu_temperature=60 + (gpu_util / 100) * 25 + random.uniform(-5, 5),
            gpu_power_draw=200 + (gpu_util / 100) * 150 + random.uniform(-20, 20)
        )
    
    async def monitor(self):
        """Main monitoring loop implementation"""
        # Refresh instance list periodically
        if not hasattr(self, '_last_refresh') or \
           (datetime.now(timezone.utc) - self._last_refresh).total_seconds() > 3600:
            await self.refresh_instances()
            self._last_refresh = datetime.now(timezone.utc)
        
        # Monitor each instance
        for instance_id, instance in self.instances.items():
            try:
                # Get current metrics
                metrics = await self._get_instance_metrics(instance_id)
                if not metrics:
                    continue
                
                # Update Prometheus metrics
                self._update_prometheus_metrics(metrics)
                
                # Store in history (keep last hour)
                self.metrics_history[instance_id].append(metrics)
                self._cleanup_old_metrics(instance_id)
                
                # Check for anomalies
                await self._check_anomalies(metrics)
                
                # Calculate and update costs
                await self._update_cost_metrics(instance_id, instance)
                
            except Exception as e:
                logger.error(f"Error monitoring instance {instance_id}: {e}")
                self.monitoring_errors.inc()
    
    def _update_prometheus_metrics(self, metrics: GPUMetrics):
        """Update Prometheus metrics with latest GPU data"""
        labels = [metrics.instance_id, metrics.instance_name, metrics.instance_type]
        
        self.gpu_utilization_gauge.labels(*labels).set(metrics.gpu_utilization)
        self.gpu_memory_gauge.labels(*labels).set(metrics.gpu_memory_utilization)
        self.gpu_temperature_gauge.labels(*labels).set(metrics.gpu_temperature)
        self.gpu_power_gauge.labels(*labels).set(metrics.gpu_power_draw)
    
    def _cleanup_old_metrics(self, instance_id: str):
        """Remove metrics older than 1 hour"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        self.metrics_history[instance_id] = [
            m for m in self.metrics_history[instance_id]
            if m.timestamp > cutoff
        ]
    
    async def _check_anomalies(self, metrics: GPUMetrics):
        """Check for anomalies in GPU metrics"""
        instance_id = metrics.instance_id
        state = self.anomaly_state[instance_id]
        now = datetime.now(timezone.utc)
        
        # Check high GPU utilization
        if metrics.gpu_utilization > self.high_gpu_threshold:
            if state["high_gpu_start"] is None:
                state["high_gpu_start"] = now
            elif (now - state["high_gpu_start"]).total_seconds() / 60 > self.high_usage_duration:
                await self._handle_high_gpu_anomaly(metrics)
                self.anomaly_gauge.labels(instance_id, "high_gpu").set(1)
        else:
            state["high_gpu_start"] = None
            self.anomaly_gauge.labels(instance_id, "high_gpu").set(0)
        
        # Check low GPU utilization
        if metrics.gpu_utilization < self.low_gpu_threshold:
            if state["low_gpu_start"] is None:
                state["low_gpu_start"] = now
            elif (now - state["low_gpu_start"]).total_seconds() / 60 > self.low_usage_duration:
                await self._handle_low_gpu_anomaly(metrics)
                self.anomaly_gauge.labels(instance_id, "low_gpu").set(1)
        else:
            state["low_gpu_start"] = None
            self.anomaly_gauge.labels(instance_id, "low_gpu").set(0)
        
        # Check high temperature
        if metrics.gpu_temperature > self.high_temp_threshold:
            if state["high_temp_start"] is None:
                state["high_temp_start"] = now
                await self._handle_high_temp_anomaly(metrics)
                self.anomaly_gauge.labels(instance_id, "high_temp").set(1)
        else:
            state["high_temp_start"] = None
            self.anomaly_gauge.labels(instance_id, "high_temp").set(0)
        
        # Check high memory usage
        if metrics.gpu_memory_utilization > self.high_memory_threshold:
            if state["high_memory_start"] is None:
                state["high_memory_start"] = now
                await self._handle_high_memory_anomaly(metrics)
                self.anomaly_gauge.labels(instance_id, "high_memory").set(1)
        else:
            state["high_memory_start"] = None
            self.anomaly_gauge.labels(instance_id, "high_memory").set(0)
    
    async def _handle_high_gpu_anomaly(self, metrics: GPUMetrics):
        """Handle sustained high GPU utilization"""
        message = f"High GPU utilization on {metrics.instance_name}"
        details = {
            "instance_id": metrics.instance_id,
            "instance_type": metrics.instance_type,
            "gpu_utilization": f"{metrics.gpu_utilization:.1f}%",
            "duration": f"{self.high_usage_duration} minutes",
            "recommendation": "Consider scaling up or optimizing workload distribution"
        }
        
        logger.info(f"{message}: {details}")
        await self.send_alert(AlertSeverity.WARNING, message, details)
    
    async def _handle_low_gpu_anomaly(self, metrics: GPUMetrics):
        """Handle sustained low GPU utilization"""
        # Calculate potential savings
        instance = self.instances.get(metrics.instance_id, {})
        hourly_rate = self._get_instance_hourly_rate(instance)
        potential_savings = hourly_rate * 24 * 30  # Monthly savings
        
        message = f"Low GPU utilization on {metrics.instance_name}"
        details = {
            "instance_id": metrics.instance_id,
            "instance_type": metrics.instance_type,
            "gpu_utilization": f"{metrics.gpu_utilization:.1f}%",
            "duration": f"{self.low_usage_duration} minutes",
            "potential_monthly_savings": f"${potential_savings:.2f}",
            "recommendation": "Consider downgrading instance or consolidating workloads"
        }
        
        logger.info(f"{message}: {details}")
        await self.send_alert(AlertSeverity.INFO, message, details)
    
    async def _handle_high_temp_anomaly(self, metrics: GPUMetrics):
        """Handle high GPU temperature"""
        message = f"High GPU temperature on {metrics.instance_name}"
        details = {
            "instance_id": metrics.instance_id,
            "instance_type": metrics.instance_type,
            "gpu_temperature": f"{metrics.gpu_temperature:.1f}°C",
            "threshold": f"{self.high_temp_threshold}°C",
            "recommendation": "Check cooling and consider reducing workload"
        }
        
        logger.warning(f"{message}: {details}")
        await self.send_alert(AlertSeverity.WARNING, message, details)
    
    async def _handle_high_memory_anomaly(self, metrics: GPUMetrics):
        """Handle high GPU memory usage"""
        message = f"High GPU memory usage on {metrics.instance_name}"
        details = {
            "instance_id": metrics.instance_id,
            "instance_type": metrics.instance_type,
            "memory_usage": f"{metrics.gpu_memory_used:.1f}/{metrics.gpu_memory_total:.1f} GB",
            "memory_utilization": f"{metrics.gpu_memory_utilization:.1f}%",
            "recommendation": "Optimize batch sizes or consider upgrading instance"
        }
        
        logger.warning(f"{message}: {details}")
        await self.send_alert(AlertSeverity.WARNING, message, details)
    
    def _get_instance_hourly_rate(self, instance: Dict[str, Any]) -> float:
        """Get hourly rate for an instance type"""
        # Lambda Labs pricing (approximate)
        instance_type = instance.get("instance_type", {}).get("name", "")
        
        rates = {
            "GH200": 2.99,
            "A100": 1.99,
            "A6000": 0.80,
            "RTX6000": 0.50,
            "RTX4090": 0.40
        }
        
        for key, rate in rates.items():
            if key in instance_type:
                return rate
        
        return 1.0  # Default rate
    
    async def _update_cost_metrics(self, instance_id: str, instance: Dict[str, Any]):
        """Update cost metrics for an instance"""
        hourly_rate = self._get_instance_hourly_rate(instance)
        
        # Calculate usage (simplified - in production would use actual launch time)
        usage_hours = 24  # Assume 24 hours for now
        current_cost = usage_hours * hourly_rate
        
        # Update Prometheus metrics
        instance_type = instance.get("instance_type", {}).get("name", "unknown")
        self.instance_cost_gauge.labels(instance_id, instance_type, "hourly").set(hourly_rate)
        self.instance_cost_gauge.labels(instance_id, instance_type, "daily").set(hourly_rate * 24)
        self.instance_cost_gauge.labels(instance_id, instance_type, "current").set(current_cost)
    
    async def send_alert(self, severity: AlertSeverity, message: str, 
                        details: Optional[Dict[str, Any]] = None):
        """
        Send alert via Slack MCP server
        
        In production, this would integrate with the Slack MCP server
        """
        # Log the alert
        await super().send_alert(severity, message, details)
        
        # TODO: Integrate with Slack MCP server
        # Example:
        # await self.slack_client.send_message(
        #     channel="#sophia-infrastructure",
        #     text=f"[{severity.value.upper()}] {message}",
        #     attachments=[{"fields": [{"title": k, "value": v} for k, v in details.items()]}]
        # )
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get cost optimization recommendations based on current metrics
        
        Returns:
            List of recommendations with potential savings
        """
        recommendations = []
        
        for instance_id, history in self.metrics_history.items():
            if not history:
                continue
            
            # Calculate average utilization over the last hour
            avg_util = sum(m.gpu_utilization for m in history) / len(history)
            instance = self.instances.get(instance_id, {})
            
            if avg_util < self.low_gpu_threshold:
                hourly_rate = self._get_instance_hourly_rate(instance)
                recommendation = {
                    "instance_id": instance_id,
                    "instance_name": instance.get("name", ""),
                    "current_type": instance.get("instance_type", {}).get("name", ""),
                    "avg_utilization": f"{avg_util:.1f}%",
                    "recommendation": "Downgrade or terminate instance",
                    "potential_monthly_savings": f"${hourly_rate * 24 * 30:.2f}"
                }
                recommendations.append(recommendation)
        
        return recommendations


# For standalone testing
async def main():
    """Test the Lambda Labs monitoring agent"""
    logging.basicConfig(level=logging.INFO)
    
    agent = LambdaLabsMonitorAgent()
    
    try:
        await agent.start()
        
        # Run for a few monitoring cycles
        await asyncio.sleep(30)
        
        # Get status and recommendations
        status = agent.get_status()
        recommendations = agent.get_optimization_recommendations()
        
        print(f"Agent Status: {status}")
        print(f"Recommendations: {recommendations}")
        
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
