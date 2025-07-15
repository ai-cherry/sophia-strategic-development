"""
Minimal FastAPI Application for Sophia AI
Simple backend with just health endpoints to get the system operational
"""

import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sophia AI - Minimal Backend",
    description="Minimal backend service for Sophia AI platform monitoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: dict

class SystemInfo(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_percent: float

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sophia AI Minimal Backend is running",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        import psutil
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        services_status = {
            "backend": "healthy",
            "system_resources": "healthy" if cpu_percent < 80 and memory.percent < 85 else "degraded",
            "memory_service": "not_initialized",
            "database": "not_connected",
            "secrets": "not_loaded"
        }
        
        overall_status = "healthy" if all(
            status in ["healthy", "not_initialized", "not_connected", "not_loaded"] 
            for status in services_status.values()
        ) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            version="1.0.0",
            services=services_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="error",
            timestamp=datetime.utcnow().isoformat(),
            version="1.0.0",
            services={"error": str(e)}
        )

@app.get("/api/health")
async def api_health():
    """API health endpoint for frontend compatibility"""
    return await health_check()

@app.get("/status")
async def status():
    """System status endpoint"""
    try:
        import psutil
        
        return {
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
            },
            "uptime": "running",
            "environment": "production"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@app.get("/api/v3/system/health")
async def system_health():
    """V3 API health endpoint"""
    return await health_check()

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Sophia AI Minimal Backend starting up...")
    logger.info("✅ Minimal backend ready for monitoring")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Sophia AI Minimal Backend shutting down...")

if __name__ == "__main__":
    uvicorn.run(
        "minimal_fastapi:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 