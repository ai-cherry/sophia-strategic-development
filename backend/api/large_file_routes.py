"""
🚀 Large File Ingestion API Routes
FastAPI routes for handling large file uploads, processing, and monitoring

Endpoints:
- POST /large-files/upload - Upload files from URLs or direct upload
- GET /large-files/jobs - List all jobs
- GET /large-files/jobs/{job_id} - Get specific job status
- DELETE /large-files/jobs/{job_id} - Cancel/delete job
- POST /large-files/jobs/{job_id}/process - Process extracted files
- GET /large-files/stats - Get processing statistics
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl
from datetime import datetime
import logging
import tempfile
import shutil
from pathlib import Path

from backend.services.large_file_ingestion_service import (
    get_large_file_service, 
    ProcessingStatus,
    LargeFileJob
)
from backend.services.archive_processor import get_archive_processor
from backend.services.binary_file_handler import get_binary_file_handler

logger = logging.getLogger(__name__)

# Pydantic models for API
class UrlUploadRequest(BaseModel):
    """Request model for URL-based uploads"""
    url: HttpUrl
    filename: Optional[str] = None

class JobResponse(BaseModel):
    """Response model for job information"""
    job_id: str
    url: str
    filename: str
    total_size: int
    downloaded_size: int
    status: str
    progress_percentage: float
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    chunks_completed: int
    total_chunks: int
    file_hash: Optional[str] = None
    metadata: Dict[str, Any]

class ProcessingStatsResponse(BaseModel):
    """Response model for processing statistics"""
    total_jobs: int
    active_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_files_processed: int
    total_size_processed: int
    average_processing_time: float

class FileAnalysisResponse(BaseModel):
    """Response model for file analysis"""
    filename: str
    file_category: str
    mime_type: str
    file_size: int
    content_summary: Optional[str] = None
    extracted_entities: List[str]
    processing_time: float
    success: bool
    error_message: Optional[str] = None

# Create router
router = APIRouter(prefix="/large-files", tags=["Large File Ingestion"])

@router.post("/upload/url", response_model=JobResponse)
async def upload_from_url(
    request: UrlUploadRequest,
    background_tasks: BackgroundTasks
):
    """
    Start downloading a large file from URL
    
    - **url**: URL of the file to download
    - **filename**: Optional custom filename
    """
    try:
        service = await get_large_file_service()
        
        job_id = await service.start_download(
            url=str(request.url),
            filename=request.filename
        )
        
        job = await service.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=500, detail="Failed to create job")
        
        return JobResponse(
            job_id=job.job_id,
            url=job.url,
            filename=job.filename,
            total_size=job.total_size,
            downloaded_size=job.downloaded_size,
            status=job.status.value,
            progress_percentage=job.progress_percentage,
            created_at=job.created_at,
            updated_at=job.updated_at,
            error_message=job.error_message,
            chunks_completed=job.chunks_completed,
            total_chunks=job.total_chunks,
            file_hash=job.file_hash,
            metadata=job.metadata
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start URL upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/file", response_model=JobResponse)
async def upload_file_direct(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload a file directly to the system
    
    - **file**: File to upload
    """
    try:
        service = await get_large_file_service()
        
        # Save uploaded file to temporary location
        temp_dir = Path("temp/uploads")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        temp_file_path = temp_dir / file.filename
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create a job for the uploaded file
        # For direct uploads, we'll use the file path as URL
        job_id = await service.start_download(
            url=f"file://{temp_file_path}",
            filename=file.filename
        )
        
        job = await service.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=500, detail="Failed to create job")
        
        # Update job to completed since file is already uploaded
        job.status = ProcessingStatus.COMPLETED
        job.downloaded_size = temp_file_path.stat().st_size
        job.total_size = job.downloaded_size
        await service._save_job_state(job)
        
        return JobResponse(
            job_id=job.job_id,
            url=job.url,
            filename=job.filename,
            total_size=job.total_size,
            downloaded_size=job.downloaded_size,
            status=job.status.value,
            progress_percentage=job.progress_percentage,
            created_at=job.created_at,
            updated_at=job.updated_at,
            error_message=job.error_message,
            chunks_completed=job.chunks_completed,
            total_chunks=job.total_chunks,
            file_hash=job.file_hash,
            metadata=job.metadata
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs", response_model=List[JobResponse])
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of jobs to return")
):
    """
    List all large file processing jobs
    
    - **status**: Optional status filter (pending, downloading, processing, completed, failed, cancelled)
    - **limit**: Maximum number of jobs to return
    """
    try:
        service = await get_large_file_service()
        
        status_filter = None
        if status:
            try:
                status_filter = ProcessingStatus(status.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        jobs = await service.list_jobs(status_filter=status_filter)
        
        # Apply limit
        jobs = jobs[:limit]
        
        return [
            JobResponse(
                job_id=job.job_id,
                url=job.url,
                filename=job.filename,
                total_size=job.total_size,
                downloaded_size=job.downloaded_size,
                status=job.status.value,
                progress_percentage=job.progress_percentage,
                created_at=job.created_at,
                updated_at=job.updated_at,
                error_message=job.error_message,
                chunks_completed=job.chunks_completed,
                total_chunks=job.total_chunks,
                file_hash=job.file_hash,
                metadata=job.metadata
            )
            for job in jobs
        ]
        
    except Exception as e:
        logger.error(f"❌ Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """
    Get status of a specific job
    
    - **job_id**: ID of the job to check
    """
    try:
        service = await get_large_file_service()
        job = await service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobResponse(
            job_id=job.job_id,
            url=job.url,
            filename=job.filename,
            total_size=job.total_size,
            downloaded_size=job.downloaded_size,
            status=job.status.value,
            progress_percentage=job.progress_percentage,
            created_at=job.created_at,
            updated_at=job.updated_at,
            error_message=job.error_message,
            chunks_completed=job.chunks_completed,
            total_chunks=job.total_chunks,
            file_hash=job.file_hash,
            metadata=job.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a running job or delete a completed job
    
    - **job_id**: ID of the job to cancel/delete
    """
    try:
        service = await get_large_file_service()
        
        success = await service.cancel_job(job_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {"message": f"Job {job_id} cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/extract")
async def extract_archive(
    job_id: str,
    safe_mode: bool = Query(True, description="Enable security checks during extraction")
):
    """
    Extract an archive file (ZIP, TAR, etc.)
    
    - **job_id**: ID of the job containing the archive
    - **safe_mode**: Enable security checks (recommended)
    """
    try:
        service = await get_large_file_service()
        job = await service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != ProcessingStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Job must be completed before extraction")
        
        # Get file path
        file_path = Path(service.download_dir) / job.filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Downloaded file not found")
        
        # Extract archive
        archive_processor = await get_archive_processor()
        
        # First analyze the archive
        archive_info = await archive_processor.analyze_archive(file_path)
        
        # Extract the archive
        extraction_result = await archive_processor.extract_archive(
            file_path, job_id, safe_mode=safe_mode
        )
        
        if not extraction_result.success:
            raise HTTPException(status_code=500, detail=extraction_result.error_message)
        
        # Update job metadata
        job.metadata.update({
            "archive_extracted": True,
            "extracted_files_count": len(extraction_result.extracted_files),
            "extraction_path": str(extraction_result.extraction_path),
            "total_extracted_size": extraction_result.total_extracted_size,
            "security_violations": extraction_result.security_violations
        })
        
        await service._save_job_state(job)
        
        return {
            "message": "Archive extracted successfully",
            "extracted_files": len(extraction_result.extracted_files),
            "skipped_files": len(extraction_result.skipped_files),
            "total_size": extraction_result.total_extracted_size,
            "security_violations": extraction_result.security_violations,
            "extraction_path": str(extraction_result.extraction_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to extract archive: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/analyze", response_model=List[FileAnalysisResponse])
async def analyze_files(
    job_id: str,
    extract_content: bool = Query(True, description="Extract file content"),
    ai_analysis: bool = Query(False, description="Perform AI analysis (requires GPU)")
):
    """
    Analyze extracted files from a job
    
    - **job_id**: ID of the job containing extracted files
    - **extract_content**: Whether to extract text content from files
    - **ai_analysis**: Whether to perform AI-powered analysis
    """
    try:
        service = await get_large_file_service()
        job = await service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if not job.metadata.get("archive_extracted"):
            raise HTTPException(status_code=400, detail="Archive must be extracted first")
        
        extraction_path = Path(job.metadata.get("extraction_path", ""))
        if not extraction_path.exists():
            raise HTTPException(status_code=404, detail="Extraction directory not found")
        
        # Process all extracted files
        file_handler = await get_binary_file_handler()
        processing_results = await file_handler.process_directory(
            extraction_path, recursive=True
        )
        
        # Convert to response format
        analysis_results = []
        for result in processing_results:
            analysis_results.append(
                FileAnalysisResponse(
                    filename=result.metadata.filename,
                    file_category=result.metadata.file_category.value,
                    mime_type=result.metadata.mime_type,
                    file_size=result.metadata.file_size,
                    content_summary=result.metadata.content_summary,
                    extracted_entities=result.metadata.extracted_entities,
                    processing_time=result.metadata.processing_time,
                    success=result.success,
                    error_message=result.error_message
                )
            )
        
        # Update job metadata with analysis results
        stats = file_handler.get_processing_stats(processing_results)
        job.metadata.update({
            "files_analyzed": True,
            "analysis_stats": stats
        })
        await service._save_job_state(job)
        
        return analysis_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to analyze files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=ProcessingStatsResponse)
async def get_processing_stats():
    """
    Get processing statistics for all jobs
    """
    try:
        service = await get_large_file_service()
        jobs = await service.list_jobs()
        
        total_jobs = len(jobs)
        active_jobs = len([j for j in jobs if j.status in [ProcessingStatus.PENDING, ProcessingStatus.DOWNLOADING, ProcessingStatus.PROCESSING]])
        completed_jobs = len([j for j in jobs if j.status == ProcessingStatus.COMPLETED])
        failed_jobs = len([j for j in jobs if j.status == ProcessingStatus.FAILED])
        
        total_files_processed = sum(1 for j in jobs if j.status == ProcessingStatus.COMPLETED)
        total_size_processed = sum(j.downloaded_size for j in jobs if j.status == ProcessingStatus.COMPLETED)
        
        processing_times = [j.metadata.get("processing_time", 0) for j in jobs if j.status == ProcessingStatus.COMPLETED]
        average_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return ProcessingStatsResponse(
            total_jobs=total_jobs,
            active_jobs=active_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            total_files_processed=total_files_processed,
            total_size_processed=total_size_processed,
            average_processing_time=average_processing_time
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get processing stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_old_jobs(
    days_old: int = Query(7, ge=1, le=30, description="Remove jobs older than this many days")
):
    """
    Clean up old completed/failed jobs
    
    - **days_old**: Remove jobs older than this many days
    """
    try:
        service = await get_large_file_service()
        cleaned_count = await service.cleanup_old_jobs(days_old=days_old)
        
        return {
            "message": f"Cleaned up {cleaned_count} old jobs",
            "cleaned_count": cleaned_count
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to cleanup jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check for large file ingestion system
    """
    try:
        service = await get_large_file_service()
        archive_processor = await get_archive_processor()
        file_handler = await get_binary_file_handler()
        
        return {
            "status": "healthy",
            "services": {
                "large_file_service": "operational",
                "archive_processor": "operational", 
                "binary_file_handler": "operational"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        } 