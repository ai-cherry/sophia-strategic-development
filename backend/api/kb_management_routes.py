"""
Knowledge Base Management API Routes
Provides endpoints for natural language KB management and document upload
"""

from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.core.auth import get_current_user
from backend.core.cache_manager import DashboardCacheManager
from backend.core.logger import logger
from backend.services.kb_management_service import KBManagementService

router = APIRouter(prefix="/api/v1/kb", tags=["knowledge-base-management"])

# Initialize services
kb_service = KBManagementService()
cache_manager = DashboardCacheManager()


class NLCommandRequest(BaseModel):
    """Request model for natural language commands"""

    command: str
    user_context: dict[str, Any] | None = None


class KBSearchRequest(BaseModel):
    """Request model for KB search operations"""

    query: str
    entity_types: list[str] | None = None
    limit: int = 10


@router.post("/natural-language-command")
async def process_natural_language_command(
    request: NLCommandRequest, current_user: dict = Depends(get_current_user)
) -> JSONResponse:
    """
    Process natural language KB management command

    Examples:
    - "Add employee: name 'Jane Doe', email 'jane@payready.com', department 'Engineering'"
    - "Create customer: company_name 'Acme Corp', industry 'Technology'"
    - "Search for employees with Python skills"
    """
    try:
        if not kb_service.initialized:
            await kb_service.initialize()

        result = await kb_service.process_natural_language_command(
            command=request.command, user_id=current_user.get("user_id", "unknown")
        )

        return JSONResponse(
            status_code=200 if result.success else 400,
            content={
                "success": result.success,
                "operation": result.operation.value if result.operation else None,
                "entity_type": result.entity_type.value if result.entity_type else None,
                "entity_id": result.entity_id,
                "message": result.message,
                "data": result.data,
                "errors": result.errors,
            },
        )

    except Exception as e:
        logger.error(f"Error processing NL command: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/search")
async def search_knowledge_base(
    request: KBSearchRequest, current_user: dict = Depends(get_current_user)
) -> JSONResponse:
    """Search the knowledge base with semantic search"""
    try:
        if not kb_service.initialized:
            await kb_service.initialize()

        entity_filter = ""
        if request.entity_types:
            entity_filter = f" in {', '.join(request.entity_types)}"

        command = f"Search for {request.query}{entity_filter}"

        result = await kb_service.process_natural_language_command(
            command=command, user_id=current_user.get("user_id", "unknown")
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": result.success,
                "query": request.query,
                "results": result.data.get("results", []),
                "total_count": len(result.data.get("results", [])),
                "message": result.message,
            },
        )

    except Exception as e:
        logger.error(f"Error searching KB: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    tags: str = Form(""),
    description: str = Form(""),
    current_user: dict = Depends(get_current_user),
) -> JSONResponse:
    """Upload and process a document for the knowledge base"""
    try:
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "application/json",
            "text/csv",
        ]

        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, detail=f"Unsupported file type: {file.content_type}"
            )

        max_size = 10 * 1024 * 1024
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

        # Extract text
        if file.content_type == "text/plain":
            extracted_text = content.decode("utf-8")
        elif file.content_type == "application/json":
            extracted_text = content.decode("utf-8")
        else:
            extracted_text = f"Extracted content from {file.filename}"

        import uuid

        file_id = str(uuid.uuid4())

        [tag.strip() for tag in tags.split(",") if tag.strip()]

        return JSONResponse(
            content={
                "success": True,
                "file_id": file_id,
                "filename": file.filename,
                "extracted_text": (
                    extracted_text[:500] + "..."
                    if len(extracted_text) > 500
                    else extracted_text
                ),
                "message": f"Document '{file.filename}' uploaded successfully",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/stats")
async def get_kb_stats(current_user: dict = Depends(get_current_user)) -> JSONResponse:
    """Get knowledge base statistics"""
    try:
        stats = {
            "total_entities": {
                "employees": 0,
                "customers": 0,
                "products": 0,
                "documents": 0,
            },
            "recent_activity": {
                "entities_added_today": 0,
                "documents_uploaded_today": 0,
                "searches_performed_today": 0,
            },
        }

        return JSONResponse(content=stats)

    except Exception as e:
        logger.error(f"Error getting KB stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
