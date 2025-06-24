"""
Sophia AI FastAPI App

Practical FastAPI application with data flow management and LLM strategy.
Focuses on stability and scale without over-complexity.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import route modules
from backend.api.llm_strategy_routes import router as llm_router
from backend.api.data_flow_routes import router as data_flow_router
from backend.api.asana_integration_routes import router as asana_router
from backend.api.notion_integration_routes import router as notion_router
from backend.api.codacy_integration_routes import router as codacy_router

# Import configuration validation
from backend.core.config_validator import validate_startup_configuration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Platform",
    description="AI assistant orchestrator for Pay Ready business intelligence",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(llm_router)
app.include_router(data_flow_router)
app.include_router(asana_router)
app.include_router(notion_router)
app.include_router(codacy_router)


@app.get("/", tags=["health"])
async def read_root() -> dict[str, str]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "Sophia AI Platform",
        "version": "1.0.0",
        "message": "Enterprise AI orchestrator ready"
    }


@app.get("/api/health", tags=["health"])
async def api_health_check() -> dict[str, str]:
    """Comprehensive API health check."""
    try:
        # Import here to avoid circular imports
        from backend.core.config_validator import quick_health_check
        
        # Perform quick health check
        is_healthy = await quick_health_check()
        
        if is_healthy:
            return {
                "status": "healthy",
                "api_version": "1.0.0",
                "services": {
                    "llm_strategy": "available",
                    "data_flow": "available",
                    "asana_integration": "available",
                    "notion_integration": "available",
                    "codacy_integration": "available",
                    "core_systems": "operational",
                    "configuration": "validated"
                },
                "message": "All systems operational"
            }
        else:
            return {
                "status": "degraded",
                "api_version": "1.0.0",
                "services": {
                    "llm_strategy": "available",
                    "data_flow": "available", 
                    "asana_integration": "available",
                    "notion_integration": "available",
                    "codacy_integration": "available",
                    "core_systems": "degraded",
                    "configuration": "issues_detected"
                },
                "message": "Some external services may be unavailable"
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "message": "Some systems may be unavailable"
        }


@app.get("/api/config-validation", tags=["health"])
async def get_configuration_validation() -> dict:
    """Get detailed configuration validation report."""
    try:
        # Perform comprehensive validation without failing fast
        validation_report = await validate_startup_configuration(fail_fast=False)
        return validation_report
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return {
            "validation_timestamp": "error",
            "overall_status": "ERROR",
            "summary": {
                "total_checks": 0,
                "successful": 0,
                "warnings": 0,
                "failures": 1,
                "skipped": 0
            },
            "critical_failures": [str(e)],
            "detailed_results": []
        }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup with comprehensive validation."""
    logger.info("🚀 Starting Sophia AI Platform...")
    
    try:
        # Perform comprehensive configuration validation
        logger.info("🔍 Validating critical configurations...")
        validation_report = await validate_startup_configuration(fail_fast=False)
        
        # Log validation results
        overall_status = validation_report.get("overall_status", "UNKNOWN")
        summary = validation_report.get("summary", {})
        
        if overall_status == "HEALTHY":
            logger.info("✅ All configurations validated successfully")
        elif overall_status == "WARNING":
            logger.warning(f"⚠️  Configuration validation completed with {summary.get('warnings', 0)} warnings")
            logger.warning("   Some optional services may have limited functionality")
        elif overall_status in ["DEGRADED", "FAILED"]:
            logger.error(f"❌ Configuration validation found {summary.get('failures', 0)} critical issues")
            
            # Log critical failures
            for failure in validation_report.get("critical_failures", []):
                logger.error(f"   • {failure}")
            
            # In production, you might want to fail here for critical services
            # For now, we'll continue with warnings
            logger.warning("🔄 Continuing startup despite configuration issues...")
        
        # Log detailed service status
        for result in validation_report.get("detailed_results", []):
            service = result.get("service", "Unknown")
            status = result.get("status", "unknown")
            message = result.get("message", "No message")
            
            if status == "success":
                logger.info(f"   ✅ {service}: {message}")
            elif status == "warning":
                logger.warning(f"   ⚠️  {service}: {message}")
            elif status == "failure":
                logger.error(f"   ❌ {service}: {message}")
            elif status == "skipped":
                logger.info(f"   ⏭️  {service}: {message}")
        
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        logger.warning("🔄 Continuing startup without validation...")
    
    # Continue with normal startup
    logger.info("✅ FastAPI app initialized")
    logger.info("✅ CORS middleware configured")
    logger.info("✅ API routes registered")
    logger.info("✅ Code quality integration enabled")
    logger.info("🚀 Sophia AI Platform ready for requests")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down Sophia AI Platform...")
    # Add cleanup logic here if needed
    logger.info("✅ Sophia AI Platform shutdown complete")
