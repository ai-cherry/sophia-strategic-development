"""
Vercel Serverless Function for Sophia AI Backend
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import Request
from fastapi.responses import JSONResponse
from backend.app.unified_chat_backend import app as fastapi_app

# Export the FastAPI app for Vercel
app = fastapi_app


# Health check endpoint
async def handler(request: Request):
    """Vercel serverless handler"""
    # For Vercel, we need to handle the request differently
    return JSONResponse({"message": "Use specific endpoints like /api/health"})
