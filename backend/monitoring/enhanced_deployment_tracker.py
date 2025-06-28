"""
Sophia AI - Enhanced Deployment Tracking & Monitoring System
Provides real-time deployment monitoring, tracking, and automated rollback capabilities
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class DeploymentStatus(Enum):
    """Deployment status enumeration."""

    INITIATED = "INITIATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    ROLLBACK_IN_PROGRESS = "ROLLBACK_IN_PROGRESS"


class ComponentType(Enum):
    """Component type enumeration."""

    INFRASTRUCTURE = "infrastructure"
    MCP_SERVERS = "mcp_servers"
    FRONTEND = "frontend"
    DATA_PIPELINE = "data_pipeline"
    INTEGRATION = "integration"
    MONITORING = "monitoring"


class Environment(Enum):
    """Deployment environment enumeration."""

    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"


@dataclass
class DeploymentEvent:
    """Deployment event data structure."""

    deployment_id: str
    component: ComponentType
    environment: Environment
    version: str
    status: DeploymentStatus
    timestamp: datetime
    duration_seconds: int | None = None
    github_sha: str | None = None
    github_ref: str | None = None
    github_actor: str | None = None
    error_message: str | None = None
    rollback_target: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class DeploymentHealth:
    """Deployment health status."""

    component: ComponentType
    environment: Environment
    status: str
    last_deployment: datetime | None
    success_rate: float
    average_duration: float
    issues: list[str]


@dataclass
class RollbackPlan:
    """Rollback plan data structure."""

    deployment_id: str
    component: ComponentType
    environment: Environment
    current_version: str
    target_version: str
    rollback_steps: list[str]
    estimated_duration: int
    risk_level: str


class EnhancedDeploymentTracker:
    """Enhanced deployment tracking with monitoring and rollback capabilities."""

    def __init__(self):
        self.deployment_history: list[DeploymentEvent] = []
        self.active_deployments: dict[str, DeploymentEvent] = {}

    def generate_deployment_id(
        self, component: ComponentType, environment: Environment
    ) -> str:
        """Generate unique deployment ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        return f"{component.value}-{environment.value}-{timestamp}"

    async def start_deployment(
        self,
        component: ComponentType,
        environment: Environment,
        version: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Start tracking a new deployment."""

        deployment_id = self.generate_deployment_id(component, environment)

        # Gather GitHub context
        github_context = self._get_github_context()

        deployment_event = DeploymentEvent(
            deployment_id=deployment_id,
            component=component,
            environment=environment,
            version=version,
            status=DeploymentStatus.INITIATED,
            timestamp=datetime.utcnow(),
            github_sha=github_context.get("sha"),
            github_ref=github_context.get("ref"),
            github_actor=github_context.get("actor"),
            metadata=metadata or {},
        )

        # Store in active deployments
        self.active_deployments[deployment_id] = deployment_event

        # Send notification
        await self._send_deployment_notification(deployment_event, "started")

        logger.info(f"🚀 Started deployment tracking: {deployment_id}")
        return deployment_id

    async def complete_deployment(
        self, deployment_id: str, success: bool, error_message: str | None = None
    ) -> bool:
        """Complete deployment tracking."""

        if deployment_id not in self.active_deployments:
            logger.error(
                f"❌ Deployment {deployment_id} not found in active deployments"
            )
            return False

        deployment = self.active_deployments[deployment_id]
        deployment.status = (
            DeploymentStatus.COMPLETED if success else DeploymentStatus.FAILED
        )
        deployment.error_message = error_message
        deployment.duration_seconds = int(
            (datetime.utcnow() - deployment.timestamp).total_seconds()
        )

        # Move to history
        self.deployment_history.append(deployment)
        del self.active_deployments[deployment_id]

        # Send notification
        status_text = "completed" if success else "failed"
        await self._send_deployment_notification(deployment, status_text)

        logger.info(
            f"📊 Completed deployment {deployment_id}: {deployment.status.value}"
        )
        return True

    def _get_github_context(self) -> dict[str, str]:
        """Get GitHub context from environment variables."""
        return {
            "sha": os.getenv("GITHUB_SHA", ""),
            "ref": os.getenv("GITHUB_REF", ""),
            "actor": os.getenv("GITHUB_ACTOR", ""),
            "workflow": os.getenv("GITHUB_WORKFLOW", ""),
            "job": os.getenv("GITHUB_JOB", ""),
        }

    async def _send_deployment_notification(
        self, event: DeploymentEvent, action: str
    ) -> bool:
        """Send deployment notification."""

        try:
            # Prepare notification message
            emoji_map = {
                "started": "🚀",
                "completed": "✅",
                "failed": "❌",
                "rolled_back": "🔄",
            }

            emoji = emoji_map.get(action, "📊")

            message = f"""
{emoji} **Deployment {action.title()}**
• **Component**: {event.component.value}
• **Environment**: {event.environment.value}
• **Version**: {event.version}
• **ID**: {event.deployment_id}
"""

            if event.duration_seconds:
                message += f"• **Duration**: {event.duration_seconds}s\n"

            if event.error_message:
                message += f"• **Error**: {event.error_message}\n"

            if event.github_sha:
                message += f"• **Commit**: {event.github_sha[:8]}\n"

            logger.info(f"📢 Deployment notification: {message}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send deployment notification: {e}")
            return False


# Global deployment tracker instance
deployment_tracker = EnhancedDeploymentTracker()
