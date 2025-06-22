"""Minimal Sophia AI Backend - Bypass Corrupted Imports

This is a minimal working version that can start the service while we fix the corrupted files.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Only import working modules
from backend.core.auto_esc_config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Minimal lifespan management."""
    logger.info("🚀 Starting Sophia AI - Minimal Mode")
    try:
        # Basic initialization - test if ESC config works
        logger.info("✅ Testing Pulumi ESC configuration...")
        
        # Test if we can access config (this will show if ESC integration works)
        try:
            test_config = config.get_all_values()
            if test_config:
                logger.info("✅ Pulumi ESC configuration loaded successfully")
                logger.info(f"✅ Found {len(test_config)} configuration groups")
            else:
                logger.warning("⚠️ No configuration found, using fallback mode")
        except Exception as e:
            logger.warning(f"⚠️ ESC configuration issue: {e}")
            logger.info("ℹ️ Continuing with environment variables fallback")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start minimal backend: {e}", exc_info=True)
        raise
    finally:
        logger.info("🛑 Shutting down Sophia AI - Minimal Mode")


app = FastAPI(
    title="Sophia AI - Minimal Mode",
    description="Minimal Sophia AI backend for testing while fixing corrupted files",
    version="0.1.0-minimal",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Status"])
async def root():
    """Root endpoint."""
    return {
        "message": "Sophia AI - Minimal Mode",
        "status": "operational",
        "version": "0.1.0-minimal",
        "mode": "minimal_recovery"
    }


@app.get("/health", tags=["Status"])
async def health_check():
    """Health check endpoint."""
    try:
        # Test ESC configuration access
        config_status = "unknown"
        config_groups = 0
        
        try:
            test_config = config.get_all_values()
            if test_config:
                config_status = "working"
                config_groups = len(test_config)
            else:
                config_status = "fallback"
        except Exception as e:
            config_status = f"error: {str(e)[:100]}"
        
        return {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "components": {
                "fastapi": "working",
                "pulumi_esc": config_status,
                "config_groups": config_groups,
                "environment": os.getenv("SOPHIA_ENV", "development")
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": asyncio.get_event_loop().time()
        }


@app.get("/config", tags=["Configuration"])
async def get_config():
    """Get configuration status and basic info."""
    try:
        config_data = config.get_all_values()
        
        # Don't expose sensitive data, just structure
        config_summary = {}
        if config_data:
            for key, value in config_data.items():
                if isinstance(value, dict):
                    config_summary[key] = f"{len(value)} items"
                else:
                    config_summary[key] = "configured"
        
        return {
            "status": "success",
            "pulumi_org": config.pulumi_org,
            "environment": config.environment,
            "config_groups": config_summary,
            "fallback_mode": len(config_summary) == 0
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "fallback_mode": True
        }


@app.get("/test/secrets", tags=["Testing"])
async def test_secrets():
    """Test secret access without exposing values."""
    try:
        config_data = config.get_all_values()
        
        # Test access to different secret categories without exposing values
        secret_tests = {}
        
        if config_data:
            # Test AI services
            if "sophia" in config_data and "ai" in config_data["sophia"]:
                ai_config = config_data["sophia"]["ai"]
                secret_tests["openai"] = "configured" if "openai" in ai_config else "missing"
                secret_tests["anthropic"] = "configured" if "anthropic" in ai_config else "missing"
            
            # Test business services  
            if "sophia" in config_data and "business" in config_data["sophia"]:
                business_config = config_data["sophia"]["business"]
                secret_tests["gong"] = "configured" if "gong" in business_config else "missing"
            
            # Test data services
            if "sophia" in config_data and "data" in config_data["sophia"]:
                data_config = config_data["sophia"]["data"]
                secret_tests["pinecone"] = "configured" if "pinecone" in data_config else "missing"
        
        return {
            "status": "success",
            "secret_categories": secret_tests,
            "total_categories_found": len(secret_tests),
            "esc_working": len(secret_tests) > 0
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "esc_working": False
        }


if __name__ == "__main__":
    # Start the minimal backend
    host = os.getenv("SOPHIA_HOST", "127.0.0.1")
    port = int(os.getenv("SOPHIA_PORT", "8000"))
    reload = os.getenv("SOPHIA_RELOAD", "true").lower() == "true"

    logger.info(f"🚀 Starting Sophia AI Minimal Backend on {host}:{port}")
    uvicorn.run(
        "backend.minimal_main:app", 
        host=host, 
        port=port, 
        reload=reload, 
        log_level="info"
    )
