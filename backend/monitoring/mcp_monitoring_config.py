#!/usr/bin/env python3
"""
MCP Monitoring and Alerting Configuration
Comprehensive monitoring system for the MCP ecosystem with Prometheus, Grafana, and custom alerting
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from backend.monitoring.mcp_metrics_collector import (
    MCPMetricsCollector, Alert, AlertSeverity
)

logger = logging.getLogger(__name__)


class MonitoringLevel(str, Enum):
    """Monitoring levels for different environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class AlertChannel(str, Enum):
    """Alert delivery channels"""
    SLACK = "slack"
    EMAIL = "email"
    WEBHOOK = "webhook"
    GITHUB_ISSUE = "github_issue"
    CONSOLE = "console"


@dataclass
class AlertRule:
    """Configuration for an alert rule"""
    rule_id: str
    name: str
    description: str
    metric_name: str
    condition: str  # "greater_than", "less_than", "equals", "not_equals"
    threshold: float
    severity: AlertSeverity
    evaluation_interval_seconds: int = 60
    alert_channels: List[AlertChannel] = None
    enabled: bool = True
    
    # Advanced configuration
    consecutive_failures_required: int = 1
    cooldown_minutes: int = 15
    auto_resolve: bool = True
    custom_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.alert_channels is None:
            self.alert_channels = [AlertChannel.CONSOLE]
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MonitoringTarget:
    """A target system/service to monitor"""
    target_id: str
    name: str
    target_type: str  # "mcp_server", "database", "api", "workflow"
    endpoint: Optional[str] = None
    health_check_interval_seconds: int = 30
    timeout_seconds: int = 10
    enabled: bool = True
    custom_checks: List[str] = None
    
    def __post_init__(self):
        if self.custom_checks is None:
            self.custom_checks = []


@dataclass
class DashboardConfig:
    """Grafana dashboard configuration"""
    dashboard_id: str
    title: str
    description: str
    panels: List[Dict[str, Any]]
    refresh_interval: str = "30s"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = ["sophia-ai", "mcp"]


