"""
AIaC Chat Integration Service
Extends unified chat to handle infrastructure commands
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from backend.services.enhanced_unified_chat_service import EnhancedUnifiedChatService
from backend.services.mem0_integration_service import get_mem0_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentCategory(str, Enum):
    """Categories of user intent"""

    INFRASTRUCTURE = "infrastructure"
    BUSINESS = "business"
    GENERAL = "general"
    HELP = "help"


class RiskLevel(str, Enum):
    """Risk levels for infrastructure changes"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IntentClassification(BaseModel):
    """Result of intent classification"""

    category: IntentCategory
    intent_type: Optional[str] = None
    is_read_only: bool = True
    target: Optional[str] = None
    confidence: float = Field(ge=0, le=1)
    requires_approval: bool = False
    extracted_params: dict[str, Any] = Field(default_factory=dict)


class ExecutionStep(BaseModel):
    """Single step in an execution plan"""

    id: str
    service: str
    action: str
    description: str
    params: dict[str, Any]
    estimated_duration: int  # seconds
    risk_level: RiskLevel


class SimulationResult(BaseModel):
    """Result of simulating a plan"""

    success: bool
    summary: str
    details: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)
    estimated_impact: dict[str, Any] = Field(default_factory=dict)


class ExecutionPlan(BaseModel):
    """Complete execution plan for approval"""

    id: str
    intent: str
    user_id: str
    steps: list[ExecutionStep]
    simulation: Optional[SimulationResult] = None
    risk_level: RiskLevel
    estimated_duration: int  # seconds
    created_at: datetime
    expires_at: datetime
    rollback_plan: Optional[dict[str, Any]] = None


class AIaCResponse(BaseModel):
    """Response from AIaC processing"""

    type: str  # "approval_required", "executed", "info", "error"
    content: Any
    plan_id: Optional[str] = None
    requires_approval: bool = False


class AIaCIntentClassifier:
    """Classifies user messages for infrastructure operations"""

    def __init__(self):
        self.infrastructure_keywords = {
            "deploy",
            "scale",
            "update",
            "rollback",
            "create",
            "delete",
            "modify",
            "infrastructure",
            "server",
            "database",
            "kubernetes",
            "k8s",
            "pulumi",
            "docker",
            "restart",
            "reboot",
            "provision",
            "configure",
        }

        self.read_only_keywords = {
            "show",
            "list",
            "describe",
            "status",
            "check",
            "preview",
            "simulate",
            "what if",
            "would",
            "view",
            "get",
            "inspect",
            "monitor",
            "health",
        }

        self.target_patterns = {
            "pulumi": ["stack", "pulumi", "infrastructure"],
            "kubernetes": ["k8s", "kubernetes", "pod", "deployment", "service"],
            "snowflake": ["database", "warehouse", "snowflake", "query"],
            "github": ["github", "repo", "repository", "pr", "pull request"],
        }

    async def classify(self, message: str) -> IntentClassification:
        """Classify user intent from message"""
        message_lower = message.lower()

        # Check for infrastructure keywords
        is_infrastructure = any(
            keyword in message_lower for keyword in self.infrastructure_keywords
        )

        if not is_infrastructure:
            # Check if asking for help about infrastructure
            if "how" in message_lower and any(
                k in message_lower for k in ["deploy", "scale", "infrastructure"]
            ):
                return IntentClassification(
                    category=IntentCategory.HELP,
                    intent_type="infrastructure_help",
                    confidence=0.8,
                )

            return IntentClassification(category=IntentCategory.GENERAL, confidence=0.9)

        # Determine if read-only or state-changing
        is_read_only = any(
            keyword in message_lower for keyword in self.read_only_keywords
        )

        # Extract specific intent
        intent_type = self._extract_intent_type(message_lower)
        target = self._extract_target(message_lower)
        params = self._extract_parameters(message)

        return IntentClassification(
            category=IntentCategory.INFRASTRUCTURE,
            intent_type=intent_type,
            is_read_only=is_read_only,
            target=target,
            confidence=0.85,
            requires_approval=not is_read_only,
            extracted_params=params,
        )

    def _extract_intent_type(self, message: str) -> str:
        """Extract the specific intent type"""
        if "scale" in message:
            return "scale"
        elif "deploy" in message:
            return "deploy"
        elif "rollback" in message:
            return "rollback"
        elif "create" in message:
            return "create"
        elif "delete" in message:
            return "delete"
        elif "update" in message:
            return "update"
        elif "restart" in message or "reboot" in message:
            return "restart"
        elif any(k in message for k in ["show", "list", "status"]):
            return "query"
        else:
            return "unknown"

    def _extract_target(self, message: str) -> Optional[str]:
        """Extract the target service"""
        for service, patterns in self.target_patterns.items():
            if any(pattern in message for pattern in patterns):
                return service
        return None

    def _extract_parameters(self, message: str) -> dict[str, Any]:
        """Extract parameters from the message"""
        params = {}

        # Extract numbers (e.g., "scale to 5 instances")
        import re

        numbers = re.findall(r"\b\d+\b", message)
        if numbers:
            params["count"] = int(numbers[0])

        # Extract environment (production, staging, dev)
        if "production" in message or "prod" in message:
            params["environment"] = "production"
        elif "staging" in message:
            params["environment"] = "staging"
        elif "dev" in message:
            params["environment"] = "development"

        # Extract specific names (quoted strings)
        quoted = re.findall(r'"([^"]*)"', message)
        if quoted:
            params["name"] = quoted[0]

        return params


