import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sophia AI API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.sophia-intel.ai",
        "https://sophia-intel.ai",
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Sophia AI API", "status": "operational"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "sophia-ai-api",
        "environment": os.getenv("ENVIRONMENT", "production"),
    }


@app.get("/api/v1/dashboard/main")
async def dashboard_main():
    return {
        "metrics": {
            "total_users": 1,
            "active_sessions": 1,
            "api_calls_today": 100,
            "system_health": "operational",
        },
        "status": "success",
    }


# Import additional routes if they exist
try:
    from backend.api import unified_chat_routes

    app.include_router(unified_chat_routes.router, prefix="/api/v1")
except ImportError:
    pass
