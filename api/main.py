"""
Sophia AI API - Distributed Architecture

This module creates FastAPI applications configured for specific Lambda Labs instances
with role-based service initialization and distributed architecture support.

Features:
- Instance-specific FastAPI configuration
- Role-based endpoint exposure
- Health monitoring integration
- Service discovery integration
- Distributed request routing
- Performance optimization per instance type

Architecture:
- Primary Instance: Full API with database endpoints
- MCP Orchestrator: AI processing and MCP endpoints
- Data Pipeline: Data processing and ML endpoints
- Development: Testing and development endpoints

Author: Sophia AI Team
Date: July 2025
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn

from config.infrastructure import InfrastructureConfig, LambdaInstance, InstanceRole
from services.service_discovery import get_service_discovery
from utils.health_check import get_health_checker

logger = logging.getLogger(__name__)

class DistributedAPIError(Exception):
    """Custom exception for distributed API errors."""
    pass

def create_openapi_schema(app: FastAPI, instance: LambdaInstance) -> Dict[str, Any]:
    """
    Create custom OpenAPI schema for the instance.
    
    Args:
        app: FastAPI application
        instance: Lambda Labs instance configuration
        
    Returns:
        OpenAPI schema dictionary
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=f"Sophia AI - {instance.name}",
        version="2.0.0",
        description=f"""
        Sophia AI Distributed Enterprise Platform
        
        **Instance**: {instance.name}
        **Role**: {instance.role.value}
        **GPU**: {instance.gpu}
        **Region**: {instance.region}
        **Services**: {[service.value for service in instance.services]}
        
        This instance provides specialized services within the Sophia AI distributed architecture.
        """,
        routes=app.routes,
    )
    
    # Add instance-specific information
    openapi_schema["info"]["x-instance"] = {
        "name": instance.name,
        "ip": instance.ip,
        "role": instance.role.value,
        "gpu": instance.gpu,
        "region": instance.region,
        "services": [service.value for service in instance.services]
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

def create_app(instance: LambdaInstance) -> FastAPI:
    """
    Create FastAPI application configured for specific Lambda Labs instance.
    
    Args:
        instance: Lambda Labs instance configuration
        
    Returns:
        Configured FastAPI application
    """
    logger.info(f"🔧 Creating FastAPI application for {instance.name}")
    
    # Create FastAPI app with instance-specific configuration
    app = FastAPI(
        title=f"Sophia AI - {instance.name}",
        description=f"Sophia AI running on {instance.gpu} in {instance.region}",
        version="2.0.0",
        docs_url="/docs" if os.getenv("ENABLE_DOCS", "true").lower() == "true" else None,
        redoc_url="/redoc" if os.getenv("ENABLE_DOCS", "true").lower() == "true" else None,
        openapi_url="/openapi.json"
    )
    
    # Configure middleware
    setup_middleware(app, instance)
    
    # Add core endpoints
    add_core_endpoints(app, instance)
    
    # Add role-specific endpoints
    add_role_specific_endpoints(app, instance)
    
    # Setup custom OpenAPI schema
    app.openapi = lambda: create_openapi_schema(app, instance)
    
    logger.info(f"✅ FastAPI application created for {instance.name}")
    return app

def setup_middleware(app: FastAPI, instance: LambdaInstance):
    """Setup middleware for the FastAPI application."""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # GZip compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = datetime.now()
        
        # Process request
        response = await call_next(request)
        
        # Log request details
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"📡 {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"Instance: {instance.name}"
        )
        
        # Add instance information to response headers
        response.headers["X-Instance-Name"] = instance.name
        response.headers["X-Instance-Role"] = instance.role.value
        response.headers["X-Instance-IP"] = instance.ip
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

