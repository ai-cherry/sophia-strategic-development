"""
Workflow Management API
Handles n8n workflow automation through natural language
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.auth import get_current_user
from backend.services.n8n_workflow_service import (
    get_n8n_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v4/workflows", tags=["workflows"])


class WorkflowCreateRequest(BaseModel):
    """Request to create a workflow"""

    description: str
    name: Optional[str] = None
    active: bool = True


class WorkflowExecuteRequest(BaseModel):
    """Request to execute a workflow"""

    workflow_id: str
    data: Optional[Dict] = None


class WorkflowListResponse(BaseModel):
    """Response for workflow list"""

    workflows: List[Dict]
    total: int


class WorkflowMetricsResponse(BaseModel):
    """Response for workflow metrics"""

    total_workflows: int
    active_workflows: int
    execution_stats: Dict
    success_rate: float


@router.post("/create", response_model=Dict)
async def create_workflow(
    request: WorkflowCreateRequest, user: Dict = Depends(get_current_user)
):
    """Create a new workflow from natural language description"""
    try:
        service = get_n8n_service()

        # Create workflow from description
        workflow = await service.create_workflow_from_description(request.description)

        # Override name if provided
        if request.name:
            workflow["name"] = request.name

        logger.info(f"Created workflow {workflow['id']} for user {user.get('id')}")

        return {
            "success": True,
            "workflow": workflow,
            "message": f"Workflow '{workflow['name']}' created successfully",
        }

    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=WorkflowListResponse)
async def list_workflows(
    active_only: bool = False, user: Dict = Depends(get_current_user)
):
    """List all workflows"""
    try:
        service = get_n8n_service()
        workflows = await service.list_workflows(active_only=active_only)

        return WorkflowListResponse(workflows=workflows, total=len(workflows))

    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/{workflow_id}", response_model=Dict)
async def execute_workflow(
    workflow_id: str,
    request: Optional[WorkflowExecuteRequest] = None,
    user: Dict = Depends(get_current_user),
):
    """Execute a specific workflow"""
    try:
        service = get_n8n_service()

        # Execute workflow
        execution = await service.execute_workflow(
            workflow_id, data=request.data if request else None
        )

        logger.info(
            f"Executed workflow {workflow_id} for user {user.get('id')}: "
            f"status={execution.status.value}"
        )

        return {
            "success": execution.status.value == "completed",
            "execution": execution.dict(),
            "message": f"Workflow execution {execution.status.value}",
        }

    except Exception as e:
        logger.error(f"Failed to execute workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/executions", response_model=Dict)
async def get_workflow_executions(
    workflow_id: str, limit: int = 10, user: Dict = Depends(get_current_user)
):
    """Get recent executions for a workflow"""
    try:
        service = get_n8n_service()
        executions = await service.get_workflow_executions(workflow_id, limit)

        return {
            "workflow_id": workflow_id,
            "executions": [e.dict() for e in executions],
            "total": len(executions),
        }

    except Exception as e:
        logger.error(f"Failed to get executions for workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{workflow_id}/pause", response_model=Dict)
async def pause_workflow(workflow_id: str, user: Dict = Depends(get_current_user)):
    """Pause a workflow"""
    try:
        service = get_n8n_service()
        success = await service.pause_workflow(workflow_id)

        if success:
            logger.info(f"Paused workflow {workflow_id} for user {user.get('id')}")
            return {"success": True, "message": f"Workflow {workflow_id} paused"}
        else:
            raise HTTPException(status_code=400, detail="Failed to pause workflow")

    except Exception as e:
        logger.error(f"Failed to pause workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{workflow_id}/resume", response_model=Dict)
async def resume_workflow(workflow_id: str, user: Dict = Depends(get_current_user)):
    """Resume a paused workflow"""
    try:
        service = get_n8n_service()
        success = await service.resume_workflow(workflow_id)

        if success:
            logger.info(f"Resumed workflow {workflow_id} for user {user.get('id')}")
            return {"success": True, "message": f"Workflow {workflow_id} resumed"}
        else:
            raise HTTPException(status_code=400, detail="Failed to resume workflow")

    except Exception as e:
        logger.error(f"Failed to resume workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{workflow_id}", response_model=Dict)
async def delete_workflow(workflow_id: str, user: Dict = Depends(get_current_user)):
    """Delete a workflow"""
    try:
        service = get_n8n_service()
        success = await service.delete_workflow(workflow_id)

        if success:
            logger.info(f"Deleted workflow {workflow_id} for user {user.get('id')}")
            return {"success": True, "message": f"Workflow {workflow_id} deleted"}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete workflow")

    except Exception as e:
        logger.error(f"Failed to delete workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=WorkflowMetricsResponse)
async def get_workflow_metrics(user: Dict = Depends(get_current_user)):
    """Get workflow performance metrics"""
    try:
        service = get_n8n_service()
        metrics = await service.get_workflow_metrics()

        # Calculate success rate
        total = metrics["execution_stats"]["total"]
        successful = metrics["execution_stats"]["successful"]
        success_rate = (successful / max(1, total)) * 100

        return WorkflowMetricsResponse(
            total_workflows=metrics["total_workflows"],
            active_workflows=metrics["active_workflows"],
            execution_stats=metrics["execution_stats"],
            success_rate=round(success_rate, 2),
        )

    except Exception as e:
        logger.error(f"Failed to get workflow metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=Dict)
async def get_workflow_templates(user: Dict = Depends(get_current_user)):
    """Get available workflow templates"""
    try:
        service = get_n8n_service()

        # Get template names and descriptions
        templates = []
        for name, template in service.workflow_templates.items():
            templates.append(
                {
                    "id": name,
                    "name": template.name,
                    "description": template.description,
                    "triggers": [t.value for t in template.triggers],
                }
            )

        return {"templates": templates, "total": len(templates)}

    except Exception as e:
        logger.error(f"Failed to get workflow templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))
