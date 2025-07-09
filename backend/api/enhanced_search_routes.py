"""
Enhanced Search API Routes
Provides multi-tier search capabilities with real-time streaming
"""

import json
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.services.enhanced_search_service import (
    EnhancedSearchService,
    SearchProvider,
    SearchRequest,
    SearchTier,
)
from backend.services.unified_chat_service import UnifiedChatService

logger = logging.getLogger(__name__)

# Initialize services
enhanced_search_service = EnhancedSearchService()
unified_chat_service = UnifiedChatService()

# Create router
router = APIRouter(prefix="/api/v1/search", tags=["enhanced_search"])


class SearchQuery(BaseModel):
    """Search query request model"""

    query: str = Field(..., description="Search query")
    tier: str = Field(
        "tier_1", description="Search tier: tier_1, tier_2, tier_3, fast, deep, deepest"
    )
    providers: list[str] = Field(
        default_factory=list, description="Specific providers to use"
    )
    max_results: int = Field(
        10, ge=1, le=100, description="Maximum results per provider"
    )
    include_context: bool = Field(True, description="Include contextual information")
    user_id: str = Field("anonymous", description="User ID")
    session_id: str = Field("default", description="Session ID")
    search_domains: list[str] = Field(
        default_factory=list, description="Specific domains to search"
    )
    exclude_domains: list[str] = Field(
        default_factory=list, description="Domains to exclude"
    )
    language: str = Field("en", description="Search language")
    safe_search: bool = Field(True, description="Enable safe search")


class SearchResponse(BaseModel):
    """Search response model"""

    type: str = Field(..., description="Response type")
    provider: str | None = Field(None, description="Search provider")
    data: list[dict[str, Any]] | None = Field(None, description="Search results")
    metadata: dict[str, Any] | None = Field(None, description="Result metadata")
    processing_time: float | None = Field(
        None, description="Processing time in seconds"
    )
    confidence: float | None = Field(None, description="Confidence score")
    cached: bool | None = Field(None, description="Whether result was cached")
    message: str | None = Field(None, description="Status message")
    timestamp: str | None = Field(None, description="Timestamp")
    error: str | None = Field(None, description="Error message")


@router.post("/search", response_model=list[SearchResponse])
async def search(query: SearchQuery) -> list[SearchResponse]:
    """
    Perform enhanced search with specified tier and providers

    Returns all results at once (non-streaming)
    """
    try:
        # Convert providers to enum
        provider_enums = []
        for provider in query.providers:
            try:
                provider_enums.append(SearchProvider(provider))
            except ValueError:
                logger.warning(f"Invalid provider: {provider}")

        # Create search request
        search_request = SearchRequest(
            query=query.query,
            tier=SearchTier(query.tier),
            providers=provider_enums,
            max_results=query.max_results,
            include_context=query.include_context,
            user_id=query.user_id,
            session_id=query.session_id,
            search_domains=query.search_domains,
            exclude_domains=query.exclude_domains,
            language=query.language,
            safe_search=query.safe_search,
        )

        # Collect all results
        results = []
        async for result in enhanced_search_service.search(search_request):
            results.append(SearchResponse(**result))

        return results

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/stream")
async def search_stream(
    query: str = Query(..., description="Search query"),
    tier: str = Query("tier_1", description="Search tier"),
    providers: str = Query("", description="Comma-separated providers"),
    max_results: int = Query(10, ge=1, le=100, description="Maximum results"),
    user_id: str = Query("anonymous", description="User ID"),
    session_id: str = Query("default", description="Session ID"),
    search_domains: str = Query("", description="Comma-separated domains"),
    exclude_domains: str = Query("", description="Comma-separated domains to exclude"),
    language: str = Query("en", description="Search language"),
    safe_search: bool = Query(True, description="Enable safe search"),
):
    """
    Stream enhanced search results in real-time

    Uses Server-Sent Events (SSE) for streaming
    """

    async def generate_search_stream():
        try:
            # Parse providers
            provider_list = [p.strip() for p in providers.split(",") if p.strip()]
            provider_enums = []
            for provider in provider_list:
                try:
                    provider_enums.append(SearchProvider(provider))
                except ValueError:
                    logger.warning(f"Invalid provider: {provider}")

            # Parse domains
            domain_list = [d.strip() for d in search_domains.split(",") if d.strip()]
            exclude_list = [d.strip() for d in exclude_domains.split(",") if d.strip()]

            # Create search request
            search_request = SearchRequest(
                query=query,
                tier=SearchTier(tier),
                providers=provider_enums,
                max_results=max_results,
                user_id=user_id,
                session_id=session_id,
                search_domains=domain_list,
                exclude_domains=exclude_list,
                language=language,
                safe_search=safe_search,
            )

            # Stream results
            async for result in enhanced_search_service.search(search_request):
                yield f"data: {json.dumps(result)}\n\n"

        except Exception as e:
            logger.error(f"Search stream failed: {e}")
            error_data = {
                "type": "error",
                "message": str(e),
                "timestamp": "2025-01-09T00:00:00Z",
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        generate_search_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        },
    )


