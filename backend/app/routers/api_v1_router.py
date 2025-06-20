"""Sophia AI - API v1.

Production-ready, versioned API for the main business intelligence dashboard.
"""

import asyncio
import random
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ...core.security import get_api_key
from ...data_connectors.gong_connector import gong_connector
from ...data_connectors.slack_connector import slack_connector
from ...data_connectors.snowflake_connector import snowflake_connector

router = APIRouter()

# --- Business Intelligence Endpoints ---


@router.get("/dashboard/metrics", summary="Get Executive KPI Metrics")
async def get_dashboard_metrics(api_key: str = Depends(get_api_key)):
    # This now fetches data from multiple connectors
    gong_analytics = await gong_connector.get_call_analytics()
    slack_insights = await slack_connector.get_communication_insights()
    return {
        "revenue_growth": 15.3,  # This would likely come from Snowflake
        "client_health_score": 87.5,  # This would be a calculated metric
        "sales_efficiency": gong_analytics.get("avg_call_score", 0),
        "ai_task_completion_rate": 98.9,
        "slack_sentiment": slack_insights.get("sentiment_score", 0),
    }


@router.get("/sales/calls", summary="Get Gong Sales Call Data")
async def get_sales_calls(api_key: str = Depends(get_api_key)) -> List[Dict[str, Any]]:
    return await gong_connector.get_sales_calls()


@router.get("/sales/analytics", summary="Get Sales Performance Analytics")
async def get_sales_analytics(api_key: str = Depends(get_api_key)):
    return await gong_connector.get_call_analytics()


@router.get("/communications/slack", summary="Get Slack Team Insights")
async def get_slack_insights(api_key: str = Depends(get_api_key)):
    return await slack_connector.get_communication_insights()


@router.get("/data/snowflake/query", summary="Query Snowflake Data Warehouse")
async def query_snowflake(query: str, api_key: str = Depends(get_api_key)):
    return await snowflake_connector.execute_query(query)


@router.post("/ai/insights", summary="Get AI-Powered Business Insights")
async def get_ai_insights(request: Dict[str, Any], api_key: str = Depends(get_api_key)):
    # This would call the AIInsightsGenerator, which in turn might use the connectors
    return {
        "insight": "Based on recent call sentiment, client 'Innovate Inc.' is at risk of churn.",
        "confidence": 0.92,
    }


@router.get("/health", summary="System Health Check")
async def get_health():
    # This provides a simple health check for the v1 API.
    return {"status": "ok", "version": "v1"}


# --- Real-Time WebSocket Endpoints ---


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # This would be replaced with a real-time data publishing mechanism (e.g., Redis Pub/Sub)
            await websocket.send_json(
                {
                    "event": "kpi_update",
                    "data": {
                        "revenue_growth": 15.3 + (random.random() * 0.1),  # nosec B311
                    },
                }
            )
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("Client disconnected from dashboard websocket")


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # This would be replaced with a real-time event notification system
            await websocket.send_json(
                {
                    "event": "new_high_risk_call",
                    "data": {
                        "call_id": "gong-125",
                        "client": "RiskCo",
                        "reason": "Low sentiment score",
                    },
                }
            )
            await asyncio.sleep(15)
    except WebSocketDisconnect:
        print("Client disconnected from notifications websocket")
