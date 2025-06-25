"""
Large Data Import API Routes
Provides endpoints for uploading and processing large datasets from various sources
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from typing import Optional, Dict, Any
import tempfile
import os
from datetime import datetime

from backend.core.auth import get_current_user
from backend.services.large_data_import_service import (
    LargeDataImportService, 
    ImportDataType, 
    ImportJob
)
from backend.core.logger import logger

router = APIRouter(prefix="/api/v1/knowledge/import", tags=["large-data-import"])

# Initialize service
import_service = LargeDataImportService()


@router.post("/upload")
async def upload_large_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    data_type: str = Form(...),
    description: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Upload and process a large dataset
    
    Supported data types:
    - gong_email: Gong email export files
    - gong_calendar: Gong calendar export files  
    - slack_export: Slack workspace export (ZIP)
    - csv_bulk: Bulk CSV data
    - json_bulk: Bulk JSON data
    - email_archive: Email archive files (MBOX, PST)
    - document_archive: Document archive files (ZIP)
    """
    try:
        # Validate data type
        try:
            import_data_type = ImportDataType(data_type)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid data type: {data_type}. Supported types: {[t.value for t in ImportDataType]}"
            )
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Save uploaded file to temporary location
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}")
        try:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            temp_file_path = temp_file.name
        finally:
            temp_file.close()
        
        # Create import job
        metadata = {
            'uploaded_by': user_id,
            'original_filename': file.filename,
            'file_size': len(content),
            'description': description,
            'upload_time': datetime.now().isoformat()
        }
        
        job = await import_service.create_import_job(
            file_path=temp_file_path,
            data_type=import_data_type,
            metadata=metadata
        )
        
        # Start processing in background
        background_tasks.add_task(process_import_job_background, job.job_id)
        
        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "estimated_records": job.total_records,
            "message": f"Import job created successfully. Processing {job.total_records} estimated records.",
            "data_type": data_type,
            "filename": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create import job: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create import job")


async def process_import_job_background(job_id: str):
    """Background task to process import job"""
    try:
        await import_service.process_import_job(job_id)
        logger.info(f"Import job {job_id} completed successfully")
    except Exception as e:
        logger.error(f"Import job {job_id} failed: {str(e)}")