class ExecutionPlanGenerator:
    """Generates execution plans from intents"""

    def __init__(self):
        self.service_handlers = {
            "pulumi": self._generate_pulumi_plan,
            "kubernetes": self._generate_k8s_plan,
            "snowflake": self._generate_snowflake_plan,
            "github": self._generate_github_plan,
        }

    async def generate_plan(
        self, intent: IntentClassification, message: str, user_id: str
    ) -> ExecutionPlan:
        """Generate an execution plan from intent"""

        # Get the appropriate handler
        target = intent.target if intent.target else "unknown"
        handler = self.service_handlers.get(target, self._generate_generic_plan)

        # Generate steps
        steps = await handler(intent, message)

        # Calculate risk level
        risk_level = self._assess_risk(steps, intent)

        # Calculate total duration
        total_duration = sum(step.estimated_duration for step in steps)

        # Create plan
        plan = ExecutionPlan(
            id=f"plan_{datetime.now().timestamp()}",
            intent=message,
            user_id=user_id,
            steps=steps,
            risk_level=risk_level,
            estimated_duration=total_duration,
            created_at=datetime.now(),
            expires_at=datetime.now().replace(hour=datetime.now().hour + 1),
        )

        return plan

    async def _generate_pulumi_plan(
        self, intent: IntentClassification, message: str
    ) -> list[ExecutionStep]:
        """Generate Pulumi-specific plan"""
        steps = []

        if intent.intent_type == "deploy":
            steps.extend(
                [
                    ExecutionStep(
                        id="1",
                        service="pulumi",
                        action="preview",
                        description="Preview infrastructure changes",
                        params={
                            "stack": intent.extracted_params.get("name", "production")
                        },
                        estimated_duration=30,
                        risk_level=RiskLevel.LOW,
                    ),
                    ExecutionStep(
                        id="2",
                        service="pulumi",
                        action="update",
                        description="Apply infrastructure updates",
                        params={
                            "stack": intent.extracted_params.get("name", "production")
                        },
                        estimated_duration=120,
                        risk_level=RiskLevel.MEDIUM,
                    ),
                ]
            )
        elif intent.intent_type == "scale":
            count = intent.extracted_params.get("count", 3)
            steps.append(
                ExecutionStep(
                    id="1",
                    service="pulumi",
                    action="config_set",
                    description=f"Update configuration to scale to {count} instances",
                    params={"key": "instanceCount", "value": str(count)},
                    estimated_duration=10,
                    risk_level=RiskLevel.LOW,
                )
            )
            steps.append(
                ExecutionStep(
                    id="2",
                    service="pulumi",
                    action="update",
                    description="Apply scaling changes",
                    params={"stack": "production"},
                    estimated_duration=60,
                    risk_level=RiskLevel.MEDIUM,
                )
            )

        return steps

    async def _generate_k8s_plan(
        self, intent: IntentClassification, message: str
    ) -> list[ExecutionStep]:
        """Generate Kubernetes-specific plan"""
        steps = []

        if intent.intent_type == "scale":
            count = intent.extracted_params.get("count", 3)
            steps.append(
                ExecutionStep(
                    id="1",
                    service="kubernetes",
                    action="scale_deployment",
                    description=f"Scale deployment to {count} replicas",
                    params={
                        "namespace": "default",
                        "deployment": intent.extracted_params.get("name", "api-server"),
                        "replicas": count,
                    },
                    estimated_duration=15,
                    risk_level=RiskLevel.LOW,
                )
            )
        elif intent.intent_type == "restart":
            steps.append(
                ExecutionStep(
                    id="1",
                    service="kubernetes",
                    action="rollout_restart",
                    description="Restart deployment with rolling update",
                    params={
                        "namespace": "default",
                        "deployment": intent.extracted_params.get("name", "api-server"),
                    },
                    estimated_duration=60,
                    risk_level=RiskLevel.MEDIUM,
                )
            )

        return steps

    async def _generate_snowflake_plan(
        self, intent: IntentClassification, message: str
    ) -> list[ExecutionStep]:
        """Generate Snowflake-specific plan"""
        # Placeholder for Snowflake operations
        return []

    async def _generate_github_plan(
        self, intent: IntentClassification, message: str
    ) -> list[ExecutionStep]:
        """Generate GitHub-specific plan"""
        # Placeholder for GitHub operations
        return []

    async def _generate_generic_plan(
        self, intent: IntentClassification, message: str
    ) -> list[ExecutionStep]:
        """Generate generic plan when service is unknown"""
        return [
            ExecutionStep(
                id="1",
                service="unknown",
                action="analyze",
                description="Analyze request to determine appropriate action",
                params={"message": message},
                estimated_duration=5,
                risk_level=RiskLevel.LOW,
            )
        ]

    def _assess_risk(
        self, steps: list[ExecutionStep], intent: IntentClassification
    ) -> RiskLevel:
        """Assess overall risk level"""
        if not steps:
            return RiskLevel.LOW

        # Production changes are higher risk
        if intent.extracted_params.get("environment") == "production":
            return RiskLevel.HIGH

        # Deletions are high risk
        if intent.intent_type == "delete":
            return RiskLevel.CRITICAL

        # Get highest risk from steps
        risk_levels = [step.risk_level for step in steps]
        if RiskLevel.CRITICAL in risk_levels:
            return RiskLevel.CRITICAL
        elif RiskLevel.HIGH in risk_levels:
            return RiskLevel.HIGH
        elif RiskLevel.MEDIUM in risk_levels:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW


