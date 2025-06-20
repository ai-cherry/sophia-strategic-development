import uuid

from fastapi import APIRouter, Depends

from ...agents.core.agent_router import agent_router
from ...agents.core.base_agent import Task
from ..security import verify_admin_key

router = APIRouter(
    prefix="/retool",
    tags=["Retool API - Simplified Auth"],
    dependencies=[Depends(verify_admin_key)],  # Secure all endpoints with the new key
)

# --- Executive Dashboard Endpoints ---


@router.get("/executive/dashboard-summary")
async def get_dashboard_summary():
    """Provides a high-level summary for the main executive dashboard KPIs."""
    return {
        "client_health": {"at_risk": 3, "healthy": 12, "total_score": 8.2},
        "sales_performance": {"calls_this_week": 47, "conversion_rate": 0.23},
        "competitive_alerts": ["Competitor X raised $50M", "New feature launch by Y"],
        "strategic_actions": ["Review Acme relationship", "Analyze Q4 pipeline"],
    }


@router.get("/executive/client-health-portfolio")
async def get_client_health_portfolio():
    """Returns a list of all clients with their current health scores for a table view."""
    # This would query the CLIENT_HEALTH_SCORES table in Snowflake
    return [
        {
            "id": "acme_corp",
            "name": "Acme Corporation",
            "health_score": 55,
            "trend": "declining",
            "renewal_date": "2024-09-15",
        },
        {
            "id": "globex",
            "name": "Globex Inc.",
            "health_score": 92,
            "trend": "stable",
            "renewal_date": "2024-11-20",
        },
        {
            "id": "initech",
            "name": "Initech",
            "health_score": 78,
            "trend": "improving",
            "renewal_date": "2025-01-10",
        },
    ]


@router.get("/executive/sales-performance")
async def get_sales_performance():
    """Returns data for sales performance charts."""
    # This would query Snowflake for aggregated call and deal data
    return {
        "team_talk_ratio": [
            {"sales_rep": "Alice", "talk_percent": 45, "listen_percent": 55},
            {"sales_rep": "Bob", "talk_percent": 60, "listen_percent": 40},
            {"sales_rep": "Charlie", "talk_percent": 52, "listen_percent": 48},
        ],
        "deal_win_rate_by_stage": [
            {"stage": "Initial Call", "win_rate": 0.8},
            {"stage": "Demo", "win_rate": 0.5},
            {"stage": "Negotiation", "win_rate": 0.3},
        ],
    }


@router.post("/executive/strategic-chat")
async def strategic_chat(query: dict):
    """Endpoint for the Retool chat interface to interact with the ExecutiveAgent."""
    executive_agent = agent_router.agent_instances.get("executive")
    if not executive_agent:
        return {"error": "ExecutiveAgent is not available."}

    task = Task(
        task_id=f"retool_chat_{uuid.uuid4().hex}",
        task_type="strategic_synthesis_query",
        agent_id="executive",
        task_data={"strategic_question": query.get("question")},
    )

    result = await executive_agent.process_task(task)
    return result.get("data", {"error": "Failed to get response."})
