#!/usr/bin/env python3
"""Minimal working API to verify deployment."""

import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(title="Sophia AI Minimal API", version="0.1.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Sophia AI Minimal API is running!"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "sophia-ai-minimal", "version": "0.1.0"}


@app.get("/api/v1/test")
async def test_endpoint():
    return {
        "status": "success",
        "message": "API is working",
        "data": {"test": True, "timestamp": "2024-01-15"},
    }


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    logger.info(f"Starting Minimal API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
