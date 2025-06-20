"""Simplified Backend for Sophia AI Dashboards
This version focuses on providing the essential APIs for Retool dashboards
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Dashboard Backend",
    description="Simplified backend for Retool dashboards",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin key for authentication
ADMIN_KEY = os.getenv("SOPHIA_ADMIN_KEY", "sophia_admin_2024")


# Authentication dependency
async def verify_admin_key(x_admin_key: str = Header(None)):
    """Verify admin key for protected endpoints"""
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return True


# Pydantic models
class StrategicChatRequest(BaseModel):
    message: str
    mode: str = "internal"
    model_id: Optional[str] = "gpt-4"


class StrategicChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    timestamp: str


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Sophia AI Dashboard Backend",
        "version": "1.0.0",
        "status": "operational",
    }


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "backend": "healthy",
            "database": "simulated",
            "integrations": "partial",
        },
    }


# CEO Dashboard endpoints
@app.get(
    "/api/retool/executive/dashboard-summary", dependencies=[Depends(verify_admin_key)]
)
async def get_dashboard_summary():
    """Get executive dashboard summary"""
    return {
        "revenue": {
            "current_month": 125000,
            "last_month": 115000,
            "growth": 8.7,
            "ytd": 1450000,
        },
        "clients": {"total": 45, "active": 42, "at_risk": 3, "new_this_month": 5},
        "ai_performance": {
            "tasks_completed": 1247,
            "avg_response_time": 2.3,
            "accuracy": 94.5,
            "user_satisfaction": 4.7,
        },
        "system_health": {
            "uptime": 99.9,
            "api_calls": 45678,
            "active_agents": 12,
            "queue_size": 23,
        },
    }


@app.get(
    "/api/retool/executive/client-health-portfolio",
    dependencies=[Depends(verify_admin_key)],
)
async def get_client_health_portfolio():
    """Get client health portfolio data"""
    return {
        "clients": [
            {
                "name": "Innovate Corp",
                "health_score": 55,
                "mrr": 12000,
                "risk_factors": ["competitor_mentioned", "usage_drop"],
                "last_interaction": "2024-06-18",
                "account_manager": "Sarah Chen",
            },
            {
                "name": "QuantumLeap",
                "health_score": 78,
                "mrr": 25000,
                "risk_factors": ["renewal_coming"],
                "last_interaction": "2024-06-19",
                "account_manager": "Mike Johnson",
            },
            {
                "name": "Stellar Solutions",
                "health_score": 92,
                "mrr": 18000,
                "risk_factors": [],
                "last_interaction": "2024-06-20",
                "account_manager": "Emily Davis",
            },
        ]
    }


@app.post(
    "/api/retool/executive/strategic-chat", dependencies=[Depends(verify_admin_key)]
)
async def strategic_chat(request: StrategicChatRequest):
    """Process strategic chat request"""
    # Simulate AI response
    responses = {
        "client health": "Based on current data, 3 clients are at risk. Innovate Corp shows the highest risk with competitor mentions and usage drop. Recommend immediate outreach.",
        "revenue": "Revenue is up 8.7% month-over-month. YTD revenue of $1.45M puts us on track to exceed annual target by 12%.",
        "default": f"I understand you're asking about '{request.message}'. Let me analyze the relevant data and provide insights.",
    }

    # Determine response based on message content
    message_lower = request.message.lower()
    if "client" in message_lower or "health" in message_lower:
        response_text = responses["client health"]
    elif "revenue" in message_lower:
        response_text = responses["revenue"]
    else:
        response_text = responses["default"]

    return StrategicChatResponse(
        response=response_text,
        sources=[
            {"type": "database", "name": "Client Health Metrics"},
            {"type": "integration", "name": "Gong Call Analysis"},
        ],
        timestamp=datetime.utcnow().isoformat(),
    )


@app.get(
    "/api/retool/executive/openrouter-models", dependencies=[Depends(verify_admin_key)]
)
async def get_openrouter_models():
    """Get available OpenRouter models"""
    return {
        "models": [
            {"id": "gpt-4", "name": "GPT-4", "provider": "OpenAI"},
            {"id": "claude-3-opus", "name": "Claude 3 Opus", "provider": "Anthropic"},
            {
                "id": "claude-3-sonnet",
                "name": "Claude 3 Sonnet",
                "provider": "Anthropic",
            },
        ]
    }


# Knowledge Admin endpoints
@app.get("/api/knowledge/stats", dependencies=[Depends(verify_admin_key)])
async def get_knowledge_stats():
    """Get knowledge base statistics"""
    return {
        "total_documents": 156,
        "total_chunks": 3421,
        "categories": {"sales": 45, "product": 38, "support": 29, "general": 44},
        "last_updated": datetime.utcnow().isoformat(),
    }


@app.get("/api/knowledge/search", dependencies=[Depends(verify_admin_key)])
async def search_knowledge(q: str):
    """Search knowledge base"""
    return {
        "query": q,
        "results": [
            {
                "id": "doc_001",
                "title": "Sales Best Practices",
                "snippet": f"...relevant content about {q}...",
                "score": 0.95,
                "category": "sales",
            },
            {
                "id": "doc_002",
                "title": "Product Guide",
                "snippet": f"...information related to {q}...",
                "score": 0.87,
                "category": "product",
            },
        ],
        "total": 2,
    }


# Project Management endpoints
@app.get(
    "/api/project-management/dashboard/summary",
    dependencies=[Depends(verify_admin_key)],
)
async def get_project_dashboard_summary():
    """Get project management dashboard summary"""
    return {
        "summary": {
            "total_projects": 12,
            "status_breakdown": {
                "on_track": 7,
                "at_risk": 3,
                "blocked": 1,
                "completed": 1,
            },
            "health_score": 78.5,
        },
        "projects": [
            {
                "id": "proj_001",
                "name": "AI Integration Phase 2",
                "status": "on_track",
                "progress": 65,
                "sources": ["linear", "github"],
                "okr_alignment": ["okr_q1_001", "okr_q1_003"],
            },
            {
                "id": "proj_002",
                "name": "Customer Portal Redesign",
                "status": "at_risk",
                "progress": 42,
                "sources": ["linear", "slack"],
                "okr_alignment": ["okr_q1_002"],
            },
        ],
    }


@app.get(
    "/api/project-management/okr/alignment", dependencies=[Depends(verify_admin_key)]
)
async def get_okr_alignment(quarter: str = "Q1_2024"):
    """Get OKR alignment data"""
    return {
        "quarter": quarter,
        "objectives": [
            {
                "id": "okr_q1_001",
                "title": "Increase Customer Satisfaction",
                "progress": 72,
                "key_results": [
                    {"title": "NPS > 50", "current": 48, "target": 50},
                    {"title": "Support Response < 2hrs", "current": 1.8, "target": 2},
                ],
            },
            {
                "id": "okr_q1_002",
                "title": "Expand Market Share",
                "progress": 58,
                "key_results": [
                    {"title": "New Customers: 20", "current": 12, "target": 20},
                    {"title": "Revenue Growth: 25%", "current": 18, "target": 25},
                ],
            },
        ],
    }


# Integration test endpoints
@app.get("/api/integrations/test-all", dependencies=[Depends(verify_admin_key)])
async def test_all_integrations():
    """Test all integrations"""
    return {
        "status": "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "integrations": {
            "snowflake": {"connected": False, "error": "Credentials not configured"},
            "gong": {"connected": False, "error": "API key missing"},
            "slack": {"connected": False, "error": "Bot token not set"},
            "pinecone": {"connected": False, "error": "API key missing"},
            "linear": {"connected": False, "error": "API key missing"},
            "openai": {"connected": True, "model": "gpt-4"},
        },
    }


@app.get("/api/integrations/{service}/test", dependencies=[Depends(verify_admin_key)])
async def test_integration(service: str):
    """Test individual integration"""
    integrations = {
        "snowflake": {"connected": False, "error": "Credentials not configured"},
        "gong": {"connected": False, "error": "API key missing"},
        "slack": {"connected": False, "error": "Bot token not set"},
        "pinecone": {"connected": False, "error": "API key missing"},
        "linear": {"connected": False, "error": "API key missing"},
        "openai": {"connected": True, "model": "gpt-4"},
    }

    if service not in integrations:
        raise HTTPException(status_code=404, detail=f"Integration {service} not found")

    return integrations[service]


# System endpoints
@app.get("/api/system/agents", dependencies=[Depends(verify_admin_key)])
async def get_agent_status():
    """Get status of AI agents"""
    return {
        "agents": [
            {"name": "Executive Agent", "status": "active", "tasks_completed": 234},
            {"name": "Sales Coach", "status": "active", "tasks_completed": 156},
            {"name": "Knowledge Manager", "status": "active", "tasks_completed": 89},
            {
                "name": "Project Intelligence",
                "status": "active",
                "tasks_completed": 312,
            },
        ]
    }


# Executive endpoints for the simplified backend
@app.get("/api/executive/summary", dependencies=[Depends(verify_admin_key)])
async def get_executive_summary():
    """Get executive summary (simplified version)"""
    return {
        "data": {
            "revenue": {"current_month": 125000, "last_month": 115000, "growth": 8.7},
            "clients": {"total": 45, "active": 42, "at_risk": 3},
            "ai_metrics": {"tasks_today": 127, "avg_response_time": 2.3},
        }
    }


@app.get("/api/executive/alerts", dependencies=[Depends(verify_admin_key)])
async def get_executive_alerts():
    """Get executive alerts"""
    return {
        "alerts": [
            {
                "id": "alert_001",
                "priority": "high",
                "type": "opportunity",
                "message": "3 upsell opportunities identified from recent Gong calls",
                "timestamp": datetime.utcnow().isoformat(),
            },
            {
                "id": "alert_002",
                "priority": "medium",
                "type": "risk",
                "message": "Client health score dropped for Innovate Corp",
                "timestamp": datetime.utcnow().isoformat(),
            },
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "main_dashboard:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
