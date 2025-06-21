#!/usr/bin/env python3
"""
Simple FastAPI server startup for Sophia AI
Bypasses complex configuration for development
"""

import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to path
sys.path.append('.')

# Set minimal required environment variables
os.environ['PULUMI_ORG'] = 'scoobyjava-org'
os.environ['PULUMI_ACCESS_TOKEN'] = 'your-pulumi-access-token'
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'
os.environ['GONG_ACCESS_KEY'] = 'your-gong-access-key'
os.environ['GONG_CLIENT_SECRET'] = 'your-gong-client-secret'
os.environ['RETOOL_API_TOKEN'] = 'your-retool-api-token'
os.environ['POSTGRES_PASSWORD'] = 'postgres'
os.environ['SECRET_KEY'] = 'sophia_ai_secret_key_2024'
os.environ['DEBUG'] = 'false'

# Create simple FastAPI app
app = FastAPI(
    title="Sophia AI API",
    description="AI-powered business intelligence platform",
    version="1.0.0"
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
    return {"message": "Sophia AI API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sophia-ai"}

@app.get("/api/v1/dashboard/metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics for CEO dashboard"""
    return {
        "revenue": {
            "current": 1250000,
            "previous": 1100000,
            "growth": 13.6
        },
        "sales": {
            "deals_closed": 23,
            "pipeline_value": 3400000,
            "conversion_rate": 18.5
        },
        "team": {
            "active_users": 156,
            "productivity_score": 87,
            "satisfaction": 4.2
        }
    }

@app.get("/api/v1/gong/insights")
async def get_gong_insights():
    """Get Gong call insights"""
    return {
        "total_calls": 145,
        "avg_duration": 28.5,
        "sentiment_score": 0.72,
        "top_topics": ["pricing", "features", "timeline"]
    }

if __name__ == "__main__":
    print("🚀 Starting Sophia AI FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

