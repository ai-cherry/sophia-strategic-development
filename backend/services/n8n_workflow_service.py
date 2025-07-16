"""
n8n Workflow Automation Service
Manages workflow execution, creation, and monitoring through n8n

This service enables natural language workflow creation and execution
with deep integration into the Sophia AI ecosystem.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

class WorkflowTriggerType(str, Enum):
    """Types of workflow triggers"""

    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    EVENT = "event"
    MANUAL = "manual"
    AI_TRIGGERED = "ai_triggered"

class WorkflowStatus(str, Enum):
    """Workflow execution status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class WorkflowNode(BaseModel):
    """Represents a node in the workflow"""

    id: str
    type: str
    name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    position: Dict[str, float] = Field(default_factory=dict)
    credentials: Optional[Dict[str, str]] = None

class WorkflowDefinition(BaseModel):
    """Complete workflow definition"""

    name: str
    description: str
    triggers: List[WorkflowTriggerType]
    nodes: List[WorkflowNode]
    connections: List[Dict[str, Any]] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)
    active: bool = True

class WorkflowExecution(BaseModel):
    """Workflow execution result"""

    id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

class N8nWorkflowService:
    """Service for managing n8n workflow automation"""

    def __init__(self):
        self.base_url = get_config_value("n8n_base_url", "http://localhost:5678")
        self.api_key = get_config_value("n8n_api_key")
        self.webhook_url = get_config_value(
            "n8n_webhook_url", f"{self.base_url}/webhook"
        )

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=(
                {"X-N8N-API-KEY": self.api_key, "Content-Type": "application/json"}
                if self.api_key
                else {}
            ),
            timeout=30.0,
        )

        # Pre-built workflow templates
        self.workflow_templates = self._initialize_templates()

        logger.info(f"n8n Workflow Service initialized - Base URL: {self.base_url}")

    def _initialize_templates(self) -> Dict[str, WorkflowDefinition]:
        """Initialize pre-built workflow templates"""
        return {
            "daily_business_intelligence": WorkflowDefinition(
                name="Daily Business Intelligence Report",
                description="Automated daily business metrics and insights",
                triggers=[WorkflowTriggerType.SCHEDULE],
                nodes=[
                    WorkflowNode(
                        id="schedule",
                        type="n8n-nodes-base.scheduleTrigger",
                        name="Daily at 9 AM",
                        parameters={
                            "rule": {
                                "interval": [{"field": "hours", "hoursInterval": 9}]
                            }
                        },
                        position={"x": 250, "y": 300},
                    ),
                    WorkflowNode(
                        id="QDRANT_query",
                        type="n8n-nodes-base.qdrant",
                        name="Query Business Metrics",
                        parameters={
                            "operation": "executeQuery",
                            "query": """
                                SELECT 
                                    DATE(created_at) as date,
                                    SUM(revenue) as daily_revenue,
                                    COUNT(DISTINCT customer_id) as unique_customers,
                                    AVG(deal_size) as avg_deal_size
                                FROM business_metrics
                                WHERE created_at >= DATEADD(day, -7, CURRENT_DATE())
                                GROUP BY DATE(created_at)
                                ORDER BY date DESC
                            """,
                        },
                        position={"x": 450, "y": 300},
                    ),
                    WorkflowNode(
                        id="ai_analysis",
                        type="n8n-nodes-base.openAi",
                        name="AI Analysis",
                        parameters={
                            "operation": "text",
                            "modelId": "gpt-4",
                            "prompt": "Analyze these business metrics and provide insights: {{$json}}",
                        },
                        position={"x": 650, "y": 300},
                    ),
                    WorkflowNode(
                        id="slack_notify",
                        type="n8n-nodes-base.slack",
                        name="Send to Slack",
                        parameters={
                            "operation": "postMessage",
                            "channel": "#executive-updates",
                            "text": "Daily Business Intelligence Report\n\n{{$node['ai_analysis'].json.choices[0].text}}",
                        },
                        position={"x": 850, "y": 300},
                    ),
                ],
            ),
            "customer_health_monitoring": WorkflowDefinition(
                name="Customer Health Monitoring",
                description="Monitor customer health scores and alert on changes",
                triggers=[WorkflowTriggerType.EVENT, WorkflowTriggerType.SCHEDULE],
                nodes=[
                    WorkflowNode(
                        id="trigger",
                        type="n8n-nodes-base.webhookTrigger",
                        name="Customer Event",
                        parameters={"path": "customer-health"},
                        position={"x": 250, "y": 300},
                    ),
                    WorkflowNode(
                        id="gong_sentiment",
                        type="n8n-nodes-custom.gong",
                        name="Get Call Sentiment",
                        parameters={
                            "operation": "getCallsByCustomer",
                            "customerId": "{{$json.customer_id}}",
                            "limit": 5,
                        },
                        position={"x": 450, "y": 200},
                    ),
                    WorkflowNode(
                        id="hubspot_deals",
                        type="n8n-nodes-base.hubspot",
                        name="Get Deal Status",
                        parameters={
                            "operation": "get",
                            "resource": "deal",
                            "filters": {"associatedCompanyId": "{{$json.customer_id}}"},
                        },
                        position={"x": 450, "y": 400},
                    ),
                    WorkflowNode(
                        id="health_calculation",
                        type="n8n-nodes-base.function",
                        name="Calculate Health Score",
                        parameters={
                            "code": """
                                const sentiment = $node['gong_sentiment'].json;
                                const deals = $node['hubspot_deals'].json;
                                
                                let healthScore = 100;
                                
                                // Sentiment impact
                                const avgSentiment = sentiment.reduce((a, b) => a + b.sentiment, 0) / sentiment.length;
                                healthScore -= (1 - avgSentiment) * 30;
                                
                                // Deal status impact
                                const stuckDeals = deals.filter(d => d.daysInStage > 30).length;
                                healthScore -= stuckDeals * 10;
                                
                                return {
                                    customer_id: $json.customer_id,
                                    health_score: Math.max(0, Math.min(100, healthScore)),
                                    factors: {
                                        sentiment: avgSentiment,
                                        stuck_deals: stuckDeals
                                    }
                                };
                            """
                        },
                        position={"x": 650, "y": 300},
                    ),
                    WorkflowNode(
                        id="alert_if_low",
                        type="n8n-nodes-base.if",
                        name="Check if Alert Needed",
                        parameters={
                            "conditions": {
                                "number": [
                                    {
                                        "value1": "{{$json.health_score}}",
                                        "operation": "smaller",
                                        "value2": 70,
                                    }
                                ]
                            }
                        },
                        position={"x": 850, "y": 300},
                    ),
                ],
            ),
            "code_quality_gate": WorkflowDefinition(
                name="Code Quality Gate",
                description="Automated code review and quality checks",
                triggers=[WorkflowTriggerType.WEBHOOK],
                nodes=[
                    WorkflowNode(
                        id="github_pr",
                        type="n8n-nodes-base.githubTrigger",
                        name="PR Created/Updated",
                        parameters={
                            "events": [
                                "pull_request.opened",
                                "pull_request.synchronize",
                            ],
                            "repository": "sophia-ai",
                        },
                        position={"x": 250, "y": 300},
                    ),
                    WorkflowNode(
                        id="codacy_scan",
                        type="n8n-nodes-custom.codacy",
                        name="Security Scan",
                        parameters={
                            "operation": "analyzePR",
                            "pullRequestId": "{{$json.pull_request.number}}",
                        },
                        position={"x": 450, "y": 200},
                    ),
                    WorkflowNode(
                        id="ai_review",
                        type="n8n-nodes-base.openAi",
                        name="AI Code Review",
                        parameters={
                            "operation": "text",
                            "modelId": "gpt-4",
                            "prompt": "Review this code change for best practices: {{$json.pull_request.diff}}",
                        },
                        position={"x": 450, "y": 400},
                    ),
                    WorkflowNode(
                        id="create_comment",
                        type="n8n-nodes-base.github",
                        name="Post Review Comment",
                        parameters={
                            "operation": "createComment",
                            "issueNumber": "{{$json.pull_request.number}}",
                            "body": "## Automated Code Review\n\n{{$node['ai_review'].json.choices[0].text}}\n\n### Security Scan Results\n{{$node['codacy_scan'].json.summary}}",
                        },
                        position={"x": 650, "y": 300},
                    ),
                ],
            ),
        }

    async def create_workflow(self, definition: WorkflowDefinition) -> Dict[str, Any]:
        """Create a new workflow in n8n"""
        try:
            # Convert our definition to n8n format
            n8n_workflow = {
                "name": definition.name,
                "nodes": [node.dict() for node in definition.nodes],
                "connections": definition.connections,
                "active": definition.active,
                "settings": definition.settings,
            }

            response = await self.client.post("/api/v1/workflows", json=n8n_workflow)
            response.raise_for_status()

            workflow = response.json()
            logger.info(f"Created workflow: {workflow['id']} - {workflow['name']}")

            return workflow

        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise

    async def execute_workflow(
        self, workflow_id: str, data: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        """Execute a workflow with optional data"""
        try:
            execution_data = {"workflowId": workflow_id, "data": data or {}}

            response = await self.client.post(
                f"/api/v1/workflows/{workflow_id}/execute", json=execution_data
            )
            response.raise_for_status()

            result = response.json()

            return WorkflowExecution(
                id=result["id"],
                workflow_id=workflow_id,
                status=(
                    WorkflowStatus.COMPLETED
                    if result.get("finished")
                    else WorkflowStatus.EXECUTING
                ),
                started_at=datetime.fromisoformat(result["startedAt"]),
                finished_at=(
                    datetime.fromisoformat(result["stoppedAt"])
                    if result.get("stoppedAt")
                    else None
                ),
                data=result.get("data", {}),
            )

        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            return WorkflowExecution(
                id="error",
                workflow_id=workflow_id,
                status=WorkflowStatus.FAILED,
                started_at=datetime.now(),
                error=str(e),
            )

    async def create_workflow_from_description(
        self, description: str
    ) -> Dict[str, Any]:
        """Create a workflow from natural language description"""
        # This would use LLM to parse the description and create a workflow
        # For now, we'll match against templates

        description_lower = description.lower()

        # Match against templates
        if "daily" in description_lower and (
            "report" in description_lower or "intelligence" in description_lower
        ):
            template = self.workflow_templates["daily_business_intelligence"]
        elif "customer" in description_lower and "health" in description_lower:
            template = self.workflow_templates["customer_health_monitoring"]
        elif "code" in description_lower and (
            "quality" in description_lower or "review" in description_lower
        ):
            template = self.workflow_templates["code_quality_gate"]
        else:
            # Create a basic workflow structure
            template = WorkflowDefinition(
                name=f"Custom Workflow - {description[:50]}",
                description=description,
                triggers=[WorkflowTriggerType.MANUAL],
                nodes=[
                    WorkflowNode(
                        id="manual",
                        type="n8n-nodes-base.manualTrigger",
                        name="Manual Trigger",
                        position={"x": 250, "y": 300},
                    )
                ],
            )

        # Create the workflow
        return await self.create_workflow(template)

    async def list_workflows(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """List all workflows"""
        try:
            params = {"active": "true"} if active_only else {}
            response = await self.client.get("/api/v1/workflows", params=params)
            response.raise_for_status()

            workflows = response.json()
            return workflows.get("data", [])

        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []

    async def get_workflow_executions(
        self, workflow_id: str, limit: int = 10
    ) -> List[WorkflowExecution]:
        """Get recent executions for a workflow"""
        try:
            response = await self.client.get(
                "/api/v1/executions",
                params={"workflowId": workflow_id, "limit": limit},
            )
            response.raise_for_status()

            executions_data = response.json().get("data", [])

            executions = []
            for exec_data in executions_data:
                executions.append(
                    WorkflowExecution(
                        id=exec_data["id"],
                        workflow_id=workflow_id,
                        status=(
                            WorkflowStatus.COMPLETED
                            if exec_data.get("finished")
                            else WorkflowStatus.FAILED
                        ),
                        started_at=datetime.fromisoformat(exec_data["startedAt"]),
                        finished_at=(
                            datetime.fromisoformat(exec_data["stoppedAt"])
                            if exec_data.get("stoppedAt")
                            else None
                        ),
                        data=exec_data.get("data", {}),
                    )
                )

            return executions

        except Exception as e:
            logger.error(f"Failed to get workflow executions: {e}")
            return []

    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a workflow"""
        try:
            response = await self.client.patch(
                f"/api/v1/workflows/{workflow_id}", json={"active": False}
            )
            response.raise_for_status()
            return True

        except Exception as e:
            logger.error(f"Failed to pause workflow {workflow_id}: {e}")
            return False

    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow"""
        try:
            response = await self.client.patch(
                f"/api/v1/workflows/{workflow_id}", json={"active": True}
            )
            response.raise_for_status()
            return True

        except Exception as e:
            logger.error(f"Failed to resume workflow {workflow_id}: {e}")
            return False

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        try:
            response = await self.client.delete(f"/api/v1/workflows/{workflow_id}")
            response.raise_for_status()
            return True

        except Exception as e:
            logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            return False

    async def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow performance metrics"""
        try:
            workflows = await self.list_workflows()

            metrics = {
                "total_workflows": len(workflows),
                "active_workflows": sum(1 for w in workflows if w.get("active")),
                "workflow_types": {},
                "execution_stats": {"total": 0, "successful": 0, "failed": 0},
            }

            # Get execution stats for each workflow
            for workflow in workflows[:10]:  # Limit to prevent too many API calls
                executions = await self.get_workflow_executions(
                    workflow["id"], limit=50
                )

                metrics["execution_stats"]["total"] += len(executions)
                metrics["execution_stats"]["successful"] += sum(
                    1 for e in executions if e.status == WorkflowStatus.COMPLETED
                )
                metrics["execution_stats"]["failed"] += sum(
                    1 for e in executions if e.status == WorkflowStatus.FAILED
                )

            return metrics

        except Exception as e:
            logger.error(f"Failed to get workflow metrics: {e}")
            return {}

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Singleton instance
_n8n_service: Optional[N8nWorkflowService] = None

def get_n8n_service() -> N8nWorkflowService:
    """Get or create the n8n service instance"""
    global _n8n_service
    if _n8n_service is None:
        _n8n_service = N8nWorkflowService()
    return _n8n_service
