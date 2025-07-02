import logging
from fastapi import APIRouter, Depends, HTTPException, Body

# Assuming a dependency injection system for services
from backend.services.ai_training.interactive_training_service import InteractiveTrainingService
# Assuming an auth system to get user and check roles
from backend.security.auth import get_current_active_user, User, has_role

logger = logging.getLogger(__name__)
router = APIRouter()

# --- User-Facing Training API ---

@router.post("/training/submit", status_code=201)
async def submit_training_data(
    topic: str = Body(..., embed=True),
    content: str = Body(..., embed=True),
    training_service: InteractiveTrainingService = Depends(),
    current_user: User = Depends(get_current_active_user)
):
    """
    Endpoint for a user to submit a piece of authoritative knowledge.
    The service will handle fetching the user's impact score.
    """
    logger.info(f"Received training submission for topic '{topic}' from user '{current_user.id}'")
    result = await training_service.submit_knowledge(
        user_id=current_user.id,
        topic=topic,
        content=content
    )
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result

# --- CEO / Admin Management API ---

@router.put("/admin/users/{user_id}/training-impact")
async def set_user_training_impact(
    user_id: str,
    impact_score: float = Body(..., ge=0.0, le=1.0, embed=True),
    admin_user: User = Depends(has_role("CEO"))
):
    """
    CEO-only endpoint to set the training impact score for a user.
    """
    logger.info(f"Admin '{admin_user.id}' setting training impact for user '{user_id}' to {impact_score}")
    # In a full implementation, this would call a service to update the user's
    # training_impact_score in the database.
    # For now, we'll just return a success message.
    # e.g., result = await user_management_service.set_impact_score(user_id, impact_score)
    
    return {
        "status": "success",
        "user_id": user_id,
        "new_impact_score": impact_score
    }

@router.get("/admin/users/training-impact")
async def list_user_training_impacts(admin_user: User = Depends(has_role("CEO"))):
    """
    CEO-only endpoint to list the training impact scores for all users.
    """
    logger.info(f"Admin '{admin_user.id}' requesting list of user impact scores.")
    # In a full implementation, this would call a service to fetch all users
    # and their scores from the database.
    # e.g., users = await user_management_service.get_all_users_with_impact()
    
    # Returning mock data for demonstration
    mock_users = [
        {"user_id": "ceo_001", "username": "Lynn", "training_impact_score": 1.0},
        {"user_id": "eng_001", "username": "SophiaDev", "training_impact_score": 0.8},
        {"user_id": "csr_001", "username": "SupportRep", "training_impact_score": 0.1},
    ]
    
    return {"users": mock_users}

@router.get("/admin/training/feed")
async def get_training_feed(
    training_service: InteractiveTrainingService = Depends(),
    admin_user: User = Depends(has_role("CEO"))
):
    """CEO-only endpoint to get a live feed of training submissions."""
    return await training_service.get_training_feed()

@router.get("/admin/training/gaps")
async def get_knowledge_gaps(
    training_service: InteractiveTrainingService = Depends(),
    admin_user: User = Depends(has_role("CEO"))
):
    """CEO-only endpoint to identify knowledge gaps."""
    return await training_service.get_knowledge_gaps()

@router.post("/admin/knowledge/{knowledge_id}/manage")
async def manage_knowledge_entry(
    knowledge_id: str,
    action: str = Body(..., embed=True, description="Action to perform: 'update' or 'delete'"),
    content: str = Body(None, embed=True, description="New content for the entry if action is 'update'"),
    training_service: InteractiveTrainingService = Depends(),
    admin_user: User = Depends(has_role("CEO"))
):
    """CEO-only endpoint to update or delete an authoritative knowledge entry."""
    result = await training_service.manage_knowledge(knowledge_id, action, content)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/admin/training/feed")
async def get_training_feed(
    training_service: InteractiveTrainingService = Depends(),
    admin_user: User = Depends(has_role("CEO"))
):
    """CEO-only endpoint to get a live feed of training submissions."""
    return await training_service.get_training_feed()

@router.get("/admin/training/gaps")
async def get_knowledge_gaps(
    training_service: InteractiveTrainingService = Depends(),
    admin_user: User = Depends(has_role("CEO"))
):
    """CEO-only endpoint to identify knowledge gaps."""
    return await training_service.get_knowledge_gaps()

@router.post("/admin/knowledge/{knowledge_id}/manage")
async def manage_knowledge_entry(
    knowledge_id: str,
    action: str = Body(..., embed=True, description="Action to perform: 'update' or 'delete'"),
    content: str = Body(None, embed=True, description="New content for the entry if action is 'update'"),
    training_service: InteractiveTrainingService = Depends(),
    admin_user: User = Depends(has_role("CEO"))
):
    """CEO-only endpoint to update or delete an authoritative knowledge entry."""
    result = await training_service.manage_knowledge(knowledge_id, action, content)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result
