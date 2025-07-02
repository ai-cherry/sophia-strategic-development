#!/usr/bin/env python3
"""Minimal working API v2 with ESC and database connectivity."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import sys
from pathlib import Path
from typing import Dict, Any
import os

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(title="Sophia AI Minimal API v2", version="0.2.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for service status
esc_status = {"connected": False, "secret_count": 0}
db_status = {"connected": False, "error": None}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Sophia AI Minimal API v2...")
    
    # Try to connect to Pulumi ESC
    try:
        from backend.core.auto_esc_config import get_config_value
        # Test by trying to get a value
        test_value = get_config_value("openai_api_key")
        if test_value:
            esc_status["connected"] = True
            # Count available secrets
            from backend.core.auto_esc_config import config
            if hasattr(config, '_config') and config._config:
                esc_status["secret_count"] = len(config._config)
            logger.info(f"ESC connected with {esc_status['secret_count']} secrets")
        else:
            logger.warning("ESC connected but no secrets found")
    except Exception as e:
        logger.error(f"Failed to connect to ESC: {e}")
        esc_status["error"] = str(e)

@app.get("/")
async def root():
    return {
        "message": "Sophia AI Minimal API v2 is running!",
        "version": "0.2.0",
        "features": ["health", "status", "config"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "sophia-ai-minimal-v2",
        "version": "0.2.0"
    }

@app.get("/api/v1/status")
async def status():
    """Get comprehensive status of all services."""
    return {
        "api": {
            "status": "running",
            "version": "0.2.0"
        },
        "esc": esc_status,
        "database": db_status,
        "environment": {
            "python_version": sys.version.split()[0],
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "pulumi_org": os.getenv("PULUMI_ORG", "unknown")
        }
    }

@app.get("/api/v1/config/test")
async def test_config():
    """Test configuration access."""
    try:
        from backend.core.auto_esc_config import get_config_value
        
        # Try to get some non-sensitive config values
        test_keys = ["environment", "pulumi_org", "project_name"]
        results = {}
        
        for key in test_keys:
            value = get_config_value(key)
            results[key] = "found" if value else "not_found"
        
        # Check for critical API keys (don't return actual values)
        critical_keys = ["openai_api_key", "anthropic_api_key", "snowflake_account"]
        for key in critical_keys:
            value = get_config_value(key)
            results[key] = "configured" if value else "missing"
        
        return {
            "status": "success",
            "config_test": results,
            "esc_connected": esc_status["connected"],
            "secret_count": esc_status["secret_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config test failed: {str(e)}")

@app.get("/api/v1/database/health")
async def database_health():
    """Check database connectivity."""
    try:
        # For now, just check if we have Snowflake credentials
        from backend.core.auto_esc_config import get_config_value
        
        snowflake_config = {
            "account": bool(get_config_value("snowflake_account")),
            "user": bool(get_config_value("snowflake_user")),
            "password": bool(get_config_value("snowflake_password")),
            "warehouse": bool(get_config_value("snowflake_warehouse")),
            "database": bool(get_config_value("snowflake_database")),
            "role": bool(get_config_value("snowflake_role"))
        }
        
        all_configured = all(snowflake_config.values())
        
        return {
            "status": "configured" if all_configured else "missing_config",
            "snowflake_config": snowflake_config,
            "ready_to_connect": all_configured
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database health check failed: {str(e)}")

@app.post("/api/v1/echo")
async def echo(data: Dict[str, Any]):
    """Simple echo endpoint for testing."""
    return {
        "status": "success",
        "echo": data,
        "timestamp": "2024-01-15"
    }

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    logger.info(f"Starting Minimal API v2 on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 