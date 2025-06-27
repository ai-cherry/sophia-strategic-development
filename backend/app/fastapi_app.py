"""
Sophia AI FastAPI App

Practical FastAPI application with data flow management and LLM strategy.
Focuses on stability and scale without over-complexity.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# Import route modules
from backend.api.llm_strategy_routes import router as llm_router
from backend.api.data_flow_routes import router as data_flow_router
from backend.api.asana_integration_routes import router as asana_router
from backend.api.notion_integration_routes import router as notion_router
from backend.api.codacy_integration_routes import router as codacy_router

# Import enhanced configuration validation
from backend.core.config_validator import validate_deployment_readiness

# Import SchemaDiscoveryService and get_logger
from backend.services.schema_discovery_service import SchemaDiscoveryService
from backend.utils.logging import get_logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment
ENVIRONMENT = os.getenv("SOPHIA_ENVIRONMENT", "dev")

# Create FastAPI app
app = FastAPI(
    title="Sophia AI Platform",
    description="AI assistant orchestrator for Pay Ready business intelligence",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
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
        "message": "Enterprise AI orchestrator ready",
        "environment": ENVIRONMENT
    }


@app.get("/api/health", tags=["health"])
async def api_health_check() -> dict[str, str]:
    """Comprehensive API health check with deployment validation."""
    try:
        # Perform deployment readiness validation
        validation_report = await validate_deployment_readiness(ENVIRONMENT)

        # Map deployment status to health status
        if validation_report.overall_status == "READY":
            status = "healthy"
            message = "All systems operational and deployment ready"
        elif validation_report.overall_status == "PARTIAL":
            status = "degraded"
            message = "Core systems operational with some warnings"
        else:
            status = "unhealthy"
            message = "Critical configuration issues detected"

        return {
            "status": status,
            "api_version": "1.0.0",
            "environment": ENVIRONMENT,
            "deployment_status": validation_report.overall_status,
            "services": {
                "llm_strategy": "available",
                "data_flow": "available",
                "asana_integration": "available",
                "notion_integration": "available",
                "codacy_integration": "available",
                "core_systems": status,
                "configuration": "validated",
            },
            "validation_summary": {
                "total_checks": validation_report.total_checks,
                "passed_checks": validation_report.passed_checks,
                "failed_checks": validation_report.failed_checks,
                "warning_checks": validation_report.warning_checks,
                "critical_failures": len(validation_report.critical_failures)
            },
            "message": message,
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Health check system failure",
            "environment": ENVIRONMENT
        }


@app.get("/api/deployment-validation", tags=["health"])
async def get_deployment_validation() -> dict:
    """Get comprehensive deployment validation report."""
    try:
        # Perform comprehensive deployment validation
        validation_report = await validate_deployment_readiness(ENVIRONMENT)
        
        # Convert to API response format
        return {
            "overall_status": validation_report.overall_status,
            "environment": validation_report.environment,
            "validation_timestamp": validation_report.validation_timestamp.isoformat(),
            "execution_time": validation_report.execution_time,
            "summary": {
                "total_checks": validation_report.total_checks,
                "passed_checks": validation_report.passed_checks,
                "failed_checks": validation_report.failed_checks,
                "warning_checks": validation_report.warning_checks,
            },
            "critical_failures": [
                {
                    "service": f.service.value,
                    "check_name": f.check_name,
                    "message": f.message,
                    "details": f.details
                } for f in validation_report.critical_failures
            ],
            "warnings": [
                {
                    "service": w.service.value,
                    "check_name": w.check_name,
                    "message": w.message,
                    "details": w.details
                } for w in validation_report.warnings
            ],
            "recommendations": validation_report.recommendations,
            "deployment_ready": validation_report.overall_status == "READY"
        }
        
    except Exception as e:
        logger.error(f"Deployment validation failed: {e}")
        return {
            "overall_status": "ERROR",
            "environment": ENVIRONMENT,
            "validation_timestamp": "error",
            "execution_time": 0.0,
            "summary": {
                "total_checks": 0,
                "passed_checks": 0,
                "failed_checks": 1,
                "warning_checks": 0,
            },
            "critical_failures": [
                {
                    "service": "validation_system",
                    "check_name": "system_error",
                    "message": f"Validation system error: {str(e)}",
                    "details": None
                }
            ],
            "warnings": [],
            "recommendations": ["Fix deployment validation system before proceeding"],
            "deployment_ready": False
        }


# Startup event with enhanced validation
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup with comprehensive deployment validation."""
    logger.info(f"🚀 Starting Sophia AI Platform in {ENVIRONMENT} environment...")

    try:
        # Perform comprehensive deployment readiness validation
        logger.info("🔍 Performing deployment readiness validation...")
        validation_report = await validate_deployment_readiness(ENVIRONMENT)

        # Log validation results with enhanced detail
        overall_status = validation_report.overall_status
        
        logger.info("📊 Validation Summary:")
        logger.info(f"   Overall Status: {overall_status}")
        logger.info(f"   Total Checks: {validation_report.total_checks}")
        logger.info(f"   Passed: {validation_report.passed_checks}")
        logger.info(f"   Failed: {validation_report.failed_checks}")
        logger.info(f"   Warnings: {validation_report.warning_checks}")
        logger.info(f"   Execution Time: {validation_report.execution_time:.2f}s")

        # Handle different validation outcomes
        if overall_status == "READY":
            logger.info("✅ All deployment validations passed - system ready for production")
            
        elif overall_status == "PARTIAL":
            logger.warning(f"⚠️  Deployment validation completed with {len(validation_report.warnings)} warnings")
            logger.warning("   Core functionality available but some features may be limited")
            
            # Log warnings
            for warning in validation_report.warnings:
                logger.warning(f"   • {warning.service.value}: {warning.message}")
                
        elif overall_status == "NOT_READY":
            logger.error(f"❌ Deployment validation failed with {len(validation_report.critical_failures)} critical issues")
            logger.error("   System is NOT ready for production deployment")
            
            # Log critical failures
            for failure in validation_report.critical_failures:
                logger.error(f"   • {failure.service.value}: {failure.message}")
            
            # Log recommendations
            logger.error("📋 Required Actions:")
            for rec in validation_report.recommendations:
                logger.error(f"   {rec}")
            
            # For production environments, fail fast on critical issues
            if ENVIRONMENT.lower() == "prod":
                logger.error("🚨 PRODUCTION DEPLOYMENT BLOCKED - Critical failures must be resolved")
                raise RuntimeError(f"Production deployment blocked: {len(validation_report.critical_failures)} critical failures")
            else:
                logger.warning("🔄 Continuing startup in development mode despite critical issues...")

        # Log recommendations if any
        if validation_report.recommendations:
            logger.info("📋 Recommendations:")
            for rec in validation_report.recommendations:
                logger.info(f"   {rec}")

        # Initialize and apply semantic layer
        logger.info("Initializing and applying semantic layer...")
        discovery_service = SchemaDiscoveryService()
        success = await discovery_service.apply_semantic_layer()
        if success:
            logger.info("Semantic layer applied successfully during startup.")
        else:
            logger.error("Failed to apply semantic layer during startup.")

    except Exception as e:
        logger.error(f"❌ Deployment validation failed: {e}")
        
        # For production, fail fast on validation errors
        if ENVIRONMENT.lower() == "prod":
            logger.error("🚨 PRODUCTION STARTUP FAILED - Validation system error")
            raise RuntimeError(f"Production startup failed: {str(e)}")
        else:
            logger.warning("🔄 Continuing startup without validation in development mode...")

    # Continue with normal startup
    logger.info("✅ FastAPI app initialized")
    logger.info("✅ CORS middleware configured")
    logger.info("✅ API routes registered")
    logger.info("✅ Enhanced deployment validation enabled")
    logger.info(f"🚀 Sophia AI Platform ready for requests in {ENVIRONMENT} environment")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down Sophia AI Platform...")
    # Add cleanup logic here if needed
    logger.info("✅ Sophia AI Platform shutdown complete")
