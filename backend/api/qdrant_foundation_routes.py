"""
Qdrant Foundation API Routes - Phase 1 Implementation
FastAPI routes for the unified Qdrant-based foundation service

Endpoints:
- POST /api/v1/foundation/query - Unified query interface
- POST /api/v1/foundation/agentic-search - Agentic RAG queries
- POST /api/v1/foundation/hypothetical-qa - Hypothetical document QA
- POST /api/v1/foundation/visual-qa - Visual document QA
- POST /api/v1/foundation/multimodal-search - Multimodal search
- GET /api/v1/foundation/metrics - Performance metrics
- GET /api/v1/foundation/health - Health check
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Tuple
import time
import logging

from backend.services.QDRANT_foundation_service import (
    QdrantFoundationService,
    QueryRequest,
    QueryResponse,
    QueryType,
    get_QDRANT_foundation_service
)
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/foundation", tags=["Qdrant Foundation"])

# Pydantic models for API
class UnifiedQueryRequest(BaseModel):
    """Unified query request model"""
    query: str = Field(..., description="The search query")
    query_type: str = Field(default="simple_search", description="Type of query to execute")
    user_id: str = Field(default="default", description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Query metadata")
    performance_requirements: Dict[str, Any] = Field(default_factory=dict, description="Performance requirements")

class AgenticSearchRequest(BaseModel):
    """Agentic RAG search request"""
    query: str = Field(..., description="Complex query requiring multi-step reasoning")
    user_id: str = Field(default="default", description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    max_iterations: int = Field(default=3, description="Maximum reasoning iterations")
    include_tools: bool = Field(default=True, description="Include MCP tool calls")

class HypotheticalQARequest(BaseModel):
    """Hypothetical document QA request"""
    query: str = Field(..., description="Question for hypothetical document generation")
    document_type: str = Field(default="answer_focused", description="Type of hypothetical document")
    boost_factor: float = Field(default=1.2, description="Boost factor for hypothetical results")

class VisualQARequest(BaseModel):
    """Visual document QA request"""
    question: str = Field(..., description="Question about visual content")
    document_id: Optional[str] = Field(None, description="Specific document to query")
    context_limit: int = Field(default=5, description="Maximum visual elements to consider")

class MultimodalSearchRequest(BaseModel):
    """Multimodal search request"""
    query: str = Field(..., description="Search query for multimodal content")
    include_visual: bool = Field(default=True, description="Include visual elements")
    include_text: bool = Field(default=True, description="Include text content")
    limit: int = Field(default=10, description="Maximum results to return")

class QueryResponseModel(BaseModel):
    """Query response model"""
    query_id: str
    results: List[Dict[str, Any]]
    confidence: float
    processing_time_ms: float
    memory_tier_used: str
    cost_optimization: Dict[str, Any]
    metadata: Dict[str, Any]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    services: Dict[str, str]
    performance: Dict[str, Any]
    timestamp: str

@router.post("/query", response_model=QueryResponseModel)
async def unified_query(request: UnifiedQueryRequest):
    """
    Unified query interface supporting all query types
    
    This endpoint automatically routes queries to the appropriate service
    based on query content and type specification.
    """
    try:
        foundation_service = await get_QDRANT_foundation_service()
        
        # Convert string query type to enum
        try:
            query_type = QueryType(request.query_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid query_type: {request.query_type}")
        
        # Create internal query request
        query_request = QueryRequest(
            query=request.query,
            query_type=query_type,
            user_id=request.user_id,
            session_id=request.session_id,
            context=request.context,
            metadata=request.metadata,
            performance_requirements=request.performance_requirements
        )
        
        # Execute query
        response = await foundation_service.query(query_request)
        
        return QueryResponseModel(
            query_id=response.query_id,
            results=response.results,
            confidence=response.confidence,
            processing_time_ms=response.processing_time_ms,
            memory_tier_used=response.memory_tier_used.value,
            cost_optimization=response.cost_optimization,
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"❌ Unified query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agentic-search", response_model=QueryResponseModel)
async def agentic_search(request: AgenticSearchRequest):
    """
    Agentic RAG search with multi-step reasoning
    
    Uses LangGraph stateful workflows for complex queries requiring
    multiple reasoning steps, tool usage, and iterative refinement.
    """
    try:
        foundation_service = await get_QDRANT_foundation_service()
        
        query_request = QueryRequest(
            query=request.query,
            query_type=QueryType.AGENTIC_RAG,
            user_id=request.user_id,
            session_id=request.session_id,
            performance_requirements={
                "max_iterations": request.max_iterations,
                "include_tools": request.include_tools
            }
        )
        
        response = await foundation_service.query(query_request)
        
        return QueryResponseModel(
            query_id=response.query_id,
            results=response.results,
            confidence=response.confidence,
            processing_time_ms=response.processing_time_ms,
            memory_tier_used=response.memory_tier_used.value,
            cost_optimization=response.cost_optimization,
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"❌ Agentic search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hypothetical-qa", response_model=QueryResponseModel)
async def hypothetical_qa(request: HypotheticalQARequest):
    """
    Hypothetical document QA with proactive generation
    
    Generates hypothetical documents to answer queries that might not
    have direct matches in the knowledge base.
    """
    try:
        foundation_service = await get_QDRANT_foundation_service()
        
        query_request = QueryRequest(
            query=request.query,
            query_type=QueryType.HYPOTHETICAL_QA,
            performance_requirements={
                "document_type": request.document_type,
                "boost_factor": request.boost_factor
            }
        )
        
        response = await foundation_service.query(query_request)
        
        return QueryResponseModel(
            query_id=response.query_id,
            results=response.results,
            confidence=response.confidence,
            processing_time_ms=response.processing_time_ms,
            memory_tier_used=response.memory_tier_used.value,
            cost_optimization=response.cost_optimization,
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"❌ Hypothetical QA failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/visual-qa", response_model=QueryResponseModel)
async def visual_qa(request: VisualQARequest):
    """
    Visual document question answering
    
    Answers questions about visual content including images, charts,
    diagrams, and other visual elements in documents.
    """
    try:
        foundation_service = await get_QDRANT_foundation_service()
        
        query_request = QueryRequest(
            query=request.question,
            query_type=QueryType.VISUAL_QA,
            context={"document_id": request.document_id},
            performance_requirements={"context_limit": request.context_limit}
        )
        
        response = await foundation_service.query(query_request)
        
        return QueryResponseModel(
            query_id=response.query_id,
            results=response.results,
            confidence=response.confidence,
            processing_time_ms=response.processing_time_ms,
            memory_tier_used=response.memory_tier_used.value,
            cost_optimization=response.cost_optimization,
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"❌ Visual QA failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/multimodal-search", response_model=QueryResponseModel)
async def multimodal_search(request: MultimodalSearchRequest):
    """
    Multimodal search across text and visual content
    
    Searches across both textual and visual content using unified
    embeddings and multimodal understanding.
    """
    try:
        foundation_service = await get_QDRANT_foundation_service()
        
        query_request = QueryRequest(
            query=request.query,
            query_type=QueryType.MULTIMODAL_SEARCH,
            performance_requirements={
                "include_visual": request.include_visual,
                "include_text": request.include_text,
                "limit": request.limit
            }
        )
        
        response = await foundation_service.query(query_request)
        
        return QueryResponseModel(
            query_id=response.query_id,
            results=response.results,
            confidence=response.confidence,
            processing_time_ms=response.processing_time_ms,
            memory_tier_used=response.memory_tier_used.value,
            cost_optimization=response.cost_optimization,
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"❌ Multimodal search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics():
    """
    Get comprehensive performance metrics
    
    Returns performance metrics for all foundation services including
    latency, accuracy, cache hit rates, and cost optimization.
    """
    try:
        foundation_service = await get_QDRANT_foundation_service()
        metrics = foundation_service.get_foundation_metrics()
        
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check for foundation services
    
    Checks the health of all integrated services and returns
    overall system status.
    """
    try:
        foundation_service = await get_QDRANT_foundation_service()
        
        # Check service health
        services_status = {
            "unified_memory": "healthy" if foundation_service.unified_memory else "unavailable",
            "hypothetical_rag": "healthy" if foundation_service.hypothetical_rag else "unavailable",
            "multimodal_memory": "healthy" if foundation_service.multimodal_memory else "unavailable"
        }
        
        # Get performance summary
        metrics = foundation_service.get_foundation_metrics()
        performance_summary = {
            "total_queries": metrics["foundation"]["total_queries"],
            "average_latency_ms": round(metrics["foundation"]["average_latency_ms"], 2),
            "accuracy_score": round(metrics["foundation"]["accuracy_score"], 3),
            "cache_hit_rate": round(metrics["foundation"]["cache_hit_rate"], 3)
        }
        
        # Determine overall status
        all_healthy = all(status == "healthy" for status in services_status.values())
        overall_status = "healthy" if all_healthy else "degraded"
        
        return HealthResponse(
            status=overall_status,
            services=services_status,
            performance=performance_summary,
            timestamp=str(time.time())
        )
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            services={},
            performance={},
            timestamp=str(time.time())
        )

@router.post("/admin/optimize")
async def trigger_optimization(background_tasks: BackgroundTasks):
    """
    Trigger manual optimization of foundation services
    
    Manually triggers cost optimization, cache pruning, and
    performance tuning across all services.
    """
    try:
        foundation_service = await get_QDRANT_foundation_service()
        
        async def run_optimization():
            """Background optimization task"""
            try:
                if foundation_service.hypothetical_rag:
                    await foundation_service.hypothetical_rag._comprehensive_pruning()
                
                logger.info("✅ Manual optimization completed")
            except Exception as e:
                logger.error(f"❌ Manual optimization failed: {e}")
        
        background_tasks.add_task(run_optimization)
        
        return {
            "status": "optimization_triggered",
            "message": "Background optimization started",
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to trigger optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 