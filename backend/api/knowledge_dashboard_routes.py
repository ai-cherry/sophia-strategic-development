#!/usr/bin/env python3
"""
Knowledge Dashboard API Routes for Sophia AI
Comprehensive API endpoints for knowledge management and chat integration
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os

# Import our services
from backend.services.knowledge_service import (
    knowledge_service,
    KnowledgeStats,
    UploadResponse,
    SearchFilters,
)
from backend.services.enhanced_unified_chat_service import snowflake_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authentication
security = HTTPBearer()
CEO_ACCESS_TOKEN = os.getenv("CEO_ACCESS_TOKEN", "sophia_ceo_access_2024")
ADMIN_USER_ID = "ceo_user"


async def authenticate_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Authenticate user with simple token"""
    if credentials.credentials == CEO_ACCESS_TOKEN:
        return ADMIN_USER_ID
    raise HTTPException(status_code=401, detail="Invalid authentication token")


# Request/Response Models
class CreateCategoryRequest(BaseModel):
    category_id: str
    category_name: str
    description: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    category_filter: Optional[str] = None


class ChatWithKnowledgeRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_knowledge: bool = True
    category_filter: Optional[str] = None


class UpdateEntryRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[str] = None


# Initialize router
router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge Management"])


@router.on_event("startup")
async def startup_knowledge_service():
    """Initialize knowledge service on startup"""
    # Knowledge service doesn't require explicit connection
    logger.info("🚀 Knowledge Dashboard API routes initialized")


@router.on_event("shutdown")
async def shutdown_knowledge_service():
    """Cleanup on shutdown"""
    # Knowledge service doesn't require explicit disconnection
    logger.info("Knowledge Dashboard API routes shut down")


# File Upload and Processing Endpoints


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    category_id: Optional[str] = Form(None),
    description: Optional[str] = Form(""),
    user_id: str = Depends(authenticate_user),
):
    """Upload and process a file for the knowledge base"""
    try:
        # Read file content
        file_content = await file.read()

        # Create content combining description and file content
        content = description if description else f"Uploaded file: {file.filename}"

        # Upload to knowledge service
        result = await knowledge_service.upload_knowledge_entry(
            title=title,
            content=content,
            category_id=category_id,
            file_data=file_content,
            filename=file.filename,
            file_type=file.content_type,
        )

        logger.info(f"File uploaded successfully: {file.filename} -> {result.entry_id}")
        return result

    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/entries", response_model=UploadResponse)
async def create_knowledge_entry(
    title: str,
    content: str,
    category_id: Optional[str] = None,
    user_id: str = Depends(authenticate_user),
):
    """Create a knowledge entry from text"""
    try:
        result = await knowledge_service.upload_knowledge_entry(
            title=title, content=content, category_id=category_id
        )

        logger.info(f"Knowledge entry created: {result.entry_id}")
        return result

    except Exception as e:
        logger.error(f"Entry creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Creation failed: {str(e)}")


# Search and Retrieval Endpoints


@router.post("/search")
async def search_knowledge(
    request: SearchRequest, user_id: str = Depends(authenticate_user)
) -> Dict[str, Any]:
    """Search knowledge base"""
    try:
        filters = (
            SearchFilters(category_id=request.category_filter)
            if request.category_filter
            else None
        )

        results = await knowledge_service.search_knowledge(
            query=request.query, limit=request.limit, filters=filters
        )

        return {
            "query": request.query,
            "results": [
                {
                    "entry_id": entry.entry_id,
                    "title": entry.title,
                    "content": entry.content[:500] + "..."
                    if len(entry.content) > 500
                    else entry.content,
                    "category_id": entry.category_id,
                    "category_name": entry.category_name,
                    "file_type": entry.file_type,
                    "created_at": entry.created_at.isoformat(),
                    "metadata": entry.metadata,
                }
                for entry in results
            ],
            "total_results": len(results),
            "search_timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/entries/{entry_id}")
async def get_knowledge_entry(
    entry_id: str, user_id: str = Depends(authenticate_user)
) -> Dict[str, Any]:
    """Get specific knowledge entry"""
    try:
        # Search for the specific entry
        results = await knowledge_service.search_knowledge(query="", limit=1000)

        for entry in results:
            if entry.entry_id == entry_id:
                return {
                    "entry_id": entry.entry_id,
                    "title": entry.title,
                    "content": entry.content,
                    "category_id": entry.category_id,
                    "category_name": entry.category_name,
                    "file_type": entry.file_type,
                    "file_size": entry.file_size,
                    "status": entry.status,
                    "metadata": entry.metadata,
                    "created_at": entry.created_at.isoformat(),
                    "updated_at": entry.updated_at.isoformat(),
                }

        raise HTTPException(status_code=404, detail="Entry not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get entry {entry_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get entry: {str(e)}")


@router.get("/entries")
async def list_knowledge_entries(
    category_id: Optional[str] = None,
    limit: int = 50,
    user_id: str = Depends(authenticate_user),
) -> List[Dict[str, Any]]:
    """List knowledge entries with optional filtering"""
    try:
        filters = SearchFilters(category_id=category_id) if category_id else None

        results = await knowledge_service.search_knowledge(
            query="",  # Empty query to get all
            limit=limit,
            filters=filters,
        )

        return [
            {
                "entry_id": entry.entry_id,
                "title": entry.title,
                "content": entry.content[:200] + "..."
                if len(entry.content) > 200
                else entry.content,
                "category_id": entry.category_id,
                "category_name": entry.category_name,
                "file_type": entry.file_type,
                "file_size": entry.file_size,
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat(),
            }
            for entry in results
        ]

    except Exception as e:
        logger.error(f"Failed to list entries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list entries: {str(e)}")


