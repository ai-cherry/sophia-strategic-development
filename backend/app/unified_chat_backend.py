#!/usr/bin/env python3
"""
🎯 SOPHIA AI - UNIFIED CHAT BACKEND
Central orchestrator for all MCP servers and provides real business intelligence for Pay Ready CEO

🚨 FILE TYPE: PERMANENT
🔐 SECRET MANAGEMENT: Pulumi ESC integrated
🏗️ ARCHITECTURE: Hub-and-spoke with MCP server orchestration

Business Context:
- Supports Pay Ready CEO (80 employees, $50M revenue)
- Real-time business intelligence across all systems
- Unified chat interface for executive decision support

Performance Requirements:
- Response Time: <200ms for simple queries, <2s for complex analysis
- Throughput: 1000+ concurrent requests
- Uptime: >99.9%
- Real-time data synchronization
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import aiohttp
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.services.unified_chat_orchestrator import UnifiedChatOrchestrator

# Import services
from backend.services.unified_chat_service import UnifiedChatService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# MCP Server Configuration
MCP_SERVERS = {
    "asana": {
        "url": "http://localhost:9100",
        "description": "Task and project management",
    },
    "notion": {
        "url": "http://localhost:9102",
        "description": "Knowledge base and documentation",
    },
    "slack": {
        "url": "http://localhost:9103",
        "description": "Team communication and insights",
    },
    "linear": {
        "url": "http://localhost:9101",
        "description": "Engineering project tracking",
    },
    "github": {
        "url": "http://localhost:9104",
        "description": "Code repository management",
    },
    "snowflake": {
        "url": "http://localhost:9200",
        "description": "Data analytics and AI processing",
    },
    "hubspot": {
        "url": "http://localhost:9006",
        "description": "CRM and sales pipeline",
    },
    "gong": {
        "url": "http://localhost:9007",
        "description": "Sales call analysis and coaching",
    },
}


@dataclass
class ChatMessage:
    """Structured chat message."""

    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    sources: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BusinessIntelligenceQuery:
    """Structured business intelligence query."""

    query: str
    intent: str  # project_status, task_management, sales_analysis, team_insights, etc.
    urgency: str  # low, medium, high, critical
    context: dict[str, Any] = field(default_factory=dict)
    user_role: str = "ceo"


class MCPServerClient:
    """Client for communicating with MCP servers."""

    def __init__(self, server_name: str, server_config: dict[str, str]):
        self.name = server_name
        self.url = server_config["url"]
        self.description = server_config["description"]
        self.session = None
        self.healthy = False
        self.response_time = 0.0

    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        await self.health_check()

    async def cleanup(self):
        """Cleanup HTTP session."""
        if self.session:
            await self.session.close()

    async def health_check(self) -> bool:
        """Check if MCP server is healthy."""
        try:
            start_time = datetime.now()

            if not self.session:
                return False

            async with self.session.get(f"{self.url}/health") as response:
                self.response_time = (datetime.now() - start_time).total_seconds()
                self.healthy = response.status == 200
                return self.healthy

        except Exception as e:
            logger.warning(f"Health check failed for {self.name}: {e}")
            self.healthy = False
            return False

    async def query(
        self, endpoint: str, method: str = "GET", data: Optional[dict] = None
    ) -> dict[str, Any]:
        """Execute query against MCP server."""
        try:
            if not self.session or not self.healthy:
                return {"error": f"Server {self.name} not available"}

            start_time = datetime.now()
            url = f"{self.url}{endpoint}"

            if method.upper() == "GET":
                async with self.session.get(url, params=data) as response:
                    result = await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    result = await response.json()
            else:
                return {"error": f"Unsupported method: {method}"}

            response_time = (datetime.now() - start_time).total_seconds()

            # Add metadata
            result["_metadata"] = {
                "server": self.name,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
            }

            return result

        except Exception as e:
            logger.error(f"Query failed for {self.name}: {e}")
            return {"error": str(e), "server": self.name}


class UnifiedChatOrchestrator:
    """Central orchestrator for all business intelligence queries."""

    def __init__(self):
        self.mcp_clients = {}
        self.chat_history = []
        self.active_connections = []

    async def initialize(self):
        """Initialize all MCP clients."""
        logger.info("Initializing MCP server clients...")

        for server_name, config in MCP_SERVERS.items():
            client = MCPServerClient(server_name, config)
            await client.initialize()
            self.mcp_clients[server_name] = client

            if client.healthy:
                logger.info(
                    f"✅ {server_name} server connected ({client.response_time:.3f}s)"
                )
            else:
                logger.warning(f"❌ {server_name} server unavailable")

    async def cleanup(self):
        """Cleanup all MCP clients."""
        for client in self.mcp_clients.values():
            await client.cleanup()

    async def get_system_health(self) -> dict[str, Any]:
        """Get comprehensive system health status."""
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "servers": {},
            "metrics": {
                "total_servers": len(self.mcp_clients),
                "healthy_servers": 0,
                "avg_response_time": 0.0,
                "active_connections": len(self.active_connections),
            },
        }

        total_response_time = 0.0

        for name, client in self.mcp_clients.items():
            await client.health_check()

            health_data["servers"][name] = {
                "healthy": client.healthy,
                "response_time": client.response_time,
                "description": client.description,
                "url": client.url,
            }

            if client.healthy:
                health_data["metrics"]["healthy_servers"] += 1
                total_response_time += client.response_time

        # Calculate averages
        healthy_count = health_data["metrics"]["healthy_servers"]
        if healthy_count > 0:
            health_data["metrics"]["avg_response_time"] = (
                total_response_time / healthy_count
            )

        # Determine overall status
        health_percentage = healthy_count / health_data["metrics"]["total_servers"]
        if health_percentage < 0.5:
            health_data["overall_status"] = "critical"
        elif health_percentage < 0.8:
            health_data["overall_status"] = "degraded"

        return health_data

    async def analyze_query_intent(self, query: str) -> BusinessIntelligenceQuery:
        """Analyze user query to determine intent and routing."""
        query_lower = query.lower()

        # Determine intent based on keywords
        if any(
            word in query_lower
            for word in ["task", "project", "deadline", "milestone", "asana"]
        ):
            intent = "project_management"
        elif any(
            word in query_lower
            for word in ["team", "slack", "communication", "message"]
        ):
            intent = "team_insights"
        elif any(
            word in query_lower
            for word in ["sale", "deal", "revenue", "hubspot", "crm"]
        ):
            intent = "sales_analysis"
        elif any(
            word in query_lower
            for word in ["code", "github", "repository", "commit", "linear"]
        ):
            intent = "engineering_insights"
        elif any(
            word in query_lower for word in ["data", "analytics", "snowflake", "report"]
        ):
            intent = "data_analysis"
        elif any(
            word in query_lower for word in ["document", "note", "knowledge", "notion"]
        ):
            intent = "knowledge_management"
        else:
            intent = "general_inquiry"

        # Determine urgency
        if any(
            word in query_lower for word in ["urgent", "asap", "critical", "emergency"]
        ):
            urgency = "critical"
        elif any(word in query_lower for word in ["important", "priority", "soon"]):
            urgency = "high"
        elif any(
            word in query_lower for word in ["when convenient", "eventually", "later"]
        ):
            urgency = "low"
        else:
            urgency = "medium"

        return BusinessIntelligenceQuery(
            query=query,
            intent=intent,
            urgency=urgency,
            context={"timestamp": datetime.now().isoformat()},
        )

    async def execute_business_intelligence_query(
        self, bi_query: BusinessIntelligenceQuery
    ) -> dict[str, Any]:
        """Execute business intelligence query across relevant MCP servers."""
        logger.info(f"Executing BI query: {bi_query.intent} - {bi_query.query[:50]}...")

        results = {
            "query": bi_query.query,
            "intent": bi_query.intent,
            "urgency": bi_query.urgency,
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "data": {},
            "insights": [],
            "recommendations": [],
        }

        # Route query to appropriate MCP servers based on intent
        if bi_query.intent == "project_management":
            # Query Asana for project and task data
            if "asana" in self.mcp_clients and self.mcp_clients["asana"].healthy:
                tasks = await self.mcp_clients["asana"].query("/tasks")
                projects = await self.mcp_clients["asana"].query("/projects")

                results["sources"].append("asana")
                results["data"]["tasks"] = tasks
                results["data"]["projects"] = projects

                # Generate insights
                if "tasks" in tasks and tasks["tasks"]:
                    completed_tasks = [t for t in tasks["tasks"] if t.get("completed")]
                    overdue_tasks = [
                        t
                        for t in tasks["tasks"]
                        if t.get("due_on")
                        and t["due_on"] < datetime.now().strftime("%Y-%m-%d")
                    ]

                    results["insights"].append(
                        f"You have {len(tasks['tasks'])} total tasks, {len(completed_tasks)} completed"
                    )
                    if overdue_tasks:
                        results["insights"].append(
                            f"⚠️ {len(overdue_tasks)} tasks are overdue and need immediate attention"
                        )

                    results["recommendations"].append(
                        "Focus on overdue tasks first to maintain project momentum"
                    )

        elif bi_query.intent == "team_insights":
            # Query Slack for team communication patterns
            if "slack" in self.mcp_clients and self.mcp_clients["slack"].healthy:
                slack_data = await self.mcp_clients["slack"].query("/insights")
                results["sources"].append("slack")
                results["data"]["slack"] = slack_data
                results["insights"].append("Team communication analysis available")

        elif bi_query.intent == "sales_analysis":
            # Query HubSpot for sales pipeline data
            if "hubspot" in self.mcp_clients and self.mcp_clients["hubspot"].healthy:
                deals = await self.mcp_clients["hubspot"].query("/deals")
                results["sources"].append("hubspot")
                results["data"]["sales"] = deals
                results["insights"].append("Sales pipeline analysis complete")

        elif bi_query.intent == "data_analysis":
            # Query Snowflake for data analytics
            if (
                "snowflake" in self.mcp_clients
                and self.mcp_clients["snowflake"].healthy
            ):
                analytics = await self.mcp_clients["snowflake"].query("/analytics")
                results["sources"].append("snowflake")
                results["data"]["analytics"] = analytics
                results["insights"].append("Data analysis complete")

        # Always provide a helpful response even if no specific data
        if not results["sources"]:
            results["insights"].append(
                "I understand your question but the relevant data sources are currently unavailable."
            )
            results["recommendations"].append(
                "Please check system status or contact support if this persists."
            )

        return results


# Create FastAPI app
app = FastAPI(
    title="Sophia AI - Unified Chat Backend with Temporal Learning",
    description="Central orchestrator for Pay Ready business intelligence with temporal learning",
    version="3.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = UnifiedChatOrchestrator()

# Initialize services
chat_service = UnifiedChatService()
temporal_service = None

# Try to import temporal learning
try:
    from backend.services.temporal_qa_learning_service import (
        get_temporal_qa_learning_service,
    )

    TEMPORAL_LEARNING_AVAILABLE = True
    temporal_service = get_temporal_qa_learning_service()
    logger.info("Temporal learning service initialized")
except ImportError:
    TEMPORAL_LEARNING_AVAILABLE = False


# Pydantic models
class ChatRequest(BaseModel):
    message: str
    context: Optional[dict[str, Any]] = None
    user_id: str = "default_user"
    session_id: str = "default_session"


class ChatResponse(BaseModel):
    response: str
    metadata: dict[str, Any]
    temporal_learning_applied: bool = False
    temporal_interaction_id: Optional[str] = None


class TemporalCorrectionRequest(BaseModel):
    interaction_id: str
    correction: str
    context: Optional[dict[str, Any]] = None


class TemporalCorrectionResponse(BaseModel):
    success: bool
    interaction_id: str
    message: str


class TemporalValidationRequest(BaseModel):
    interaction_id: str
    is_correct: bool
    feedback: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator and services on startup."""
    logger.info("🚀 Starting Sophia AI Unified Chat Backend with Temporal Learning...")
    await orchestrator.initialize()
    await chat_service.initialize()
    logger.info("✅ Unified Chat Backend with Temporal Learning ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Shutting down Unified Chat Backend with Temporal Learning...")
    await orchestrator.cleanup()
    await chat_service.cleanup()
    logger.info("Services shutdown complete")


