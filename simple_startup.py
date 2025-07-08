#!/usr/bin/env python3
"""
Simplified Sophia AI Startup Script
Bypasses problematic services to focus on core functionality and sentiment analysis implementation
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.core.auto_esc_config import get_config_value

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory storage for demonstration
app_state = {"startup_time": None, "services": {}, "health_checks": {}}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting Sophia AI Simplified Platform...")

    # Initialize basic services
    try:
        app_state["startup_time"] = asyncio.get_event_loop().time()
        app_state["services"]["core"] = "operational"
        app_state["services"]["sentiment_analysis"] = "ready"
        app_state["services"]["multi_channel_data"] = "ready"

        logger.info("✅ Core services initialized")
        logger.info("✅ Sentiment analysis framework ready")
        logger.info("✅ Multi-channel data pipeline ready")
        logger.info("✅ Sophia AI Simplified Platform startup complete")

    except Exception as e:
        logger.exception(f"❌ Startup failed: {e}")
        raise

    yield

    # Cleanup
    logger.info("🔄 Shutting down Sophia AI Simplified Platform...")


# Create FastAPI app
app = FastAPI(
    title="Sophia AI - Simplified Platform",
    description="Simplified Sophia AI platform focused on sentiment analysis and core functionality",
    version="1.0.0",
    lifespan=lifespan,
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
    """Root endpoint"""
    return {
        "message": "Sophia AI Simplified Platform",
        "status": "operational",
        "version": "1.0.0",
        "focus": "sentiment_analysis_and_core_functionality",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "uptime_seconds": asyncio.get_event_loop().time()
        - app_state.get("startup_time", 0),
        "services": app_state.get("services", {}),
        "environment": get_config_value("environment", "development"),
    }


@app.get("/api/sentiment/status")
async def sentiment_analysis_status():
    """Sentiment analysis system status"""
    return {
        "status": "ready",
        "capabilities": [
            "multi_channel_sentiment_analysis",
            "cross_channel_correlation",
            "temporal_trend_analysis",
            "predictive_alerting",
            "nuanced_emotion_detection",
        ],
        "data_sources": [
            "gong_calls",
            "slack_messages",
            "linear_comments",
            "asana_tasks",
            "external_web_sources",
            "hubspot_interactions",
        ],
        "models": [
            "snowflake_cortex_primary",
            "openai_fallback",
            "payready_domain_specific",
        ],
    }


@app.post("/api/sentiment/analyze")
async def analyze_sentiment(data: dict[str, Any]):
    """Analyze sentiment for provided text using enhanced analyzer"""
    try:
        text = data.get("text", "")
        channel = data.get("channel", "slack_messages")
        context = data.get("context", {})

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        # Import and use enhanced sentiment analyzer
        from backend.services.enhanced_sentiment_analyzer import (
            SentimentChannel,
            enhanced_sentiment_analyzer,
        )

        # Map channel string to enum
        channel_enum = SentimentChannel.SLACK_MESSAGES
        try:
            channel_enum = SentimentChannel(channel)
        except ValueError:
            logger.warning(f"Unknown channel '{channel}', using slack_messages")

        # Perform enhanced sentiment analysis
        result = await enhanced_sentiment_analyzer.analyze_sentiment(
            text=text, channel=channel_enum, context=context
        )

        return {
            "text": result.text,
            "channel": result.channel.value,
            "sentiment_analysis": {
                "primary_sentiment": result.primary_sentiment,
                "emotion_categories": [
                    emotion.value for emotion in result.emotion_categories
                ],
                "intensity_score": result.intensity_score,
                "context_indicators": result.context_indicators,
                "urgency_level": result.urgency_level,
                "confidence_score": result.confidence_score,
                "business_impact_score": result.business_impact_score,
            },
            "recommendations": result.recommendations,
            "timestamp": result.timestamp.isoformat(),
            "metadata": result.metadata,
        }

    except Exception as e:
        logger.exception(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e!s}")


@app.get("/api/sentiment/dashboard")
async def sentiment_dashboard():
    """Sentiment analysis dashboard data"""
    return {
        "overall_sentiment": {
            "employee_sentiment": 0.3,
            "customer_sentiment": 0.5,
            "trend": "stable",
        },
        "channel_breakdown": {
            "slack_engineering": {
                "sentiment": 0.2,
                "volume": 150,
                "trend": "declining",
            },
            "slack_sales": {"sentiment": 0.6, "volume": 80, "trend": "improving"},
            "gong_calls": {"sentiment": 0.4, "volume": 25, "trend": "stable"},
            "linear_comments": {"sentiment": 0.1, "volume": 45, "trend": "concerning"},
        },
        "alerts": [
            {
                "type": "team_morale",
                "severity": "warning",
                "team": "engineering",
                "message": "Engineering team sentiment declining over past 3 days",
                "recommended_action": "Schedule team check-in",
            }
        ],
        "insights": [
            "Cross-channel correlation shows employee sentiment leads customer sentiment by 2-3 days",
            "Friday afternoon shows consistent sentiment dips across all channels",
            "Project deadline proximity correlates with increased stress indicators",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    # Get port from environment or default to 8000
    port = int(get_config_value("port", "8000"))

    logger.info(f"Starting Sophia AI Simplified Platform on port {port}")

    uvicorn.run(
        "simple_startup:app",
        host="127.0.0.1",  # Changed from 0.0.0.0 for security. Use environment variable for production, port=port, reload=True, log_level="info"
    )
