"""Minimal FastAPI app for testing deployment"""
import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Sophia AI Backend - Minimal", version="1.0.0")


@app.get("/")
async def root():
    return {
        "message": "Sophia AI Backend is running",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "pulumi_org": os.getenv("PULUMI_ORG", "unknown"),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health")
async def health():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "sophia-backend",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.get("/api/health")
async def api_health():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "sophia-backend-api",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
