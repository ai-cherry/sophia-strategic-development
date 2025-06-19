"""
LangGraph Workflow Engine for Sophia AI
Prototype multi-step agent workflows with state management
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

from backend.agents.core.agent_router import agent_router
from backend.core.context_manager import context_manager

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Status of a workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkflowState:
    """State container for workflow execution"""
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: int = 0
    steps_completed: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "current_step": self.current_step,
            "steps_completed": self.steps_completed,
            "results": self.results,
            "errors": self.errors,
            "context": self.context,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

@dataclass
class WorkflowStep:
    """Definition of a workflow step"""
    name: str
    agent: str
    command: str
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[Callable[[WorkflowState], bool]] = None
    retry_count: int = 3
    timeout_seconds: int = 300

class LangGraphWorkflow:
    """
    LangGraph-based workflow engine for multi-step agent orchestration
    """
    
    def __init__(self, workflow_id: str, description: str):
        self.workflow_id = workflow_id
        self.description = description
        self.steps: List[WorkflowStep] = []
        self.state = WorkflowState(workflow_id=workflow_id)
        
    def add_step(self, step: WorkflowStep):
        """Add a step to the workflow"""
        self.steps.append(step)
        
    async def execute(self, initial_context: Dict[str, Any]) -> WorkflowState:
        """Execute the workflow"""
        self.state.context.update(initial_context)
        self.state.status = WorkflowStatus.RUNNING
        self.state.started_at = datetime.utcnow()
        
        logger.info(f"Starting workflow: {self.workflow_id}")
        
        try:
            for i, step in enumerate(self.steps):
                self.state.current_step = i
                
                # Check dependencies
                if not self._check_dependencies(step):
                    logger.warning(f"Skipping step {step.name}: dependencies not met")
                    continue
                
                # Check condition
                if step.condition and not step.condition(self.state):
                    logger.info(f"Skipping step {step.name}: condition not met")
                    continue
                
                # Execute step
                result = await self._execute_step(step)
                
                if result["status"] == "error":
                    self.state.errors.append({
                        "step": step.name,
                        "error": result.get("message", "Unknown error"),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    # Decide whether to continue or fail
                    if self._should_fail_workflow(step, result):
                        self.state.status = WorkflowStatus.FAILED
                        break
                else:
                    self.state.steps_completed.append(step.name)
                    self.state.results[step.name] = result
            
            if self.state.status == WorkflowStatus.RUNNING:
                self.state.status = WorkflowStatus.COMPLETED
                
        except Exception as e:
            logger.error(f"Workflow {self.workflow_id} failed: {e}")
            self.state.status = WorkflowStatus.FAILED
            self.state.errors.append({
                "step": "workflow",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        self.state.completed_at = datetime.utcnow()
        logger.info(f"Workflow {self.workflow_id} completed with status: {self.state.status}")
        
        return self.state
    
    async def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step with retries"""
        logger.info(f"Executing step: {step.name}")
        
        for attempt in range(step.retry_count):
            try:
                # Add step context
                step_context = {
                    **self.state.context,
                    "workflow_id": self.workflow_id,
                    "step_name": step.name,
                    "previous_results": self.state.results
                }
                
                # Execute via agent router
                result = await asyncio.wait_for(
                    agent_router.route_command(step.command, step_context),
                    timeout=step.timeout_seconds
                )
                
                if result["status"] == "success":
                    return result
                
                # Retry on error
                if attempt < step.retry_count - 1:
                    logger.warning(f"Step {step.name} failed, retrying... (attempt {attempt + 1})")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except asyncio.TimeoutError:
                logger.error(f"Step {step.name} timed out after {step.timeout_seconds}s")
                if attempt < step.retry_count - 1:
                    continue
                return {
                    "status": "error",
                    "message": f"Step timed out after {step.timeout_seconds} seconds"
                }
            except Exception as e:
                logger.error(f"Step {step.name} failed: {e}")
                if attempt < step.retry_count - 1:
                    continue
                return {
                    "status": "error",
                    "message": str(e)
                }
        
        return {
            "status": "error",
            "message": f"Step failed after {step.retry_count} attempts"
        }
    
    def _check_dependencies(self, step: WorkflowStep) -> bool:
        """Check if all dependencies for a step are satisfied"""
        for dep in step.depends_on:
            if dep not in self.state.steps_completed:
                return False
        return True
    
    def _should_fail_workflow(self, step: WorkflowStep, result: Dict[str, Any]) -> bool:
        """Determine if a step failure should fail the entire workflow"""
        # For now, any step failure fails the workflow
        # Can be customized per step or based on error type
        return True

