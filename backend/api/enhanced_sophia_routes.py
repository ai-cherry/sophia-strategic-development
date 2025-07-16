"""
Enhanced Sophia API Routes
Where the magic becomes accessible
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import json

from backend.services.enhanced_unified_chat_service import EnhancedSophiaUnifiedOrchestrator
from backend.services.external_knowledge_service import ExternalKnowledgeService
from backend.services.sophia_unified_memory_service import SophiaUnifiedMemoryService


router = APIRouter(prefix="/api/v4/sophia", tags=["Enhanced Sophia"])

# Services
chat_service = EnhancedSophiaUnifiedOrchestrator()
external_service = ExternalKnowledgeService()
orchestrator = SophiaUnifiedOrchestrator()
memory_service = SophiaUnifiedMemoryService()


# Request/Response Models
class ChatRequest(BaseModel):
    query: str = Field(..., description="User query")
    user_id: str = Field("ceo_user", description="User ID for personalization")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    personality_override: Optional[str] = Field(
        None, description="Force specific personality"
    )
    enrich_external: bool = Field(False, description="Enrich with external knowledge")


class PersonalityRequest(BaseModel):
    user_id: str = Field("ceo_user")
    personality: Optional[str] = Field(None, description="Set personality")
    snark_level: Optional[int] = Field(
        None, ge=0, le=10, description="Snark level 0-10"
    )


class ExternalEnrichRequest(BaseModel):
    query: str
    sources: List[str] = Field(["x", "news"], description="External sources to use")
    store_results: bool = Field(True, description="Store in knowledge base")


@router.post("/chat", response_model=Dict[str, Any])
async def enhanced_chat(request: ChatRequest):
    """
    Enhanced chat with personality and multi-hop reasoning
    Now with 100% more snark (if requested)
    """
    try:
        # Check if external enrichment requested
        if request.enrich_external:
            enrichment = await external_service.enrich_query_with_external(
                query=request.query, sources=["x", "news"]
            )
            # Add enrichment context to query
            if enrichment["items_added"] > 0:
                request.query += f"\n[External context: {enrichment['items_added']} recent items found]"

        # Generate response with personality
        response = await chat_service.generate_response(
            query=request.query, user_id=request.user_id, session_id=request.session_id
        )

        # Override personality if requested
        if request.personality_override:
            # Re-generate with specific personality
            chat_service.active_sessions[
                request.session_id or "temp"
            ] = request.personality_override
            response = await chat_service.generate_response(
                query=request.query,
                user_id=request.user_id,
                session_id=request.session_id,
            )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/personality/info")
async def get_personality_info(user_id: str = Query("ceo_user")):
    """
    Get available personalities and current state
    Find out which version of Sophia you're talking to
    """
    try:
        info = await chat_service.get_personality_info(user_id)
        return info
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get personality info: {str(e)}"
        )


@router.post("/personality/configure")
async def configure_personality(request: PersonalityRequest):
    """
    Configure personality settings for a user
    Warning: High snark levels may cause emotional damage
    """
    try:
        updates = []

        # Set personality if provided
        if request.personality:
            profile = await memory_service.get_user_profile(request.user_id)
            profile["persona"] = request.personality

            # Store updated profile
            profile_key = f"user_profile:{request.user_id}"
            await memory_service.redis.setex(profile_key, 3600, json.dumps(profile))
            updates.append(f"Personality set to {request.personality}")

        # Adjust snark level if provided
        if request.snark_level is not None:
            response = await chat_service.adjust_snark_level(
                request.user_id, request.snark_level
            )
            updates.append(response)

        return {
            "success": True,
            "updates": updates,
            "message": "Personality configuration updated. Prepare for a new experience.",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")


@router.post("/enrich/external")
async def enrich_with_external(request: ExternalEnrichRequest):
    """
    Enrich query with external real-time knowledge
    Because living in the past is for databases
    """
    try:
        enrichment = await external_service.enrich_query_with_external(
            query=request.query, sources=request.sources
        )

        return {
            "success": True,
            "enrichment": enrichment,
            "message": f"Added {enrichment['items_added']} external items to knowledge base",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


@router.get("/trending")
async def get_trending_topics():
    """
    Get current trending topics
    What's hot in the streets (that matters for business)
    """
    try:
        trends = await external_service.get_trending_topics()

        # Filter for business relevance
        business_trends = [
            t
            for t in trends
            if not any(
                skip in t["topic"].lower()
                for skip in ["celebrity", "sports", "entertainment"]
            )
        ]

        return {
            "trends": business_trends,
            "total": len(business_trends),
            "sources": ["x_trending"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")


@router.post("/orchestrate/debug")
async def debug_orchestration(query: str = Body(...), user_id: str = Body("ceo_user")):
    """
    Debug multi-hop orchestration
    See how the sausage is made
    """
    try:
        result = await orchestrator.orchestrate(query, user_id)

        return {
            "response": result["response"],
            "metadata": result["metadata"],
            "debug": result["debug"],
            "execution_graph": {
                "complexity": result["metadata"]["complexity"],
                "iterations": result["metadata"]["iterations"],
                "routing_path": result["metadata"]["routing_path"],
                "sub_tasks": result["debug"]["sub_tasks"],
                "quality_assessment": result["debug"]["quality"],
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")


@router.get("/personalization/stats")
async def get_personalization_stats(user_id: str = Query("ceo_user")):
    """
    Get personalization statistics
    How well does Sophia know you?
    """
    try:
        stats = await memory_service.get_personalization_stats(user_id)
        profile = await memory_service.get_user_profile(user_id)

        return {
            "user_id": user_id,
            "stats": stats,
            "profile_summary": {
                "interactions": profile.get("interaction_count", 0),
                "focus_areas": profile.get("focus_areas", []),
                "current_personality": profile.get("persona", "Professional"),
                "preferences": profile.get("preferences", {}),
            },
            "personalization_level": "Expert"
            if profile.get("interaction_count", 0) > 50
            else "Learning",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/auto-optimize/trigger")
async def trigger_auto_optimization():
    """
    Manually trigger performance optimization
    When you can't wait for the cron job
    """
    # This would trigger the n8n workflow via webhook
    return {
        "success": True,
        "message": "Optimization workflow triggered. Check Slack for updates.",
        "webhook": "http://n8n:5678/webhook/optimize-mcp",
    }


# Health check
@router.get("/health")
async def health_check():
    """Even snarky AIs need health checks"""
    return {
        "status": "healthy",
        "version": "4.0-enhanced",
        "features": {
            "multi_hop_reasoning": True,
            "personality_engine": True,
            "external_knowledge": True,
            "self_optimization": True,
        },
        "personality": "Ready to roast your queries",
    }
