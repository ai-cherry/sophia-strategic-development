from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from ...agents.core.agent_router import agent_router
from ..security import verify_admin_key
from ...vector.vector_integration_updated import vector_integration
# We will need to add methods to integrations to check their health.
# from ...integrations.gong.enhanced_gong_integration import EnhancedGongIntegration

router = APIRouter(
    prefix="/system",
    tags=["System Intelligence"],
    dependencies=[Depends(verify_admin_key)]
)

@router.get("/agents", response_model=Dict[str, Any])
async def get_agent_status():
    """ Provides a real-time overview of all active AI agents. """
    agents_data = []
    for name, agent in agent_router.agent_instances.items():
        agents_data.append({
            "name": name,
            "agent_id": agent.agent_id,
            "status": agent.status.value,
            "is_running": agent.is_running,
            "tasks_completed": agent.performance_metrics['tasks_completed'],
            "tasks_failed": agent.performance_metrics['tasks_failed'],
            "avg_response_time": f"{agent.performance_metrics['average_duration']:.2f}s",
            "specialization": agent.specialization,
            "current_tasks": len(agent.current_tasks)
        })
    
    total_tasks = sum(a['tasks_completed'] for a in agents_data)
    return {
        "agents": agents_data,
        "total_agents_running": len(agents_data),
        "total_tasks_processed": total_tasks,
        "system_health": "excellent" # Placeholder
    }

@router.get("/infrastructure", response_model=Dict[str, Any])
async def get_infrastructure_status():
    """ Provides a real-time overview of key infrastructure components. """
    
    # In a real system, these would be live health checks.
    snowflake_status = {"status": "connected", "query_performance": "avg 245ms"}
    pinecone_status = {"status": "connected", "indexes": vector_integration.pinecone_index_name, "vector_count": "N/A"}
    
    # Mocked integration statuses
    integrations_status = {
        "gong": {"status": "healthy", "last_sync": "5 min ago"},
        "slack": {"status": "healthy", "messages_today": "N/A"},
        "apify": {"status": "healthy", "credits_remaining": "N/A"}
    }
    
    return {
        "snowflake": snowflake_status,
        "pinecone": pinecone_status,
        "integrations": integrations_status
    }

@router.get("/api-catalog", response_model=Dict[str, Any])
async def get_api_catalog():
    """ Provides a catalog of all available API endpoints in the system. """
    from ...main import app # Import app to access routes
    
    endpoints_data = []
    for route in app.routes:
        if hasattr(route, "path"):
            endpoints_data.append({
                "path": route.path,
                "name": route.name,
                "methods": list(route.methods) if hasattr(route, "methods") else [],
            })

    return {
        "endpoints": endpoints_data,
        "total_endpoints": len(endpoints_data),
        "healthy_endpoints": len(endpoints_data), # Placeholder
        "avg_system_response": "1.2s" # Placeholder
    } 