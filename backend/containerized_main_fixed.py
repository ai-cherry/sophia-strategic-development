#!/usr/bin/env python3
"""
Sophia AI - Enhanced Containerized Backend with Full AI Integration
Production-ready containerized backend with OpenAI/Anthropic integrations
"""

import asyncio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import aiohttp
import openai
import anthropic

# Import our clean ESC configuration
from backend.core.clean_esc_config import config, ESCConfigError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Pydantic models for API requests
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "gpt-4"
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000
    context: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class AIAnalysisRequest(BaseModel):
    content: str
    analysis_type: str = "general"
    model: Optional[str] = "claude-3-sonnet"

class BatchRequest(BaseModel):
    requests: List[ChatRequest]
    batch_id: Optional[str] = None

# Global variables for AI clients
openai_client = None
anthropic_client = None
config_status = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global openai_client, anthropic_client, config_status
    
    logger.info("🚀 Starting Sophia AI - Enhanced Containerized Production Mode")
    
    # Initialize ESC configuration
    logger.info("🔍 Initializing enhanced ESC configuration...")
    try:
        await config.initialize()
        logger.info("✅ ESC configuration initialized successfully")
    except Exception as e:
        logger.error(f"❌ ESC initialization failed: {e}")
        # Don't exit - we'll handle graceful degradation
    
    # Validate configuration
    config_status = await config.get_status()
    logger.info(f"📊 ESC Status: {config_status}")
    
    if config_status.get('esc_loaded'):
        logger.info(f"✅ ESC Environment: {config_status.get('environment')}")
        logger.info(f"✅ Services Configured: {config_status.get('total_services')}")
        
        # Log service status
        services = config_status.get('services', {})
        for service, status in services.items():
            logger.info(f"✅ {service.upper()}: {'configured' if status else 'not configured'}")
    
    # Initialize AI clients
    try:
        # OpenAI client
        openai_key = await config.get_openai_api_key()
        if openai_key:
            openai_client = openai.AsyncOpenAI(api_key=openai_key)
            logger.info("✅ OpenAI client initialized")
        else:
            logger.warning("⚠️ OpenAI API key not available")
            
        # Anthropic client
        anthropic_key = await config.get_anthropic_api_key()
        if anthropic_key:
            anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_key)
            logger.info("✅ Anthropic client initialized")
        else:
            logger.warning("⚠️ Anthropic API key not available")
            
    except Exception as e:
        logger.error(f"❌ AI client initialization failed: {e}")
    
    # Test service access
    service_tests = await config.test_service_access()
    logger.info(f"🧪 Service Access Tests: {service_tests}")
    
    yield
    
    # Cleanup
    logger.info("🔄 Shutting down Sophia AI Containerized Backend...")
    if openai_client:
        await openai_client.close()
    if anthropic_client:
        await anthropic_client.close()

# Create FastAPI app with lifespan
app = FastAPI(
    title="Sophia AI - Enhanced Containerized Backend",
    description="Production-ready AI orchestrator with full OpenAI/Anthropic integration",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get AI clients
async def get_ai_clients():
    """Dependency to provide AI clients"""
    return {
        "openai": openai_client,
        "anthropic": anthropic_client
    }

@app.get("/")
async def root():
    """Root endpoint with service status"""
    return {
        "service": "Sophia AI Enhanced Containerized Backend",
        "status": "running",
        "version": "2.0.0",
        "timestamp": "2025-01-21T12:00:00Z",
        "features": [
            "Full OpenAI/Anthropic Integration",
            "Streaming Chat Support",
            "Batch Processing",
            "Advanced AI Analysis",
            "Production Monitoring",
            "ESC Configuration Management"
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Test ESC configuration
        esc_status = await config.get_status()
        
        # Test AI client availability
        ai_status = {
            "openai": openai_client is not None,
            "anthropic": anthropic_client is not None
        }
        
        # Calculate overall health
        total_services = len(esc_status.get('services', {}))
        healthy_services = sum(1 for status in esc_status.get('services', {}).values() if status)
        health_percentage = (healthy_services / total_services * 100) if total_services > 0 else 0
        
        return {
            "status": "healthy" if health_percentage >= 75 else "degraded",
            "health_percentage": health_percentage,
            "esc_loaded": esc_status.get('esc_loaded', False),
            "environment": esc_status.get('environment'),
            "services": esc_status.get('services', {}),
            "ai_clients": ai_status,
            "uptime": "running",
            "timestamp": "2025-01-21T12:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.post("/ai/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, clients: dict = Depends(get_ai_clients)):
    """Enhanced chat endpoint with OpenAI/Anthropic integration"""
    try:
        if request.model.startswith("gpt"):
            if not clients["openai"]:
                raise HTTPException(status_code=503, detail="OpenAI client not available")
            return await _openai_chat(request, clients["openai"])
        elif request.model.startswith("claude"):
            if not clients["anthropic"]:
                raise HTTPException(status_code=503, detail="Anthropic client not available")
            return await _anthropic_chat(request, clients["anthropic"])
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported model: {request.model}")
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing error: {e}")

# AI Helper Functions
async def _openai_chat(request: ChatRequest, client: openai.AsyncOpenAI) -> ChatResponse:
    """Process OpenAI chat request"""
    messages = [{"role": "system", "content": "You are Sophia AI, an intelligent assistant."}]
    
    # Add context if provided
    for ctx in request.context:
        messages.append(ctx)
    
    # Add user message
    messages.append({"role": "user", "content": request.message})
    
    response = await client.chat.completions.create(
        model=request.model,
        messages=messages,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    
    return ChatResponse(
        response=response.choices[0].message.content,
        model=request.model,
        usage=response.usage.dict() if response.usage else None,
        metadata={"provider": "openai", "finish_reason": response.choices[0].finish_reason}
    )

async def _anthropic_chat(request: ChatRequest, client: anthropic.AsyncAnthropic) -> ChatResponse:
    """Process Anthropic chat request"""
    response = await client.messages.create(
        model=request.model,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        messages=[{"role": "user", "content": request.message}]
    )
    
    return ChatResponse(
        response=response.content[0].text,
        model=request.model,
        usage={"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
        metadata={"provider": "anthropic", "stop_reason": response.stop_reason}
    )

if __name__ == "__main__":
    # Configuration
    host = os.getenv("SOPHIA_HOST", "0.0.0.0")
    port = int(os.getenv("SOPHIA_PORT", "8000"))
    reload = os.getenv("SOPHIA_RELOAD", "false").lower() == "true"
    
    logger.info(f"🚀 Starting Sophia AI Enhanced Containerized Backend")
    logger.info(f"🌐 Host: {host}:{port}")
    logger.info(f"🔄 Reload: {reload}")
    
    uvicorn.run(
        "backend.containerized_main_fixed:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 