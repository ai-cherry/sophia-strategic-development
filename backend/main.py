"""Pay Ready AI Agent Orchestrator - Main Entry Point.

Centralized orchestration for all Pay Ready specialized AI agents, powered by Agno.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.agents.core.agent_framework import (  # The new Agno-based framework
    agent_framework,
)
from backend.app.routers import agno_router, api_v1_router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application's lifespan, starting and stopping services."""
    logger.info("Initializing Pay Ready AI Agent System with Agno Framework...")
    try:
        # The agent_framework will initialize itself using the auto_esc_config
        # This will include setting up connections to Arize, Vector DBs, etc.
        await agent_framework.initialize()
        logger.info("Agno Agent Framework initialized successfully.")

        # Start any background tasks or services managed by the framework
        asyncio.create_task(agent_framework.run_background_services())
        logger.info("Agent background services started.")

        yield
    except Exception as e:
        logger.error(
            f"Failed to initialize Pay Ready AI Agent System: {e}", exc_info=True
        )
        # In a real scenario, you might want to handle this more gracefully
        # For now, we'll re-raise to prevent the app from starting in a broken state.
        raise
    finally:
        logger.info("Shutting down Pay Ready AI Agent System...")
        await agent_framework.shutdown()
        logger.info("Agno Agent Framework has been shut down.")


app = FastAPI(
    title="Sophia AI - Agno-Powered Agent System",
    description="Centralized AI agent orchestration for Pay Ready B2B operations using the Agno framework.",
    version="2.0.0",  # Version bump to signify major architectural change
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be a list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Core API Routers ---

# Agno router will handle all agent-based interactions
app.include_router(agno_router.router, prefix="/agno", tags=["Agno Agents"])

# The v1 API router can be kept for dashboard/BI endpoints
app.include_router(api_v1_router.router, prefix="/api/v1", tags=["Dashboard API v1"])


# --- Health and Status Endpoints ---
@app.get("/", tags=["Status"])
async def root():
    """Return the root endpoint message."""
    return {
        "message": "Sophia AI - Agno-Powered Agent System",
        "status": "operational",
        "version": app.version,
    }


@app.get("/health", tags=["Status"])
async def health_check():
    """Perform a health check of the system and its core components."""
    framework_status = await agent_framework.get_status()
    return {
        "status": "healthy" if framework_status.get("is_healthy") else "degraded",
        "timestamp": framework_status.get("timestamp"),
        "components": framework_status,
    }


if __name__ == "__main__":
    # The application host and port can be configured via environment variables
    # or a dedicated config file, falling back to defaults.
    host = os.getenv("SOPHIA_HOST", "127.0.0.1")
    port = int(os.getenv("SOPHIA_PORT", "8000"))
    reload = os.getenv("SOPHIA_RELOAD", "true").lower() == "true"

    uvicorn.run(
        "backend.main:app", host=host, port=port, reload=reload, log_level="info"
    )
