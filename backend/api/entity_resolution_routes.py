"""
Entity Resolution API Routes for Sophia AI
Handles entity disambiguation, clarification, and learning endpoints
"""

import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from backend.services.sophia_unified_orchestrator import SophiaUnifiedOrchestrator as SophiaUnifiedOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entity-resolution", tags=["Entity Resolution"])

# ========================================================================================
# REQUEST/RESPONSE MODELS
# ========================================================================================


class EntityResolutionRequest(BaseModel):
    """Request model for entity resolution"""

    query: str = Field(
        ..., description="Natural language query containing entity references"
    )
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    entity_type: Optional[str] = Field(None, description="Optional entity type filter")


class EntityClarificationRequest(BaseModel):
    """Request model for entity clarification response"""

    event_id: str = Field(..., description="Resolution event ID")
    selected_entity_id: str = Field(..., description="User-selected entity ID")
    user_query: str = Field(..., description="Original user query")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")


class EntityRegistrationRequest(BaseModel):
    """Request model for registering new entities"""

    entity_type: str = Field(
        ..., description="Type of entity (company, person, property, customer)"
    )
    entity_name: str = Field(..., description="Name of the entity")
    source_id: Optional[str] = Field(None, description="Source system ID")
    source_system: Optional[str] = Field(None, description="Source system name")
    metadata: Optional[dict[str, Any]] = Field(
        None, description="Additional entity metadata"
    )


class EntityCandidateModel(BaseModel):
    """Model for entity candidates"""

    entity_id: str
    canonical_name: str
    similarity_score: float
    match_reason: str
    aliases: list[str]


class EntityResolutionResponse(BaseModel):
    """Response model for entity resolution"""

    type: str = Field(
        ...,
        description="Response type: 'clarification_needed', 'query_result', or 'error'",
    )
    message: Optional[str] = Field(
        None, description="Response message or clarification question"
    )
    entity_matches: Optional[dict[str, Any]] = Field(
        None, description="Entity match details"
    )
    query_result: Optional[dict[str, Any]] = Field(
        None, description="Query results if resolved"
    )
    event_id: Optional[str] = Field(None, description="Event ID for tracking")


# ========================================================================================
# ENTITY RESOLUTION SERVICE INSTANCE
# ========================================================================================

chat_service = SophiaUnifiedOrchestrator()

# ========================================================================================
# API ENDPOINTS
# ========================================================================================


@router.post("/resolve", response_model=EntityResolutionResponse)
async def resolve_entities(request: EntityResolutionRequest):
    """
    Resolve entities in a natural language query.

    This endpoint analyzes the query for entity references (companies, people, properties)
    and either auto-resolves them or asks for clarification if multiple matches are found.
    """
    try:
        # Initialize chat service if needed
        if not chat_service.servers:
            await chat_service.initialize()

        # Analyze query context with entity resolution
        query_context = await chat_service._analyze_query_context(
            request.query, request.user_id
        )

        if query_context.needs_clarification:
            # Generate event ID for tracking
            event_id = f"EID_{int(datetime.now().timestamp() * 1000)}"

            return EntityResolutionResponse(
                type="clarification_needed",
                message=query_context.clarification_message,
                entity_matches=query_context.entity_context,
                event_id=event_id,
            )
        else:
            # Process query with resolved entities
            result = await chat_service.process_query(
                request.query, request.user_id, request.session_id
            )

            return EntityResolutionResponse(
                type="query_result",
                query_result=result,
                entity_matches=query_context.entity_context,
            )

    except Exception as e:
        logger.error(f"Entity resolution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clarify")
