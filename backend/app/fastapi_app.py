"""
Sophia AI FastAPI App

Minimal FastAPI app stub for Sophia AI backend.
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/", tags=["health"])
async def read_root() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok"}
