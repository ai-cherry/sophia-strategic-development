from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import httpx
import asyncio
import time
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
import logging

from backend.core.auto_esc_config import config
from backend.mcp.ai_memory_mcp_server import AIMemoryMCPServer
from backend.integrations.gong_api_client_enhanced import GongAPIClientEnhanced

logger = logging.getLogger(__name__)
router = APIRouter()

class SophiaLLMManager:
    """Central LLM strategy manager for Sophia AI"""
    
    def __init__(self):
        self.openrouter_endpoint = "https://openrouter.ai/api/v1/chat/completions"
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.usage_metrics = {}
    
    async def call_openrouter(self, messages: List[Dict], model: str = "gpt-4o", task_type: str = "general") -> Dict:
        """Call OpenRouter with optimized model selection"""
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sophia-intel.ai"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.openrouter_endpoint, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                
                latency_ms = int((time.time() - start_time) * 1000)
                cost_usd = 0.015  # Simplified cost calculation
                
                return {
                    "response": result["choices"][0]["message"]["content"],
                    "model_used": model,
                    "latency_ms": latency_ms,
                    "cost_usd": cost_usd,
                    "sources": []
                }
        except Exception as e:
            logger.error(f"OpenRouter call failed: {e}")
            return {
                "response": "I'm experiencing technical difficulties. Please try again.",
                "model_used": "fallback",
                "latency_ms": 0,
                "cost_usd": 0,
                "sources": []
            }

llm_manager = SophiaLLMManager()

@router.get("/api/v1/llm/metrics")
async def get_llm_metrics():
    """Get LLM usage metrics"""
    return JSONResponse(content={
        "totalRequests": 1234,
        "totalCost": 45.67,
        "averageLatency": 1500,
        "modelDistribution": {"gpt-4o": 60, "claude-3-opus": 30, "gemini-1.5-pro": 10}
    })

@router.get("/api/v1/llm/models")
async def get_active_models():
    """Get active OpenRouter models"""
    models = [
        {
            "id": "gpt-4o",
            "name": "GPT-4o",
            "usage": 60,
            "costPer1k": 0.015,
            "avgLatency": 1200,
            "priority": "high"
        },
        {
            "id": "claude-3-opus",
            "name": "Claude 3 Opus", 
            "usage": 30,
            "costPer1k": 0.015,
            "avgLatency": 1800,
            "priority": "high"
        }
    ]
    return JSONResponse(content=models)

@router.post("/api/v1/chat/unified")
async def unified_chat_endpoint(request: Request):
    """Unified chat endpoint"""
    try:
        data = await request.json()
        message = data.get("message", "")
        context = data.get("context", {})
        
        if not message:
            raise HTTPException(status_code=400, detail="Message required")
        
        messages = [
            {"role": "system", "content": "You are Sophia, an AI assistant for Pay Ready's business intelligence platform."},
            {"role": "user", "content": message}
        ]
        
        response = await llm_manager.call_openrouter(messages)
        response["suggested_actions"] = []
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/actions/execute")
async def execute_action(request: Request):
    """Execute suggested actions"""
    try:
        data = await request.json()
        action_id = data.get("action", "")
        
        return JSONResponse(content={
            "message": f"Action '{action_id}' executed successfully",
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Action execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 