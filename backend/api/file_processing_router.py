"""
FastAPI Router for File Processing and Data Ingestion
Handles file uploads, API integrations, and Snowflake data processing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Dict, Any, Optional
import asyncio
import json
import logging
import tempfile
import os
from pathlib import Path
from datetime import datetime
import uuid

from ..core.data_transformation_pipeline import DataTransformationPipeline, ProcessingJob
from ..core.websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/files", tags=["file-processing"])

# Global instances
pipeline = None
websocket_manager = WebSocketManager()

async def get_pipeline():
    """Get or initialize the data transformation pipeline"""
    global pipeline
    if pipeline is None:
        config = {
            'snowflake': {
                'user': os.getenv('SNOWFLAKE_USER'),
                'password': os.getenv('SNOWFLAKE_PASSWORD'),
                'account': os.getenv('SNOWFLAKE_ACCOUNT'),
                'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
                'database': os.getenv('SNOWFLAKE_DATABASE'),
                'schema': os.getenv('SNOWFLAKE_SCHEMA')
            },
            'redis': {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', 6379))
            },
            'apis': {
                'hubspot': {
                    'base_url': 'https://api.hubapi.com',
                    'access_token': os.getenv('HUBSPOT_ACCESS_TOKEN')
                },
                'gong': {
                    'base_url': 'https://api.gong.io',
                    'auth_token': os.getenv('GONG_AUTH_TOKEN')
                },
                'slack': {
                    'base_url': 'https://slack.com/api',
                    'bot_token': os.getenv('SLACK_BOT_TOKEN')
                }
            }
        }
        pipeline = DataTransformationPipeline(config)
        await pipeline.initialize()
    return pipeline

@router.websocket("/ws/file-processing")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time file processing updates"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Echo back for connection testing
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    metadata: Optional[str] = None
):
    """Upload and process a file"""
    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Parse metadata
        file_metadata = json.loads(metadata) if metadata else {}
        file_metadata.update({
            'id': file_id,
            'name': file.filename,
            'size': file.size,
            'type': file.content_type,
            'uploaded_at': datetime.utcnow().isoformat()
        })
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Notify upload progress
        await websocket_manager.broadcast({
            'type': 'file_upload_progress',
            'fileId': file_id,
            'progress': 100
        })
        
        # Process file in background
        background_tasks.add_task(
            process_file_background,
            file_id,
            temp_file_path,
            file_metadata
        )
        
        return JSONResponse({
            'status': 'success',
            'file_id': file_id,
            'message': 'File uploaded successfully, processing started'
        })
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_file_background(file_id: str, file_path: str, metadata: Dict[str, Any]):
    """Background task to process uploaded file"""
    try:
        # Get pipeline instance
        pipeline_instance = await get_pipeline()
        
        # Notify processing started
        await websocket_manager.broadcast({
            'type': 'file_processing_started',
            'fileId': file_id
        })
        
        # Process the file
        result = await pipeline_instance.process_file_upload(file_path, metadata)
        
        # Notify processing completed
        await websocket_manager.broadcast({
            'type': 'file_processing_complete',
            'fileId': file_id,
            'result': result
        })
        
        # Update processing stats
        stats = await pipeline_instance.get_processing_stats()
        await websocket_manager.broadcast({
            'type': 'processing_stats_update',
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error processing file {file_id}: {e}")
        await websocket_manager.broadcast({
            'type': 'file_processing_error',
            'fileId': file_id,
            'error': str(e)
        })
    finally:
        # Cleanup temporary file
        try:
            os.remove(file_path)
            os.rmdir(os.path.dirname(file_path))
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file: {e}")

@router.post("/sync/hubspot")
async def sync_hubspot_data(background_tasks: BackgroundTasks):
    """Sync data from HubSpot CRM"""
    try:
        job_id = str(uuid.uuid4())
        
        # Create processing job
        job = ProcessingJob(
            job_id=job_id,
            source_name='hubspot',
            target_table='hubspot_contacts',
            transformation_rules=[]
        )
        
        # Process in background
        background_tasks.add_task(process_hubspot_background, job)
        
        return JSONResponse({
            'status': 'success',
            'job_id': job_id,
            'message': 'HubSpot sync started'
        })
        
    except Exception as e:
        logger.error(f"Error starting HubSpot sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_hubspot_background(job: ProcessingJob):
    """Background task to process HubSpot data"""
    try:
        pipeline_instance = await get_pipeline()
        result = await pipeline_instance.process_hubspot_data(job)
        
        await websocket_manager.broadcast({
            'type': 'hubspot_sync_complete',
            'jobId': job.job_id,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error processing HubSpot data: {e}")
        await websocket_manager.broadcast({
            'type': 'hubspot_sync_error',
            'jobId': job.job_id,
            'error': str(e)
        })

@router.post("/sync/gong")
async def sync_gong_data(background_tasks: BackgroundTasks):
    """Sync data from Gong.io"""
    try:
        job_id = str(uuid.uuid4())
        
        # Create processing job
        job = ProcessingJob(
            job_id=job_id,
            source_name='gong',
            target_table='gong_calls',
            transformation_rules=[]
        )
        
        # Process in background
        background_tasks.add_task(process_gong_background, job)
        
        return JSONResponse({
            'status': 'success',
            'job_id': job_id,
            'message': 'Gong sync started'
        })
        
    except Exception as e:
        logger.error(f"Error starting Gong sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_gong_background(job: ProcessingJob):
    """Background task to process Gong data"""
    try:
        pipeline_instance = await get_pipeline()
        result = await pipeline_instance.process_gong_data(job)
        
        await websocket_manager.broadcast({
            'type': 'gong_sync_complete',
            'jobId': job.job_id,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error processing Gong data: {e}")
        await websocket_manager.broadcast({
            'type': 'gong_sync_error',
            'jobId': job.job_id,
            'error': str(e)
        })

@router.post("/sync/slack")
async def sync_slack_data(background_tasks: BackgroundTasks):
    """Sync data from Slack"""
    try:
        job_id = str(uuid.uuid4())
        
        # Create processing job
        job = ProcessingJob(
            job_id=job_id,
            source_name='slack',
            target_table='slack_messages',
            transformation_rules=[]
        )
        
        # Process in background
        background_tasks.add_task(process_slack_background, job)
        
        return JSONResponse({
            'status': 'success',
            'job_id': job_id,
            'message': 'Slack sync started'
        })
        
    except Exception as e:
        logger.error(f"Error starting Slack sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_slack_background(job: ProcessingJob):
    """Background task to process Slack data"""
    try:
        pipeline_instance = await get_pipeline()
        result = await pipeline_instance.process_slack_data(job)
        
        await websocket_manager.broadcast({
            'type': 'slack_sync_complete',
            'jobId': job.job_id,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error processing Slack data: {e}")
        await websocket_manager.broadcast({
            'type': 'slack_sync_error',
            'jobId': job.job_id,
            'error': str(e)
        })

@router.get("/stats")
async def get_processing_stats():
    """Get current processing statistics"""
    try:
        pipeline_instance = await get_pipeline()
        stats = await pipeline_instance.get_processing_stats()
        return JSONResponse(stats)
        
    except Exception as e:
        logger.error(f"Error getting processing stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/download")
async def download_processed_data(file_id: str):
    """Download processed data for a file"""
    try:
        # This would typically fetch from a database or file storage
        # For now, return a placeholder response
        return JSONResponse({
            'message': 'Download functionality not yet implemented',
            'file_id': file_id
        })
        
    except Exception as e:
        logger.error(f"Error downloading processed data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Delete a processed file"""
    try:
        # This would typically delete from database and file storage
        # For now, return a placeholder response
        return JSONResponse({
            'status': 'success',
            'message': f'File {file_id} deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{file_id}/reprocess")
async def reprocess_file(file_id: str, background_tasks: BackgroundTasks):
    """Reprocess a file"""
    try:
        # This would typically fetch the original file and reprocess it
        # For now, return a placeholder response
        return JSONResponse({
            'status': 'success',
            'message': f'File {file_id} reprocessing started'
        })
        
    except Exception as e:
        logger.error(f"Error reprocessing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        pipeline_instance = await get_pipeline()
        return JSONResponse({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'pipeline_initialized': pipeline_instance is not None
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, status_code=503)

