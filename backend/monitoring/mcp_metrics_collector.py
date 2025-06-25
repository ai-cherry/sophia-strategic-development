"""
Sophia AI - MCP Metrics Collector
Comprehensive metrics collection and monitoring for all MCP servers
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

import psutil
from prometheus_client import Counter, Histogram, Gauge, Info, Summary, start_http_server, CollectorRegistry, REGISTRY

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    INFO = "info"

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    FATAL = "fatal"

@dataclass
class MetricDefinition:
    """Definition of a metric to be collected."""
    name: str
    metric_type: MetricType
    description: str
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None  # For histograms
    objectives: Optional[Dict[float, float]] = None  # For summaries

@dataclass
class HealthThreshold:
    """Health monitoring thresholds."""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    comparison_operator: str = "gt"  # gt, lt, eq, gte, lte
    evaluation_period_seconds: int = 300  # 5 minutes
    min_samples: int = 3

@dataclass
class Alert:
    """Alert generated from metrics."""
    alert_id: str
    severity: AlertSeverity
    message: str
    metric_name: str
    current_value: float
    threshold_value: float
    triggered_at: datetime
    server_name: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class MCPMetricsCollector:
    """
    Comprehensive metrics collector for MCP servers with enterprise-grade monitoring.
    
    Features:
    - Prometheus metrics integration
    - Real-time health monitoring
    - Automated alerting
    - Business intelligence metrics
    - Performance analytics
    - Resource utilization tracking
    """
    
    def __init__(self, 
                 server_name: str,
                 enable_prometheus: bool = True,
                 prometheus_port: int = 8000,
                 enable_health_monitoring: bool = True):
        self.server_name = server_name
        self.enable_prometheus = enable_prometheus
        self.prometheus_port = prometheus_port
        self.enable_health_monitoring = enable_health_monitoring
        
        # Metrics storage
        self.prometheus_metrics: Dict[str, Any] = {}
        self.custom_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.health_checks: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Alerting
        self.health_thresholds: List[HealthThreshold] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_callbacks: List[Callable] = []
        
        # Performance tracking
        self.request_latencies: deque = deque(maxlen=1000)
        self.error_rates: Dict[str, int] = defaultdict(int)
        self.success_rates: Dict[str, int] = defaultdict(int)
        
        # Initialize Prometheus metrics
        if self.enable_prometheus:
            self._initialize_prometheus_metrics()
    
    def _initialize_prometheus_metrics(self) -> None:
        """Initialize standard Prometheus metrics for MCP servers."""
        try:
            # Define standard metrics
            standard_metrics = [
                MetricDefinition(
                    name=f"mcp_{self.server_name}_requests_total",
                    metric_type=MetricType.COUNTER,
                    description="Total requests to MCP server",
                    labels=["method", "status", "endpoint"]
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_request_duration_seconds",
                    metric_type=MetricType.HISTOGRAM,
                    description="Request duration in seconds",
                    labels=["method", "endpoint"],
                    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_health_status",
                    metric_type=MetricType.GAUGE,
                    description="Health status of MCP server (1=healthy, 0=unhealthy)"
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_sync_success_rate",
                    metric_type=MetricType.GAUGE,
                    description="Success rate of data synchronization"
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_data_freshness_seconds",
                    metric_type=MetricType.GAUGE,
                    description="Age of the most recent data in seconds"
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_records_processed_total",
                    metric_type=MetricType.COUNTER,
                    description="Total records processed",
                    labels=["operation", "status"]
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_ai_processing_duration_seconds",
                    metric_type=MetricType.HISTOGRAM,
                    description="Duration of AI processing operations",
                    labels=["operation"],
                    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_ai_accuracy_score",
                    metric_type=MetricType.GAUGE,
                    description="AI processing accuracy score"
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_memory_usage_bytes",
                    metric_type=MetricType.GAUGE,
                    description="Memory usage in bytes"
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_cpu_usage_percent",
                    metric_type=MetricType.GAUGE,
                    description="CPU usage percentage"
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_sync_conflicts_total",
                    metric_type=MetricType.COUNTER,
                    description="Total sync conflicts detected",
                    labels=["conflict_type", "platforms"]
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_workflow_execution_duration_seconds",
                    metric_type=MetricType.HISTOGRAM,
                    description="Multi-agent workflow execution duration",
                    labels=["workflow_type", "status"],
                    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0]
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_business_insights_generated_total",
                    metric_type=MetricType.COUNTER,
                    description="Total business insights generated",
                    labels=["insight_type", "confidence_level"]
                ),
                MetricDefinition(
                    name=f"mcp_{self.server_name}_info",
                    metric_type=MetricType.INFO,
                    description="MCP server information"
                )
            ]
            
            # Create Prometheus metric objects
            for metric_def in standard_metrics:
                self._create_prometheus_metric(metric_def)
            
            # Set server info
            if f"mcp_{self.server_name}_info" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_info"].info({
                    'version': '2.0.0',
                    'server_name': self.server_name,
                    'monitoring_enabled': 'true',
                    'ai_enabled': 'true'
                })
            
            logger.info(f"✅ Prometheus metrics initialized for {self.server_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Prometheus metrics for {self.server_name}: {e}")
    
    def _create_prometheus_metric(self, metric_def: MetricDefinition) -> None:
        """Create a Prometheus metric object."""
        try:
            if metric_def.metric_type == MetricType.COUNTER:
                self.prometheus_metrics[metric_def.name] = Counter(
                    metric_def.name,
                    metric_def.description,
                    metric_def.labels
                )
            elif metric_def.metric_type == MetricType.GAUGE:
                self.prometheus_metrics[metric_def.name] = Gauge(
                    metric_def.name,
                    metric_def.description,
                    metric_def.labels
                )
            elif metric_def.metric_type == MetricType.HISTOGRAM:
                self.prometheus_metrics[metric_def.name] = Histogram(
                    metric_def.name,
                    metric_def.description,
                    metric_def.labels,
                    buckets=metric_def.buckets
                )
            elif metric_def.metric_type == MetricType.SUMMARY:
                self.prometheus_metrics[metric_def.name] = Summary(
                    metric_def.name,
                    metric_def.description,
                    metric_def.labels,
                    quantiles=metric_def.objectives or {0.5: 0.05, 0.9: 0.01, 0.99: 0.001}
                )
            elif metric_def.metric_type == MetricType.INFO:
                self.prometheus_metrics[metric_def.name] = Info(
                    metric_def.name,
                    metric_def.description
                )
                
        except Exception as e:
            logger.error(f"Failed to create Prometheus metric {metric_def.name}: {e}")
    
    def start_prometheus_server(self) -> None:
        """Start Prometheus metrics server."""
        if self.enable_prometheus:
            try:
                start_http_server(self.prometheus_port)
                logger.info(f"✅ Prometheus metrics server started on port {self.prometheus_port}")
            except Exception as e:
                logger.error(f"❌ Failed to start Prometheus server: {e}")
    
    def record_request(self, method: str, endpoint: str, status: str, duration_seconds: float) -> None:
        """Record a request with metrics."""
        try:
            # Prometheus metrics
            if f"mcp_{self.server_name}_requests_total" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_requests_total"].labels(
                    method=method, status=status, endpoint=endpoint
                ).inc()
            
            if f"mcp_{self.server_name}_request_duration_seconds" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_request_duration_seconds"].labels(
                    method=method, endpoint=endpoint
                ).observe(duration_seconds)
            
            # Custom metrics
            self.request_latencies.append(duration_seconds)
            
            # Update success/error rates
            if status == "success":
                self.success_rates[endpoint] += 1
            else:
                self.error_rates[endpoint] += 1
                
        except Exception as e:
            logger.error(f"Failed to record request metrics: {e}")
    
    def record_sync_metrics(self, 
                          records_processed: int, 
                          success_rate: float, 
                          data_age_seconds: int,
                          conflicts_detected: int = 0,
                          operation: str = "sync") -> None:
        """Record synchronization metrics."""
        try:
            # Records processed
            if f"mcp_{self.server_name}_records_processed_total" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_records_processed_total"].labels(
                    operation=operation, status="success"
                ).inc(records_processed)
            
            # Success rate
            if f"mcp_{self.server_name}_sync_success_rate" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_sync_success_rate"].set(success_rate)
            
            # Data freshness
            if f"mcp_{self.server_name}_data_freshness_seconds" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_data_freshness_seconds"].set(data_age_seconds)
            
            # Conflicts
            if conflicts_detected > 0 and f"mcp_{self.server_name}_sync_conflicts_total" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_sync_conflicts_total"].labels(
                    conflict_type="data_mismatch", platforms="cross_platform"
                ).inc(conflicts_detected)
            
            # Custom metrics for trend analysis
            self.custom_metrics['sync_success_rate'].append({
                'timestamp': datetime.utcnow(),
                'value': success_rate,
                'records_processed': records_processed,
                'data_age_seconds': data_age_seconds,
                'conflicts_detected': conflicts_detected
            })
            
        except Exception as e:
            logger.error(f"Failed to record sync metrics: {e}")
    
    def record_ai_processing_metrics(self, 
                                   operation: str, 
                                   duration_seconds: float,
                                   accuracy_score: Optional[float] = None,
                                   insights_generated: int = 0,
                                   confidence_level: str = "medium") -> None:
        """Record AI processing metrics."""
        try:
            # Processing duration
            if f"mcp_{self.server_name}_ai_processing_duration_seconds" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_ai_processing_duration_seconds"].labels(
                    operation=operation
                ).observe(duration_seconds)
            
            # Accuracy score
            if accuracy_score is not None and f"mcp_{self.server_name}_ai_accuracy_score" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_ai_accuracy_score"].set(accuracy_score)
            
            # Business insights generated
            if insights_generated > 0 and f"mcp_{self.server_name}_business_insights_generated_total" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_business_insights_generated_total"].labels(
                    insight_type=operation, confidence_level=confidence_level
                ).inc(insights_generated)
            
            # Custom AI metrics
            self.custom_metrics['ai_processing_times'].append({
                'timestamp': datetime.utcnow(),
                'operation': operation,
                'duration': duration_seconds,
                'accuracy': accuracy_score,
                'insights_generated': insights_generated,
                'confidence_level': confidence_level
            })
            
        except Exception as e:
            logger.error(f"Failed to record AI processing metrics: {e}")
    
    def record_workflow_metrics(self, 
                              workflow_type: str,
                              status: str,
                              duration_seconds: float,
                              tasks_completed: int,
                              tasks_failed: int) -> None:
        """Record multi-agent workflow metrics."""
        try:
            # Workflow execution duration
            if f"mcp_{self.server_name}_workflow_execution_duration_seconds" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_workflow_execution_duration_seconds"].labels(
                    workflow_type=workflow_type, status=status
                ).observe(duration_seconds)
            
            # Custom workflow metrics
            self.custom_metrics['workflow_executions'].append({
                'timestamp': datetime.utcnow(),
                'workflow_type': workflow_type,
                'status': status,
                'duration': duration_seconds,
                'tasks_completed': tasks_completed,
                'tasks_failed': tasks_failed,
                'success_rate': tasks_completed / (tasks_completed + tasks_failed) if (tasks_completed + tasks_failed) > 0 else 0
            })
            
        except Exception as e:
            logger.error(f"Failed to record workflow metrics: {e}")
    
    def update_health_status(self, is_healthy: bool, component: str = "overall") -> None:
        """Update health status metrics."""
        try:
            # Prometheus health gauge
            if f"mcp_{self.server_name}_health_status" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_health_status"].set(1 if is_healthy else 0)
            
            # Custom health tracking
            self.health_checks[component].append({
                'timestamp': datetime.utcnow(),
                'healthy': is_healthy
            })
            
            # Check for alert conditions
            if self.enable_health_monitoring:
                self._evaluate_health_alerts(component, is_healthy)
                
        except Exception as e:
            logger.error(f"Failed to update health status: {e}")
    
    def update_resource_metrics(self) -> None:
        """Update system resource metrics."""
        try:
            # Get current process
            process = psutil.Process()
            
            # Memory usage
            memory_bytes = process.memory_info().rss
            if f"mcp_{self.server_name}_memory_usage_bytes" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_memory_usage_bytes"].set(memory_bytes)
            
            # CPU usage
            cpu_percent = process.cpu_percent()
            if f"mcp_{self.server_name}_cpu_usage_percent" in self.prometheus_metrics:
                self.prometheus_metrics[f"mcp_{self.server_name}_cpu_usage_percent"].set(cpu_percent)
            
            # Custom resource tracking
            self.custom_metrics['resource_usage'].append({
                'timestamp': datetime.utcnow(),
                'memory_bytes': memory_bytes,
                'cpu_percent': cpu_percent
            })
            
        except Exception as e:
            logger.error(f"Failed to update resource metrics: {e}")
    
    def add_health_threshold(self, threshold: HealthThreshold) -> None:
        """Add a health monitoring threshold."""
        self.health_thresholds.append(threshold)
        logger.info(f"Added health threshold for {threshold.metric_name}")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Add a callback function for alerts."""
        self.alert_callbacks.append(callback)
    
    def _evaluate_health_alerts(self, component: str, current_status: bool) -> None:
        """Evaluate health status against thresholds and generate alerts."""
        try:
            # Check for status change alerts
            alert_id = f"{self.server_name}_{component}_health"
            
            if not current_status and alert_id not in self.active_alerts:
                # Generate new alert
                alert = Alert(
                    alert_id=alert_id,
                    severity=AlertSeverity.CRITICAL,
                    message=f"Health check failed for {component} on {self.server_name}",
                    metric_name=f"{component}_health",
                    current_value=0,
                    threshold_value=1,
                    triggered_at=datetime.utcnow(),
                    server_name=self.server_name
                )
                
                self.active_alerts[alert_id] = alert
                self._trigger_alert(alert)
                
            elif current_status and alert_id in self.active_alerts:
                # Resolve existing alert
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                
                self._resolve_alert(alert)
                del self.active_alerts[alert_id]
                
        except Exception as e:
            logger.error(f"Failed to evaluate health alerts: {e}")
    
    def _trigger_alert(self, alert: Alert) -> None:
        """Trigger an alert by calling all registered callbacks."""
        logger.warning(f"🚨 ALERT: {alert.message}")
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    def _resolve_alert(self, alert: Alert) -> None:
        """Resolve an alert."""
        logger.info(f"✅ RESOLVED: {alert.message}")
        
        # Could add resolution callbacks here
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        try:
            summary = {
                'server_name': self.server_name,
                'timestamp': datetime.utcnow().isoformat(),
                'health_status': len(self.active_alerts) == 0,
                'active_alerts': len(self.active_alerts),
                'metrics': {}
            }
            
            # Request metrics
            if self.request_latencies:
                avg_latency = sum(self.request_latencies) / len(self.request_latencies)
                p95_latency = sorted(self.request_latencies)[int(len(self.request_latencies) * 0.95)] if len(self.request_latencies) > 1 else 0
                summary['metrics']['average_request_latency'] = avg_latency
                summary['metrics']['p95_request_latency'] = p95_latency
            
            # Success/error rates
            total_requests = sum(self.success_rates.values()) + sum(self.error_rates.values())
            if total_requests > 0:
                overall_success_rate = sum(self.success_rates.values()) / total_requests
                summary['metrics']['overall_success_rate'] = overall_success_rate
            
            # Recent sync performance
            if 'sync_success_rate' in self.custom_metrics and self.custom_metrics['sync_success_rate']:
                recent_sync = self.custom_metrics['sync_success_rate'][-1]
                summary['metrics']['latest_sync_success_rate'] = recent_sync['value']
            
            # Recent AI performance
            if 'ai_processing_times' in self.custom_metrics and self.custom_metrics['ai_processing_times']:
                recent_ai = self.custom_metrics['ai_processing_times'][-5:]  # Last 5 AI operations
                avg_ai_time = sum(op['duration'] for op in recent_ai) / len(recent_ai)
                summary['metrics']['average_ai_processing_time'] = avg_ai_time
            
            # Workflow performance
            if 'workflow_executions' in self.custom_metrics and self.custom_metrics['workflow_executions']:
                recent_workflows = self.custom_metrics['workflow_executions'][-10:]  # Last 10 workflows
                workflow_success_rate = sum(1 for w in recent_workflows if w['status'] == 'completed') / len(recent_workflows)
                summary['metrics']['workflow_success_rate'] = workflow_success_rate
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate metrics summary: {e}")
            return {
                'server_name': self.server_name,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def get_business_intelligence_metrics(self) -> Dict[str, Any]:
        """Get business-focused metrics summary."""
        try:
            # Calculate business metrics from custom metrics
            bi_metrics = {
                'server_name': self.server_name,
                'reporting_period': 'last_24_hours',
                'timestamp': datetime.utcnow().isoformat(),
                'business_metrics': {}
            }
            
            # Data processing efficiency
            if 'sync_success_rate' in self.custom_metrics:
                recent_syncs = [
                    m for m in self.custom_metrics['sync_success_rate'] 
                    if m['timestamp'] > datetime.utcnow() - timedelta(hours=24)
                ]
                if recent_syncs:
                    avg_efficiency = sum(m['value'] for m in recent_syncs) / len(recent_syncs)
                    bi_metrics['business_metrics']['data_processing_efficiency'] = avg_efficiency
            
            # AI insights generation rate
            if 'ai_processing_times' in self.custom_metrics:
                recent_ai = [
                    m for m in self.custom_metrics['ai_processing_times']
                    if m['timestamp'] > datetime.utcnow() - timedelta(hours=24)
                ]
                bi_metrics['business_metrics']['ai_insights_generated_24h'] = len(recent_ai)
            
            # Workflow automation success
            if 'workflow_executions' in self.custom_metrics:
                recent_workflows = [
                    w for w in self.custom_metrics['workflow_executions']
                    if w['timestamp'] > datetime.utcnow() - timedelta(hours=24)
                ]
                if recent_workflows:
                    automation_success = sum(1 for w in recent_workflows if w['status'] == 'completed') / len(recent_workflows)
                    bi_metrics['business_metrics']['automation_success_rate'] = automation_success
            
            # System reliability
            bi_metrics['business_metrics']['system_reliability'] = len(self.active_alerts) == 0
            bi_metrics['business_metrics']['active_issues'] = len(self.active_alerts)
            
            return bi_metrics
            
        except Exception as e:
            logger.error(f"Failed to generate business intelligence metrics: {e}")
            return {'error': str(e)}
    
    async def start_continuous_monitoring(self, interval_seconds: int = 60) -> None:
        """Start continuous monitoring loop."""
        logger.info(f"🔄 Starting continuous monitoring for {self.server_name}")
        
        while True:
            try:
                # Update resource metrics
                self.update_resource_metrics()
                
                # Check health thresholds
                for threshold in self.health_thresholds:
                    await self._check_threshold(threshold)
                
                # Clean up old metrics (keep last 24 hours)
                self._cleanup_old_metrics()
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def _check_threshold(self, threshold: HealthThreshold) -> None:
        """Check a specific threshold and generate alerts if needed."""
        # Implementation would depend on the specific metric being monitored
        pass
    
    def _cleanup_old_metrics(self) -> None:
        """Clean up metrics older than 24 hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        for metric_name, metric_data in self.custom_metrics.items():
            # Remove old entries
            while metric_data and metric_data[0]['timestamp'] < cutoff_time:
                metric_data.popleft() 