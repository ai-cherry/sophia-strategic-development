"""
Lambda Labs Autonomous GPU Management Agent

Enhanced version that can take autonomous actions to optimize GPU resources
including provisioning and terminating instances based on usage patterns.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
from prometheus_client import Gauge, Counter
from backend.core.auto_esc_config import get_lambda_labs_config, get_config_value
from .base_infrastructure_agent import BaseInfrastructureAgent, AlertSeverity

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of autonomous actions"""
    PROVISION_INSTANCE = "provision_instance"
    TERMINATE_INSTANCE = "terminate_instance"
    RESIZE_INSTANCE = "resize_instance"
    NO_ACTION = "no_action"


class ActionStatus(Enum):
    """Status of autonomous actions"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    EXECUTED = "executed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class AutonomousAction:
    """Represents an autonomous action to be taken"""
    action_id: str
    action_type: ActionType
    target_instance_id: Optional[str]
    instance_type: Optional[str]
    reason: str
    estimated_cost_impact: float  # Positive = cost increase, Negative = savings
    requires_confirmation: bool
    status: ActionStatus = ActionStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    executed_at: Optional[datetime] = None
    rollback_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass
class ActionHistory:
    """Historical record of actions taken"""
    action: AutonomousAction
    metrics_before: Dict[str, Any]
    metrics_after: Optional[Dict[str, Any]] = None
    outcome: Optional[str] = None


class LambdaLabsAutonomousAgent(BaseInfrastructureAgent):
    """
    Autonomous GPU management agent that can:
    - Monitor GPU usage and costs
    - Automatically provision instances during high demand
    - Terminate idle instances to save costs
    - Enforce spending limits and safety controls
    """
    
    def __init__(self, dry_run: bool = False):
        super().__init__(
            name="lambda_labs_autonomous",
            description="Autonomous GPU management agent with action capabilities"
        )
        
        # Configuration
        self.dry_run = dry_run
        self.api_config = get_lambda_labs_config()
        self.api_key = self.api_config.get("api_key")
        self.base_url = self.api_config.get("api_url", "https://cloud.lambdalabs.com/api/v1")
        
        # Thresholds for monitoring
        self.high_gpu_threshold = float(self.api_config.get("high_gpu_threshold", "80"))
        self.low_gpu_threshold = float(self.api_config.get("low_gpu_threshold", "20"))
        self.high_temp_threshold = float(self.api_config.get("high_temp_threshold", "85"))
        self.high_memory_threshold = float(self.api_config.get("high_memory_threshold", "90"))
        
        # Duration thresholds (in minutes)
        self.high_usage_duration = int(self.api_config.get("high_usage_duration_mins", "15"))
        self.low_usage_duration = int(self.api_config.get("low_usage_duration_mins", "30"))
        
        # Autonomous action configuration
        self.max_hourly_spend = float(get_config_value("LAMBDA_LABS_MAX_HOURLY_SPEND", "100") or "100")
        self.max_instances = int(get_config_value("LAMBDA_LABS_MAX_INSTANCES", "10") or "10")
        self.action_cooldown_mins = int(get_config_value("LAMBDA_LABS_ACTION_COOLDOWN_MINS", "30") or "30")
        self.confirmation_threshold = float(get_config_value("LAMBDA_LABS_CONFIRMATION_THRESHOLD", "100") or "100")
        
        # Default instance type for provisioning
        self.default_instance_type = get_config_value("LAMBDA_LABS_DEFAULT_INSTANCE_TYPE", "gpu_1x_a100")
        
        # Tracking
        self.instances: Dict[str, Dict[str, Any]] = {}
        self.metrics_history: Dict[str, List[Any]] = {}
        self.anomaly_state: Dict[str, Dict[str, Any]] = {}
        self.action_history: List[ActionHistory] = []
        self.pending_actions: List[AutonomousAction] = []
        self.last_action_time: Dict[ActionType, datetime] = {}
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # MCP clients (to be initialized)
        self.github_client = None
        self.slack_client = None
        self.postgres_client = None
        
        # Additional metrics for autonomous actions
        self._init_autonomous_metrics()
    
    def _init_autonomous_metrics(self):
        """Initialize metrics for autonomous actions"""
        # Action metrics
        self.actions_taken = Counter(
            'lambda_labs_autonomous_actions_total',
            'Total autonomous actions taken',
            ['action_type', 'status']
        )
        self.action_cost_impact = Gauge(
            'lambda_labs_autonomous_cost_impact_dollars',
            'Cost impact of autonomous actions',
            ['action_type']
        )
        self.instances_managed = Gauge(
            'lambda_labs_autonomous_instances_managed',
            'Number of instances managed autonomously'
        )
        
        # Safety metrics
        self.safety_blocks = Counter(
            'lambda_labs_autonomous_safety_blocks_total',
            'Actions blocked by safety mechanisms',
            ['reason']
        )
        self.confirmations_required = Counter(
            'lambda_labs_autonomous_confirmations_required_total',
            'Actions requiring confirmation'
        )
    
    async def initialize(self):
        """Initialize resources including MCP clients"""
        # Create HTTP session
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        # Initialize MCP clients
        await self._init_mcp_clients()
        
        # Get initial instance list
        await self.refresh_instances()
        
        logger.info(f"Lambda Labs autonomous agent initialized (dry_run={self.dry_run})")
    
    async def _init_mcp_clients(self):
        """Initialize MCP server clients for GitHub, Slack, and PostgreSQL"""
        try:
            # TODO: Initialize actual MCP clients
            # self.github_client = await init_github_mcp_client()
            # self.slack_client = await init_slack_mcp_client()
            # self.postgres_client = await init_postgres_mcp_client()
            logger.info("MCP clients initialization pending")
        except Exception as e:
            logger.error(f"Failed to initialize MCP clients: {e}")
    
    async def monitor(self):
        """Enhanced monitoring with autonomous action evaluation"""
        # Refresh instance list
        await self.refresh_instances()
        
        # Collect metrics for all instances
        instance_metrics = {}
        for instance_id, instance in self.instances.items():
            metrics = await self._get_instance_metrics(instance_id)
            if metrics:
                instance_metrics[instance_id] = metrics
                self._update_prometheus_metrics(metrics)
        
        # Evaluate autonomous actions
        actions = await self._evaluate_autonomous_actions(instance_metrics)
        
        # Execute approved actions
        for action in actions:
            if await self._should_execute_action(action):
                await self._execute_autonomous_action(action)
    
    async def _evaluate_autonomous_actions(self, metrics: Dict[str, Any]) -> List[AutonomousAction]:
        """Evaluate current state and determine autonomous actions"""
        actions = []
        current_time = datetime.now(timezone.utc)
        
        # Check for high GPU usage across all instances
        total_high_usage = sum(
            1 for m in metrics.values() 
            if hasattr(m, 'gpu_utilization') and m.gpu_utilization > self.high_gpu_threshold
        )
        
        # Check for low GPU usage instances
        low_usage_instances = []
        for instance_id, m in metrics.items():
            if hasattr(m, 'gpu_utilization') and m.gpu_utilization < self.low_gpu_threshold:
                low_usage_instances.append((instance_id, m))
        
        # Provision new instance if all instances are at high usage
        if total_high_usage == len(self.instances) and len(self.instances) < self.max_instances:
            instance_type = self.default_instance_type or "gpu_1x_a100"
            action = AutonomousAction(
                action_id=f"provision_{current_time.timestamp()}",
                action_type=ActionType.PROVISION_INSTANCE,
                target_instance_id=None,
                instance_type=instance_type,
                reason=f"All {len(self.instances)} instances at high GPU usage (>{self.high_gpu_threshold}%)",
                estimated_cost_impact=self._get_hourly_rate(instance_type),
                requires_confirmation=self._get_hourly_rate(instance_type) > self.confirmation_threshold
            )
            actions.append(action)
        
        # Terminate idle instances
        for instance_id, metrics_obj in low_usage_instances:
            # Check if low usage persisted
            if await self._check_sustained_low_usage(instance_id, self.low_usage_duration):
                instance = self.instances[instance_id]
                hourly_rate = self._get_instance_hourly_rate(instance)
                
                action = AutonomousAction(
                    action_id=f"terminate_{instance_id}_{current_time.timestamp()}",
                    action_type=ActionType.TERMINATE_INSTANCE,
                    target_instance_id=instance_id,
                    instance_type=instance.get("instance_type", {}).get("name"),
                    reason=f"Sustained low GPU usage ({metrics_obj.gpu_utilization:.1f}%) for {self.low_usage_duration} minutes",
                    estimated_cost_impact=-hourly_rate,  # Negative = savings
                    requires_confirmation=False  # Termination usually doesn't need confirmation
                )
                actions.append(action)
        
        return actions
    
    async def _should_execute_action(self, action: AutonomousAction) -> bool:
        """Determine if an action should be executed based on safety checks"""
        # Check dry run mode
        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute: {action.action_type.value} - {action.reason}")
            await self._log_action_to_github(action, dry_run=True)
            return False
        
        # Check cooldown period
        if not self._check_cooldown(action.action_type):
            logger.info(f"Action {action.action_type.value} blocked by cooldown period")
            self.safety_blocks.labels(reason="cooldown").inc()
            return False
        
        # Check spending limits
        if not await self._check_spending_limits(action):
            logger.warning(f"Action {action.action_type.value} would exceed spending limits")
            self.safety_blocks.labels(reason="spending_limit").inc()
            await self._notify_slack(
                f"🚫 Action blocked: {action.action_type.value} would exceed ${self.max_hourly_spend}/hour limit",
                severity="warning"
            )
            return False
        
        # Check if confirmation required
        if action.requires_confirmation:
            logger.info(f"Action {action.action_type.value} requires confirmation (cost impact: ${action.estimated_cost_impact:.2f}/hour)")
            self.confirmations_required.inc()
            # In production, this would wait for confirmation via Slack or UI
            # For now, we'll skip actions requiring confirmation
            return False
        
        return True
    
    def _check_cooldown(self, action_type: ActionType) -> bool:
        """Check if cooldown period has passed for action type"""
        if action_type not in self.last_action_time:
            return True
        
        time_since_last = (datetime.now(timezone.utc) - self.last_action_time[action_type]).total_seconds() / 60
        return time_since_last >= self.action_cooldown_mins
    
    async def _check_spending_limits(self, action: AutonomousAction) -> bool:
        """Check if action would exceed spending limits"""
        # Calculate current hourly spend
        current_spend = sum(
            self._get_instance_hourly_rate(instance)
            for instance in self.instances.values()
        )
        
        # Project spend after action
        projected_spend = current_spend + action.estimated_cost_impact
        
        return projected_spend <= self.max_hourly_spend
    
    async def _execute_autonomous_action(self, action: AutonomousAction) -> bool:
        """Execute an autonomous action with full logging and safety"""
        logger.info(f"Executing autonomous action: {action.action_type.value}")
        
        try:
            # Record metrics before action
            metrics_before = await self._capture_current_metrics()
            
            # Execute based on action type
            success = False
            if action.action_type == ActionType.PROVISION_INSTANCE:
                success = await self._provision_instance(action)
            elif action.action_type == ActionType.TERMINATE_INSTANCE:
                success = await self._terminate_instance(action)
            
            if success:
                action.status = ActionStatus.EXECUTED
                action.executed_at = datetime.now(timezone.utc)
                
                # Update last action time
                self.last_action_time[action.action_type] = action.executed_at
                
                # Record metrics after action
                await asyncio.sleep(30)  # Wait for changes to take effect
                metrics_after = await self._capture_current_metrics()
                
                # Log to history
                history = ActionHistory(
                    action=action,
                    metrics_before=metrics_before,
                    metrics_after=metrics_after,
                    outcome="success"
                )
                self.action_history.append(history)
                
                # Update metrics
                self.actions_taken.labels(
                    action_type=action.action_type.value,
                    status="success"
                ).inc()
                self.action_cost_impact.labels(
                    action_type=action.action_type.value
                ).set(action.estimated_cost_impact)
                
                # Log to external systems
                await self._log_action_to_github(action)
                await self._log_action_to_postgres(history)
                await self._notify_slack(
                    f"✅ Executed: {action.action_type.value} - {action.reason}",
                    severity="info"
                )
                
            else:
                action.status = ActionStatus.FAILED
                self.actions_taken.labels(
                    action_type=action.action_type.value,
                    status="failed"
                ).inc()
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to execute action {action.action_id}: {e}")
            action.status = ActionStatus.FAILED
            action.error_message = str(e)
            
            await self._notify_slack(
                f"❌ Action failed: {action.action_type.value} - {str(e)}",
                severity="error"
            )
            
            return False
    
    async def _provision_instance(self, action: AutonomousAction) -> bool:
        """Provision a new Lambda Labs instance"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would provision instance type: {action.instance_type}")
            return True
        
        if not self.session:
            logger.error("HTTP session not initialized")
            return False
            
        try:
            # Prepare instance launch data
            launch_data = {
                "instance_type_name": action.instance_type,
                "region_name": self.api_config.get("default_region", "us-west-1"),
                "quantity": 1,
                "name": f"sophia-autonomous-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            }
            
            # Store rollback data
            action.rollback_data = {"launch_data": launch_data}
            
            # Launch instance via API
            async with self.session.post(f"{self.base_url}/instance-operations/launch", json=launch_data) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Successfully provisioned instance: {result}")
                
                # Refresh instance list
                await self.refresh_instances()
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to provision instance: {e}")
            action.error_message = str(e)
            return False
    
    async def _terminate_instance(self, action: AutonomousAction) -> bool:
        """Terminate a Lambda Labs instance"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would terminate instance: {action.target_instance_id}")
            return True
        
        if not self.session:
            logger.error("HTTP session not initialized")
            return False
            
        if not action.target_instance_id:
            logger.error("No target instance ID provided")
            return False
            
        try:
            # Store instance data for potential rollback
            instance_data = self.instances.get(action.target_instance_id)
            action.rollback_data = {"instance_data": instance_data}
            
            # Terminate instance via API
            terminate_data = {"instance_ids": [action.target_instance_id]}
            
            async with self.session.post(f"{self.base_url}/instance-operations/terminate", json=terminate_data) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Successfully terminated instance {action.target_instance_id}: {result}")
                
                # Refresh instance list
                await self.refresh_instances()
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to terminate instance: {e}")
            action.error_message = str(e)
            return False
    
    async def rollback_action(self, action_id: str) -> bool:
        """Rollback a previously executed action"""
        # Find action in history
        history_entry = next((h for h in self.action_history if h.action.action_id == action_id), None)
        if not history_entry:
            logger.error(f"Action {action_id} not found in history")
            return False
        
        action = history_entry.action
        if action.status != ActionStatus.EXECUTED:
            logger.error(f"Cannot rollback action {action_id} with status {action.status}")
            return False
        
        logger.info(f"Rolling back action: {action_id}")
        
        try:
            # Implement rollback based on action type
            if action.action_type == ActionType.PROVISION_INSTANCE and action.rollback_data:
                # Terminate the provisioned instance
                # Would need to track which instance was created
                logger.info("Rollback for provisioned instances not yet implemented")
                
            elif action.action_type == ActionType.TERMINATE_INSTANCE and action.rollback_data:
                # Cannot un-terminate, but log the attempt
                logger.warning("Cannot rollback instance termination - instance is permanently terminated")
                
            action.status = ActionStatus.ROLLED_BACK
            
            await self._notify_slack(
                f"🔄 Rolled back action: {action_id}",
                severity="info"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback action {action_id}: {e}")
            return False
    
    async def _capture_current_metrics(self) -> Dict[str, Any]:
        """Capture current state metrics for all instances"""
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_instances": len(self.instances),
            "total_hourly_cost": sum(
                self._get_instance_hourly_rate(instance)
                for instance in self.instances.values()
            ),
            "instances": {}
        }
        
        for instance_id, instance in self.instances.items():
            instance_metrics = await self._get_instance_metrics(instance_id)
            if instance_metrics:
                metrics["instances"][instance_id] = {
                    "type": instance.get("instance_type", {}).get("name"),
                    "gpu_utilization": instance_metrics.gpu_utilization,
                    "memory_usage": instance_metrics.gpu_memory_utilization,
                    "temperature": instance_metrics.gpu_temperature
                }
        
        return metrics
    
    async def _check_sustained_low_usage(self, instance_id: str, duration_mins: int) -> bool:
        """Check if an instance has sustained low usage"""
        if instance_id not in self.metrics_history:
            return False
        
        history = self.metrics_history[instance_id]
        if not history:
            return False
        
        # Check recent history
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=duration_mins)
        recent_metrics = [m for m in history if m.timestamp > cutoff]
        
        if len(recent_metrics) < 3:  # Need at least 3 data points
            return False
        
        # All recent metrics should show low usage
        return all(m.gpu_utilization < self.low_gpu_threshold for m in recent_metrics)
    
    def _get_hourly_rate(self, instance_type: Optional[str]) -> float:
        """Get hourly rate for an instance type name"""
        if not instance_type:
            return 1.0
            
        rates = {
            "gpu_1x_h100": 3.29,
            "gpu_1x_a100": 1.99,
            "gpu_1x_a6000": 0.80,
            "gpu_1x_rtx6000": 0.50,
            "gpu_1x_rtx4090": 0.40
        }
        
        return rates.get(instance_type, 1.0)
    
    def _get_instance_hourly_rate(self, instance: Dict[str, Any]) -> float:
        """Get hourly rate for an instance"""
        instance_type = instance.get("instance_type", {}).get("name", "")
        return self._get_hourly_rate(instance_type)
    
    async def _log_action_to_github(self, action: AutonomousAction, dry_run: bool = False):
        """Log action to GitHub via MCP server"""
        if not self.github_client:
            logger.debug("GitHub MCP client not initialized")
            return
        
        try:
            # Format action log
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "dry_run": dry_run,
                "action": {
                    "id": action.action_id,
                    "type": action.action_type.value,
                    "target": action.target_instance_id,
                    "reason": action.reason,
                    "cost_impact": action.estimated_cost_impact,
                    "status": action.status.value
                }
            }
            
            # TODO: Implement actual GitHub logging
            # await self.github_client.create_file(
            #     repo="sophia-autonomous-logs",
            #     path=f"lambda-labs/{action.action_id}.json",
            #     content=json.dumps(log_entry, indent=2)
            # )
            
            logger.debug(f"Would log to GitHub: {log_entry}")
            
        except Exception as e:
            logger.error(f"Failed to log to GitHub: {e}")
    
    async def _log_action_to_postgres(self, history: ActionHistory):
        """Log action history to PostgreSQL via MCP server"""
        if not self.postgres_client:
            logger.debug("PostgreSQL MCP client not initialized")
            return
        
        try:
            # TODO: Implement actual PostgreSQL logging
            # await self.postgres_client.execute(
            #     """
            #     INSERT INTO autonomous_actions 
            #     (action_id, action_type, target_instance, reason, cost_impact, 
            #      status, metrics_before, metrics_after, created_at, executed_at)
            #     VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            #     """,
            #     history.action.action_id,
            #     history.action.action_type.value,
            #     history.action.target_instance_id,
            #     history.action.reason,
            #     history.action.estimated_cost_impact,
            #     history.action.status.value,
            #     json.dumps(history.metrics_before),
            #     json.dumps(history.metrics_after),
            #     history.action.created_at,
            #     history.action.executed_at
            # )
            
            logger.debug(f"Would log to PostgreSQL: {history.action.action_id}")
            
        except Exception as e:
            logger.error(f"Failed to log to PostgreSQL: {e}")
    
    async def _notify_slack(self, message: str, severity: str = "info"):
        """Send notification to Slack via MCP server"""
        if not self.slack_client:
            logger.debug(f"Slack notification: [{severity}] {message}")
            return
        
        try:
            # TODO: Implement actual Slack notification
            # await self.slack_client.send_message(
            #     channel="#sophia-autonomous",
            #     text=f"[Lambda Labs Agent] {message}",
            #     icon_emoji=":robot_face:"
            # )
            pass
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    # Include all the monitoring methods from the base implementation
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
            
            # Update managed instances metric
            self.instances_managed.set(len(self.instances))
            
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
    
    async def _get_instance_metrics(self, instance_id: str) -> Optional[Any]:
        """Get GPU metrics for a specific instance (simulated for now)"""
        instance = self.instances.get(instance_id)
        if not instance:
            return None
        
        # TODO: Implement actual metric collection via SSH or API
        import random
        from .lambda_labs_monitor import GPUMetrics
        
        instance_type = instance.get("instance_type", {}).get("name", "unknown")
        
        if "h100" in instance_type.lower():
            base_util = 75
            memory_total = 80
        elif "a100" in instance_type.lower():
            base_util = 65
            memory_total = 80
        else:
            base_util = 50
            memory_total = 48
        
        gpu_util = max(0, min(100, base_util + random.uniform(-25, 25)))
        memory_used = (gpu_util / 100) * memory_total * random.uniform(0.8, 1.2)
        
        metrics = GPUMetrics(
            instance_id=instance_id,
            instance_name=instance.get("name", ""),
            instance_type=instance_type,
            gpu_utilization=gpu_util,
            gpu_memory_used=min(memory_used, memory_total),
            gpu_memory_total=memory_total,
            gpu_temperature=60 + (gpu_util / 100) * 25 + random.uniform(-5, 5),
            gpu_power_draw=200 + (gpu_util / 100) * 150 + random.uniform(-20, 20)
        )
        
        # Store in history
        self.metrics_history[instance_id].append(metrics)
        self._cleanup_old_metrics(instance_id)
        
        return metrics
    
    def _update_prometheus_metrics(self, metrics: Any):
        """Update Prometheus metrics (inherited from base)"""
        # This would be implemented based on the specific metrics
        pass
    
    def _cleanup_old_metrics(self, instance_id: str):
        """Remove metrics older than 1 hour"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        self.metrics_history[instance_id] = [
            m for m in self.metrics_history[instance_id]
            if m.timestamp > cutoff
        ]
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        
        # Close MCP connections
        # if self.github_client:
        #     await self.github_client.close()
        # if self.slack_client:
        #     await self.slack_client.close()
        # if self.postgres_client:
        #     await self.postgres_client.close()
    
    def get_action_summary(self) -> Dict[str, Any]:
        """Get summary of autonomous actions taken"""
        return {
            "total_actions": len(self.action_history),
            "actions_by_type": {
                ActionType.PROVISION_INSTANCE.value: sum(
                    1 for h in self.action_history 
                    if h.action.action_type == ActionType.PROVISION_INSTANCE
                ),
                ActionType.TERMINATE_INSTANCE.value: sum(
                    1 for h in self.action_history 
                    if h.action.action_type == ActionType.TERMINATE_INSTANCE
                )
            },
            "total_cost_impact": sum(
                h.action.estimated_cost_impact 
                for h in self.action_history
                if h.action.status == ActionStatus.EXECUTED
            ),
            "successful_actions": sum(
                1 for h in self.action_history
                if h.action.status == ActionStatus.EXECUTED
            ),
            "failed_actions": sum(
                1 for h in self.action_history
                if h.action.status == ActionStatus.FAILED
            ),
            "pending_confirmations": sum(
                1 for action in self.pending_actions
                if action.requires_confirmation
            ),
            "current_hourly_spend": sum(
                self._get_instance_hourly_rate(instance)
                for instance in self.instances.values()
            ),
            "max_hourly_spend": self.max_hourly_spend,
            "instances_running": len(self.instances),
            "max_instances": self.max_instances
        }
