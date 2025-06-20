"""Simplified Sophia AI Backend"""
import logging
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Executive Dashboard API",
    description="Simplified API for CEO Dashboard",
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


@app.get("/")
async def root():
    return {
        "message": "Sophia AI Executive Dashboard API",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/executive/summary")
async def get_executive_summary():
    """Get executive summary data"""
    return {
        "revenue": {"current": 2500000, "target": 3000000, "growth": 0.15},
        "customers": {"total": 150, "new_this_month": 12, "churn_rate": 0.02},
        "operations": {"efficiency_score": 0.92, "cost_reduction": 0.08},
        "ai_insights": {"opportunities": 5, "risks": 2, "recommendations": 3},
    }


@app.get("/api/executive/metrics")
async def get_executive_metrics():
    """Get detailed metrics"""
    return {
        "kpis": [
            {"name": "Revenue Growth", "value": 15, "unit": "%", "trend": "up"},
            {
                "name": "Customer Satisfaction",
                "value": 4.8,
                "unit": "/5",
                "trend": "stable",
            },
            {"name": "Operational Efficiency", "value": 92, "unit": "%", "trend": "up"},
            {"name": "AI Automation Rate", "value": 78, "unit": "%", "trend": "up"},
        ],
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/executive/alerts")
async def get_executive_alerts():
    """Get executive alerts"""
    return {
        "alerts": [
            {
                "id": 1,
                "type": "opportunity",
                "title": "High-value lead identified",
                "description": "AI detected a potential $500K opportunity",
                "priority": "high",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "id": 2,
                "type": "risk",
                "title": "Customer churn risk",
                "description": "3 enterprise customers showing churn indicators",
                "priority": "medium",
                "timestamp": datetime.now().isoformat(),
            },
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