@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "service": "Sophia AI - Unified Chat Backend with Temporal Learning",
        "version": "3.0.0",
        "status": "operational",
        "description": "Central orchestrator for Pay Ready business intelligence with temporal learning",
        "features": [
            "Natural language business intelligence",
            "MCP server integration",
            "Temporal learning and adaptation",
            "Multi-source data synthesis",
            "Interactive learning corrections",
        ],
        "endpoints": {
            "health": "/health",
            "chat": "/api/v3/chat",
            "system_status": "/api/v3/system/status",
            "mcp_servers": "/api/v3/mcp/servers",
            "temporal_learning": "/api/v1/temporal-learning/",
        },
        "company": "Pay Ready",
        "user_base": "CEO and executive team",
        "temporal_learning_available": TEMPORAL_LEARNING_AVAILABLE,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "unified_chat_backend_with_temporal_learning",
        "version": "3.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }


@app.get("/api/v3/system/status")
async def get_system_status():
    """Get comprehensive system status including all MCP servers and temporal learning."""
    mcp_servers = {}

    # Check MCP server status
    for server_name, server_client in chat_service.servers.items():
        mcp_servers[server_name] = {
            "name": server_name,
            "url": server_client.url,
            "healthy": server_client.healthy,
            "response_time": server_client.response_time,
            "description": server_client.description,
        }

    # Check temporal learning status
    temporal_status = {
        "available": TEMPORAL_LEARNING_AVAILABLE,
        "service_healthy": temporal_service is not None,
        "interactions_count": len(temporal_service.learning_interactions)
        if temporal_service
        else 0,
        "knowledge_count": len(temporal_service.temporal_knowledge)
        if temporal_service
        else 0,
    }

    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "mcp_servers": mcp_servers,
        "temporal_learning": temporal_status,
        "services": {
            "chat_service": "healthy",
            "temporal_learning": "healthy" if temporal_service else "unavailable",
        },
    }


