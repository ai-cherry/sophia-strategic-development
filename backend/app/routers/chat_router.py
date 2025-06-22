import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.agents.specialized.metrics_agent import AgentConfig, MetricsAgent
from backend.agents.specialized.sentry_agent import SentryAgent
from backend.agents.specialized.call_analysis_agent import CallAnalysisAgent
from backend.agents.specialized.executive_agent import ExecutiveAgent
from backend.agents.specialized.sales_coach_agent import SalesCoachAgent
from backend.agents.specialized.crm_sync_agent import CRMSyncAgent
from backend.agents.specialized.insight_extraction_agent import InsightExtractionAgent
from backend.agents.specialized.project_intelligence_agent import ProjectIntelligenceAgent
from backend.agents.specialized.hr_agent import HRAgent
from backend.agents.core.base_agent import Task

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Configurable Intent-to-Agent Mapping ---
AGNO_AGENT_MAP = {
    "show_metrics": (MetricsAgent, "show_metrics"),
    "analyze_call": (CallAnalysisAgent, "analyze_call"),
    "sentry_issue": (SentryAgent, "fetch_sentry_issue_context"),
    "executive": (ExecutiveAgent, "executive_summary"),
    "sales_coach": (SalesCoachAgent, "coach_sales"),
    "crm_sync": (CRMSyncAgent, "sync_crm"),
    "insight_extraction": (InsightExtractionAgent, "extract_insights"),
    "project_intel": (ProjectIntelligenceAgent, "project_report"),
    "hr": (HRAgent, "hr_status"),
}

# --- Enhanced Intent Parser ---
def parse_intent(message: str):
    msg = message.lower()
    if "metrics" in msg or "agent status" in msg:
        return {"intent": "show_metrics"}
    elif "call analysis" in msg or "analyze call" in msg:
        return {"intent": "analyze_call"}
    elif "sentry" in msg or "issue" in msg:
        return {"intent": "sentry_issue"}
    elif "executive" in msg:
        return {"intent": "executive"}
    elif "sales coach" in msg:
        return {"intent": "sales_coach"}
    elif "crm sync" in msg or "sync crm" in msg:
        return {"intent": "crm_sync"}
    elif "insight" in msg:
        return {"intent": "insight_extraction"}
    elif "project" in msg:
        return {"intent": "project_intel"}
    elif "hr" in msg or "human resources" in msg:
        return {"intent": "hr"}
    elif "refactor" in msg:
        return {"intent": "refactor", "target": "codebase"}
    elif "deploy" in msg:
        return {"intent": "deploy", "target": "infrastructure"}
    elif "review" in msg:
        return {"intent": "review", "target": "code"}
    else:
        return {"intent": "unknown"}

# --- Pooled Agent Instances (cache for session) ---
pooled_agents = {}
async def get_pooled_agent(agent_class, agent_id):
    key = (agent_class.__name__, agent_id)
    if key not in pooled_agents:
        config = AgentConfig(agent_id=agent_id, agent_type="chat", specialization=agent_class.__name__)
        pooled_agents[key] = await agent_class.pooled(config)
    return pooled_agents[key]

# --- Enhanced Agno Agent Router ---
async def route_to_agno_agent(intent: dict, message: str):
    agent_info = AGNO_AGENT_MAP.get(intent["intent"])
    if agent_info:
        agent_class, task_type = agent_info
        agent_id = f"{intent['intent']}_agent"
        agent = await get_pooled_agent(agent_class, agent_id)
        task = Task(
            task_id=f"{intent['intent']}_{datetime.utcnow().isoformat()}",
            task_type=task_type,
            agent_id=agent_id,
            task_data={"query": message, "timestamp": datetime.utcnow().isoformat()},
            status=None,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            result=None,
            error_message=None,
            priority=1,
        )
        try:
            result = await agent.process_task(task)
            return {"response": result, "type": intent["intent"]}
        except Exception as e:
            logger.error(f"[Agno] Agent {agent_id} failed: {e}", exc_info=True)
            return {"response": f"Agent error: {e}", "type": intent["intent"]}
    elif intent["intent"] == "refactor":
        return {"response": "RefactorAgent: Refactoring codebase as requested.", "type": "refactor"}
    elif intent["intent"] == "deploy":
        return {"response": "DeploymentAgent: Deploying infrastructure to staging.", "type": "deploy"}
    elif intent["intent"] == "review":
        return {"response": "ReviewAgent: Reviewing code for issues.", "type": "review"}
    else:
        return {"response": f"Sorry, I didn't understand: '{message}'", "type": "unknown"}

# --- Placeholder for MCP Memory Integration ---
# TODO: Integrate with MCP memory for persistent context
# Example: store/retrieve session context, user history, etc.

@router.websocket("/api/chat/agent")
async def chat_agent_ws(websocket: WebSocket):
    """WebSocket endpoint for conversational agent orchestration.

    - Receives natural language messages from Cursor AI (or other chat clients)
    - Parses intent and routes to Agno agents (config-driven)
    - Streams responses and logs back to the client
    - (Future) Integrates with MCP memory for persistent context
    """
    await websocket.accept()
    session_id = f"session_{datetime.utcnow().isoformat()}"
    logger.info(f"[Chat] New session started: {session_id}")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"[Chat] Received: {data}")
            intent = parse_intent(data)
            # TODO: Retrieve session context from MCP memory here
            result = await route_to_agno_agent(intent, data)
            # TODO: Store updated session context to MCP memory here
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
        logger.error(f"[Chat] Error: {e}", exc_info=True)
        await websocket.close(code=1011)
