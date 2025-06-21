import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.agents.specialized.metrics_agent import AgentConfig, MetricsAgent

# Placeholder imports for intent parsing, agent routing, and MCP memory
# from backend.agents.core.intent_router import IntentRouter
# from backend.agents.core.agno_performance_optimizer import AgnoPerformanceOptimizer
# from backend.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)

router = APIRouter()


# --- Simple Rule-Based Intent Parser ---
def parse_intent(message: str):
    msg = message.lower()
    if "metrics" in msg or "agent status" in msg:
        return {"intent": "show_metrics"}
    elif "refactor" in msg:
        return {"intent": "refactor", "target": "codebase"}
    elif "deploy" in msg:
        return {"intent": "deploy", "target": "infrastructure"}
    elif "review" in msg:
        return {"intent": "review", "target": "code"}
    else:
        return {"intent": "unknown"}


# --- MetricsAgent Setup ---
metrics_agent_config = AgentConfig(
    agent_id="metrics_agent_01",
    agent_type="utility",
    specialization="Metrics",
)
# Use a global event loop for pooled instantiation
loop = asyncio.get_event_loop()
metrics_agent = loop.run_until_complete(MetricsAgent.pooled(metrics_agent_config))


# --- Placeholder Agno Agent Router ---
async def route_to_agno_agent(intent: dict, message: str):
    if intent["intent"] == "show_metrics":
        # Call the real MetricsAgent
        from backend.agents.core.base_agent import Task

        task = Task(
            task_id=f"metrics_{datetime.utcnow().isoformat()}",
            task_type="show_metrics",
            agent_id="metrics",
            task_data={"query": message, "timestamp": datetime.utcnow().isoformat()},
            status=None,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            result=None,
            error_message=None,
            priority=1,
        )
        result = await metrics_agent.process_task(task)
        return {"response": result, "type": "metrics"}
    elif intent["intent"] == "refactor":
        return {
            "response": "RefactorAgent: Refactoring codebase as requested.",
            "type": "refactor",
        }
    elif intent["intent"] == "deploy":
        return {
            "response": "DeploymentAgent: Deploying infrastructure to staging.",
            "type": "deploy",
        }
    elif intent["intent"] == "review":
        return {"response": "ReviewAgent: Reviewing code for issues.", "type": "review"}
    else:
        return {
            "response": f"Sorry, I didn't understand: '{message}'",
            "type": "unknown",
        }


@router.websocket("/api/chat/agent")
async def chat_agent_ws(websocket: WebSocket):
    """WebSocket endpoint for conversational agent orchestration.
    - Receives natural language messages from Cursor AI (or other chat clients)
    - Parses intent and routes to Agno agents (rule-based for now)
    - Integrates with MCP memory for persistent context (future)
    - Streams responses and logs back to the client

    Intent Mapping (for AI/human devs):
      - 'metrics', 'agent status' → show_metrics
      - 'refactor' → refactor
      - 'deploy' → deploy
      - 'review' → review
      - else → unknown
    """
    await websocket.accept()
    session_id = f"session_{datetime.utcnow().isoformat()}"
    logger.info(f"[Chat] New session started: {session_id}")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"[Chat] Received: {data}")
            intent = parse_intent(data)
            result = await route_to_agno_agent(intent, data)
            await websocket.send_json(
                {
                    "response": result["response"],
                    "intent": intent["intent"],
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
    except WebSocketDisconnect:
        logger.info(f"[Chat] Session ended: {session_id}")
    except Exception as e:
        logger.error(f"[Chat] Error: {e}")
        await websocket.close(code=1011)
