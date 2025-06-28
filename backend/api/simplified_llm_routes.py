"""
Simplified LLM API Routes for Sophia AI
100% Portkey with Virtual Keys - Replaces all complex multi-provider routes

This module provides a single, unified API interface for all LLM operations
using Portkey virtual keys for simplified management and enhanced reliability.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
import asyncio
import json
from datetime import datetime

from backend.services.simplified_portkey_service import (
    SophiaLLM, 
    SimplifiedLLMRequest, 
    SimplifiedLLMResponse,
    TaskType,
    simplified_llm_service
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/llm", tags=["Simplified LLM"])


# Pydantic models for API
class ChatRequest(BaseModel):
    """Simplified chat request"""
    message: str = Field(..., description="User message")
    task_type: str = Field(default="chat_general", description="Task type for optimization")
    max_tokens: int = Field(default=2000, ge=1, le=8000, description="Maximum tokens")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature")
    stream: bool = Field(default=False, description="Enable streaming")
    user_id: str = Field(default="anonymous", description="User identifier")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class ChatResponse(BaseModel):
    """Simplified chat response"""
    content: str
    model_used: str
    tokens_used: int
    cost_estimate: float
    processing_time_ms: int
    task_type: str
    success: bool
    error: Optional[str] = None
    timestamp: str


class BusinessAnalysisRequest(BaseModel):
    """Business analysis request"""
    query: str = Field(..., description="Business query")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Business context")
    include_recommendations: bool = Field(default=True, description="Include recommendations")
    include_risk_assessment: bool = Field(default=True, description="Include risk assessment")


class CodeGenerationRequest(BaseModel):
    """Code generation request"""
    requirements: str = Field(..., description="Code requirements")
    language: str = Field(default="python", description="Programming language")
    include_tests: bool = Field(default=True, description="Include test code")
    include_documentation: bool = Field(default=True, description="Include documentation")


class LLMStatus(BaseModel):
    """LLM service status"""
    service_name: str
    status: str
    portkey_connected: bool
    virtual_key_configured: bool
    last_health_check: str
    supported_models: List[str]
    cost_tracking_enabled: bool


@router.get("/status", response_model=LLMStatus)
async def get_llm_status():
    """Get simplified LLM service status"""
    try:
        # Initialize service if needed
        service = await SophiaLLM._get_service()
        
        # Check virtual key configuration
        virtual_key_configured = bool(service.virtual_key)
        
        # Perform health check
        portkey_connected = await service._health_check()
        
        # Get supported model tiers
        supported_models = [
            "Premium Tier (GPT-4o, Claude Opus)",
            "Balanced Tier (Claude Sonnet, GPT-4 Turbo)", 
            "Efficient Tier (Claude Haiku, GPT-3.5)"
        ]
        
        return LLMStatus(
            service_name="Simplified Portkey Service",
            status="healthy" if portkey_connected else "degraded",
            portkey_connected=portkey_connected,
            virtual_key_configured=virtual_key_configured,
            last_health_check=datetime.utcnow().isoformat(),
            supported_models=supported_models,
            cost_tracking_enabled=True
        )
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Unified chat completion endpoint
    
    Replaces all provider-specific endpoints with single Portkey interface.
    Intelligently routes to optimal models based on task type.
    """
    try:
        # Validate task type
        try:
            task_type = TaskType(request.task_type)
        except ValueError:
            # Default to general chat for unknown task types
            task_type = TaskType.CHAT_GENERAL
            logger.warning(f"Unknown task type '{request.task_type}', defaulting to chat_general")
        
        # Create LLM request
        llm_request = SimplifiedLLMRequest(
            messages=[{"role": "user", "content": request.message}],
            task_type=task_type,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=request.stream,
            user_id=request.user_id,
            metadata=request.context
        )
        
        # Get response from Portkey
        service = await SophiaLLM._get_service()
        response = await service.complete(llm_request)
        
        # Convert to API response
        return ChatResponse(
            content=response.content,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            cost_estimate=response.cost_estimate,
            processing_time_ms=response.processing_time_ms,
            task_type=response.task_type.value,
            success=response.success,
            error=response.error,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint
    
    Provides real-time streaming responses through Portkey virtual keys.
    """
    try:
        # Validate task type
        try:
            task_type = TaskType(request.task_type)
        except ValueError:
            task_type = TaskType.CHAT_GENERAL
        
        # Create streaming request
        llm_request = SimplifiedLLMRequest(
            messages=[{"role": "user", "content": request.message}],
            task_type=task_type,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=True,
            user_id=request.user_id,
            metadata=request.context
        )
        
        # Stream response
        service = await SophiaLLM._get_service()
        
        async def generate_stream():
            async for chunk in service.stream_complete(llm_request):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except Exception as e:
        logger.error(f"Stream completion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stream completion failed: {str(e)}")


@router.post("/business/analyze", response_model=ChatResponse)
async def analyze_business(request: BusinessAnalysisRequest):
    """
    CEO/Business analysis endpoint
    
    Optimized for executive insights with premium model routing.
    """
    try:
        response = await SophiaLLM.analyze_business(
            query=request.query,
            context=request.context
        )
        
        return ChatResponse(
            content=response.content,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            cost_estimate=response.cost_estimate,
            processing_time_ms=response.processing_time_ms,
            task_type=response.task_type.value,
            success=response.success,
            error=response.error,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Business analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Business analysis failed: {str(e)}")


@router.post("/code/generate", response_model=ChatResponse)
async def generate_code(request: CodeGenerationRequest):
    """
    Code generation endpoint
    
    Optimized for code generation with balanced model routing.
    """
    try:
        response = await SophiaLLM.generate_code(
            requirements=request.requirements,
            language=request.language
        )
        
        return ChatResponse(
            content=response.content,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            cost_estimate=response.cost_estimate,
            processing_time_ms=response.processing_time_ms,
            task_type=response.task_type.value,
            success=response.success,
            error=response.error,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")


@router.get("/models")
async def list_available_models():
    """
    List available model tiers through Portkey virtual keys
    """
    return {
        "provider": "Portkey Virtual Keys",
        "model_tiers": {
            "premium": {
                "description": "Premium models for CEO insights and complex analysis",
                "models": ["gpt-4o", "claude-3-opus-20240229"],
                "cost_per_1k_tokens": 0.025,
                "use_cases": ["ceo_insights", "business_analysis", "creative_design", "research_deep"]
            },
            "balanced": {
                "description": "Balanced models for general business and coding tasks",
                "models": ["claude-3-sonnet-20240229", "gpt-4-turbo"],
                "cost_per_1k_tokens": 0.015,
                "use_cases": ["code_generation", "data_analysis", "chat_general"]
            },
            "efficient": {
                "description": "Efficient models for quick responses and high-volume tasks",
                "models": ["claude-3-haiku-20240307", "gpt-3.5-turbo"],
                "cost_per_1k_tokens": 0.005,
                "use_cases": ["simple_queries", "batch_processing"]
            }
        },
        "routing": "Automatic based on task_type",
        "fallbacks": "Built-in through Portkey",
        "caching": "Semantic caching enabled",
        "cost_optimization": "40-60% savings through intelligent routing"
    }


@router.get("/usage/stats")
async def get_usage_stats():
    """
    Get LLM usage statistics
    
    Note: Detailed usage tracking would be implemented in the service layer
    or retrieved from Portkey dashboard APIs.
    """
    return {
        "provider": "Portkey Virtual Keys",
        "period": "last_30_days",
        "total_requests": "Available in Portkey Dashboard",
        "total_tokens": "Available in Portkey Dashboard", 
        "total_cost": "Available in Portkey Dashboard",
        "model_distribution": "Available in Portkey Dashboard",
        "cache_hit_rate": "Available in Portkey Dashboard",
        "dashboard_url": "https://app.portkey.ai/",
        "note": "Detailed analytics available in Portkey dashboard with unified view across all models"
    }


@router.post("/test")
async def test_simplified_llm():
    """
    Test endpoint for simplified LLM service
    """
    try:
        # Test basic chat
        response = await SophiaLLM.chat(
            "Hello! Please confirm that the simplified Portkey service is working.",
            TaskType.CHAT_GENERAL
        )
        
        if response.success:
            return {
                "status": "success",
                "message": "Simplified Portkey LLM service is operational",
                "test_response": response.content,
                "model_used": response.model_used,
                "tokens_used": response.tokens_used,
                "cost_estimate": response.cost_estimate,
                "processing_time_ms": response.processing_time_ms
            }
        else:
            return {
                "status": "error", 
                "message": "LLM service test failed",
                "error": response.error
            }
            
    except Exception as e:
        logger.error(f"LLM test failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM test failed: {str(e)}")


# Convenience endpoint for quick testing
@router.get("/health")
async def health_check():
    """Quick health check endpoint"""
    try:
        service = await SophiaLLM._get_service()
        is_healthy = await service._health_check()
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "service": "Simplified Portkey LLM",
            "virtual_key_configured": bool(service.virtual_key),
            "portkey_connected": is_healthy,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 