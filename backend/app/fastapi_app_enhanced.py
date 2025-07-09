"""
Enhanced FastAPI Application with Lambda Labs Serverless Integration
====================================================================
Production-ready FastAPI application with Lambda Labs Serverless,
cost monitoring, and intelligent AI orchestration.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Lambda Labs Serverless components
from backend.api.lambda_labs_serverless_routes import router as lambda_serverless_router
from backend.services.lambda_labs_serverless_service import get_lambda_service
from backend.services.lambda_labs_cost_monitor import get_cost_monitor, start_cost_monitoring
from backend.services.unified_chat_service_enhanced import get_enhanced_chat_service
from backend.core.auto_esc_config import get_lambda_labs_serverless_config, validate_lambda_labs_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for Lambda Labs Serverless
    
    Handles startup and shutdown of Lambda Labs services,
    cost monitoring, and background tasks.
    """
    # Startup
    logger.info("🚀 Starting Lambda Labs Serverless FastAPI application")
    
    try:
        # Validate configuration
        if not validate_lambda_labs_config():
            raise ValueError("Lambda Labs configuration validation failed")
        
        # Initialize services
        logger.info("Initializing Lambda Labs Serverless service...")
        lambda_service = await get_lambda_service()
        
        # Test service health
        health_check = await lambda_service.health_check()
        if health_check["status"] != "healthy":
            logger.warning(f"Lambda Labs service health check warning: {health_check}")
        
        # Initialize cost monitor
        logger.info("Initializing cost monitor...")
        cost_monitor = await get_cost_monitor()
        
        # Start cost monitoring
        logger.info("Starting cost monitoring...")
        await start_cost_monitoring()
        
        # Initialize enhanced chat service
        logger.info("Initializing enhanced chat service...")
        chat_service = await get_enhanced_chat_service()
        
        # Test chat service
        chat_health = await chat_service.health_check()
        if chat_health["overall_status"] == "unhealthy":
            logger.warning(f"Chat service health check warning: {chat_health}")
        
        # Store services in app state
        app.state.lambda_service = lambda_service
        app.state.cost_monitor = cost_monitor
        app.state.chat_service = chat_service
        
        # Log startup summary
        config = get_lambda_labs_serverless_config()
        logger.info(f"✅ Lambda Labs Serverless started successfully")
        logger.info(f"   Models available: {len(lambda_service.models)}")
        logger.info(f"   Daily budget: ${config.get('daily_budget', 0)}")
        logger.info(f"   Routing strategy: {config.get('routing_strategy')}")
        logger.info(f"   Monitoring active: {cost_monitor.monitoring_task is not None}")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    # Shutdown
    logger.info("🛑 Shutting down Lambda Labs Serverless application")
    
    try:
        # Stop cost monitoring
        if hasattr(app.state, 'cost_monitor'):
            await app.state.cost_monitor.stop_monitoring()
        
        # Close Lambda Labs service
        if hasattr(app.state, 'lambda_service'):
            await app.state.lambda_service.close()
        
        logger.info("✅ Shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title="Sophia AI - Lambda Labs Serverless",
    description="Revolutionary AI orchestration with Lambda Labs Serverless inference",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Lambda Labs Serverless routes
app.include_router(lambda_serverless_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Application health check
    
    Returns comprehensive health status including all Lambda Labs services.
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        # Check Lambda Labs service
        try:
            lambda_service = await get_lambda_service()
            lambda_health = await lambda_service.health_check()
            health_status["services"]["lambda_labs"] = lambda_health
        except Exception as e:
            health_status["services"]["lambda_labs"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check cost monitor
        try:
            cost_monitor = await get_cost_monitor()
            cost_report = await cost_monitor.get_cost_report()
            health_status["services"]["cost_monitor"] = {
                "status": "healthy",
                "monitoring_active": cost_report.get("monitoring_status", {}).get("active", False),
                "daily_cost": cost_report.get("current_costs", {}).get("daily_cost", 0),
                "alerts_count": len(cost_report.get("active_alerts", []))
            }
        except Exception as e:
            health_status["services"]["cost_monitor"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check enhanced chat service
        try:
            chat_service = await get_enhanced_chat_service()
            chat_health = await chat_service.health_check()
            health_status["services"]["chat_service"] = {
                "status": chat_health["overall_status"],
                "providers": chat_health["services"]
            }
        except Exception as e:
            health_status["services"]["chat_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Determine overall status
        service_statuses = [
            service.get("status", "unknown") 
            for service in health_status["services"].values()
        ]
        
        if any(status == "unhealthy" for status in service_statuses):
            health_status["status"] = "degraded"
        elif any(status not in ["healthy", "degraded"] for status in service_statuses):
            health_status["status"] = "unknown"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with Lambda Labs Serverless information
    """
    try:
        config = get_lambda_labs_serverless_config()
        lambda_service = await get_lambda_service()
        
        return {
            "message": "Sophia AI - Lambda Labs Serverless",
            "version": "1.0.0",
            "status": "operational",
            "features": [
                "Lambda Labs Serverless AI inference",
                "Intelligent model routing",
                "Cost optimization and monitoring",
                "Hybrid AI orchestration",
                "Real-time performance tracking"
            ],
            "models_available": len(lambda_service.models),
            "routing_strategy": config.get("routing_strategy"),
            "daily_budget": config.get("daily_budget"),
            "endpoints": {
                "chat": "/api/v1/lambda-labs-serverless/chat/completions",
                "analyze": "/api/v1/lambda-labs-serverless/analyze",
                "models": "/api/v1/lambda-labs-serverless/models/list",
                "usage": "/api/v1/lambda-labs-serverless/usage/stats",
                "health": "/health",
                "docs": "/docs"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Root endpoint error: {e}")
        return {
            "message": "Sophia AI - Lambda Labs Serverless",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# Chat endpoint (simplified interface)
@app.post("/chat")
async def simple_chat(request: dict):
    """
    Simplified chat endpoint for easy integration
    
    Accepts: {"message": "your question here"}
    Returns: {"response": "AI response", "metadata": {...}}
    """
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        chat_service = await get_enhanced_chat_service()
        result = await chat_service.chat_completion(message)
        
        return {
            "response": result["response"],
            "metadata": {
                "provider": result["provider"],
                "model_used": result["model_used"],
                "cost": result["cost"],
                "response_time": result["response_time"],
                "cached": result["cached"]
            }
        }
        
    except Exception as e:
        logger.error(f"Simple chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Analysis endpoint (simplified interface)
@app.post("/analyze")
async def simple_analyze(request: dict):
    """
    Simplified analysis endpoint
    
    Accepts: {"data": "data to analyze", "type": "analysis type"}
    Returns: {"analysis": "results", "metadata": {...}}
    """
    try:
        data = request.get("data", "")
        analysis_type = request.get("type", "general")
        
        if not data:
            raise HTTPException(status_code=400, detail="Data is required")
        
        chat_service = await get_enhanced_chat_service()
        
        # Create analysis prompt
        analysis_prompt = f"Analyze the following {analysis_type} data:\n\n{data}"
        
        result = await chat_service.chat_completion(
            analysis_prompt,
            {"analysis_type": analysis_type}
        )
        
        return {
            "analysis": result["response"],
            "metadata": {
                "provider": result["provider"],
                "model_used": result["model_used"],
                "cost": result["cost"],
                "response_time": result["response_time"],
                "analysis_type": analysis_type
            }
        }
        
    except Exception as e:
        logger.error(f"Simple analyze error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Dashboard endpoint
@app.get("/dashboard")
async def dashboard():
    """
    Dashboard endpoint with comprehensive system status
    """
    try:
        # Get services
        lambda_service = await get_lambda_service()
        cost_monitor = await get_cost_monitor()
        chat_service = await get_enhanced_chat_service()
        
        # Get statistics
        usage_stats = await lambda_service.get_usage_stats()
        cost_report = await cost_monitor.get_cost_report()
        performance_stats = await chat_service.get_performance_stats()
        
        return {
            "title": "Lambda Labs Serverless Dashboard",
            "timestamp": datetime.now().isoformat(),
            "usage": {
                "total_requests": usage_stats.get("total_requests", 0),
                "success_rate": usage_stats.get("success_rate", 0),
                "daily_cost": usage_stats.get("daily_cost", 0),
                "budget_remaining": usage_stats.get("budget_remaining", 0),
                "average_response_time": usage_stats.get("average_response_time", 0)
            },
            "cost_monitoring": {
                "current_daily_cost": cost_report.get("current_costs", {}).get("daily_cost", 0),
                "budget_utilization": cost_report.get("budget_status", {}).get("daily_utilization", 0),
                "active_alerts": len(cost_report.get("active_alerts", [])),
                "monitoring_active": cost_report.get("monitoring_status", {}).get("active", False)
            },
            "performance": {
                "total_requests": performance_stats.get("total_requests", 0),
                "average_response_time": performance_stats.get("average_response_time", 0),
                "cache_hit_rate": performance_stats.get("cache_hit_rate", 0),
                "provider_distribution": performance_stats.get("provider_distribution", {})
            },
            "models": {
                "available": len(lambda_service.models),
                "usage_distribution": usage_stats.get("model_usage", {}),
                "fallback_chain": lambda_service.fallback_chain
            }
        }
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Configuration endpoint
@app.get("/config")
async def get_configuration():
    """
    Get current configuration (without sensitive data)
    """
    try:
        config = get_lambda_labs_serverless_config()
        
        # Remove sensitive data
        safe_config = {
            "inference_endpoint": config.get("inference_endpoint"),
            "daily_budget": config.get("daily_budget"),
            "monthly_budget": config.get("monthly_budget"),
            "routing_strategy": config.get("routing_strategy"),
            "enable_hybrid_ai": config.get("enable_hybrid_ai"),
            "enable_cost_optimization": config.get("enable_cost_optimization"),
            "response_time_target": config.get("response_time_target"),
            "availability_target": config.get("availability_target"),
            "max_input_tokens": config.get("max_input_tokens"),
            "max_output_tokens": config.get("max_output_tokens")
        }
        
        return {
            "configuration": safe_config,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Configuration endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


# Development server
if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "prod") != "prod"
    
    logger.info(f"Starting Lambda Labs Serverless FastAPI server on {host}:{port}")
    
    uvicorn.run(
        "backend.app.fastapi_app_enhanced:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 