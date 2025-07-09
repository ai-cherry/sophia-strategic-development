"""
Temporal Learning API Routes for Sophia AI
Integrates with existing unified chat and knowledge base infrastructure
"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.services.temporal_qa_learning_service import (
    get_temporal_qa_learning_service,
)

# Try to import auth, fallback to mock if not available
try:
    from backend.core.auth import get_current_user
except ImportError:
    # Fallback mock auth for development
    def get_current_user():
        return {"id": "default_user", "username": "system", "role": "admin"}


router = APIRouter(prefix="/api/v1/temporal-learning", tags=["temporal-learning"])


# Pydantic models for request/response
class TemporalLearningRequest(BaseModel):
    message: str
    context: Optional[dict[str, Any]] = None
    user_id: str
    session_id: Optional[str] = None


class TemporalLearningResponse(BaseModel):
    learning_applied: bool
    interaction_id: Optional[str] = None
    response: Optional[str] = None
    learning_type: Optional[str] = None
    confidence: Optional[float] = None
    suggestions: list[str] = []
    follow_up_questions: list[str] = []
    reason: Optional[str] = None
    error: Optional[str] = None


class CorrectionRequest(BaseModel):
    interaction_id: str
    correction: str
    context: Optional[dict[str, Any]] = None


class CorrectionResponse(BaseModel):
    success: bool
    interaction_id: Optional[str] = None
    learning_applied: bool = False
    updated_knowledge: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class ValidationRequest(BaseModel):
    interaction_id: str
    is_correct: bool
    feedback: Optional[str] = None


# Routes
@router.post("/chat/process", response_model=TemporalLearningResponse)
async def process_temporal_learning_message(
    request: TemporalLearningRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Process a message for temporal learning opportunities
    Integrates with existing chat infrastructure
    """
    try:
        service = get_temporal_qa_learning_service()

        # Add user context to the request
        enhanced_context = request.context or {}
        enhanced_context.update(
            {
                "user_id": request.user_id,
                "session_id": request.session_id,
                "authenticated_user": current_user,
            }
        )

        result = await service.process_qa_interaction(
            user_message=request.message, context=enhanced_context
        )

        return TemporalLearningResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/correct", response_model=CorrectionResponse)
async def process_correction(
    request: CorrectionRequest, current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Process a user correction to improve temporal learning
    """
    try:
        service = get_temporal_qa_learning_service()

        # Add user context to the correction
        enhanced_context = request.context or {}
        enhanced_context.update(
            {
                "corrected_by": current_user,
                "correction_timestamp": None,  # Will be set by service
            }
        )

        result = await service.process_user_correction(
            interaction_id=request.interaction_id,
            correction=request.correction,
            context=enhanced_context,
        )

        return CorrectionResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interactions/{interaction_id}/validate")
async def validate_interaction(
    interaction_id: str,
    request: ValidationRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Validate a temporal learning interaction
    """
    try:
        service = get_temporal_qa_learning_service()

        # Find and update the interaction
        interaction = next(
            (i for i in service.learning_interactions if i.id == interaction_id), None
        )

        if not interaction:
            raise HTTPException(status_code=404, detail="Interaction not found")

        # Update validation status
        interaction.validated = request.is_correct
        if request.feedback:
            interaction.context["validation_feedback"] = request.feedback
            interaction.context["validated_by"] = current_user

        return {
            "success": True,
            "interaction_id": interaction_id,
            "validated": request.is_correct,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/data")
async def get_dashboard_data(current_user: dict[str, Any] = Depends(get_current_user)):
    """
    Get comprehensive learning data for the dashboard
    """
    try:
        service = get_temporal_qa_learning_service()
        data = await service.get_learning_dashboard_data()
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/suggestions")
async def get_learning_suggestions(
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Get suggestions for improving temporal learning
    """
    try:
        service = get_temporal_qa_learning_service()
        suggestions = await service.get_learning_suggestions()
        return suggestions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/summary")
async def get_analytics_summary(
    current_user: dict[str, Any] = Depends(get_current_user)
):
    """
    Get analytics summary for temporal learning
    """
    try:
        service = get_temporal_qa_learning_service()
        data = await service.get_learning_dashboard_data()

        # Return focused analytics summary
        return {
            "total_interactions": data["summary"]["total_interactions"],
            "learning_accuracy": data["summary"]["learning_accuracy"],
            "knowledge_concepts": data["summary"]["knowledge_concepts"],
            "learning_type_distribution": data["distributions"]["learning_types"],
            "confidence_distribution": data["distributions"]["confidence_levels"],
            "system_status": data["system_status"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base")
async def get_knowledge_base(current_user: dict[str, Any] = Depends(get_current_user)):
    """
    Get the temporal knowledge base
    """
    try:
        service = get_temporal_qa_learning_service()
        data = await service.get_learning_dashboard_data()
        return data["knowledge_base"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/interactions")
async def get_interactions(
    limit: int = 20,
    learning_type: Optional[str] = None,
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """
    Get temporal learning interactions with optional filtering
    """
    try:
        service = get_temporal_qa_learning_service()
        interactions = service.learning_interactions

        # Filter by learning type if specified
        if learning_type:
            interactions = [
                i for i in interactions if i.learning_type.value == learning_type
            ]

        # Sort by timestamp (newest first) and limit
        interactions = sorted(interactions, key=lambda x: x.timestamp, reverse=True)[
            :limit
        ]

        # Convert to dict format
        return [
            {
                "id": i.id,
                "user_question": i.user_question,
                "system_response": i.system_response,
                "user_correction": i.user_correction,
                "learning_type": i.learning_type.value,
                "confidence": i.confidence.value,
                "timestamp": i.timestamp.isoformat(),
                "validated": i.validated,
                "applied": i.applied,
                "context": i.context,
            }
            for i in interactions
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check for temporal learning service
    """
    try:
        service = get_temporal_qa_learning_service()
        return {
            "status": "healthy",
            "service": "temporal_qa_learning",
            "system_date": service.system_date,
            "total_interactions": len(service.learning_interactions),
            "total_knowledge": len(service.temporal_knowledge),
        }

    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