# Chat Integration Endpoints


@router.post("/chat")
async def chat_with_knowledge(
    request: ChatWithKnowledgeRequest, user_id: str = Depends(authenticate_user)
) -> Dict[str, Any]:
    """Chat with AI using knowledge base context"""
    try:
        session_id = request.session_id

        # Create session if not provided
        if not session_id:
            session_id = await snowflake_service.create_session(
                user_id=user_id,
                title=f"Knowledge Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            )

        # Save user message
        user_message_id = await snowflake_service.save_message(
            session_id, user_id, request.message, "user"
        )

        # Search knowledge base if requested
        knowledge_results = []
        if request.use_knowledge:
            filters = (
                SearchFilters(category_id=request.category_filter)
                if request.category_filter
                else None
            )
            knowledge_results = await knowledge_service.search_knowledge(
                query=request.message, limit=5, filters=filters
            )

        # Generate AI response with knowledge context
        ai_response = await snowflake_service.generate_ai_response(
            request.message,
            [
                {
                    "TITLE": entry.title,
                    "CONTENT": entry.content,
                    "CATEGORY_NAME": entry.category_name,
                }
                for entry in knowledge_results
            ],
        )

        # Save AI response
        ai_message_id = await snowflake_service.save_message(
            session_id, "system", ai_response, "assistant"
        )

        return {
            "session_id": session_id,
            "user_message_id": user_message_id,
            "ai_message_id": ai_message_id,
            "response": ai_response,
            "knowledge_sources": [
                {
                    "entry_id": entry.entry_id,
                    "title": entry.title,
                    "category": entry.category_name,
                    "relevance": "high",  # Placeholder
                }
                for entry in knowledge_results[:3]
            ],
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Chat with knowledge failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


# Management Endpoints


@router.get("/stats", response_model=KnowledgeStats)
async def get_knowledge_stats(user_id: str = Depends(authenticate_user)):
    """Get knowledge base statistics"""
    try:
        stats = await knowledge_service.get_knowledge_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/categories")
async def get_categories(
    user_id: str = Depends(authenticate_user),
) -> List[Dict[str, Any]]:
    """Get all knowledge categories"""
    try:
        query = "SELECT CATEGORY_ID, CATEGORY_NAME, DESCRIPTION, CREATED_AT FROM KNOWLEDGE_CATEGORIES ORDER BY CATEGORY_NAME"
        results = await knowledge_service.execute_query(query)

        return [
            {
                "category_id": row["CATEGORY_ID"],
                "category_name": row["CATEGORY_NAME"],
                "description": row["DESCRIPTION"],
                "created_at": row["CREATED_AT"].isoformat()
                if row["CREATED_AT"]
                else None,
            }
            for row in results
        ]

    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get categories: {str(e)}"
        )


@router.post("/categories")
async def create_category(
    request: CreateCategoryRequest, user_id: str = Depends(authenticate_user)
) -> Dict[str, str]:
    """Create a new knowledge category"""
    try:
        await knowledge_service.ensure_category_exists(request.category_id)

        # Update category details if different from auto-created
        if request.category_name:
            update_query = """
            UPDATE KNOWLEDGE_CATEGORIES 
            SET CATEGORY_NAME = %s, DESCRIPTION = %s 
            WHERE CATEGORY_ID = %s
            """
            await knowledge_service.execute_query(
                update_query,
                (request.category_name, request.description, request.category_id),
            )

        return {
            "category_id": request.category_id,
            "status": "created",
            "message": "Category created successfully",
        }

    except Exception as e:
        logger.error(f"Failed to create category: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create category: {str(e)}"
        )


@router.put("/entries/{entry_id}")
async def update_knowledge_entry(
    entry_id: str,
    request: UpdateEntryRequest,
    user_id: str = Depends(authenticate_user),
) -> Dict[str, str]:
    """Update knowledge entry"""
    try:
        updates = []
        params = []

        if request.title:
            updates.append("TITLE = %s")
            params.append(request.title)

        if request.content:
            updates.append("CONTENT = %s")
            params.append(request.content)

        if request.category_id:
            await knowledge_service.ensure_category_exists(request.category_id)
            updates.append("CATEGORY_ID = %s")
            params.append(request.category_id)

        if updates:
            updates.append("UPDATED_AT = %s")
            params.append(datetime.now())
            params.append(entry_id)

            update_query = f"""
            UPDATE KNOWLEDGE_BASE_ENTRIES 
            SET {", ".join(updates)}
            WHERE ENTRY_ID = %s
            """

            await knowledge_service.execute_query(update_query, tuple(params))

        return {
            "entry_id": entry_id,
            "status": "updated",
            "message": "Entry updated successfully",
        }

    except Exception as e:
        logger.error(f"Failed to update entry {entry_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update entry: {str(e)}")


@router.delete("/entries/{entry_id}")
async def delete_knowledge_entry(
    entry_id: str, user_id: str = Depends(authenticate_user)
) -> Dict[str, str]:
    """Delete knowledge entry"""
    try:
        await knowledge_service.delete_knowledge_entry(entry_id)

        return {
            "entry_id": entry_id,
            "status": "deleted",
            "message": "Entry deleted successfully",
        }

    except Exception as e:
        logger.error(f"Failed to delete entry {entry_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete entry: {str(e)}")


# Health and System Endpoints


@router.get("/health")
async def knowledge_health_check():
    """Health check for knowledge service"""
    try:
        # Test knowledge service connection
        await knowledge_service.execute_query("SELECT 1 as test")

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "knowledge_service": "connected",
                "snowflake": "operational",
                "file_processing": "ready",
            },
            "version": "1.0.0",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# Export router
knowledge_router = router