@router.get("/jobs")
async def list_import_jobs(
    limit: int = 50,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    List recent import jobs
    """
    try:
        jobs = await import_service.list_import_jobs(limit=limit)
        
        return {
            "jobs": [
                {
                    "job_id": job.job_id,
                    "data_type": job.data_type.value,
                    "status": job.status.value,
                    "total_records": job.total_records,
                    "processed_records": job.processed_records,
                    "progress_percentage": (job.processed_records / job.total_records * 100) if job.total_records > 0 else 0,
                    "started_at": job.started_at.isoformat(),
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "error_message": job.error_message,
                    "metadata": job.metadata
                }
                for job in jobs
            ],
            "total_jobs": len(jobs)
        }
        
    except Exception as e:
        logger.error(f"Failed to list import jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list import jobs")


@router.get("/jobs/{job_id}")
async def get_import_job_status(
    job_id: str,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the status of a specific import job
    """
    try:
        job = await import_service.get_import_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Import job not found")
        
        return {
            "job_id": job.job_id,
            "data_type": job.data_type.value,
            "status": job.status.value,
            "total_records": job.total_records,
            "processed_records": job.processed_records,
            "progress_percentage": (job.processed_records / job.total_records * 100) if job.total_records > 0 else 0,
            "started_at": job.started_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message,
            "metadata": job.metadata,
            "estimated_completion": _estimate_completion_time(job) if job.status.value == "processing" else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get import job status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get import job status")


@router.post("/jobs/{job_id}/cancel")
async def cancel_import_job(
    job_id: str,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Cancel a running import job
    """
    try:
        success = await import_service.cancel_import_job(job_id)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Import job not found or cannot be cancelled"
            )
        
        return {
            "job_id": job_id,
            "status": "cancelled",
            "message": "Import job cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel import job: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel import job")


@router.get("/data-types")
async def get_supported_data_types(
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get supported data types for import
    """
    data_types = {
        "gong_email": {
            "name": "Gong Email Export",
            "description": "Email data exported from Gong.io",
            "supported_formats": ["CSV", "JSON"],
            "max_file_size": "5GB",
            "example_fields": ["email_id", "subject", "sender", "recipients", "sent_time", "body"]
        },
        "gong_calendar": {
            "name": "Gong Calendar Export", 
            "description": "Calendar event data exported from Gong.io",
            "supported_formats": ["CSV", "JSON"],
            "max_file_size": "5GB",
            "example_fields": ["event_id", "title", "start_time", "end_time", "attendees", "location"]
        },
        "slack_export": {
            "name": "Slack Workspace Export",
            "description": "Complete Slack workspace export including channels, users, and messages",
            "supported_formats": ["ZIP"],
            "max_file_size": "5GB",
            "example_fields": ["channels", "users", "messages", "files"]
        },
        "csv_bulk": {
            "name": "Bulk CSV Data",
            "description": "Generic CSV data for bulk import",
            "supported_formats": ["CSV"],
            "max_file_size": "5GB",
            "example_fields": ["Any CSV columns"]
        },
        "json_bulk": {
            "name": "Bulk JSON Data",
            "description": "Generic JSON data for bulk import",
            "supported_formats": ["JSON"],
            "max_file_size": "5GB",
            "example_fields": ["Any JSON structure"]
        },
        "email_archive": {
            "name": "Email Archive",
            "description": "Email archive files from various email clients",
            "supported_formats": ["MBOX", "PST", "EML"],
            "max_file_size": "5GB",
            "example_fields": ["sender", "recipients", "subject", "body", "date"]
        },
        "document_archive": {
            "name": "Document Archive",
            "description": "Archive files containing multiple documents",
            "supported_formats": ["ZIP"],
            "max_file_size": "5GB",
            "example_fields": ["Multiple document files"]
        }
    }
    
    return {
        "supported_data_types": data_types,
        "total_types": len(data_types),
        "max_file_size": "5GB",
        "processing_info": {
            "batch_size": 1000,
            "estimated_processing_time": "Varies by file size and complexity",
            "background_processing": True,
            "progress_tracking": True
        }
    }


@router.get("/stats")
async def get_import_stats(
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get import statistics and metrics
    """
    try:
        # This would typically query the database for actual stats
        # For now, return mock statistics
        
        return {
            "total_imports": 45,
            "successful_imports": 38,
            "failed_imports": 4,
            "in_progress_imports": 3,
            "total_records_imported": 156789,
            "data_type_breakdown": {
                "gong_email": 12,
                "slack_export": 8,
                "csv_bulk": 15,
                "json_bulk": 6,
                "document_archive": 4
            },
            "average_processing_time_minutes": 23.5,
            "largest_import_records": 45000,
            "recent_activity": {
                "last_24_hours": 5,
                "last_7_days": 18,
                "last_30_days": 45
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get import stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get import statistics")


@router.post("/validate")
async def validate_import_file(
    file: UploadFile = File(...),
    data_type: str = Form(...),
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validate an import file without processing it
    """
    try:
        # Validate data type
        try:
            import_data_type = ImportDataType(data_type)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid data type: {data_type}"
            )
        
        # Read file content for validation
        content = await file.read()
        file_size = len(content)
        
        # Basic validations
        validations = {
            "file_size_ok": file_size <= import_service.max_file_size,
            "file_format_ok": _validate_file_format(file.filename, import_data_type),
            "estimated_records": 0,
            "validation_errors": [],
            "validation_warnings": []
        }
        
        # Estimate record count
        if validations["file_size_ok"] and validations["file_format_ok"]:
            # Save to temp file for estimation
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            try:
                temp_file.write(content)
                temp_file.flush()
                validations["estimated_records"] = await import_service._estimate_record_count(
                    temp_file.name, import_data_type
                )
            finally:
                temp_file.close()
                os.unlink(temp_file.name)
        
        # Add validation errors
        if not validations["file_size_ok"]:
            validations["validation_errors"].append(
                f"File size ({file_size} bytes) exceeds maximum allowed size ({import_service.max_file_size} bytes)"
            )
        
        if not validations["file_format_ok"]:
            validations["validation_errors"].append(
                f"File format not supported for data type {data_type}"
            )
        
        # Add warnings
        if file_size > 1024 * 1024 * 1024:  # 1GB
            validations["validation_warnings"].append(
                "Large file detected. Processing may take significant time."
            )
        
        return {
            "filename": file.filename,
            "data_type": data_type,
            "file_size": file_size,
            "is_valid": len(validations["validation_errors"]) == 0,
            **validations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate import file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to validate import file")


def _validate_file_format(filename: str, data_type: ImportDataType) -> bool:
    """Validate file format against data type"""
    if not filename:
        return False
    
    filename_lower = filename.lower()
    
    format_map = {
        ImportDataType.GONG_EMAIL: ['.csv', '.json'],
        ImportDataType.GONG_CALENDAR: ['.csv', '.json'],
        ImportDataType.SLACK_EXPORT: ['.zip'],
        ImportDataType.CSV_BULK: ['.csv'],
        ImportDataType.JSON_BULK: ['.json'],
        ImportDataType.EMAIL_ARCHIVE: ['.mbox', '.pst', '.eml'],
        ImportDataType.DOCUMENT_ARCHIVE: ['.zip']
    }
    
    allowed_extensions = format_map.get(data_type, [])
    return any(filename_lower.endswith(ext) for ext in allowed_extensions)


def _estimate_completion_time(job: ImportJob) -> str:
    """Estimate completion time for a running job"""
    if job.processed_records == 0:
        return "Calculating..."
    
    # Calculate processing rate
    elapsed_time = (datetime.now() - job.started_at).total_seconds()
    records_per_second = job.processed_records / elapsed_time
    
    if records_per_second > 0:
        remaining_records = job.total_records - job.processed_records
        remaining_seconds = remaining_records / records_per_second
        
        if remaining_seconds < 60:
            return f"{int(remaining_seconds)} seconds"
        elif remaining_seconds < 3600:
            return f"{int(remaining_seconds / 60)} minutes"
        else:
            return f"{int(remaining_seconds / 3600)} hours"
    
    return "Unknown" 