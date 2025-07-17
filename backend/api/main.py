"""
Main FastAPI Application for Sophia AI Backend
Provides the core API structure and routing
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from backend.core.auto_esc_config import get_config_value
from backend.core.database import init_database, check_database_health
from backend.core.security import check_security_health
from backend.services.service_discovery import get_service_discovery
from backend.security.config import get_security_config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    
    # Startup
    logger.info("🚀 Starting Sophia AI Backend...")
    
    try:
        # Initialize database
        init_database()
        logger.info("✅ Database initialized")
        
        # Initialize service discovery
        service_discovery = await get_service_discovery()
        logger.info("✅ Service discovery started")
        
        # Store in app state
        app.state.service_discovery = service_discovery
        
        logger.info("🎯 Sophia AI Backend started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise
        
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Sophia AI Backend...")
    
    try:
        if hasattr(app.state, 'service_discovery'):
            await app.state.service_discovery.stop()
            logger.info("✅ Service discovery stopped")
            
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")
        
    logger.info("✅ Sophia AI Backend shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    # Get security configuration
    security_config = get_security_config()
    
    # Create FastAPI app
    app = FastAPI(
        title="Sophia AI Backend API",
        description="Enterprise AI orchestration platform for Pay Ready",
        version="4.0.0",
        lifespan=lifespan,
        docs_url="/docs" if not security_config.environment == "prod" else None,
        redoc_url="/redoc" if not security_config.environment == "prod" else None
    )
    
    # Add security middleware
    _add_security_middleware(app, security_config)
    
    # Add API routes
    _add_routes(app)
    
    # Add exception handlers
    _add_exception_handlers(app)
    
    logger.info(f"✅ FastAPI app created for {security_config.environment} environment")
    return app


def _add_security_middleware(app: FastAPI, security_config):
    """Add security middleware to the application"""
    
    # CORS middleware
    api_config = security_config.get_api_security_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_config["cors_origins"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware for production
    if security_config.environment == "prod":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["app.sophia-intel.ai", "api.sophia-intel.ai"]
        )
        
    logger.info("✅ Security middleware configured")


def _add_routes(app: FastAPI):
    """Add API routes to the application"""
    
    @app.get("/")
    async def root():
        """Root endpoint with basic info"""
        return {
            "service": "Sophia AI Backend",
            "version": "4.0.0",
            "status": "operational",
            "environment": get_config_value("ENVIRONMENT", "prod")
        }
        
    @app.get("/health")
    async def health_check():
        """Comprehensive health check endpoint"""
        try:
            # Check database health
            db_health = check_database_health()
            
            # Check security health
            security_health = check_security_health()
            
            # Check service discovery health
            service_discovery = await get_service_discovery()
            service_health = await service_discovery.get_health_summary()
            
            # Overall health determination
            overall_healthy = (
                db_health.get("status") == "healthy" and
                security_health.get("status") == "healthy" and
                service_health.get("healthy_services", 0) > 0
            )
            
            return {
                "status": "healthy" if overall_healthy else "degraded",
                "timestamp": service_health["last_check"],
                "components": {
                    "database": db_health,
                    "security": security_health,
                    "services": service_health
                },
                "environment": get_config_value("ENVIRONMENT", "prod")
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "environment": get_config_value("ENVIRONMENT", "prod")
                }
            )
            
    @app.get("/api/v1/info")
    async def api_info():
        """API information endpoint"""
        return {
            "api_version": "1.0",
            "features": [
                "service_discovery",
                "health_monitoring", 
                "configuration_management",
                "security_validation"
            ],
            "endpoints": {
                "health": "/health",
                "services": "/api/v1/services",
                "config": "/api/v1/config"
            }
        }
        
    @app.get("/api/v1/services")
    async def list_services():
        """List all registered services"""
        try:
            service_discovery = await get_service_discovery()
            services = await service_discovery.get_all_services()
            
            return {
                "services": [
                    {
                        "name": service.name,
                        "host": service.host,
                        "port": service.port,
                        "status": service.status.value,
                        "is_healthy": service.is_healthy,
                        "metadata": service.metadata
                    }
                    for service in services.values()
                ],
                "total_count": len(services),
                "healthy_count": len([s for s in services.values() if s.is_healthy])
            }
            
        except Exception as e:
            logger.error(f"Failed to list services: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve services")
            
    @app.get("/api/v1/config/validate")
    async def validate_config():
        """Validate configuration and secrets"""
        try:
            security_config = get_security_config()
            is_valid = security_config.validate()
            
            return {
                "valid": is_valid,
                "environment": security_config.environment,
                "debug_mode": security_config.debug_mode,
                "security_features": {
                    "api_rate_limiting": security_config.api_rate_limit_enabled,
                    "secure_cookies": security_config.secure_cookies,
                    "audit_logging": security_config.audit_logging_enabled
                }
            }
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise HTTPException(status_code=500, detail="Configuration validation failed")
    
    logger.info("✅ API routes configured")


def _add_exception_handlers(app: FastAPI):
    """Add global exception handlers"""
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler"""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "path": str(request.url.path)
            }
        )
        
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        """Handle 404 errors"""
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not found",
                "message": f"The requested path {request.url.path} was not found",
                "available_endpoints": [
                    "/",
                    "/health", 
                    "/api/v1/info",
                    "/api/v1/services",
                    "/api/v1/config/validate"
                ]
            }
        )
        
    logger.info("✅ Exception handlers configured")


# Create the app instance
app = create_app()


def main():
    """Main entry point for running the application"""
    
    # Get configuration
    environment = get_config_value("ENVIRONMENT", "prod")
    debug_mode = environment != "prod"
    
    # Server configuration
    server_config = {
        "host": "0.0.0.0",
        "port": 8000,
        "reload": debug_mode,
        "log_level": "debug" if debug_mode else "info",
        "access_log": True
    }
    
    logger.info(f"🚀 Starting Sophia AI Backend on {server_config['host']}:{server_config['port']}")
    logger.info(f"📊 Environment: {environment}")
    logger.info(f"🐛 Debug mode: {debug_mode}")
    
    # Run the server
    uvicorn.run(app, **server_config)


if __name__ == "__main__":
    main() 