class AIaCChatIntegration:
    """
    Extends unified chat to handle infrastructure commands
    """

    def __init__(self):
        self.mem0_service = get_mem0_service()
        self.intent_classifier = AIaCIntentClassifier()
        self.plan_generator = ExecutionPlanGenerator()
        self.unified_chat = EnhancedUnifiedChatService()
        self.active_plans: dict[str, ExecutionPlan] = {}

    async def process_message(self, message: str, user_id: str) -> AIaCResponse:
        """Process a message and route appropriately"""

        # Classify intent
        intent = await self.intent_classifier.classify(message)

        # Log classification for debugging
        logger.info(f"Classified intent: {intent}")

        # Route based on category
        if intent.category == IntentCategory.INFRASTRUCTURE:
            return await self.handle_infrastructure_command(message, user_id, intent)
        elif intent.category == IntentCategory.HELP:
            return await self.handle_help_request(message, user_id, intent)
        else:
            # Regular chat processing
            return await self.process_regular_chat(message, user_id)

    async def handle_infrastructure_command(
        self, message: str, user_id: str, intent: IntentClassification
    ) -> AIaCResponse:
        """Handle infrastructure-related commands"""

        # Check if read-only
        if intent.is_read_only:
            # Execute immediately without approval
            result = await self.execute_read_only_command(intent, message)
            return AIaCResponse(type="info", content=result, requires_approval=False)

        # Generate execution plan
        plan = await self.plan_generator.generate_plan(intent, message, user_id)

        # Simulate the plan
        simulation = await self.simulate_plan(plan)
        plan.simulation = simulation

        # Store plan for approval
        self.active_plans[plan.id] = plan

        # Store in memory for learning
        await self.mem0_service.store_conversation_memory(
            user_id=user_id,
            conversation=[
                {"role": "user", "content": message},
                {
                    "role": "assistant",
                    "content": f"Generated infrastructure plan {plan.id} requiring approval",
                },
            ],
            metadata={
                "category": "aiac",
                "plan_id": plan.id,
                "risk_level": plan.risk_level.value,
                "requires_approval": True,
            },
        )

        # Return approval request
        return AIaCResponse(
            type="approval_required",
            content=self.format_approval_content(plan),
            plan_id=plan.id,
            requires_approval=True,
        )

    async def execute_read_only_command(
        self, intent: IntentClassification, message: str
    ) -> dict[str, Any]:
        """Execute read-only infrastructure commands"""
        # This would call the appropriate MCP server
        # For now, return mock data

        if intent.intent_type == "query":
            return {
                "title": "Infrastructure Status",
                "data": {
                    "pulumi_stacks": [
                        {"name": "production", "status": "up-to-date", "resources": 45},
                        {
                            "name": "staging",
                            "status": "update-available",
                            "resources": 38,
                        },
                    ],
                    "kubernetes_clusters": [
                        {
                            "name": "primary",
                            "nodes": 5,
                            "pods": 127,
                            "health": "healthy",
                        }
                    ],
                },
            }

        return {"message": "Command executed successfully"}

    async def simulate_plan(self, plan: ExecutionPlan) -> SimulationResult:
        """Simulate execution plan"""
        # This would call the simulation engine
        # For now, return mock simulation

        warnings = []
        if plan.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            warnings.append("This operation affects production systems")

        if plan.estimated_duration > 300:
            warnings.append("This operation may take more than 5 minutes")

        return SimulationResult(
            success=True,
            summary=f"Simulation successful. {len(plan.steps)} steps will be executed.",
            details={
                "resources_affected": 12,
                "estimated_cost_change": "$0.00",
                "downtime_expected": False,
            },
            warnings=warnings,
            estimated_impact={
                "availability": "No impact",
                "performance": "Temporary degradation possible",
                "cost": "No change",
            },
        )

    def format_approval_content(self, plan: ExecutionPlan) -> dict[str, Any]:
        """Format plan for approval UI"""
        return {
            "plan": plan.dict(),
            "formatted_steps": [
                {
                    "number": i + 1,
                    "description": step.description,
                    "duration": f"{step.estimated_duration}s",
                    "risk": step.risk_level.value,
                }
                for i, step in enumerate(plan.steps)
            ],
            "summary": {
                "total_steps": len(plan.steps),
                "total_duration": f"{plan.estimated_duration}s",
                "risk_level": plan.risk_level.value,
                "expires_in": int((plan.expires_at - datetime.now()).total_seconds()),
            },
        }

    async def handle_help_request(
        self, message: str, user_id: str, intent: IntentClassification
    ) -> AIaCResponse:
        """Handle help requests about infrastructure"""

        help_content = {
            "title": "Infrastructure Management Help",
            "examples": [
                "Show me the status of all Pulumi stacks",
                "Scale the API servers to 5 instances",
                "Deploy the latest changes to staging",
                "Rollback the production deployment",
            ],
            "capabilities": [
                "Preview changes before applying",
                "Automatic simulation of all changes",
                "Rollback support for all operations",
                "Complete audit trail",
            ],
            "safety": "All state-changing operations require your explicit approval",
        }

        return AIaCResponse(type="info", content=help_content, requires_approval=False)

    async def process_regular_chat(self, message: str, user_id: str) -> AIaCResponse:
        """Process non-infrastructure chat messages"""
        # Use the regular unified chat service
        response = await self.unified_chat.process_chat_message(
            message=message, user_id=user_id, session_id=f"aiac_{user_id}"
        )

        return AIaCResponse(type="chat", content=response, requires_approval=False)

    async def approve_plan(self, plan_id: str, user_id: str) -> dict[str, Any]:
        """Approve and execute a plan"""
        if plan_id not in self.active_plans:
            raise ValueError(f"Plan {plan_id} not found or expired")

        plan = self.active_plans[plan_id]

        # Verify user authorization
        if plan.user_id != user_id:
            raise ValueError("Unauthorized to approve this plan")

        # Execute the plan
        # This would call the appropriate MCP servers
        # For now, return success

        result = {
            "success": True,
            "plan_id": plan_id,
            "execution_time": plan.estimated_duration,
            "steps_completed": len(plan.steps),
            "message": "Infrastructure changes applied successfully",
        }

        # Store execution result in memory
        await self.mem0_service.store_conversation_memory(
            user_id=user_id,
            conversation=[
                {"role": "user", "content": f"Approved plan {plan_id}"},
                {
                    "role": "assistant",
                    "content": f"Executed infrastructure plan successfully: {result['message']}",
                },
            ],
            metadata={
                "category": "aiac",
                "plan_id": plan_id,
                "execution_time": plan.estimated_duration,
                "success": True,
            },
        )

        # Clean up
        del self.active_plans[plan_id]

        return result

    async def reject_plan(
        self, plan_id: str, user_id: str, reason: str = ""
    ) -> dict[str, Any]:
        """Reject a plan"""
        if plan_id not in self.active_plans:
            raise ValueError(f"Plan {plan_id} not found or expired")

        plan = self.active_plans[plan_id]

        # Verify user authorization
        if plan.user_id != user_id:
            raise ValueError("Unauthorized to reject this plan")

        # Store rejection in memory
        await self.mem0_service.store_conversation_memory(
            user_id=user_id,
            conversation=[
                {"role": "user", "content": f"Rejected plan {plan_id}: {reason}"},
                {"role": "assistant", "content": "Plan rejected and cancelled"},
            ],
            metadata={"category": "aiac", "plan_id": plan_id, "rejected": True},
        )

        # Clean up
        del self.active_plans[plan_id]

        return {"success": True, "message": "Plan rejected", "plan_id": plan_id}
