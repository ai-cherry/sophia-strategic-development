"""
Knowledge Dashboard API Routes
Provides endpoints for knowledge base management, document ingestion, and data source synchronization
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import json

from backend.core.database import get_session
from backend.core.auth import get_current_user
from backend.services.knowledge_service import KnowledgeService
from backend.services.ingestion_service import IngestionService
from backend.services.data_source_service import DataSourceService
from backend.services.sync_service import SyncService
from backend.models.knowledge import (
    KnowledgeStats,
    IngestionJob,
    DataSource,
    Document,
    SyncStatus,
)
from backend.core.cache_manager import DashboardCacheManager
from backend.core.logger import logger

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])

# Initialize services
knowledge_service = KnowledgeService()
ingestion_service = IngestionService()
data_source_service = DataSourceService()
sync_service = SyncService()
cache_manager = DashboardCacheManager()


@router.get("/stats", response_model=KnowledgeStats)
async def get_knowledge_stats(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> KnowledgeStats:
    """
    Get knowledge base statistics including document counts, storage usage, and activity metrics

    Returns:
        Comprehensive knowledge base statistics
    """
    try:
        # Use cache for stats
        cache_key = f"knowledge_stats:{user_id}"

        async def fetch_stats():
            return await knowledge_service.get_stats(session, user_id)

        stats = await cache_manager.get_or_set(
            cache_key, fetch_stats, ttl=300  # 5 minutes cache
        )

        return stats
    except Exception as e:
        logger.error(f"Error fetching knowledge stats: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch knowledge statistics"
        )


@router.get("/ingestion-jobs", response_model=List[IngestionJob])
async def get_ingestion_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    limit: int = Query(20, description="Number of jobs to return"),
    offset: int = Query(0, description="Number of jobs to skip"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[IngestionJob]:
    """
    Get recent document ingestion job status

    Returns:
        List of recent ingestion jobs with their status and metadata
    """
    try:
        jobs = await ingestion_service.get_recent_jobs(
            session, user_id=user_id, status=status, limit=limit, offset=offset
        )
        return jobs
    except Exception as e:
        logger.error(f"Error fetching ingestion jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch ingestion jobs")


@router.get("/data-sources", response_model=List[DataSource])
async def get_data_sources(
    active_only: bool = Query(True, description="Return only active data sources"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[DataSource]:
    """
    Get configured data sources for knowledge base

    Returns:
        List of configured data sources with their sync status
    """
    try:
        sources = await data_source_service.get_all_sources(
            session, user_id=user_id, active_only=active_only
        )
        return sources
    except Exception as e:
        logger.error(f"Error fetching data sources: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch data sources")


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = Query(
        None, description="Additional metadata as JSON string"
    ),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Upload a document to the knowledge base

    Returns:
        Document ID and ingestion job details
    """
    try:
        # Validate file type
        allowed_types = {
            "application/pdf",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
            "text/markdown",
            "text/csv",
        }

        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, detail=f"File type {file.content_type} not supported"
            )

        # Parse metadata if provided
        doc_metadata = {}
        if metadata:
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")

        # Create ingestion job
        job = await ingestion_service.create_ingestion_job(
            session, user_id=user_id, file=file, metadata=doc_metadata
        )

        # Process document asynchronously
        await ingestion_service.process_document_async(job.id)

        # Invalidate cache
        await cache_manager.invalidate_pattern(f"knowledge_stats:{user_id}")

        return {
            "job_id": job.id,
            "status": job.status,
            "document_name": file.filename,
            "estimated_completion": job.estimated_completion,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload document")


@router.post("/sync/{source_id}")
async def sync_data_source(
    source_id: str,
    full_sync: bool = Query(
        False, description="Perform full sync instead of incremental"
    ),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Trigger synchronization for a specific data source

    Returns:
        Sync job details and status
    """
    try:
        # Verify data source exists and user has access
        source = await data_source_service.get_source(session, source_id, user_id)
        if not source:
            raise HTTPException(status_code=404, detail="Data source not found")

        # Check if sync is already in progress
        if await sync_service.is_sync_in_progress(session, source_id):
            raise HTTPException(
                status_code=409, detail="Sync already in progress for this source"
            )

        # Create sync job
        sync_job = await sync_service.create_sync_job(
            session, source_id=source_id, user_id=user_id, full_sync=full_sync
        )

        # Trigger async sync
        await sync_service.trigger_sync_async(sync_job.id)

        # Invalidate cache
        await cache_manager.invalidate_pattern(f"knowledge_stats:{user_id}")

        return {
            "sync_job_id": sync_job.id,
            "source_name": source.name,
            "sync_type": "full" if full_sync else "incremental",
            "status": sync_job.status,
            "started_at": sync_job.started_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering sync: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to trigger sync")


@router.get("/documents", response_model=List[Document])
async def get_documents(
    source_id: Optional[str] = Query(None, description="Filter by data source"),
    search_query: Optional[str] = Query(None, description="Search documents"),
    limit: int = Query(50, description="Number of documents to return"),
    offset: int = Query(0, description="Number of documents to skip"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[Document]:
    """
    Get documents from the knowledge base with optional filtering

    Returns:
        List of documents matching the criteria
    """
    try:
        documents = await knowledge_service.get_documents(
            session,
            user_id=user_id,
            source_id=source_id,
            search_query=search_query,
            limit=limit,
            offset=offset,
        )
        return documents
    except Exception as e:
        logger.error(f"Error fetching documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")


@router.post("/search")
async def search_knowledge_base(
    query: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Perform semantic search across the knowledge base

    Returns:
        Search results with relevance scores and metadata
    """
    try:
        # Extract search parameters
        search_query = query.get("query", "")
        filters = query.get("filters", {})
        limit = query.get("limit", 10)
        search_type = query.get("type", "semantic")  # semantic, keyword, hybrid

        if not search_query:
            raise HTTPException(status_code=400, detail="Search query is required")

        # Perform search based on type
        if search_type == "semantic":
            results = await knowledge_service.semantic_search(
                query=search_query, user_id=user_id, filters=filters, limit=limit
            )
        elif search_type == "keyword":
            results = await knowledge_service.keyword_search(
                query=search_query, user_id=user_id, filters=filters, limit=limit
            )
        else:  # hybrid
            results = await knowledge_service.hybrid_search(
                query=search_query, user_id=user_id, filters=filters, limit=limit
            )

        return {
            "query": search_query,
            "type": search_type,
            "results": results,
            "total_results": len(results),
            "search_time_ms": results.get("search_time_ms", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing search: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to perform search")


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, str]:
    """
    Delete a document from the knowledge base

    Returns:
        Confirmation of deletion
    """
    try:
        # Verify document exists and user has access
        document = await knowledge_service.get_document(session, document_id, user_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete from vector stores
        await knowledge_service.delete_document_embeddings(document_id)

        # Delete from database
        await knowledge_service.delete_document(session, document_id)

        # Invalidate cache
        await cache_manager.invalidate_pattern(f"knowledge_stats:{user_id}")

        return {"message": f"Document {document_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete document")


@router.get("/sync-status/{source_id}", response_model=SyncStatus)
async def get_sync_status(
    source_id: str,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SyncStatus:
    """
    Get current sync status for a data source

    Returns:
        Detailed sync status information
    """
    try:
        status = await sync_service.get_sync_status(session, source_id, user_id)
        if not status:
            raise HTTPException(status_code=404, detail="No sync status found")

        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sync status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch sync status")


@router.post("/data-sources")
async def create_data_source(
    source_config: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> DataSource:
    """
    Create a new data source configuration

    Returns:
        Created data source details
    """
    try:
        # Validate source configuration
        required_fields = ["name", "type", "connection_config"]
        for field in required_fields:
            if field not in source_config:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        # Create data source
        source = await data_source_service.create_source(
            session, user_id=user_id, **source_config
        )

        return source

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating data source: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create data source")


@router.put("/data-sources/{source_id}")
async def update_data_source(
    source_id: str,
    source_update: Dict[str, Any],
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> DataSource:
    """
    Update an existing data source configuration

    Returns:
        Updated data source details
    """
    try:
        # Update data source
        source = await data_source_service.update_source(
            session, source_id=source_id, user_id=user_id, **source_update
        )

        if not source:
            raise HTTPException(status_code=404, detail="Data source not found")

        return source

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating data source: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update data source")


@router.get("/analytics/usage", response_model=Dict[str, Any])
async def get_knowledge_usage_analytics(
    time_period: str = Query("30d", description="Time period (7d, 30d, 90d)"),
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Get knowledge base usage analytics

    Returns:
        Usage analytics including search queries, document access, and trends
    """
    try:
        # Parse time period
        days = {"7d": 7, "30d": 30, "90d": 90}.get(time_period, 30)
        start_date = datetime.now() - timedelta(days=days)

        analytics = await knowledge_service.get_usage_analytics(
            session, user_id=user_id, start_date=start_date
        )

        return analytics

    except Exception as e:
        logger.error(f"Error fetching usage analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch usage analytics")