def add_core_endpoints(app: FastAPI, instance: LambdaInstance):
    """Add core endpoints available on all instances."""
    
    @app.get("/")
    async def root():
        """Root endpoint with instance information."""
        return {
            "message": "Sophia AI Distributed Enterprise Platform",
            "instance": {
                "name": instance.name,
                "role": instance.role.value,
                "ip": instance.ip,
                "gpu": instance.gpu,
                "region": instance.region,
                "services": [service.value for service in instance.services]
            },
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat()
        }
    
    @app.get("/health")
    async def health_check():
        """Comprehensive health check endpoint."""
        try:
            health_checker = await get_health_checker()
            health_status = await health_checker.get_health_status()
            
            return {
                "status": "healthy",
                "instance": {
                    "name": instance.name,
                    "ip": instance.ip,
                    "role": instance.role.value,
                    "gpu": instance.gpu,
                    "services": [service.value for service in instance.services]
                },
                "health": health_status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
    
    @app.get("/status")
    async def instance_status():
        """Get detailed instance status."""
        try:
            service_discovery = await get_service_discovery()
            service_status = await service_discovery.get_service_status()
            
            return {
                "instance": {
                    "name": instance.name,
                    "ip": instance.ip,
                    "role": instance.role.value,
                    "gpu": instance.gpu,
                    "region": instance.region,
                    "port_range": f"{instance.port_allocation.start}-{instance.port_allocation.end}",
                    "services": [service.value for service in instance.services],
                    "max_connections": instance.max_connections,
                    "timeout": instance.timeout_seconds
                },
                "service_discovery": service_status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Status check failed: {e}")
            raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
    
    @app.get("/metrics")
    async def get_metrics():
        """Get instance metrics."""
        try:
            health_checker = await get_health_checker()
            service_discovery = await get_service_discovery()
            
            return {
                "instance": instance.name,
                "health_metrics": health_checker.get_metrics() if hasattr(health_checker, 'get_metrics') else {},
                "service_metrics": service_discovery.get_metrics(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Metrics collection failed: {e}")
            raise HTTPException(status_code=500, detail=f"Metrics collection failed: {str(e)}")

def add_role_specific_endpoints(app: FastAPI, instance: LambdaInstance):
    """Add endpoints specific to the instance role."""
    
    if instance.role == InstanceRole.PRIMARY:
        add_primary_endpoints(app, instance)
    elif instance.role == InstanceRole.MCP_ORCHESTRATOR:
        add_mcp_endpoints(app, instance)
    elif instance.role == InstanceRole.DATA_PIPELINE:
        add_data_endpoints(app, instance)
    elif instance.role == InstanceRole.DEVELOPMENT:
        add_development_endpoints(app, instance)

def add_primary_endpoints(app: FastAPI, instance: LambdaInstance):
    """Add endpoints for the primary instance."""
    
    @app.get("/api/v1/instances")
    async def get_all_instances():
        """Get information about all instances in the cluster."""
        try:
            config = InfrastructureConfig()
            instances_info = []
            
            for name, inst in config.INSTANCES.items():
                instances_info.append({
                    "name": inst.name,
                    "ip": inst.ip,
                    "role": inst.role.value,
                    "gpu": inst.gpu,
                    "region": inst.region,
                    "services": [service.value for service in inst.services],
                    "endpoint": inst.endpoint,
                    "health_endpoint": inst.health_endpoint
                })
            
            return {
                "instances": instances_info,
                "total_count": len(instances_info),
                "queried_from": instance.name
            }
        except Exception as e:
            logger.error(f"❌ Failed to get instances: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/orchestrate")
    async def orchestrate_request(request: Dict[str, Any]):
        """Orchestrate request across distributed instances."""
        try:
            # Placeholder for distributed request orchestration
            return {
                "message": "Request orchestration not yet implemented",
                "request": request,
                "orchestrated_by": instance.name,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Orchestration failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

def add_mcp_endpoints(app: FastAPI, instance: LambdaInstance):
    """Add endpoints for the MCP orchestrator instance."""
    
    @app.post("/api/v1/mcp/process")
    async def process_mcp_request(request: Dict[str, Any]):
        """Process MCP requests."""
        try:
            # Placeholder for MCP request processing
            return {
                "message": "MCP processing not yet implemented",
                "request": request,
                "processed_by": instance.name,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ MCP processing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/mcp/servers")
    async def get_mcp_servers():
        """Get status of MCP servers."""
        try:
            return {
                "mcp_servers": [],  # Placeholder
                "instance": instance.name,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Failed to get MCP servers: {e}")
            raise HTTPException(status_code=500, detail=str(e))

def add_data_endpoints(app: FastAPI, instance: LambdaInstance):
    """Add endpoints for the data pipeline instance."""
    
    @app.post("/api/v1/data/process")
    async def process_data(request: Dict[str, Any]):
        """Process data requests."""
        try:
            # Placeholder for data processing
            return {
                "message": "Data processing not yet implemented",
                "request": request,
                "processed_by": instance.name,
                "gpu": instance.gpu,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Data processing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/ml/train")
    async def train_model(request: Dict[str, Any]):
        """Train ML models."""
        try:
            # Placeholder for ML training
            return {
                "message": "ML training not yet implemented",
                "request": request,
                "trained_by": instance.name,
                "gpu": instance.gpu,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ ML training failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/embeddings/generate")
    async def generate_embeddings(request: Dict[str, Any]):
        """Generate embeddings."""
        try:
            # Placeholder for embedding generation
            return {
                "message": "Embedding generation not yet implemented",
                "request": request,
                "generated_by": instance.name,
                "gpu": instance.gpu,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

def add_development_endpoints(app: FastAPI, instance: LambdaInstance):
    """Add endpoints for the development instance."""
    
    @app.post("/api/v1/test")
    async def test_endpoint(request: Dict[str, Any]):
        """Test endpoint for development."""
        try:
            return {
                "message": "Test endpoint",
                "request": request,
                "tested_by": instance.name,
                "environment": "development",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/debug")
    async def debug_info():
        """Get debug information."""
        try:
            import psutil
            
            return {
                "instance": instance.name,
                "environment": "development",
                "system": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent
                },
                "python_version": f"{psutil.version_info}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Debug info failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Global application factory function
def get_app_for_current_instance() -> FastAPI:
    """
    Get FastAPI application for the current instance.
    
    Returns:
        Configured FastAPI application
    """
    try:
        config = InfrastructureConfig()
        current_instance = config.get_current_instance()
        
        if not current_instance:
            # Fallback to development instance
            current_instance = config.get_instance_by_role(InstanceRole.DEVELOPMENT)
            if not current_instance:
                raise DistributedAPIError("Unable to determine current instance")
        
        return create_app(current_instance)
        
    except Exception as e:
        logger.error(f"❌ Failed to create app for current instance: {e}")
        raise DistributedAPIError(f"Application creation failed: {e}")

# Application instance for direct access
app = get_app_for_current_instance()

if __name__ == "__main__":
    # Direct execution for testing
    config = InfrastructureConfig()
    current_instance = config.get_current_instance()
    
    if not current_instance:
        current_instance = config.get_instance_by_role(InstanceRole.DEVELOPMENT)
    
    if current_instance:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=current_instance.primary_port,
            log_level="info"
        )
    else:
        logger.error("❌ Unable to determine instance configuration")
