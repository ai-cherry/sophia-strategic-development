
import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime

# Set environment
os.environ["PULUMI_ORG"] = "scoobyjava-org"
sys.path.append("/Users/lynnmusil/sophia-main")

# Create minimal FastAPI app
app = FastAPI(title="Sophia AI Backend", version="2.0.0")

@app.get("/health")
async def health_check():
    return JSONResponse(content={
        "status": "healthy",
        "service": "sophia-backend",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    })

@app.get("/api/v1/status")
async def system_status():
    return JSONResponse(content={
        "backend": "running",
        "mcp_servers": {
            "ai_memory": "http://localhost:9000",
            "codacy": "http://localhost:3008", 
            "asana": "http://localhost:3006",
            "notion": "http://localhost:3007"
        },
        "infrastructure": {
            "postgres": "running",
            "redis": "running"
        }
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
