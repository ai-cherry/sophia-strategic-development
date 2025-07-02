"""
Sophia AI Unified API - Simple Working Version
"""

import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sophia AI Unified Platform", version="3.0.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "Sophia AI Platform",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Import and mount available routers
try:
    from backend.api.data_flow_routes import router as data_flow_router

    app.include_router(data_flow_router, prefix="/api/v3", tags=["Data Flow"])
    logger.info("Mounted data_flow_router")
except Exception as e:
    logger.warning(f"Could not mount data_flow_router: {e}")

try:
    from backend.api.llm_strategy_routes import router as llm_router

    app.include_router(llm_router, prefix="/api/v3", tags=["LLM"])
    logger.info("Mounted llm_strategy_router")
except Exception as e:
    logger.warning(f"Could not mount llm_strategy_router: {e}")

try:
    from backend.api.mcp_integration_routes import router as mcp_router

    app.include_router(mcp_router, prefix="/api/mcp", tags=["MCP"])
    logger.info("Mounted mcp_integration_router")
except Exception as e:
    logger.warning(f"Could not mount mcp_integration_router: {e}")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
