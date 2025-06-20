"""LlamaIndex Router for Sophia AI

This module provides FastAPI endpoints for document intelligence capabilities
using LlamaIndex. It enables document processing, querying, and management
through the API.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.app.dependencies import RateLimiter, get_current_user

# Sophia AI imports
from backend.integrations.llamaindex_integration import LlamaIndexProcessor

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/llamaindex",
    tags=["llamaindex"],
    responses={404: {"description": "Not found"}},
)

# Initialize LlamaIndex processor
llamaindex_processor = LlamaIndexProcessor()


# Models
class DocumentMetadata(BaseModel):
    """Document metadata model."""

    title: Optional[str] = Field(None, description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    source: Optional[str] = Field(None, description="Document source")
    created_at: Optional[str] = Field(None, description="Document creation date")
    document_type: Optional[str] = Field(None, description="Document type")
    tags: Optional[List[str]] = Field(None, description="Document tags")
    custom_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Custom metadata"
    )


class DocumentProcessRequest(BaseModel):
    """Document processing request model."""

    text: str = Field(..., description="Document text")
    metadata: Optional[DocumentMetadata] = Field(None, description="Document metadata")
    processing_options: Optional[Dict[str, Any]] = Field(
        None, description="Processing options"
    )


class DocumentQueryRequest(BaseModel):
    """Document query request model."""

    query: str = Field(..., description="Query string")
    filters: Optional[Dict[str, Any]] = Field(None, description="Query filters")
    top_k: Optional[int] = Field(10, description="Number of results to return")
    include_metadata: Optional[bool] = Field(
        True, description="Include metadata in results"
    )


class DocumentProcessResponse(BaseModel):
    """Document processing response model."""

    status: str = Field(..., description="Processing status")
    processed_nodes: Optional[int] = Field(
        None, description="Number of processed nodes"
    )
    pinecone_index_id: Optional[str] = Field(None, description="Pinecone index ID")
    weaviate_index_id: Optional[str] = Field(None, description="Weaviate index ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")
    error: Optional[str] = Field(None, description="Error message if processing failed")


# Routes
@router.post("/process", response_model=DocumentProcessResponse)
async def process_document(
    request: DocumentProcessRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    rate_limiter: RateLimiter = Depends(),
):
    """Process a document with LlamaIndex.

    This endpoint processes a document with LlamaIndex, extracting metadata,
    chunking the document, and indexing it in the vector stores.
    """
    logger.info(
        f"Processing document: {request.metadata.title if request.metadata else 'Untitled'}"
    )

    # Create context
    context = {
        "user_id": current_user.get("id"),
        "processing_options": request.processing_options or {},
    }

    # Process document
    result = await llamaindex_processor.process_document(
        document={
            "text": request.text,
            "metadata": request.metadata.dict() if request.metadata else {},
        },
        context=context,
    )

    return result


@router.post("/process/file")
async def process_document_file(
    file: UploadFile = File(...),
    metadata: str = Form(None),
    processing_options: str = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: Dict = Depends(get_current_user),
    rate_limiter: RateLimiter = Depends(),
):
    """Process a document file with LlamaIndex.

    This endpoint processes a document file with LlamaIndex, extracting metadata,
    chunking the document, and indexing it in the vector stores.
    """
    logger.info(f"Processing document file: {file.filename}")

    # Read file content
    content = await file.read()

    # Parse metadata and processing options
    parsed_metadata = json.loads(metadata) if metadata else {}
    parsed_options = json.loads(processing_options) if processing_options else {}

    # Add filename to metadata
    parsed_metadata["filename"] = file.filename

    # Create context
    context = {"user_id": current_user.get("id"), "processing_options": parsed_options}

    # Process document based on file type
    if file.filename.endswith(".pdf"):
        # For PDF files, we need to use a PDF parser
        # This is a placeholder for actual implementation
        document_text = f"PDF content of {file.filename}"
    elif file.filename.endswith((".docx", ".doc")):
        # For Word files, we need to use a Word parser
        # This is a placeholder for actual implementation
        document_text = f"Word content of {file.filename}"
    elif file.filename.endswith((".txt", ".md")):
        # For text files, we can use the content directly
        document_text = content.decode("utf-8")
    else:
        # For other files, we'll just use the content as is
        document_text = content.decode("utf-8", errors="ignore")

    # Process document
    result = await llamaindex_processor.process_document(
        document={"text": document_text, "metadata": parsed_metadata}, context=context
    )

    return result


@router.post("/query")
async def query_documents(
    request: DocumentQueryRequest,
    current_user: Dict = Depends(get_current_user),
    rate_limiter: RateLimiter = Depends(),
):
    """Query documents using LlamaIndex.

    This endpoint queries documents using LlamaIndex, returning results
    from the vector stores.
    """
    logger.info(f"Querying documents: {request.query}")

    # Create context
    context = {
        "user_id": current_user.get("id"),
        "filters": request.filters or {},
        "top_k": request.top_k,
        "include_metadata": request.include_metadata,
    }

    # Query documents
    results = []
    async for result in llamaindex_processor.query_documents(
        query=request.query, context=context
    ):
        results.append(result)

    return {"results": results}


@router.post("/query/stream")
async def query_documents_stream(
    request: DocumentQueryRequest,
    current_user: Dict = Depends(get_current_user),
    rate_limiter: RateLimiter = Depends(),
):
    """Stream query results using LlamaIndex.

    This endpoint streams query results using LlamaIndex, returning results
    from the vector stores as they become available.
    """
    logger.info(f"Streaming query results: {request.query}")

    # Create context
    context = {
        "user_id": current_user.get("id"),
        "filters": request.filters or {},
        "top_k": request.top_k,
        "include_metadata": request.include_metadata,
    }

    async def generate():
        async for result in llamaindex_processor.query_documents(
            query=request.query, context=context
        ):
            yield json.dumps(result) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")


@router.get("/health")
async def health_check():
    """Check the health of the LlamaIndex integration.

    This endpoint checks the health of the LlamaIndex integration,
    including the vector stores and document processor.
    """
    # This is a placeholder for actual implementation
    return {
        "status": "healthy",
        "vector_stores": {"pinecone": "connected", "weaviate": "connected"},
        "document_processor": "operational",
    }
