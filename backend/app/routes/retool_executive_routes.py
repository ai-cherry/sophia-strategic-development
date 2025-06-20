"""
Enhanced Retool Executive Dashboard API Routes
Provides comprehensive strategic intelligence and system oversight endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import json
import uuid
from pydantic import BaseModel

from ...agents.core.agent_router import agent_router
from ...agents.core.base_agent import Task
from ...core.config_manager import get_secret, get_config
from ...integrations.openrouter_integration import OpenRouterClient
from ...integrations.portkey_client import PortkeyClient
from ...mcp.mcp_client import MCPClient
from ..websockets import manager as ws_manager
from ..security import get_current_user_role, UserRole

router = APIRouter(prefix="/api/retool", tags=["Retool Executive Dashboard"])

# Pydantic models for request/response
class StrategicChatMessage(BaseModel):
    message: str
    mode: str = "combined"  # internal, external, combined
    model_id: Optional[str] = None
    conversation_id: Optional[str] = None
    context_window_required: Optional[int] = None
    
class ModelSelectionRequest(BaseModel):
    provider: Optional[str] = None
    capability: Optional[str] = None
    search_query: Optional[str] = None
    min_context_window: Optional[int] = None
    max_cost_per_token: Optional[float] = None

class DashboardMetrics(BaseModel):
    revenue_growth: float
    client_health_score: float
    sales_efficiency: float
    agent_performance: float
    system_health: float

class ModelPreset(BaseModel):
    name: str
    description: str
    model_id: str
    use_cases: List[str]

class ModelPerformanceMetrics(BaseModel):
    model_id: str
    avg_response_time: float
    avg_quality_score: float
    total_uses: int
    cost_per_query: float
    last_used: datetime

# Initialize clients
openrouter_client = None
portkey_client = None
mcp_client = None

async def get_openrouter_client():
    global openrouter_client
    if not openrouter_client:
        api_key = await get_secret("OPENROUTER_API_KEY")
        openrouter_client = OpenRouterClient(api_key)
    return openrouter_client

async def get_portkey_client():
    global portkey_client
    if not portkey_client:
        api_key = await get_secret("PORTKEY_API_KEY")
        portkey_client = PortkeyClient(api_key)
    return portkey_client

async def get_mcp_client():
    global mcp_client
    if not mcp_client:
        mcp_client = MCPClient("http://localhost:8090")
        await mcp_client.connect()
    return mcp_client

# Strategic Intelligence Hub Endpoints
@router.get("/executive/dashboard-summary")
async def get_dashboard_summary(
    current_role: UserRole = Depends(get_current_user_role)
) -> DashboardMetrics:
    """Get high-level executive dashboard metrics"""
    if current_role != UserRole.CEO:
        raise HTTPException(status_code=403, detail="Executive access required")
    
    # Aggregate metrics from various agents
    executive_agent = agent_router.agent_instances.get("executive")
    client_health_agent = agent_router.agent_instances.get("client_health")
    
    # Get real-time metrics
    metrics = DashboardMetrics(
        revenue_growth=15.3,  # Would come from actual data
        client_health_score=87.5,
        sales_efficiency=92.1,
        agent_performance=94.7,
        system_health=98.2
    )
    
    return metrics

@router.get("/executive/client-health-portfolio")
async def get_client_health_portfolio(
    current_role: UserRole = Depends(get_current_user_role)
) -> List[Dict[str, Any]]:
    """Get detailed client health scores and risk analysis"""
    if current_role != UserRole.CEO:
        raise HTTPException(status_code=403, detail="Executive access required")
    
    client_health_agent = agent_router.agent_instances.get("client_health")
    if not client_health_agent:
        raise HTTPException(status_code=503, detail="Client Health Agent unavailable")
    
    task = Task(
        task_id=f"health_portfolio_{uuid.uuid4().hex}",
        task_type="get_portfolio_health",
        agent_id="client_health",
        task_data={}
    )
    
    result = await client_health_agent.process_task(task)
    return result.get("data", [])

@router.get("/executive/sales-performance")
async def get_sales_performance(
    timeframe: str = "30d",
    current_role: UserRole = Depends(get_current_user_role)
) -> Dict[str, Any]:
    """Get sales performance metrics and trends"""
    if current_role != UserRole.CEO:
        raise HTTPException(status_code=403, detail="Executive access required")
    
    sales_coach_agent = agent_router.agent_instances.get("sales_coach")
    if not sales_coach_agent:
        raise HTTPException(status_code=503, detail="Sales Coach Agent unavailable")
    
    task = Task(
        task_id=f"sales_perf_{uuid.uuid4().hex}",
        task_type="get_performance_metrics",
        agent_id="sales_coach",
        task_data={"timeframe": timeframe}
    )
    
    result = await sales_coach_agent.process_task(task)
    return result.get("data", {})

# Strategic Chat Endpoints
@router.post("/executive/strategic-chat")
async def strategic_chat(
    message: StrategicChatMessage,
    current_role: UserRole = Depends(get_current_user_role)
) -> Dict[str, Any]:
    """Advanced strategic chat with hybrid intelligence"""
    if current_role != UserRole.CEO:
        raise HTTPException(status_code=403, detail="Executive access required")
    
    # Get clients
    or_client = await get_openrouter_client()
    mcp = await get_mcp_client()
    
    # Process based on mode
    internal_results = None
    external_results = None
    
    if message.mode in ["internal", "combined"]:
        # Internal search across Sophia ecosystem
        internal_tasks = []
        
        # Vector search in Pinecone
        internal_tasks.append(
            mcp.call_tool("knowledge", "search", query=message.message)
        )
        
        # Search AI memory
        internal_tasks.append(
            mcp.call_tool("ai_memory", "recall_memory", query=message.message)
        )
        
        # Get operational insights from Snowflake
        internal_tasks.append(
            mcp.call_tool("snowflake", "query", 
                query=f"SELECT insights related to: {message.message}")
        )
        
        # Execute internal searches in parallel
        internal_results = await asyncio.gather(*internal_tasks, return_exceptions=True)
    
    if message.mode in ["external", "combined"]:
        # External search via MCP servers
        external_tasks = []
        
        # Apify web search with Pay Ready context
        external_tasks.append(
            mcp.call_tool("apify", "search_proptech", query=message.message)
        )
        
        # HuggingFace AI insights
        external_tasks.append(
            mcp.call_tool("huggingface", "analyze", query=message.message)
        )
        
        # Execute external searches in parallel
        external_results = await asyncio.gather(*external_tasks, return_exceptions=True)
    
    # Use selected model or intelligent routing
    model_id = message.model_id or await _select_optimal_model(message.message)
    
    # Synthesize response with OpenRouter
    synthesis_prompt = _build_synthesis_prompt(
        query=message.message,
        internal_results=internal_results,
        external_results=external_results,
        mode=message.mode
    )
    
    response = await or_client.chat_completion(
        model=model_id,
        messages=[{"role": "user", "content": synthesis_prompt}],
        stream=True
    )
    
    # Store conversation in AI memory
    await mcp.call_tool("ai_memory", "store_conversation", 
        content=f"Q: {message.message}\nA: {response['content']}",
        category="strategic_chat",
        metadata={"model": model_id, "mode": message.mode}
    )
    
    return {
        "response": response["content"],
        "model_used": model_id,
        "sources": {
            "internal": _format_sources(internal_results) if internal_results else None,
            "external": _format_sources(external_results) if external_results else None
        },
        "conversation_id": message.conversation_id or str(uuid.uuid4())
    }

# Model Management Endpoints
@router.get("/executive/openrouter-models")
async def get_openrouter_models(
    request: ModelSelectionRequest = None,
    current_role: UserRole = Depends(get_current_user_role)
) -> Dict[str, Any]:
    """Get available OpenRouter models with dynamic discovery and metadata"""
    if current_role != UserRole.CEO:
        raise HTTPException(status_code=403, detail="Executive access required")
    
    or_client = await get_openrouter_client()
    models = await or_client.get_models(force_refresh=True)
    
    # Enhanced categorization with performance data
    categorized = await _enhance_model_categorization(models)
    
    # Apply advanced filters
    filtered = categorized
    if request:
        if request.provider:
            filtered = [m for m in filtered if m["provider"] == request.provider]
        if request.capability:
            filtered = [m for m in filtered if request.capability in m["capabilities"]]
        if request.search_query:
            query = request.search_query.lower()
            filtered = [m for m in filtered if 
                       query in m["name"].lower() or 
                       query in m["id"].lower() or
                       any(query in cap for cap in m["capabilities"])]
        if request.min_context_window:
            filtered = [m for m in filtered if m["context_window"] >= request.min_context_window]
        if request.max_cost_per_token:
            filtered = [m for m in filtered if 
                       m["pricing"]["prompt"] <= request.max_cost_per_token]
    
    # Get performance metrics for filtered models
    performance_data = await _get_model_performance_metrics([m["id"] for m in filtered])
    
    return {
        "models": filtered,
        "performance_metrics": performance_data,
        "categories": _get_model_categories(filtered),
        "providers": list(set(m["provider"] for m in filtered)),
        "total_available": len(models),
        "filtered_count": len(filtered),
        "last_updated": datetime.utcnow().isoformat()
    }

@router.get("/executive/model-presets")
async def get_model_presets(
    current_role: UserRole = Depends(get_current_user_role)
) -> List[ModelPreset]:
    """Get executive model presets for common use cases"""
    if current_role != UserRole.CEO:
        raise HTTPException(status_code=403, detail="Executive access required")
    
    return [
        ModelPreset(
            name="Strategic Planning",
            description="Deep reasoning for complex strategic decisions",
            model_id="openai/o1-preview",
            use_cases=["Long-term planning", "Complex analysis", "Strategic decisions"]
        ),
        ModelPreset(
            name="Quick Intelligence",
            description="Fast, high-quality responses for rapid decisions",
            model_id="openai/gpt-4-turbo",
            use_cases=["Quick summaries", "Rapid insights", "Time-sensitive queries"]
        ),
        ModelPreset(
            name="Deep Analysis",
            description="Maximum analytical capability for comprehensive insights",
            model_id="anthropic/claude-3.5-sonnet",
            use_cases=["Market analysis", "Competitive intelligence", "Research synthesis"]
        ),
        ModelPreset(
            name="Cost Optimized",
            description="Best performance-to-cost ratio for routine queries",
            model_id="meta-llama/llama-3.1-70b-instruct",
            use_cases=["Routine queries", "High-volume analysis", "Cost-conscious operations"]
        ),
        ModelPreset(
            name="Latest & Greatest",
            description="Newest models with cutting-edge capabilities",
            model_id=await _get_latest_model(),
            use_cases=["Experimental features", "Breakthrough capabilities", "Innovation testing"]
        )
    ]

@router.post("/executive/model-comparison")
async def compare_models(
    query: str,
    model_ids: List[str],
    current_role: UserRole = Depends(get_current_user_role)
) -> Dict[str, Any]:
    """Compare multiple models on the same query"""
    if current_role != UserRole.CEO:
        raise HTTPException(status_code=403, detail="Executive access required")
    
    if len(model_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 models for comparison")
    
    or_client = await get_openrouter_client()
    comparison_results = []
    
    # Run query through each model in parallel
    tasks = []
    for model_id in model_ids:
        tasks.append(_run_model_comparison(or_client, model_id, query))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            comparison_results.append({
                "model_id": model_ids[i],
                "error": str(result),
                "success": False
            })
        else:
            comparison_results.append(result)
    
    return {
        "query": query,
        "comparisons": comparison_results,
        "recommendation": _recommend_best_model(comparison_results),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/executive/model-performance")
async def track_model_performance(
    model_id: str,
    response_time: float,
    quality_score: float,
    query_type: str,
    current_role: UserRole = Depends(get_current_user_role)
) -> Dict[str, Any]:
    """Track model performance for analytics"""
    if current_role != UserRole.CEO:
        raise HTTPException(status_code=403, detail="Executive access required")
    
    # Store performance data
    mcp = await get_mcp_client()
    await mcp.call_tool("ai_memory", "store_conversation",
        content=f"Model Performance: {model_id}",
        category="model_analytics",
        metadata={
            "model_id": model_id,
            "response_time": response_time,
            "quality_score": quality_score,
            "query_type": query_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    return {"status": "tracked", "model_id": model_id}

# AI System Command Center Endpoints
@router.get("/system/agents")
async def get_agent_status(
    current_role: UserRole = Depends(get_current_user_role)
) -> List[Dict[str, Any]]:
    """Get real-time status of all AI agents"""
    agents = []
    for agent_id, agent in agent_router.agent_instances.items():
        agents.append({
            "id": agent_id,
            "name": agent.__class__.__name__,
            "status": "active" if agent else "inactive",
            "last_activity": getattr(agent, "last_activity", None),
            "performance_metrics": getattr(agent, "get_metrics", lambda: {})()
        })
    return agents

@router.get("/system/infrastructure")
async def get_infrastructure_health(
    current_role: UserRole = Depends(get_current_user_role)
) -> Dict[str, Any]:
    """Get infrastructure component health status"""
    mcp = await get_mcp_client()
    
    # Check various infrastructure components
    health_checks = await asyncio.gather(
        mcp.call_tool("docker", "list_containers"),
        mcp.call_tool("snowflake", "health_check"),
        mcp.call_tool("pinecone", "health_check"),
        return_exceptions=True
    )
    
    return {
        "docker_containers": health_checks[0] if not isinstance(health_checks[0], Exception) else {"error": str(health_checks[0])},
        "snowflake": health_checks[1] if not isinstance(health_checks[1], Exception) else {"error": str(health_checks[1])},
        "pinecone": health_checks[2] if not isinstance(health_checks[2], Exception) else {"error": str(health_checks[2])},
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/system/api-catalog")
async def get_api_catalog(
    current_role: UserRole = Depends(get_current_user_role)
) -> List[Dict[str, Any]]:
    """Get catalog of all available API endpoints"""
    from fastapi import FastAPI
    from ...main import app
    
    endpoints = []
    for route in app.routes:
        if hasattr(route, "methods"):
            endpoints.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name,
                "tags": getattr(route, "tags", [])
            })
    
    return endpoints

# WebSocket for real-time updates
@router.websocket("/ws/executive-updates")
async def executive_updates_websocket(websocket: WebSocket):
    """WebSocket for real-time executive dashboard updates"""
    await ws_manager.connect(websocket, "executive_dashboard")
    try:
        while True:
            # Send periodic updates
            metrics = await get_dashboard_summary(UserRole.CEO)
            await websocket.send_json({
                "type": "metrics_update",
                "data": metrics.dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Wait before next update
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        ws_manager.disconnect("executive_dashboard")

# Helper functions
async def _select_optimal_model(query: str, context_size: int = 0) -> str:
    """Intelligently select optimal model based on query analysis"""
    or_client = await get_openrouter_client()
    
    # Analyze query characteristics
    query_lower = query.lower()
    query_length = len(query)
    
    # Determine query type and requirements
    query_type = "general"
    if any(word in query_lower for word in ["strategic", "plan", "long-term", "vision"]):
        query_type = "strategic_analysis"
    elif any(word in query_lower for word in ["quick", "summary", "brief", "tldr"]):
        query_type = "quick_response"
    elif any(word in query_lower for word in ["analyze", "deep", "comprehensive", "detailed"]):
        query_type = "deep_analysis"
    elif any(word in query_lower for word in ["code", "implement", "function", "algorithm"]):
        query_type = "code_generation"
    elif any(word in query_lower for word in ["cost", "budget", "economical"]):
        query_type = "cost_optimized"
    
    # Get optimal model for query type
    selected_model = await or_client.select_optimal_model(
        query_type=query_type,
        context_size=context_size or query_length,
        max_cost_per_token=0.01 if "cost" in query_lower else None
    )
    
    return selected_model

async def _enhance_model_categorization(models: List[Dict]) -> List[Dict[str, Any]]:
    """Enhanced model categorization with performance insights"""
    or_client = await get_openrouter_client()
    categorized = []
    
    for model in models:
        enhanced = {
            "id": model.get("id"),
            "name": model.get("name"),
            "provider": model.get("id", "").split("/")[0],
            "category": or_client.categorize_model(model),
            "context_window": model.get("context_length", 0),
            "pricing": model.get("pricing", {}),
            "capabilities": or_client.get_model_capabilities(model),
            "architecture": model.get("architecture", {}),
            "top_provider": model.get("top_provider", {}),
            "per_request_limits": model.get("per_request_limits", {}),
            "quality_score": _calculate_quality_score(model),
            "speed_rating": _calculate_speed_rating(model),
            "value_score": _calculate_value_score(model)
        }
        categorized.append(enhanced)
    
    return sorted(categorized, key=lambda x: x["quality_score"], reverse=True)

async def _get_model_performance_metrics(model_ids: List[str]) -> Dict[str, ModelPerformanceMetrics]:
    """Get performance metrics for specified models"""
    mcp = await get_mcp_client()
    metrics = {}
    
    for model_id in model_ids:
        # Query stored performance data
        perf_data = await mcp.call_tool("ai_memory", "recall_memory",
            query=f"model_performance:{model_id}",
            category="model_analytics"
        )
        
        if perf_data:
            # Aggregate metrics
            metrics[model_id] = ModelPerformanceMetrics(
                model_id=model_id,
                avg_response_time=perf_data.get("avg_response_time", 0),
                avg_quality_score=perf_data.get("avg_quality_score", 0),
                total_uses=perf_data.get("total_uses", 0),
                cost_per_query=perf_data.get("cost_per_query", 0),
                last_used=perf_data.get("last_used", datetime.utcnow())
            )
    
    return metrics

async def _get_latest_model() -> str:
    """Get the latest cutting-edge model available"""
    or_client = await get_openrouter_client()
    models = await or_client.get_models()
    
    # Sort by release date or version indicators
    latest_models = []
    for model in models:
        model_id = model.get("id", "")
        # Prioritize models with version numbers or "preview" in name
        if any(indicator in model_id.lower() for indicator in ["preview", "latest", "3.5", "4", "o1"]):
            latest_models.append(model)
    
    if latest_models:
        # Return the one with highest quality score
        return max(latest_models, key=lambda m: _calculate_quality_score(m)).get("id")
    
    return "openai/gpt-4-turbo"  # Fallback

async def _run_model_comparison(client: OpenRouterClient, model_id: str, query: str) -> Dict[str, Any]:
    """Run a single model comparison"""
    start_time = datetime.utcnow()
    
    try:
        response = await client.chat_completion(
            model=model_id,
            messages=[{"role": "user", "content": query}],
            temperature=0.7,
            max_tokens=1000
        )
        
        end_time = datetime.utcnow()
        response_time = (end_time - start_time).total_seconds()
        
        return {
            "model_id": model_id,
            "response": response["content"],
            "response_time": response_time,
            "tokens_used": response.get("usage", {}),
            "cost": _calculate_query_cost(model_id, response.get("usage", {})),
            "success": True
        }
    except Exception as e:
        return {
            "model_id": model_id,
            "error": str(e),
            "success": False
        }

def _recommend_best_model(comparison_results: List[Dict]) -> Dict[str, Any]:
    """Recommend the best model based on comparison results"""
    successful_results = [r for r in comparison_results if r.get("success")]
    
    if not successful_results:
        return {"recommendation": None, "reason": "All models failed"}
    
    # Score based on response time and cost
    scored_results = []
    for result in successful_results:
        score = 100  # Base score
        score -= result["response_time"] * 10  # Penalize slow responses
        score -= result.get("cost", 0) * 1000  # Penalize expensive models
        
        scored_results.append({
            "model_id": result["model_id"],
            "score": score,
            "response_time": result["response_time"],
            "cost": result.get("cost", 0)
        })
    
    best = max(scored_results, key=lambda x: x["score"])
    
    return {
        "recommendation": best["model_id"],
        "reason": f"Best balance of speed ({best['response_time']:.2f}s) and cost (${best['cost']:.4f})",
        "scores": scored_results
    }

def _calculate_quality_score(model: Dict) -> float:
    """Calculate quality score for a model"""
    score = 50.0  # Base score
    
    # Boost for known high-quality models
    model_id = model.get("id", "").lower()
    if "gpt-4" in model_id:
        score += 20
    if "claude" in model_id:
        score += 20
    if "o1" in model_id:
        score += 25
    
    # Boost for large context windows
    context = model.get("context_length", 0)
    if context >= 200000:
        score += 15
    elif context >= 100000:
        score += 10
    elif context >= 32000:
        score += 5
    
    return min(score, 100.0)

def _calculate_speed_rating(model: Dict) -> str:
    """Calculate speed rating for a model"""
    model_id = model.get("id", "").lower()
    
    if "turbo" in model_id or "haiku" in model_id:
        return "fast"
    elif "o1" in model_id or "opus" in model_id:
        return "slow"
    else:
        return "medium"

def _calculate_value_score(model: Dict) -> float:
    """Calculate value score (quality per dollar)"""
    quality = _calculate_quality_score(model)
    pricing = model.get("pricing", {})
    prompt_cost = pricing.get("prompt", 1.0)
    
    if prompt_cost > 0:
        return quality / (prompt_cost * 1000)  # Quality per $0.001
    return 0.0

def _calculate_query_cost(model_id: str, usage: Dict) -> float:
    """Calculate the cost of a query"""
    # This would need real pricing data
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    
    # Simplified cost calculation
    cost_per_1k = 0.01  # Default
    if "gpt-4" in model_id:
        cost_per_1k = 0.03
    elif "claude" in model_id:
        cost_per_1k = 0.025
    
    total_tokens = prompt_tokens + completion_tokens
    return (total_tokens / 1000) * cost_per_1k

def _get_model_categories(models: List[Dict]) -> Dict[str, List[str]]:
    """Get model categories with counts"""
    categories = {}
    for model in models:
        category = model.get("category", "general")
        if category not in categories:
            categories[category] = []
        categories[category].append(model["id"])
    
    return {cat: len(models) for cat, models in categories.items()}

def _build_synthesis_prompt(query: str, internal_results: List, external_results: List, mode: str) -> str:
    """Build synthesis prompt for LLM"""
    prompt = f"Strategic Query: {query}\n\n"
    
    if internal_results and mode in ["internal", "combined"]:
        prompt += "Internal Intelligence:\n"
        for i, result in enumerate(internal_results):
            if not isinstance(result, Exception):
                prompt += f"- Source {i+1}: {str(result)[:500]}...\n"
    
    if external_results and mode in ["external", "combined"]:
        prompt += "\nExternal Intelligence:\n"
        for i, result in enumerate(external_results):
            if not isinstance(result, Exception):
                prompt += f"- Source {i+1}: {str(result)[:500]}...\n"
    
    prompt += "\nProvide a comprehensive strategic response synthesizing all available intelligence."
    return prompt

def _format_sources(results: List) -> List[Dict[str, Any]]:
    """Format source results for response"""
    formatted = []
    for i, result in enumerate(results):
        if not isinstance(result, Exception):
            formatted.append({
                "source_id": i,
                "type": "internal" if i < 3 else "external",
                "summary": str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
            })
    return formatted

def _categorize_models(models: List[Dict]) -> List[Dict[str, Any]]:
    """Categorize models for executive use"""
    categorized = []
    for model in models:
        category = "general"
        if "o1" in model.get("id", ""):
            category = "reasoning"
        elif "claude" in model.get("id", ""):
            category = "analysis"
        elif "gpt-4-turbo" in model.get("id", ""):
            category = "speed"
        
        categorized.append({
            "id": model.get("id"),
            "name": model.get("name"),
            "provider": model.get("id", "").split("/")[0],
            "category": category,
            "context_window": model.get("context_length", 0),
            "pricing": model.get("pricing", {}),
            "capabilities": _extract_capabilities(model)
        })
    
    return categorized

def _extract_capabilities(model: Dict) -> List[str]:
    """Extract model capabilities"""
    capabilities = []
    model_id = model.get("id", "").lower()
    
    if "vision" in model_id:
        capabilities.append("vision")
    if "o1" in model_id:
        capabilities.append("advanced_reasoning")
    if "claude" in model_id:
        capabilities.append("deep_analysis")
    if "gpt-4" in model_id:
        capabilities.append("general_intelligence")
    if "turbo" in model_id:
        capabilities.append("fast_response")
    
    return capabilities
