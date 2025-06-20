"""Pay Ready AI Agent Orchestrator - Main Entry Point.

Centralized orchestration for all Pay Ready specialized AI agents.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agents.core.agent_router import agent_router
from backend.agents.core.base_agent import AgentConfig, BaseAgent
from backend.agents.core.orchestrator import SophiaOrchestrator
from backend.agents.specialized.executive_agent import ExecutiveAgent
from backend.analytics.real_time_business_intelligence import (
    RealTimeBusinessIntelligence,
)
from backend.app.api import file_processing_router, hybrid_rag_router
from backend.app.routers import agno_router, api_v1_router, llamaindex_router
from backend.app.routes import executive_routes, retool_api_routes, system_intel_routes
from backend.app.websockets import manager
from backend.core.config_manager import get_secret
from backend.integrations.enhanced_natural_language_processor import (
    EnhancedNaturalLanguageProcessor,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances
agent_orchestrator: Optional[SophiaOrchestrator] = None
nlp_processor: Optional[EnhancedNaturalLanguageProcessor] = None
business_intelligence: Optional[RealTimeBusinessIntelligence] = None


async def start_agents():
    """Initialize and start all registered agents."""
    logger.info("Starting all registered agents...")

    if "executive" not in agent_router.agent_instances:
        exec_config = AgentConfig(
            agent_id="executive_01",
            agent_type="specialized",
            specialization="Executive Synthesis",
        )
        executive_agent = ExecutiveAgent(exec_config)
        agent_router.agent_instances["executive"] = executive_agent
        agent_router.register_agent(
            name="executive",
            capabilities=[],
            handler=executive_agent.process_task,
            description="The CEO's dedicated interface for strategic intelligence.",
        )

    for agent_name, agent_instance in agent_router.agent_instances.items():
        if isinstance(agent_instance, BaseAgent) and not agent_instance.is_running:
            try:
                asyncio.create_task(agent_instance.start())
                logger.info(f"Agent '{agent_name}' has been scheduled to start.")
            except Exception as e:
                logger.error(f"Failed to start agent '{agent_name}': {e}")


async def shutdown_agents():
    """Stop all running agents gracefully."""
    logger.info("Shutting down all agents...")
    for agent_name, agent_instance in agent_router.agent_instances.items():
        if isinstance(agent_instance, BaseAgent) and agent_instance.is_running:
            try:
                await agent_instance.stop()
                logger.info(f"Agent '{agent_name}' has been stopped.")
            except Exception as e:
                logger.error(f"Failed to stop agent '{agent_name}': {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application's lifespan, starting and stopping services."""
    global agent_orchestrator, nlp_processor, business_intelligence
    logger.info("Initializing Pay Ready AI Agent System...")
    try:
        redis_host = await get_secret("redis", "host") or "localhost"
        postgres_conn = (
            await get_secret("postgres", "url")
            or "postgresql://user:pass@localhost/sophia_payready"
        )
        openai_api_key = await get_secret("openai", "api_key")

        agent_orchestrator = SophiaOrchestrator(
            redis_host=redis_host, postgres_connection=postgres_conn
        )
        nlp_config = {"openai_api_key": openai_api_key}
        nlp_processor = EnhancedNaturalLanguageProcessor(nlp_config)
        business_intelligence = None  # Placeholder initialization

        await agent_orchestrator.start()
        await start_agents()
        logger.info("Pay Ready AI Agent System initialized successfully.")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize Pay Ready AI Agent System: {e}")
        raise
    finally:
        logger.info("Shutting down Pay Ready AI Agent System...")
        if agent_orchestrator:
            await agent_orchestrator.stop()
        await shutdown_agents()


