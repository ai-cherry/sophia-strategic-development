#!/usr/bin/env python3
"""
Self-Healing Minimal API for Sophia AI
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sophia AI Self-Healing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "self_healing_api"}

@app.get("/")
async def root():
    return {"message": "Sophia AI Self-Healing API is running"}

@app.get("/api/v1/status")
async def api_status():
    return {
        "api_version": "1.0.0",
        "status": "operational",
        "self_healing": True
    }

if __name__ == "__main__":
    logger.info("🚀 Starting Self-Healing API on port 8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