@router.websocket("/search/ws")
async def search_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time search

    Provides bidirectional communication for search queries
    """
    await websocket.accept()

    try:
        while True:
            # Receive search query
            data = await websocket.receive_text()
            query_data = json.loads(data)

            # Validate query
            if "query" not in query_data:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": "Missing 'query' field",
                            "timestamp": "2025-01-09T00:00:00Z",
                        }
                    )
                )
                continue

            # Extract parameters
            query = query_data["query"]
            tier = query_data.get("tier", "tier_1")
            providers = query_data.get("providers", [])
            max_results = query_data.get("max_results", 10)
            user_id = query_data.get("user_id", "anonymous")
            session_id = query_data.get("session_id", "default")

            # Convert providers to enum
            provider_enums = []
            for provider in providers:
                try:
                    provider_enums.append(SearchProvider(provider))
                except ValueError:
                    logger.warning(f"Invalid provider: {provider}")

            # Create search request
            search_request = SearchRequest(
                query=query,
                tier=SearchTier(tier),
                providers=provider_enums,
                max_results=max_results,
                user_id=user_id,
                session_id=session_id,
            )

            # Stream results through WebSocket
            async for result in enhanced_search_service.search(search_request):
                await websocket.send_text(json.dumps(result))

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "error",
                        "message": str(e),
                        "timestamp": "2025-01-09T00:00:00Z",
                    }
                )
            )
        except:
            pass  # Connection might be closed


@router.get("/search/intelligent")
async def intelligent_search(
    query: str = Query(..., description="Search query"),
    user_id: str = Query("anonymous", description="User ID"),
    session_id: str = Query("default", description="Session ID"),
    context: str = Query("", description="Additional context"),
):
    """
    Intelligent search that automatically determines the best tier and providers
    """
    try:
        # Parse context
        context_dict = {}
        if context:
            try:
                context_dict = json.loads(context)
            except json.JSONDecodeError:
                context_dict = {"raw_context": context}

        # Use unified chat service for intelligent routing
        search_tier = await unified_chat_service.intelligent_search_routing(
            query, context_dict
        )

        # Create search request
        search_request = SearchRequest(
            query=query, tier=search_tier, user_id=user_id, session_id=session_id
        )

        # Collect results
        results = []
        async for result in enhanced_search_service.search(search_request):
            results.append(result)

        return {
            "query": query,
            "selected_tier": search_tier.value,
            "results": results,
            "metadata": {
                "intelligent_routing": True,
                "context_used": bool(context_dict),
            },
        }

    except Exception as e:
        logger.error(f"Intelligent search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def get_providers():
    """Get available search providers"""
    return {
        "providers": [
            {
                "name": "brave",
                "display_name": "Brave Search",
                "description": "Privacy-focused search engine",
                "supported_tiers": ["tier_1", "tier_2", "tier_3"],
            },
            {
                "name": "searxng",
                "display_name": "SearXNG",
                "description": "Open-source metasearch engine",
                "supported_tiers": ["tier_2", "tier_3"],
            },
            {
                "name": "perplexity",
                "display_name": "Perplexity AI",
                "description": "AI-powered search with analysis",
                "supported_tiers": ["tier_3"],
            },
            {
                "name": "browser",
                "display_name": "Browser Automation",
                "description": "Direct browser-based search",
                "supported_tiers": ["tier_2", "tier_3"],
            },
            {
                "name": "internal",
                "display_name": "Internal Knowledge",
                "description": "Search internal knowledge base",
                "supported_tiers": ["tier_1", "tier_2", "tier_3"],
            },
        ],
        "tiers": [
            {
                "name": "tier_1",
                "display_name": "Fast Search",
                "description": "Quick search results (<2s)",
                "aliases": ["fast"],
            },
            {
                "name": "tier_2",
                "display_name": "Deep Search",
                "description": "Comprehensive search with context (<30s)",
                "aliases": ["deep"],
            },
            {
                "name": "tier_3",
                "display_name": "Deep Deep Search",
                "description": "Exhaustive search with analysis (<5min)",
                "aliases": ["deepest"],
            },
        ],
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test basic functionality
        test_request = SearchRequest(
            query="test", tier=SearchTier.TIER_1, max_results=1
        )

        # Try to get at least one result
        result_count = 0
        async for result in enhanced_search_service.search(test_request):
            result_count += 1
            if result_count >= 1:
                break

        return {
            "status": "healthy",
            "service": "enhanced_search",
            "timestamp": "2025-01-09T00:00:00Z",
            "test_results": result_count,
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "enhanced_search",
            "error": str(e),
            "timestamp": "2025-01-09T00:00:00Z",
        }


@router.post("/cleanup")
async def cleanup():
    """Clean up search service resources"""
    try:
        await enhanced_search_service.cleanup()
        return {
            "status": "cleaned_up",
            "service": "enhanced_search",
            "timestamp": "2025-01-09T00:00:00Z",
        }
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