@app.get("/api/v3/mcp/servers")
async def get_mcp_servers():
    """Get list of all MCP servers and their status."""
    servers = {}
    for name, client in orchestrator.mcp_clients.items():
        servers[name] = {
            "name": name,
            "description": client.description,
            "url": client.url,
            "healthy": client.healthy,
            "response_time": client.response_time,
        }
    return {"servers": servers, "total": len(servers)}


@app.post("/api/v3/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for business intelligence queries with temporal learning."""
    try:
        # Process the query with temporal learning integration
        result = await chat_service.process_query(
            query=request.message,
            user_id=request.user_id,
            session_id=request.session_id,
            context=request.context or {},
        )

        return ChatResponse(
            response=result["response"],
            metadata=result["metadata"],
            temporal_learning_applied=result["metadata"].get(
                "temporal_learning_applied", False
            ),
            temporal_interaction_id=result["metadata"].get("temporal_interaction_id"),
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    orchestrator.active_connections.append(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Process message
            bi_query = await orchestrator.analyze_query_intent(
                message_data.get("message", "")
            )
            results = await orchestrator.execute_business_intelligence_query(bi_query)

            # Send response
            response = {
                "type": "chat_response",
                "response": f"Based on your {bi_query.intent} query:",
                "insights": results["insights"],
                "recommendations": results["recommendations"],
                "sources": results["sources"],
                "timestamp": datetime.now().isoformat(),
            }

            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        orchestrator.active_connections.remove(websocket)
        logger.info("WebSocket client disconnected")


# Temporal learning endpoints
@app.post(
    "/api/v1/temporal-learning/chat/correct", response_model=TemporalCorrectionResponse
)
async def temporal_correction_endpoint(request: TemporalCorrectionRequest):
    """
    Process user correction for temporal learning
    """
    if not temporal_service:
        raise HTTPException(
            status_code=503, detail="Temporal learning service not available"
        )

    try:
        result = await chat_service.process_temporal_correction(
            interaction_id=request.interaction_id,
            correction=request.correction,
            user_id="default_user",
            session_id="default_session",
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return TemporalCorrectionResponse(
            success=True,
            interaction_id=request.interaction_id,
            message="Correction processed successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Temporal correction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/temporal-learning/interactions/{interaction_id}/validate")
async def temporal_validation_endpoint(
    interaction_id: str, request: TemporalValidationRequest
):
    """
    Validate a temporal learning interaction
    """
    if not temporal_service:
        raise HTTPException(
            status_code=503, detail="Temporal learning service not available"
        )

    try:
        # Find and update the interaction
        interaction = next(
            (
                i
                for i in temporal_service.learning_interactions
                if i.id == interaction_id
            ),
            None,
        )

        if not interaction:
            raise HTTPException(status_code=404, detail="Interaction not found")

        # Update validation status
        interaction.validated = request.is_correct
        if request.feedback:
            interaction.context["validation_feedback"] = request.feedback

        return {
            "success": True,
            "interaction_id": interaction_id,
            "validated": request.is_correct,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Temporal validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/temporal-learning/dashboard/data")
async def temporal_dashboard_data():
    """
    Get temporal learning dashboard data
    """
    if not temporal_service:
        # Return mock data if service not available
        return {
            "total_interactions": 0,
            "learning_accuracy": 0.0,
            "knowledge_concepts": 0,
            "system_status": "unavailable",
            "recent_interactions": [],
            "learning_suggestions": ["Temporal learning service not available"],
        }

    try:
        insights = await chat_service.get_temporal_learning_insights("default_user")

        if "error" in insights:
            raise HTTPException(status_code=503, detail=insights["error"])

        return insights

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Temporal dashboard data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/temporal-learning/health")
async def temporal_health_check():
    """
    Health check for temporal learning service
    """
    if not temporal_service:
        return {
            "status": "unavailable",
            "service": "temporal_qa_learning",
            "error": "Service not initialized",
        }

    try:
        return {
            "status": "healthy",
            "service": "temporal_qa_learning",
            "system_date": datetime.now().isoformat(),
            "total_interactions": len(temporal_service.learning_interactions),
            "total_knowledge": len(temporal_service.temporal_knowledge),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    port = int(os.getenv("CHAT_BACKEND_PORT", "8000"))
    logger.info(
        f"🚀 Starting Sophia AI Unified Chat Backend with Temporal Learning on port {port}"
    )

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info", access_log=True)