async def clarify_entity_selection(request: EntityClarificationRequest):
    """
    Handle user's clarification response for entity disambiguation.

    When the system asks for clarification about which entity the user meant,
    this endpoint processes their selection and learns from it for future queries.
    """
    try:
        # Process the clarification
        result = await chat_service.resolve_entity_clarification(
            request.event_id,
            request.selected_entity_id,
            request.user_query,
            request.user_id,
            request.session_id,
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {
            "status": "success",
            "message": "Entity clarification processed",
            "result": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Entity clarification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register")
async def register_new_entity(request: EntityRegistrationRequest):
    """
    Register a new entity in the system.

    Use this endpoint when a user mentions an entity that's not found in the system
    and needs to be added for future recognition.
    """
    try:
        result = await chat_service.register_new_entity(
            request.entity_type,
            request.entity_name,
            request.source_id,
            request.source_system,
            request.metadata,
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Entity registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_entity_resolution_analytics(user_id: str):
    """
    Get analytics on entity resolution performance.

    Returns metrics on resolution accuracy, common clarifications,
    and system learning effectiveness.
    """
    try:
        analytics = await chat_service.get_entity_resolution_analytics(user_id)

        if "error" in analytics:
            raise HTTPException(status_code=500, detail=analytics["error"])

        return analytics

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/search")
async def search_entities(
    query: str,
    entity_type: Optional[str] = None,
    limit: int = 10,
    threshold: float = 0.75,
):
    """
    Search for entities by name with fuzzy matching.

    Returns a ranked list of entities that match the search query,
    useful for autocomplete and entity suggestion features.
    """
    try:
        if not chat_service.entity_resolution_service:
            raise HTTPException(
                status_code=503, detail="Entity resolution service not available"
            )

        # Find entity matches
        matches = await chat_service.entity_resolution_service._find_entity_matches(
            query, entity_type
        )

        # Filter by threshold and limit
        filtered_matches = [
            match for match in matches if match["similarity_score"] >= threshold
        ][:limit]

        return {
            "query": query,
            "matches": filtered_matches,
            "total_found": len(filtered_matches),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Entity search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/{entity_id}")
async def get_entity_details(entity_id: str):
    """
    Get detailed information about a specific entity.

    Returns canonical name, aliases, source systems, and metadata
    for the specified entity.
    """
    try:
        if not chat_service.entity_resolution_service:
            raise HTTPException(
                status_code=503, detail="Entity resolution service not available"
            )

        conn = await chat_service.entity_resolution_service._get_connection()
        cursor = conn.cursor()

        # Get entity details
        cursor.execute(
            """
            SELECT
                entity_id,
                entity_type,
                canonical_name,
                normalized_name,
                primary_ids,
                aliases,
                confidence,
                metadata,
                source_system_count,
                created_at,
                updated_at,
                last_seen_at
            FROM SOPHIA_ENTITY_RESOLUTION.ENTITY_CANONICAL
            WHERE entity_id = ?
        """,
            [entity_id],
        )

        result = cursor.fetchone()
        cursor.close()

        if not result:
            raise HTTPException(status_code=404, detail="Entity not found")

        # Convert to dictionary
        columns = [
            "entity_id",
            "entity_type",
            "canonical_name",
            "normalized_name",
            "primary_ids",
            "aliases",
            "confidence",
            "metadata",
            "source_system_count",
            "created_at",
            "updated_at",
            "last_seen_at",
        ]

        entity_data = dict(zip(columns, result, strict=False))

        return entity_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get entity details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def entity_resolution_health():
    """
    Check the health of the entity resolution system.

    Returns status information about the entity resolution service,
    including total entities and system capabilities.
    """
    try:
        if not chat_service.entity_resolution_service:
            return {
                "status": "unavailable",
                "message": "Entity resolution service not initialized",
            }

        health_check = await chat_service.entity_resolution_service.health_check()

        return {
            "status": "operational",
            "entity_resolution": health_check,
            "capabilities": {
                "fuzzy_matching": True,
                "entity_learning": True,
                "clarification_questions": True,
                "multi_source_resolution": True,
            },
        }

    except Exception as e:
        logger.error(f"Entity resolution health check failed: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/bulk-populate")
async def bulk_populate_entities(background_tasks: BackgroundTasks):
    """
    Bulk populate entities from existing data sources.

    This endpoint triggers a background job to scan existing data sources
    (HubSpot, Slack, Gong, etc.) and populate the entity registry.
    """
    try:
        if not chat_service.entity_resolution_service:
            raise HTTPException(
                status_code=503, detail="Entity resolution service not available"
            )

        # Add background task to populate entities
        background_tasks.add_task(_populate_entities_background)

        return {
            "status": "started",
            "message": "Entity population job started in background",
            "estimated_completion": "2-5 minutes depending on data volume",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start entity population: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================================================================
# BACKGROUND TASKS
# ========================================================================================


async def _populate_entities_background():
    """Background task to populate entities from data sources"""
    try:
        if chat_service.entity_resolution_service:
            conn = await chat_service.entity_resolution_service._get_connection()
            cursor = conn.cursor()

            # Call the population procedure
            cursor.execute(
                """
                CALL SOPHIA_ENTITY_RESOLUTION.POPULATE_ENTITIES_FROM_SOURCES()
            """
            )

            result = cursor.fetchone()
            conn.commit()
            cursor.close()

            logger.info(
                f"Entity population completed: {result[0] if result else 'Success'}"
            )

    except Exception as e:
        logger.error(f"Background entity population failed: {e}")


# ========================================================================================
# UTILITY FUNCTIONS
# ========================================================================================


def generate_clarification_options(
    entity_matches: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate user-friendly clarification options"""
    options = []

    for entity_text, match_info in entity_matches.items():
        if match_info.get("needs_clarification") and "candidates" in match_info:
            for candidate in match_info["candidates"][:3]:  # Top 3 candidates
                options.append(
                    {
                        "entity_id": candidate["entity_id"],
                        "display_name": candidate["canonical_name"],
                        "similarity_score": candidate["similarity_score"],
                        "context": f"Matched '{entity_text}' with {candidate['match_reason']}",
                    }
                )

    return options