# Predefined workflow templates
class WorkflowTemplates:
    """Collection of predefined workflow templates"""
    
    @staticmethod
    def create_deployment_workflow(environment: str = "staging") -> LangGraphWorkflow:
        """Create a deployment workflow"""
        workflow = LangGraphWorkflow(
            workflow_id=f"deploy-{environment}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            description=f"Deploy application to {environment}"
        )
        
        # Build and test
        workflow.add_step(WorkflowStep(
            name="build_docker_image",
            agent="docker_agent",
            command="build Docker image as sophia-app:latest"
        ))
        
        workflow.add_step(WorkflowStep(
            name="run_tests",
            agent="docker_agent",
            command="run pytest in sophia-app:latest",
            depends_on=["build_docker_image"]
        ))
        
        # Infrastructure preview
        workflow.add_step(WorkflowStep(
            name="preview_infrastructure",
            agent="pulumi_agent",
            command=f"preview stack {environment}",
            depends_on=["run_tests"]
        ))
        
        # Deploy infrastructure
        workflow.add_step(WorkflowStep(
            name="deploy_infrastructure",
            agent="pulumi_agent",
            command=f"deploy stack {environment}",
            depends_on=["preview_infrastructure"],
            condition=lambda state: state.results.get("preview_infrastructure", {}).get("status") == "success"
        ))
        
        # Deploy application
        workflow.add_step(WorkflowStep(
            name="deploy_application",
            agent="docker_agent",
            command="deploy sophia-app:latest to production",
            depends_on=["deploy_infrastructure"]
        ))
        
        # Verify deployment
        workflow.add_step(WorkflowStep(
            name="verify_deployment",
            agent="claude_agent",
            command=f"verify deployment health for {environment}",
            depends_on=["deploy_application"]
        ))
        
        return workflow
    
    @staticmethod
    def create_code_review_workflow(code_path: str) -> LangGraphWorkflow:
        """Create a code review and analysis workflow"""
        workflow = LangGraphWorkflow(
            workflow_id=f"code-review-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            description=f"Review and analyze code at {code_path}"
        )
        
        # Security scan
        workflow.add_step(WorkflowStep(
            name="security_scan",
            agent="claude_agent",
            command=f"analyze code for security vulnerabilities in {code_path}"
        ))
        
        # Code quality review
        workflow.add_step(WorkflowStep(
            name="code_review",
            agent="claude_agent",
            command=f"review code for best practices in {code_path}"
        ))
        
        # Performance analysis
        workflow.add_step(WorkflowStep(
            name="performance_analysis",
            agent="claude_agent",
            command=f"analyze code for performance issues in {code_path}"
        ))
        
        # Generate report
        workflow.add_step(WorkflowStep(
            name="generate_report",
            agent="claude_agent",
            command="generate comprehensive code review report",
            depends_on=["security_scan", "code_review", "performance_analysis"]
        ))
        
        return workflow
    
    @staticmethod
    def create_infrastructure_update_workflow() -> LangGraphWorkflow:
        """Create an infrastructure update workflow"""
        workflow = LangGraphWorkflow(
            workflow_id=f"infra-update-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            description="Update infrastructure with latest configurations"
        )
        
        # Refresh state
        workflow.add_step(WorkflowStep(
            name="refresh_dev",
            agent="pulumi_agent",
            command="refresh stack dev"
        ))
        
        workflow.add_step(WorkflowStep(
            name="refresh_staging",
            agent="pulumi_agent",
            command="refresh stack staging"
        ))
        
        # Preview all changes
        workflow.add_step(WorkflowStep(
            name="preview_all",
            agent="pulumi_agent",
            command="preview all stack changes",
            depends_on=["refresh_dev", "refresh_staging"]
        ))
        
        # Update dev first
        workflow.add_step(WorkflowStep(
            name="update_dev",
            agent="pulumi_agent",
            command="deploy stack dev",
            depends_on=["preview_all"]
        ))
        
        # Test dev
        workflow.add_step(WorkflowStep(
            name="test_dev",
            agent="claude_agent",
            command="run integration tests on dev environment",
            depends_on=["update_dev"]
        ))
        
        # Update staging if dev passes
        workflow.add_step(WorkflowStep(
            name="update_staging",
            agent="pulumi_agent",
            command="deploy stack staging",
            depends_on=["test_dev"],
            condition=lambda state: state.results.get("test_dev", {}).get("status") == "success"
        ))
        
        return workflow

    @staticmethod
    def create_gong_sync_workflow(days_back: int = 7) -> LangGraphWorkflow:
        """
        Creates a workflow to sync and analyze recent Gong calls.
        """
        workflow = LangGraphWorkflow(
            workflow_id=f"gong-sync-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            description=f"Sync and analyze Gong calls from the last {days_back} days."
        )

        # Step 1: Fetch recent calls from the Gong MCP server
        workflow.add_step(WorkflowStep(
            name="fetch_recent_calls",
            agent="gong_agent", # Assumes a GongAgent that maps to the GongMCPServer
            command=f"get calls from the last {days_back} days"
        ))
        
        # Step 2: Process each call for analytics
        # Note: A real LangGraph implementation would loop over the results of the first step.
        # This is a simplified representation where we imagine an agent capable of this.
        workflow.add_step(WorkflowStep(
            name="process_calls_for_analytics",
            agent="gong_agent",
            command="process and store analytics for all fetched calls",
            depends_on=["fetch_recent_calls"]
        ))
        
        # Step 3: Generate a summary report
        workflow.add_step(WorkflowStep(
            name="generate_sync_report",
            agent="brain_agent",
            command="generate a summary report of the Gong sync",
            depends_on=["process_calls_for_analytics"]
        ))
        
        return workflow

# Workflow manager for tracking and managing workflows
class WorkflowManager:
    """Manages workflow execution and tracking"""
    
    def __init__(self):
        self.workflows: Dict[str, LangGraphWorkflow] = {}
        self.execution_history: List[WorkflowState] = []
        
    async def execute_workflow(
        self,
        workflow: LangGraphWorkflow,
        context: Dict[str, Any]
    ) -> WorkflowState:
        """Execute a workflow and track its state"""
        self.workflows[workflow.workflow_id] = workflow
        
        # Execute workflow
        state = await workflow.execute(context)
        
        # Track execution
        self.execution_history.append(state)
        
        # Limit history size
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
        
        return state
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get the status of a workflow"""
        if workflow_id in self.workflows:
            return self.workflows[workflow_id].state
        
        # Check history
        for state in reversed(self.execution_history):
            if state.workflow_id == workflow_id:
                return state
        
        return None
    
    def get_recent_workflows(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow executions"""
        recent = self.execution_history[-limit:]
        return [state.to_dict() for state in reversed(recent)]

# Global workflow manager instance
workflow_manager = WorkflowManager() 