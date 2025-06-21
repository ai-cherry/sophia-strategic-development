"""API Router for all Agno-based agent interactions.

This is the single entry point for any user- or system-initiated agent tasks.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.agents.core.agent_framework import agent_framework

logger = logging.getLogger(__name__)
router = APIRouter()


class AgentTaskRequest(BaseModel):
    """Defines the structure for a request to an agent."""

    agent_name: str
    task_description: str
    payload: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class AgentTaskResponse(BaseModel):
    """Defines the structure for a response from an agent task."""task_id: str.

    status: str
    message: str
    result: Optional[Dict[str, Any]] = None


@router.post(
    "/task", response_model=AgentTaskResponse, status_code=status.HTTP_202_ACCEPTED
)
async def execute_agent_task(request: AgentTaskRequest):
    """Receives a task, validates it, and forwards it to the specified Agno agent.

            This endpoint is the primary interaction point with the agent framework.
    """if not agent_framework.is_initialized:.

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Agent Framework is not initialized. Please try again later.",
        )

    logger.info(f"Received task for agent: '{request.agent_name}'")

    try:
        # Here, you would interface with the Agno client to dispatch the task.
        # The agent_framework would handle the actual invocation.
        # For now, we'll use a mock response.

        # Example of how it might look:
        # task_id, status, result = await agent_framework.dispatch_task(
        #     agent_name=request.agent_name,
        #     task_description=request.task_description,
        #     payload=request.payload
        # )

        mock_task_id = "mock_task_12345"
        logger.info(f"Dispatching task to Agno client. Mock Task ID: {mock_task_id}")

        # Arize tracing would happen within the agent_framework dispatch method
        agent_framework.arize_client.trace(
            {
                "event": "task_received",
                "agent_name": request.agent_name,
                "task_id": mock_task_id,
            }
        )

        return AgentTaskResponse(
            task_id=mock_task_id,
            status="accepted",
            message=f"Task for agent '{request.agent_name}' has been accepted and is being processed.",
        )

    except Exception as e:
        logger.error(
            f"Failed to execute task for agent '{request.agent_name}': {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while processing the task for agent '{request.agent_name}'.",
        )


@router.get("/status", status_code=status.HTTP_200_OK)
async def get_agents_status():
    """Retrieves the current status of the agent framework and all registered agents."""
    if not agent_framework.is_initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The Agent Framework is not initialized.",
        )

    return await agent_framework.get_status()