class MCPMonitoringConfig:
    """
    Comprehensive monitoring configuration for the MCP ecosystem
    """
    
    def __init__(self, monitoring_level: MonitoringLevel = MonitoringLevel.PRODUCTION):
        self.monitoring_level = monitoring_level
        self.metrics_collectors: Dict[str, MCPMetricsCollector] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.monitoring_targets: Dict[str, MonitoringTarget] = {}
        self.dashboard_configs: Dict[str, DashboardConfig] = {}
        self.alert_handlers: Dict[AlertChannel, Callable] = {}
        
        # Monitoring state
        self.monitoring_active = False
        self.alert_states: Dict[str, Dict] = {}
        self.health_checks_running = False
        
        # Initialize default configurations
        self._initialize_default_alert_rules()
        self._initialize_monitoring_targets()
        self._initialize_dashboard_configs()
        self._initialize_alert_handlers()
    
    def _initialize_default_alert_rules(self):
        """Initialize default alert rules for the MCP ecosystem"""
        default_rules = [
            # Server Health Rules
            AlertRule(
                rule_id="server_health_critical",
                name="MCP Server Health Critical",
                description="MCP server health status is critical",
                metric_name="server_health_status",
                condition="equals",
                threshold=0,  # 0 = unhealthy
                severity=AlertSeverity.CRITICAL,
                evaluation_interval_seconds=30,
                alert_channels=[AlertChannel.SLACK, AlertChannel.EMAIL],
                consecutive_failures_required=2,
                cooldown_minutes=5
            ),
            
            # Performance Rules
            AlertRule(
                rule_id="high_response_time",
                name="High Response Time",
                description="Response time exceeds acceptable threshold",
                metric_name="average_response_time_ms",
                condition="greater_than",
                threshold=2000.0,  # 2 seconds
                severity=AlertSeverity.WARNING,
                evaluation_interval_seconds=60,
                alert_channels=[AlertChannel.SLACK],
                consecutive_failures_required=3,
                cooldown_minutes=10
            ),
            
            AlertRule(
                rule_id="high_error_rate",
                name="High Error Rate",
                description="Error rate is above acceptable threshold",
                metric_name="error_rate",
                condition="greater_than",
                threshold=0.05,  # 5%
                severity=AlertSeverity.ERROR,
                evaluation_interval_seconds=60,
                alert_channels=[AlertChannel.SLACK, AlertChannel.WEBHOOK],
                consecutive_failures_required=2,
                cooldown_minutes=15
            ),
            
            # Resource Rules
            AlertRule(
                rule_id="memory_usage_high",
                name="High Memory Usage",
                description="Memory usage is approaching limits",
                metric_name="memory_usage_percent",
                condition="greater_than",
                threshold=85.0,
                severity=AlertSeverity.WARNING,
                evaluation_interval_seconds=120,
                alert_channels=[AlertChannel.SLACK],
                cooldown_minutes=30
            ),
            
            AlertRule(
                rule_id="cpu_usage_high",
                name="High CPU Usage", 
                description="CPU usage is consistently high",
                metric_name="cpu_usage_percent",
                condition="greater_than",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                evaluation_interval_seconds=120,
                alert_channels=[AlertChannel.SLACK],
                consecutive_failures_required=5,
                cooldown_minutes=20
            ),
            
            # Business Logic Rules
            AlertRule(
                rule_id="sync_failure_rate_high",
                name="High Sync Failure Rate",
                description="Data sync failure rate is too high",
                metric_name="sync_failure_rate",
                condition="greater_than",
                threshold=0.10,  # 10%
                severity=AlertSeverity.ERROR,
                evaluation_interval_seconds=300,  # 5 minutes
                alert_channels=[AlertChannel.SLACK, AlertChannel.EMAIL],
                consecutive_failures_required=2,
                cooldown_minutes=30
            ),
            
            AlertRule(
                rule_id="workflow_execution_failure",
                name="Workflow Execution Failure",
                description="Multi-agent workflow execution failed",
                metric_name="workflow_failure_count",
                condition="greater_than",
                threshold=0,
                severity=AlertSeverity.ERROR,
                evaluation_interval_seconds=60,
                alert_channels=[AlertChannel.SLACK, AlertChannel.GITHUB_ISSUE],
                cooldown_minutes=10
            ),
            
            # AI/ML Specific Rules
            AlertRule(
                rule_id="ai_processing_latency_high",
                name="High AI Processing Latency",
                description="AI processing is taking too long",
                metric_name="ai_processing_latency_ms",
                condition="greater_than",
                threshold=10000.0,  # 10 seconds
                severity=AlertSeverity.WARNING,
                evaluation_interval_seconds=120,
                alert_channels=[AlertChannel.SLACK],
                consecutive_failures_required=3,
                cooldown_minutes=15
            ),
            
            AlertRule(
                rule_id="embedding_generation_failure",
                name="Embedding Generation Failure",
                description="High failure rate in embedding generation",
                metric_name="embedding_failure_rate",
                condition="greater_than",
                threshold=0.15,  # 15%
                severity=AlertSeverity.WARNING,
                evaluation_interval_seconds=300,
                alert_channels=[AlertChannel.SLACK],
                cooldown_minutes=20
            )
        ]
        
        # Adjust rules based on monitoring level
        if self.monitoring_level == MonitoringLevel.DEVELOPMENT:
            # More relaxed thresholds for development
            for rule in default_rules:
                if rule.metric_name == "average_response_time_ms":
                    rule.threshold = 5000.0  # 5 seconds
                elif rule.metric_name == "error_rate":
                    rule.threshold = 0.20  # 20%
                rule.alert_channels = [AlertChannel.CONSOLE]
        
        elif self.monitoring_level == MonitoringLevel.STAGING:
            # Moderate thresholds for staging
            for rule in default_rules:
                if rule.metric_name == "average_response_time_ms":
                    rule.threshold = 3000.0  # 3 seconds
                elif rule.metric_name == "error_rate":
                    rule.threshold = 0.10  # 10%
                rule.alert_channels = [AlertChannel.SLACK]
        
        # Store rules
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule
    
    def _initialize_monitoring_targets(self):
        """Initialize monitoring targets for all MCP servers and services"""
        targets = [
            MonitoringTarget(
                target_id="ai_memory_server",
                name="AI Memory MCP Server",
                target_type="mcp_server",
                endpoint="http://localhost:9000/health",
                health_check_interval_seconds=30,
                custom_checks=["memory_embedding_check", "pinecone_connectivity"]
            ),
            
            MonitoringTarget(
                target_id="asana_server",
                name="Asana MCP Server", 
                target_type="mcp_server",
                endpoint="http://localhost:3006/health",
                health_check_interval_seconds=60,
                custom_checks=["asana_api_connectivity"]
            ),
            
            MonitoringTarget(
                target_id="notion_server",
                name="Notion MCP Server",
                target_type="mcp_server",
                endpoint="http://localhost:3007/health",
                health_check_interval_seconds=60,
                custom_checks=["notion_api_connectivity"]
            ),
            
            MonitoringTarget(
                target_id="codacy_server",
                name="Codacy MCP Server",
                target_type="mcp_server",
                endpoint="http://localhost:3008/health",
                health_check_interval_seconds=120,
                custom_checks=["code_analysis_capability"]
            ),
            
            MonitoringTarget(
                target_id="snowflake_admin_server",
                name="Snowflake Admin MCP Server",
                target_type="mcp_server",
                endpoint="http://localhost:3009/health",
                health_check_interval_seconds=60,
                custom_checks=["snowflake_connectivity", "admin_permissions"]
            ),
            
            MonitoringTarget(
                target_id="sync_orchestrator",
                name="Cross-Platform Sync Orchestrator",
                target_type="workflow",
                health_check_interval_seconds=120,
                custom_checks=["sync_queue_health", "dependency_resolution"]
            ),
            
            MonitoringTarget(
                target_id="multi_agent_workflow",
                name="Multi-Agent Workflow System",
                target_type="workflow",
                health_check_interval_seconds=180,
                custom_checks=["agent_availability", "workflow_queue_health"]
            ),
            
            MonitoringTarget(
                target_id="snowflake_cortex",
                name="Snowflake Cortex Service",
                target_type="api",
                health_check_interval_seconds=300,  # 5 minutes
                custom_checks=["cortex_model_availability", "embedding_service"]
            )
        ]
        
        for target in targets:
            self.monitoring_targets[target.target_id] = target
    
    def _initialize_dashboard_configs(self):
        """Initialize Grafana dashboard configurations"""
        
        # Main MCP Ecosystem Dashboard
        main_dashboard = DashboardConfig(
            dashboard_id="mcp_ecosystem_overview",
            title="Sophia AI - MCP Ecosystem Overview",
            description="Comprehensive overview of all MCP servers and services",
            panels=[
                {
                    "id": 1,
                    "title": "Server Health Status",
                    "type": "stat",
                    "targets": [{"expr": "mcp_server_health_status"}],
                    "gridPos": {"h": 6, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "Request Rate",
                    "type": "graph",
                    "targets": [{"expr": "rate(mcp_requests_total[5m])"}],
                    "gridPos": {"h": 6, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "Response Time Distribution",
                    "type": "heatmap",
                    "targets": [{"expr": "mcp_request_duration_seconds_bucket"}],
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 6}
                },
                {
                    "id": 4,
                    "title": "Error Rate by Server",
                    "type": "graph",
                    "targets": [{"expr": "rate(mcp_errors_total[5m]) by (server_name)"}],
                    "gridPos": {"h": 6, "w": 12, "x": 0, "y": 14}
                },
                {
                    "id": 5,
                    "title": "Sync Operations",
                    "type": "graph",
                    "targets": [{"expr": "rate(mcp_sync_operations_total[5m])"}],
                    "gridPos": {"h": 6, "w": 12, "x": 12, "y": 14}
                }
            ],
            tags=["sophia-ai", "mcp", "overview"]
        )
        
        # AI Processing Dashboard
        ai_dashboard = DashboardConfig(
            dashboard_id="mcp_ai_processing",
            title="Sophia AI - AI Processing Metrics",
            description="AI/ML processing metrics across all services",
            panels=[
                {
                    "id": 1,
                    "title": "Embedding Generation Rate",
                    "type": "graph",
                    "targets": [{"expr": "rate(mcp_embeddings_generated_total[5m])"}],
                    "gridPos": {"h": 6, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "AI Processing Latency",
                    "type": "graph",
                    "targets": [{"expr": "mcp_ai_processing_duration_seconds"}],
                    "gridPos": {"h": 6, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "Model Usage Distribution",
                    "type": "pie",
                    "targets": [{"expr": "mcp_ai_model_usage_total by (model_name)"}],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 6}
                },
                {
                    "id": 4,
                    "title": "AI Confidence Scores",
                    "type": "histogram",
                    "targets": [{"expr": "mcp_ai_confidence_score"}],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 6}
                }
            ],
            tags=["sophia-ai", "ai", "ml", "processing"]
        )
        
        # Business Intelligence Dashboard
        bi_dashboard = DashboardConfig(
            dashboard_id="mcp_business_intelligence",
            title="Sophia AI - Business Intelligence Metrics",
            description="Business intelligence and workflow metrics",
            panels=[
                {
                    "id": 1,
                    "title": "Workflow Execution Rate",
                    "type": "graph",
                    "targets": [{"expr": "rate(mcp_workflows_executed_total[5m])"}],
                    "gridPos": {"h": 6, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "Deal Risk Assessments",
                    "type": "stat",
                    "targets": [{"expr": "mcp_deal_assessments_total"}],
                    "gridPos": {"h": 6, "w": 6, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "Data Sync Success Rate",
                    "type": "gauge",
                    "targets": [{"expr": "mcp_sync_success_rate"}],
                    "gridPos": {"h": 6, "w": 6, "x": 18, "y": 0}
                },
                {
                    "id": 4,
                    "title": "Memory Storage Growth",
                    "type": "graph",
                    "targets": [{"expr": "mcp_memories_stored_total"}],
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 6}
                }
            ],
            tags=["sophia-ai", "business", "intelligence"]
        )
        
        self.dashboard_configs["main"] = main_dashboard
        self.dashboard_configs["ai_processing"] = ai_dashboard
        self.dashboard_configs["business_intelligence"] = bi_dashboard
    
    def _initialize_alert_handlers(self):
        """Initialize alert delivery handlers"""
        
        async def console_handler(alert: Alert) -> bool:
            """Simple console alert handler"""
            timestamp = alert.triggered_at.strftime("%Y-%m-%d %H:%M:%S")
            severity_icon = {
                AlertSeverity.INFO: "ℹ️",
                AlertSeverity.WARNING: "⚠️", 
                AlertSeverity.ERROR: "❌",
                AlertSeverity.CRITICAL: "🚨"
            }.get(alert.severity, "📢")
            
            print(f"\n{severity_icon} ALERT [{alert.severity.value.upper()}] - {timestamp}")
            print(f"Server: {alert.server_name}")
            print(f"Metric: {alert.metric_name}")
            print(f"Message: {alert.message}")
            print(f"Current Value: {alert.current_value}")
            print(f"Threshold: {alert.threshold_value}")
            print("-" * 50)
            
            return True
        
        async def slack_handler(alert: Alert) -> bool:
            """Slack webhook alert handler"""
            try:
                # This would integrate with actual Slack webhook
                # For now, log the alert that would be sent
                logger.info(f"SLACK ALERT: {alert.severity.value} - {alert.message}")
                return True
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {e}")
                return False
        
        async def email_handler(alert: Alert) -> bool:
            """Email alert handler"""
            try:
                # This would integrate with actual email service
                logger.info(f"EMAIL ALERT: {alert.severity.value} - {alert.message}")
                return True
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
                return False
        
        async def webhook_handler(alert: Alert) -> bool:
            """Generic webhook alert handler"""
            try:
                # This would send to configured webhook endpoints
                logger.info(f"WEBHOOK ALERT: {alert.severity.value} - {alert.message}")
                return True
            except Exception as e:
                logger.error(f"Failed to send webhook alert: {e}")
                return False
        
        async def github_issue_handler(alert: Alert) -> bool:
            """GitHub issue creation handler for critical alerts"""
            try:
                # This would create GitHub issues for critical problems
                logger.info(f"GITHUB ISSUE ALERT: {alert.severity.value} - {alert.message}")
                return True
            except Exception as e:
                logger.error(f"Failed to create GitHub issue: {e}")
                return False
        
        self.alert_handlers = {
            AlertChannel.CONSOLE: console_handler,
            AlertChannel.SLACK: slack_handler,
            AlertChannel.EMAIL: email_handler,
            AlertChannel.WEBHOOK: webhook_handler,
            AlertChannel.GITHUB_ISSUE: github_issue_handler
        }
    
    async def start_monitoring(self) -> Dict[str, Any]:
        """Start the monitoring system"""
        if self.monitoring_active:
            return {"status": "already_running", "message": "Monitoring is already active"}
        
        logger.info("🚀 Starting MCP monitoring system...")
        
        startup_results = {
            "monitoring_started": False,
            "health_checks_started": False,
            "alert_engine_started": False,
            "collectors_initialized": 0,
            "targets_monitored": 0,
            "errors": []
        }
        
        try:
            # Initialize metrics collectors for each target
            for target_id, target in self.monitoring_targets.items():
                try:
                    collector = MCPMetricsCollector(target.name)
                    self.metrics_collectors[target_id] = collector
                    startup_results["collectors_initialized"] += 1
                except Exception as e:
                    error_msg = f"Failed to initialize collector for {target_id}: {e}"
                    startup_results["errors"].append(error_msg)
                    logger.error(error_msg)
            
            # Start health check loops
            await self._start_health_checks()
            startup_results["health_checks_started"] = True
            
            # Start alert evaluation engine
            await self._start_alert_engine()
            startup_results["alert_engine_started"] = True
            
            self.monitoring_active = True
            startup_results["monitoring_started"] = True
            startup_results["targets_monitored"] = len(self.monitoring_targets)
            
            logger.info("✅ MCP monitoring system started successfully")
            
        except Exception as e:
            error_msg = f"Failed to start monitoring system: {e}"
            startup_results["errors"].append(error_msg)
            logger.error(error_msg)
        
        return startup_results
    
    async def _start_health_checks(self):
        """Start health check loops for all targets"""
        self.health_checks_running = True
        
        # Create health check tasks for each target
        for target_id, target in self.monitoring_targets.items():
            if target.enabled:
                asyncio.create_task(self._health_check_loop(target_id, target))
        
        logger.info(f"Started health checks for {len(self.monitoring_targets)} targets")
    
    async def _health_check_loop(self, target_id: str, target: MonitoringTarget):
        """Health check loop for a specific target"""
        collector = self.metrics_collectors.get(target_id)
        
        while self.health_checks_running and target.enabled:
            try:
                # Perform health check based on target type
                health_status = await self._perform_health_check(target)
                
                # Record health status
                if collector:
                    collector.update_health_status(health_status)
                    
                    # Record response time if available
                    if hasattr(health_status, 'response_time_ms'):
                        collector.record_request(
                            "GET", "/health", "success" if health_status else "failed",
                            health_status.response_time_ms / 1000.0
                        )
                
                # Sleep until next check
                await asyncio.sleep(target.health_check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Health check failed for {target_id}: {e}")
                if collector:
                    collector.update_health_status(False)
                await asyncio.sleep(target.health_check_interval_seconds)
    
    async def _perform_health_check(self, target: MonitoringTarget) -> bool:
        """Perform health check for a specific target"""
        try:
            if target.endpoint:
                # HTTP health check
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        target.endpoint,
                        timeout=aiohttp.ClientTimeout(total=target.timeout_seconds)
                    ) as response:
                        return response.status == 200
            else:
                # Custom health check based on target type
                if target.target_type == "workflow":
                    # Check workflow system health
                    return True  # Placeholder
                elif target.target_type == "api":
                    # Check API availability
                    return True  # Placeholder
                else:
                    return True  # Default healthy
                    
        except Exception as e:
            logger.debug(f"Health check failed for {target.target_id}: {e}")
            return False
    
    async def _start_alert_engine(self):
        """Start the alert evaluation engine"""
        asyncio.create_task(self._alert_evaluation_loop())
        logger.info("Alert evaluation engine started")
    
    async def _alert_evaluation_loop(self):
        """Main alert evaluation loop"""
        while self.monitoring_active:
            try:
                # Evaluate all alert rules
                for rule_id, rule in self.alert_rules.items():
                    if rule.enabled:
                        await self._evaluate_alert_rule(rule)
                
                # Sleep before next evaluation cycle
                await asyncio.sleep(30)  # Evaluate every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in alert evaluation loop: {e}")
                await asyncio.sleep(60)  # Sleep longer on error
    
    async def _evaluate_alert_rule(self, rule: AlertRule):
        """Evaluate a specific alert rule"""
        try:
            # Get current metric value
            current_value = await self._get_metric_value(rule.metric_name)
            
            if current_value is None:
                return  # Metric not available
            
            # Check if alert condition is met
            alert_triggered = self._check_alert_condition(
                current_value, rule.condition, rule.threshold
            )
            
            # Get or initialize alert state
            if rule.rule_id not in self.alert_states:
                self.alert_states[rule.rule_id] = {
                    "consecutive_failures": 0,
                    "last_alert_time": None,
                    "currently_alerting": False
                }
            
            alert_state = self.alert_states[rule.rule_id]
            
            if alert_triggered:
                alert_state["consecutive_failures"] += 1
                
                # Check if we should trigger alert
                should_alert = (
                    alert_state["consecutive_failures"] >= rule.consecutive_failures_required and
                    not alert_state["currently_alerting"] and
                    self._check_cooldown(alert_state["last_alert_time"], rule.cooldown_minutes)
                )
                
                if should_alert:
                    await self._trigger_alert(rule, current_value)
                    alert_state["currently_alerting"] = True
                    alert_state["last_alert_time"] = datetime.now()
            
            else:
                # Reset failure count and resolve alert if auto-resolve enabled
                alert_state["consecutive_failures"] = 0
                if alert_state["currently_alerting"] and rule.auto_resolve:
                    await self._resolve_alert(rule, current_value)
                    alert_state["currently_alerting"] = False
                    
        except Exception as e:
            logger.error(f"Error evaluating alert rule {rule.rule_id}: {e}")
    
    async def _get_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value for a metric across all collectors"""
        try:
            # Aggregate metric value from all collectors
            total_value = 0.0
            collector_count = 0
            
            for collector in self.metrics_collectors.values():
                metrics = collector.get_metrics_summary()
                if metric_name in metrics:
                    total_value += metrics[metric_name]
                    collector_count += 1
            
            if collector_count > 0:
                return total_value / collector_count  # Average value
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting metric value for {metric_name}: {e}")
            return None
    
    def _check_alert_condition(self, current_value: float, condition: str, threshold: float) -> bool:
        """Check if alert condition is met"""
        if condition == "greater_than":
            return current_value > threshold
        elif condition == "less_than":
            return current_value < threshold
        elif condition == "equals":
            return abs(current_value - threshold) < 0.001  # Float comparison
        elif condition == "not_equals":
            return abs(current_value - threshold) >= 0.001
        else:
            logger.warning(f"Unknown alert condition: {condition}")
            return False
    
    def _check_cooldown(self, last_alert_time: Optional[datetime], cooldown_minutes: int) -> bool:
        """Check if cooldown period has passed"""
        if last_alert_time is None:
            return True
        
        cooldown_period = timedelta(minutes=cooldown_minutes)
        return datetime.now() - last_alert_time >= cooldown_period
    
    async def _trigger_alert(self, rule: AlertRule, current_value: float):
        """Trigger an alert"""
        try:
            # Create alert object
            alert = Alert(
                alert_id=f"{rule.rule_id}_{int(datetime.now().timestamp())}",
                severity=rule.severity,
                message=rule.custom_message or f"{rule.name}: {rule.description}",
                metric_name=rule.metric_name,
                current_value=current_value,
                threshold_value=rule.threshold,
                triggered_at=datetime.now(),
                server_name="mcp_monitoring"
            )
            
            # Send alert through configured channels
            for channel in rule.alert_channels:
                if channel in self.alert_handlers:
                    try:
                        success = await self.alert_handlers[channel](alert)
                        if success:
                            logger.info(f"Alert sent via {channel.value}: {rule.name}")
                        else:
                            logger.warning(f"Failed to send alert via {channel.value}")
                    except Exception as e:
                        logger.error(f"Error sending alert via {channel.value}: {e}")
            
        except Exception as e:
            logger.error(f"Error triggering alert for rule {rule.rule_id}: {e}")
    
    async def _resolve_alert(self, rule: AlertRule, current_value: float):
        """Resolve an alert"""
        logger.info(f"Alert resolved: {rule.name} (current value: {current_value})")
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        logger.info("🛑 Stopping MCP monitoring system...")
        
        self.monitoring_active = False
        self.health_checks_running = False
        
        # Clean up collectors
        for collector in self.metrics_collectors.values():
            # Perform any cleanup if needed
            pass
        
        logger.info("MCP monitoring system stopped")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "monitoring_active": self.monitoring_active,
            "monitoring_level": self.monitoring_level.value,
            "health_checks_running": self.health_checks_running,
            "active_collectors": len(self.metrics_collectors),
            "monitored_targets": len(self.monitoring_targets),
            "configured_alert_rules": len(self.alert_rules),
            "enabled_alert_rules": len([r for r in self.alert_rules.values() if r.enabled]),
            "dashboard_configs": len(self.dashboard_configs),
            "alert_states": {
                rule_id: {
                    "consecutive_failures": state["consecutive_failures"],
                    "currently_alerting": state["currently_alerting"],
                    "last_alert_time": state["last_alert_time"].isoformat() if state["last_alert_time"] else None
                }
                for rule_id, state in self.alert_states.items()
            }
        }
    
    def add_custom_alert_rule(self, rule: AlertRule):
        """Add a custom alert rule"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added custom alert rule: {rule.name}")
    
    def get_grafana_dashboard_json(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Get Grafana dashboard JSON configuration"""
        if dashboard_id not in self.dashboard_configs:
            return None
        
        config = self.dashboard_configs[dashboard_id]
        
        # Generate Grafana dashboard JSON
        dashboard_json = {
            "dashboard": {
                "id": None,
                "title": config.title,
                "description": config.description,
                "tags": config.tags,
                "refresh": config.refresh_interval,
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "panels": config.panels
            },
            "folderId": 0,
            "overwrite": True
        }
        
        return dashboard_json


# Global monitoring configuration instance
mcp_monitoring_config = MCPMonitoringConfig()


async def initialize_mcp_monitoring(
    monitoring_level: MonitoringLevel = MonitoringLevel.PRODUCTION
) -> Dict[str, Any]:
    """Initialize the global MCP monitoring system"""
    global mcp_monitoring_config
    mcp_monitoring_config = MCPMonitoringConfig(monitoring_level)
    return await mcp_monitoring_config.start_monitoring()


async def stop_mcp_monitoring():
    """Stop the global MCP monitoring system"""
    await mcp_monitoring_config.stop_monitoring()


def get_mcp_monitoring_status() -> Dict[str, Any]:
    """Get the status of the MCP monitoring system"""
    return mcp_monitoring_config.get_monitoring_status()


if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize monitoring
        result = await initialize_mcp_monitoring(MonitoringLevel.DEVELOPMENT)
        print(f"Monitoring initialization result: {result}")
        
        # Let it run for a while
        await asyncio.sleep(30)
        
        # Check status
        status = get_mcp_monitoring_status()
        print(f"Monitoring status: {status}")
        
        # Stop
        await stop_mcp_monitoring()
    
    asyncio.run(main()) 