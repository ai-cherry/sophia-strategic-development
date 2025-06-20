from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import HTTPBearer
from jose import jwt
from pydantic import BaseModel
import uuid

from ...agents.core.agent_router import agent_router
from ...agents.core.base_agent import Task
from .security import UserRole, get_current_user_role
from ...core.config_manager import get_secret

router = APIRouter()

class StrategicQuery(BaseModel):
    question: str

@router.post("/strategic-query", tags=["Executive Intelligence"])
async def strategic_query(
    query: StrategicQuery,
    current_role: UserRole = Depends(get_current_user_role)
):
    """
    Accepts a high-level strategic question from the CEO, routes it to the
    ExecutiveAgent, and returns the synthesized intelligence briefing.
    """
    if current_role != UserRole.CEO:
        raise HTTPException(status_code=403, detail="Forbidden: This endpoint is for executive use only.")

    executive_agent = agent_router.agent_instances.get("executive")
    if not executive_agent:
        raise HTTPException(status_code=503, detail="ExecutiveAgent is not available.")

    # Create and process the task
    task = Task(
        task_id=f"exec_task_{uuid.uuid4().hex}",
        task_type="strategic_synthesis_query",
        agent_id="executive",
        task_data={"strategic_question": query.question}
    )
    
    result = await executive_agent.process_task(task)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to process strategic query."))

    return result.get("data") 