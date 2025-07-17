"""
Self-Healing Infrastructure System

Orchestrates all autonomous agents to provide comprehensive infrastructure monitoring,
anomaly detection, and automatic remediation with ML-based learning capabilities.
"""

import asyncio
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from prometheus_client import Counter, Gauge, Histogram, Summary
from backend.core.auto_esc_config import get_config_value

# Import our autonomous agents
from ..infrastructure.lambda_labs_monitor import LambdaLabsMonitor
from ..infrastructure.lambda_labs_autonomous import LambdaLabsAutonomousAgent
from ..infrastructure.qdrant_optimizer import QdrantOptimizer
from ..monitoring.prometheus_exporter import PrometheusExporter
from ..infrastructure.base_infrastructure_agent import BaseInfrastructureAgent, AlertSeverity

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types of services monitored"""
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    GPU = "gpu"
    CONTAINER = "container"
    NETWORK = "network"


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class HealingActionType(Enum):
    """Types of healing actions"""
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    CLEAR_CACHE = "clear_cache"
    OPTIMIZE_DATABASE = "optimize_database"
    REALLOCATE_RESOURCES = "reallocate_resources"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    INCREASE_LIMITS = "increase_limits"
    KILL_QUERIES = "kill_queries"
    ROTATE_LOGS = "rotate_logs"


@dataclass
class ServiceHealth:
    """Health status of a service"""
    service_name: str
    service_type: ServiceType
    status: HealthStatus
    metrics: Dict[str, float]
    last_check: datetime
    error_count: int = 0
    response_time: Optional[float] = None
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealingAction:
    """Represents a healing action to be taken"""
    action_id: str
    action_type: HealingActionType
    target_service: str
    reason: str
    severity: AlertSeverity
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    executed_at: Optional[datetime] = None
    success: Optional[bool] = None
    result: Optional[str] = None
    rollback_data: Optional[Dict[str, Any]] = None


@dataclass
class AnomalyPattern:
    """Detected anomaly pattern"""
    pattern_id: str
    service: str
    metric_name: str
    anomaly_score: float
    timestamp: datetime
    context: Dict[str, Any]


class SelfHealingSystem:
    """
    Comprehensive self-healing infrastructure system that:
    - Monitors all infrastructure components
    - Detects anomalies using ML
    - Coordinates healing actions across agents
    - Learns from past actions
    - Escalates to humans when needed
    """
    
    def __init__(self):
        """Initialize the self-healing system"""
        self.name = "self_healing_orchestrator"
        self.monitoring_interval = 30  # seconds
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Configuration
        self.anomaly_threshold = float(get_config_value("ANOMALY_THRESHOLD", "0.7"))
        self.max_auto_actions_per_hour = int(get_config_value("MAX_AUTO_ACTIONS_PER_HOUR", "20"))
        self.cost_threshold_usd = float(get_config_value("HEALING_COST_THRESHOLD_USD", "500"))
        self.human_escalation_threshold = int(get_config_value("HUMAN_ESCALATION_THRESHOLD", "3"))
        
        # State tracking
        self.service_health: Dict[str, ServiceHealth] = {}
        self.healing_history: List[HealingAction] = []
        self.anomaly_patterns: List[AnomalyPattern] = []
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.action_effectiveness: Dict[str, List[float]] = defaultdict(list)
        
        # ML components
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_ml_trained = False
        
        # Agents
        self.agents: Dict[str, BaseInfrastructureAgent] = {}
        self.mcp_clients: Dict[str, Any] = {}
        
        # Metrics
        self._init_metrics()
        
        logger.info("Self-healing system initialized")
    
    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        self.health_checks_total = Counter(
            'self_healing_health_checks_total',
            'Total health checks performed',
            ['service_type']
        )
        self.anomalies_detected = Counter(
            'self_healing_anomalies_detected_total',
            'Total anomalies detected',
            ['service', 'severity']
        )
        self.healing_actions_total = Counter(
            'self_healing_actions_total',
            'Total healing actions taken',
            ['action_type', 'status']
        )
        self.healing_effectiveness = Gauge(
            'self_healing_effectiveness_ratio',
            'Effectiveness ratio of healing actions',
            ['action_type']
        )
        self.escalations_total = Counter(
            'self_healing_escalations_total',
            'Total escalations to humans',
            ['reason']
        )
        self.services_health_status = Gauge(
            'self_healing_services_health',
            'Current health status of services (0=critical, 1=unhealthy, 2=degraded, 3=healthy)',
            ['service_name', 'service_type']
        )
    
    async def start(self):
        """Start the self-healing system"""
        try:
            logger.info("Starting self-healing system...")
            
            # Initialize agents
            await self._initialize_agents()
            
            # Initialize MCP clients
            await self._initialize_mcp_clients()
            
            # Start monitoring loop
            self._running = True
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("Self-healing system started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start self-healing system: {e}")
            raise
    
    async def stop(self):
        """Stop the self-healing system"""
        logger.info("Stopping self-healing system...")
        self._running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Stop all agents
        for agent in self.agents.values():
            await agent.stop()
        
        logger.info("Self-healing system stopped")
    
    async def _initialize_agents(self):
        """Initialize all monitoring agents"""
        try:
            # Lambda Labs monitoring
            lambda_monitor = LambdaLabsMonitor()
            await lambda_monitor.start()
            self.agents['lambda_monitor'] = lambda_monitor
            
            # Lambda Labs autonomous management
            lambda_auto = LambdaLabsAutonomousAgent(dry_run=False)
            await lambda_auto.start()
            self.agents['lambda_autonomous'] = lambda_auto
            
            # Qdrant optimizer
            qdrant_opt = QdrantOptimizer()
            await qdrant_opt.start()
            self.agents['qdrant_optimizer'] = qdrant_opt
            
            # Prometheus exporter
            prom_exporter = PrometheusExporter()
            await prom_exporter.start()
            self.agents['prometheus_exporter'] = prom_exporter
            
            logger.info(f"Initialized {len(self.agents)} monitoring agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    async def _initialize_mcp_clients(self):
        """Initialize MCP server clients"""
        # TODO: Initialize actual MCP clients when available
        logger.info("MCP client initialization pending")
    
    async def _monitoring_loop(self):
        """Main monitoring and healing loop"""
        while self._running:
            try:
                # Perform health checks
                await self._perform_health_checks()
                
                # Detect anomalies
                anomalies = await self._detect_anomalies()
                
                # Evaluate healing actions
                if anomalies:
                    actions = await self._evaluate_healing_actions(anomalies)
                    
                    # Execute approved actions
                    for action in actions:
                        if await self._should_execute_action(action):
                            await self._execute_healing_action(action)
                
                # Update ML model periodically
                if len(self.metrics_history) > 100 and not self.is_ml_trained:
                    await self._train_anomaly_detector()
                
                # Clean up old data
                await self._cleanup_old_data()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            await asyncio.sleep(self.monitoring_interval)
    
    async def _perform_health_checks(self):
        """Perform health checks on all services"""
        checks = [
            self._check_api_health(),
            self._check_database_health(),
            self._check_cache_health(),
            self._check_gpu_health(),
            self._check_container_health(),
            self._check_network_health()
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Health check failed: {result}")
            elif result:
                self.service_health[result.service_name] = result
                
                # Update metrics
                self.health_checks_total.labels(service_type=result.service_type.value).inc()
                
                # Map health status to numeric value for Prometheus
                status_map = {
                    HealthStatus.HEALTHY: 3,
                    HealthStatus.DEGRADED: 2,
                    HealthStatus.UNHEALTHY: 1,
                    HealthStatus.CRITICAL: 0
                }
                self.services_health_status.labels(
                    service_name=result.service_name,
                    service_type=result.service_type.value
                ).set(status_map.get(result.status, 0))
    
    async def _check_api_health(self) -> Optional[ServiceHealth]:
        """Check API service health"""
        try:
            # TODO: Implement actual API health check
            # For now, return simulated data
            import random
            
            response_time = random.uniform(50, 200)
            error_rate = random.uniform(0, 5)
            
            status = HealthStatus.HEALTHY
            if response_time > 150 or error_rate > 3:
                status = HealthStatus.DEGRADED
            if response_time > 300 or error_rate > 10:
                status = HealthStatus.UNHEALTHY
            
            health = ServiceHealth(
                service_name="sophia-api",
                service_type=ServiceType.API,
                status=status,
                metrics={
                    "response_time_ms": response_time,
                    "error_rate_percent": error_rate,
                    "requests_per_second": random.uniform(10, 100)
                },
                last_check=datetime.now(timezone.utc),
                response_time=response_time
            )
            
            # Store metrics for ML
            self._store_metrics("api", health.metrics)
            
            return health
            
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return None
    
    async def _check_database_health(self) -> Optional[ServiceHealth]:
        """Check database health"""
        try:
            # TODO: Implement actual database health check
            import random
            
            query_time = random.uniform(5, 50)
            connections = random.randint(10, 100)
            lock_waits = random.randint(0, 10)
            
            status = HealthStatus.HEALTHY
            if query_time > 30 or connections > 80:
                status = HealthStatus.DEGRADED
            if query_time > 100 or connections > 95 or lock_waits > 5:
                status = HealthStatus.UNHEALTHY
            
            health = ServiceHealth(
                service_name="postgres-main",
                service_type=ServiceType.DATABASE,
                status=status,
                metrics={
                    "avg_query_time_ms": query_time,
                    "active_connections": connections,
                    "lock_waits": lock_waits,
                    "replication_lag_mb": random.uniform(0, 100)
                },
                last_check=datetime.now(timezone.utc)
            )
            
            self._store_metrics("database", health.metrics)
            return health
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return None
    
    async def _check_cache_health(self) -> Optional[ServiceHealth]:
        """Check Redis cache health"""
        try:
            # TODO: Implement actual Redis health check
            import random
            
            memory_usage = random.uniform(20, 90)
            hit_rate = random.uniform(70, 99)
            evictions = random.randint(0, 1000)
            
            status = HealthStatus.HEALTHY
            if memory_usage > 80 or hit_rate < 80:
                status = HealthStatus.DEGRADED
            if memory_usage > 95 or hit_rate < 60:
                status = HealthStatus.UNHEALTHY
            
            health = ServiceHealth(
                service_name="redis-cache",
                service_type=ServiceType.CACHE,
                status=status,
                metrics={
                    "memory_usage_percent": memory_usage,
                    "hit_rate_percent": hit_rate,
                    "evictions_per_minute": evictions,
                    "connected_clients": random.randint(5, 50)
                },
                last_check=datetime.now(timezone.utc)
            )
            
            self._store_metrics("cache", health.metrics)
            return health
            
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return None
    
    async def _check_gpu_health(self) -> Optional[ServiceHealth]:
        """Check GPU health from Lambda Labs agents"""
        try:
            # Get data from Lambda Labs agents
            if 'lambda_monitor' in self.agents:
                agent_status = self.agents['lambda_monitor'].get_status()
                
                # Aggregate GPU metrics
                gpu_util = 0
                gpu_temp = 0
                gpu_count = 0
                
                # TODO: Get actual metrics from agent
                import random
                gpu_util = random.uniform(30, 90)
                gpu_temp = random.uniform(50, 85)
                gpu_count = 4
                
                status = HealthStatus.HEALTHY
                if gpu_util > 80 or gpu_temp > 75:
                    status = HealthStatus.DEGRADED
                if gpu_util > 95 or gpu_temp > 85:
                    status = HealthStatus.UNHEALTHY
                
                health = ServiceHealth(
                    service_name="lambda-labs-gpu",
                    service_type=ServiceType.GPU,
                    status=status,
                    metrics={
                        "avg_gpu_utilization": gpu_util,
                        "avg_gpu_temperature": gpu_temp,
                        "active_gpus": gpu_count,
                        "gpu_memory_usage_percent": random.uniform(20, 80)
                    },
                    last_check=datetime.now(timezone.utc)
                )
                
                self._store_metrics("gpu", health.metrics)
                return health
            
        except Exception as e:
            logger.error(f"GPU health check failed: {e}")
            return None
    
    async def _check_container_health(self) -> Optional[ServiceHealth]:
        """Check Docker container health"""
        try:
            # TODO: Implement actual Docker health check
            import random
            
            running_containers = random.randint(5, 20)
            cpu_usage = random.uniform(20, 80)
            memory_usage = random.uniform(30, 85)
            
            status = HealthStatus.HEALTHY
            if cpu_usage > 70 or memory_usage > 80:
                status = HealthStatus.DEGRADED
            if cpu_usage > 90 or memory_usage > 95:
                status = HealthStatus.UNHEALTHY
            
            health = ServiceHealth(
                service_name="docker-containers",
                service_type=ServiceType.CONTAINER,
                status=status,
                metrics={
                    "running_containers": running_containers,
                    "avg_cpu_percent": cpu_usage,
                    "avg_memory_percent": memory_usage,
                    "failed_containers": random.randint(0, 3)
                },
                last_check=datetime.now(timezone.utc)
            )
            
            self._store_metrics("container", health.metrics)
            return health
            
        except Exception as e:
            logger.error(f"Container health check failed: {e}")
            return None
    
    async def _check_network_health(self) -> Optional[ServiceHealth]:
        """Check network health"""
        try:
            # TODO: Implement actual network health check
            import random
            
            latency = random.uniform(5, 50)
            packet_loss = random.uniform(0, 2)
            bandwidth_usage = random.uniform(10, 80)
            
            status = HealthStatus.HEALTHY
            if latency > 30 or packet_loss > 1:
                status = HealthStatus.DEGRADED
            if latency > 100 or packet_loss > 5:
                status = HealthStatus.UNHEALTHY
            
            health = ServiceHealth(
                service_name="network-main",
                service_type=ServiceType.NETWORK,
                status=status,
                metrics={
                    "latency_ms": latency,
                    "packet_loss_percent": packet_loss,
                    "bandwidth_usage_percent": bandwidth_usage,
                    "active_connections": random.randint(100, 1000)
                },
                last_check=datetime.now(timezone.utc)
            )
            
            self._store_metrics("network", health.metrics)
            return health
            
        except Exception as e:
            logger.error(f"Network health check failed: {e}")
            return None
    
    def _store_metrics(self, service: str, metrics: Dict[str, float]):
        """Store metrics for ML training"""
        timestamp = datetime.now(timezone.utc)
        for metric_name, value in metrics.items():
            key = f"{service}.{metric_name}"
            self.metrics_history[key].append((timestamp, value))
    
    async def _detect_anomalies(self) -> List[AnomalyPattern]:
        """Detect anomalies using ML"""
        anomalies = []
        
        if not self.is_ml_trained:
            # Use simple threshold-based detection until ML is trained
            for service_name, health in self.service_health.items():
                if health.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                    anomaly = AnomalyPattern(
                        pattern_id=f"threshold_{service_name}_{datetime.now().timestamp()}",
                        service=service_name,
                        metric_name="health_status",
                        anomaly_score=0.9 if health.status == HealthStatus.CRITICAL else 0.7,
                        timestamp=datetime.now(timezone.utc),
                        context={"health": health}
                    )
                    anomalies.append(anomaly)
                    
                    self.anomalies_detected.labels(
                        service=service_name,
                        severity=AlertSeverity.CRITICAL.value if health.status == HealthStatus.CRITICAL else AlertSeverity.WARNING.value
                    ).inc()
        else:
            # Use ML-based anomaly detection
            anomalies.extend(await self._ml_detect_anomalies())
        
        self.anomaly_patterns.extend(anomalies)
        return anomalies
    
    async def _ml_detect_anomalies(self) -> List[AnomalyPattern]:
        """Detect anomalies using trained ML model"""
        anomalies = []
        
        try:
            # Prepare current metrics for ML
            current_metrics = []
            metric_names = []
            
            for key, values in self.metrics_history.items():
                if values:
                    # Get latest value
                    _, value = values[-1]
                    current_metrics.append(value)
                    metric_names.append(key)
            
            if current_metrics:
                # Scale and predict
                X = np.array(current_metrics).reshape(1, -1)
                X_scaled = self.scaler.transform(X)
                
                # Get anomaly scores
                scores = self.anomaly_detector.score_samples(X_scaled)
                predictions = self.anomaly_detector.predict(X_scaled)
                
                # Create anomaly patterns for detected anomalies
                for i, (score, pred) in enumerate(zip(scores[0], predictions[0])):
                    if pred == -1:  # Anomaly detected
                        service = metric_names[i].split('.')[0]
                        anomaly = AnomalyPattern(
                            pattern_id=f"ml_{service}_{datetime.now().timestamp()}",
                            service=service,
                            metric_name=metric_names[i],
                            anomaly_score=abs(score),
                            timestamp=datetime.now(timezone.utc),
                            context={"metric_value": current_metrics[i]}
                        )
                        anomalies.append(anomaly)
        
        except Exception as e:
            logger.error(f"ML anomaly detection failed: {e}")
        
        return anomalies
    
    async def _train_anomaly_detector(self):
        """Train the ML anomaly detector on historical data"""
        try:
            # Prepare training data
            training_data = []
            
            # Get aligned timestamps
            all_timestamps = set()
            for values in self.metrics_history.values():
                for timestamp, _ in values:
                    all_timestamps.add(timestamp)
            
            # Build feature matrix
            for timestamp in sorted(all_timestamps):
                row = []
                for key in sorted(self.metrics_history.keys()):
                    # Find value at timestamp
                    value = None
                    for ts, val in self.metrics_history[key]:
                        if ts == timestamp:
                            value = val
                            break
                    
                    if value is not None:
                        row.append(value)
                    else:
                        # Use interpolation or last known value
                        if self.metrics_history[key]:
                            # Use last known value
                            _, value = self.metrics_history[key][-1]
                            row.append(value)
                        else:
                            row.append(0)
                
                if row:
                    training_data.append(row)
            
            if len(training_data) > 50:
                X = np.array(training_data)
                
                # Scale data
                X_scaled = self.scaler.fit_transform(X)
                
                # Train anomaly detector
                self.anomaly_detector.fit(X_scaled)
                self.is_ml_trained = True
                
                logger.info(f"Trained anomaly detector on {len(training_data)} samples")
        
        except Exception as e:
            logger.error(f"Failed to train anomaly detector: {e}")
    
    async def _evaluate_healing_actions(self, anomalies: List[AnomalyPattern]) -> List[HealingAction]:
        """Evaluate what healing actions to take based on anomalies"""
        actions = []
        
        for anomaly in anomalies:
            service_health = self.service_health.get(anomaly.service)
            if not service_health:
                continue
            
            # Determine action based on service type and issue
            if service_health.service_type == ServiceType.API:
                if service_health.metrics.get("error_rate_percent", 0) > 10:
                    action = HealingAction(
                        action_id=f"heal_api_{datetime.now().timestamp()}",
                        action_type=HealingActionType.RESTART_SERVICE,
                        target_service=anomaly.service,
                        reason=f"High error rate: {service_health.metrics.get('error_rate_percent', 0):.1f}%",
                        severity=AlertSeverity.WARNING
                    )
                    actions.append(action)
                
                elif service_health.metrics.get("response_time_ms", 0) > 300:
                    action = HealingAction(
                        action_id=f"heal_api_scale_{datetime.now().timestamp()}",
                        action_type=HealingActionType.SCALE_UP,
                        target_service=anomaly.service,
                        reason=f"High response time: {service_health.metrics.get('response_time_ms', 0):.0f}ms",
                        severity=AlertSeverity.WARNING
                    )
                    actions.append(action)
            
            elif service_health.service_type == ServiceType.DATABASE:
                if service_health.metrics.get("lock_waits", 0) > 5:
                    action = HealingAction(
                        action_id=f"heal_db_locks_{datetime.now().timestamp()}",
                        action_type=HealingActionType.KILL_QUERIES,
                        target_service=anomaly.service,
                        reason=f"High lock waits: {service_health.metrics.get('lock_waits', 0)}",
                        severity=AlertSeverity.ERROR
                    )
                    actions.append(action)
                
                elif service_health.metrics.get("avg_query_time_ms", 0) > 100:
                    action = HealingAction(
                        action_id=f"heal_db_optimize_{datetime.now().timestamp()}",
                        action_type=HealingActionType.OPTIMIZE_DATABASE,
                        target_service=anomaly.service,