app = FastAPI(
    title="Pay Ready AI Agent System",
    description="Centralized AI agent orchestration for Pay Ready B2B operations",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class AgentTaskRequest(BaseModel):
    agent_type: str
    task_type: str
    data: Dict[str, Any]
    priority: str = "medium"
    context: Optional[Dict[str, Any]] = None


class MetricsRequest(BaseModel):
    time_period: str = "30_days"
    metric_types: Optional[List[str]] = None


@app.get("/")
async def root():
    """Return the root endpoint message."""
    return {
        "message": "Pay Ready AI Agent System",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Perform a health check of the system."""
    if not agent_orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    try:
        agents = await agent_orchestrator.agent_registry.get_all_agents()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "agent_orchestrator": (
                    "operational" if agent_orchestrator.is_running else "stopped"
                ),
                "nlp_processor": "operational" if nlp_processor else "inactive",
                "business_intelligence": (
                    "operational" if business_intelligence else "inactive"
                ),
            },
            "agent_summary": {
                "total_agents": len(agents),
                "active_agents": len([a for a in agents if a.status == "active"]),
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="System health check failed")


@app.post("/chat")
async def process_chat(request: ChatRequest):
    """Process a natural language chat request."""
    if not nlp_processor:
        raise HTTPException(status_code=503, detail="NLP Processor not initialized")
    try:
        response = await nlp_processor.process_request(
            query=request.message, context=request.context
        )
        return {"success": True, "response": response.to_dict()}
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.post("/agents/task")
async def submit_agent_task(request: AgentTaskRequest):
    """Submit a task to the orchestrator."""
    if not agent_orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    try:
        priority_map = {"critical": 5, "high": 4, "medium": 3, "low": 2, "default": 1}
        priority = priority_map.get(request.priority.lower(), 1)
        task_id = await agent_orchestrator.submit_task(
            task_type=request.task_type,
            task_data=request.data,
            priority=priority,
            context=request.context or {},
        )
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task submitted for {request.task_type}",
        }
    except Exception as e:
        logger.error(f"Agent task submission failed: {e}")
        raise HTTPException(status_code=500, detail=f"Task submission failed: {str(e)}")


@app.get("/agents/task/{task_id}")
async def get_task_result(task_id: str):
    """Get the result of a task."""
    if not agent_orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    try:
        result = await agent_orchestrator.task_router.get_task_status(task_id)
        if result is None:
            return {"success": False, "message": "Task not found or still processing"}
        return {"success": True, "result": result.result if result else None}
    except Exception as e:
        logger.error(f"Task result retrieval failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Task result retrieval failed: {str(e)}"
        )


@app.get("/agents/status")
async def get_agent_status(agent_type: Optional[str] = None):
    """Get the status of registered agents."""
    if not agent_orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    try:
        agents = await agent_orchestrator.agent_registry.get_all_agents()
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]
        return {"success": True, "status": [asdict(a) for a in agents]}
    except Exception as e:
        logger.error(f"Agent status retrieval failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Agent status retrieval failed: {str(e)}"
        )


@app.post("/metrics/dashboard")
async def get_business_dashboard(request: MetricsRequest):
    """Get a comprehensive business dashboard."""
    if not business_intelligence:
        raise HTTPException(status_code=503, detail="BI Service not initialized")
    try:
        dashboard = await business_intelligence.get_business_dashboard(
            time_period=request.time_period
        )
        return {"success": True, "dashboard": dashboard}
    except Exception as e:
        logger.error(f"Dashboard retrieval failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Dashboard retrieval failed: {str(e)}"
        )


@app.get("/metrics/executive-report")
async def get_executive_report(time_period: str = "30_days"):
    """Get an executive summary report."""
    if not business_intelligence:
        raise HTTPException(status_code=503, detail="BI Service not initialized")
    try:
        report = await business_intelligence.generate_executive_report(time_period)
        return {"success": True, "report": report}
    except Exception as e:
        logger.error(f"Executive report generation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Executive report generation failed: {str(e)}"
        )


@app.get("/nlp/performance")
async def get_nlp_performance():
    """Get NLP processor performance metrics."""
    if not nlp_processor:
        raise HTTPException(status_code=503, detail="NLP Processor not initialized")
    try:
        metrics = nlp_processor.get_performance_metrics()
        return {"success": True, "metrics": metrics}
    except Exception as e:
        logger.error(f"NLP performance retrieval failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"NLP performance retrieval failed: {str(e)}"
        )


@app.post("/agents/start-health-monitoring")
async def start_client_health_monitoring(background_tasks: BackgroundTasks):
    """Start continuous client health monitoring."""
    if not agent_orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    try:
        task_id = await agent_orchestrator.submit_task(
            task_type="analyze_client_health", task_data={}, priority=4
        )
        return {
            "success": True,
            "task_id": task_id,
            "message": "Client health monitoring started",
        }
    except Exception as e:
        logger.error(f"Health monitoring start failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Health monitoring start failed: {str(e)}"
        )


@app.post("/agents/analyze-sales-performance")
async def analyze_sales_performance():
    """Trigger a sales performance analysis."""
    if not agent_orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    try:
        task_id = await agent_orchestrator.submit_task(
            task_type="analyze_sales_performance", task_data={}, priority=4
        )
        return {
            "success": True,
            "task_id": task_id,
            "message": "Sales performance analysis started",
        }
    except Exception as e:
        logger.error(f"Sales analysis start failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Sales analysis start failed: {str(e)}"
        )


@app.post("/agents/market-research")
async def conduct_market_research(research_type: str = "industry_trends"):
    """Conduct a market research analysis."""
    if not agent_orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    try:
        task_id = await agent_orchestrator.submit_task(
            task_type=research_type, task_data={}, priority=3
        )
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Market research ({research_type}) started",
        }
    except Exception as e:
        logger.error(f"Market research start failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Market research start failed: {str(e)}"
        )


app.include_router(
    file_processing_router.router, prefix="/files", tags=["File Processing"]
)
app.include_router(hybrid_rag_router.router, prefix="/rag", tags=["RAG"])
app.include_router(agno_router.router, prefix="/agno", tags=["AGNO"])
app.include_router(llamaindex_router.router, prefix="/llamaindex", tags=["LlamaIndex"])
app.include_router(
    executive_routes.router, prefix="/executive", tags=["Executive Intelligence"]
)
app.include_router(
    retool_api_routes.router, prefix="/api", tags=["Retool API - Simplified Auth"]
)
app.include_router(
    system_intel_routes.router, prefix="/api", tags=["System Intelligence"]
)
app.include_router(api_v1_router.router, prefix="/api/v1", tags=["Dashboard API v1"])


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Handle websocket connections."""
    await manager.connect(websocket, client_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(client_id)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
