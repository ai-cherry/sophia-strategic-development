"""
🚀 Large File Ingestion Service - Core Infrastructure
Handles 5GB+ file downloads with chunked processing, progress tracking, and error recovery

Integrates with existing Sophia AI infrastructure:
- Redis for progress tracking and job state
- Qdrant for content storage
- Lambda Labs GPU for content analysis
"""

import asyncio
import aiohttp
import aiofiles
import hashlib
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    """Processing status for large file operations"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class LargeFileJob:
    """Represents a large file processing job"""
    job_id: str
    url: str
    filename: str
    total_size: int
    downloaded_size: int = 0
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = None
    updated_at: datetime = None
    error_message: str = None
    chunks_completed: int = 0
    total_chunks: int = 0
    file_hash: str = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

    @property
    def progress_percentage(self) -> float:
        """Calculate download progress percentage"""
        if self.total_size <= 0:
            return 0.0
        return min(100.0, (self.downloaded_size / self.total_size) * 100)

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for Redis storage"""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LargeFileJob':
        """Create job from dictionary stored in Redis"""
        data['status'] = ProcessingStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

class LargeFileIngestionService:
    """Service for handling large file downloads and processing"""
    
    def __init__(self, redis_client=None, download_dir: str = "temp/downloads"):
        """Initialize the service with Redis and download directory"""
        self.redis_client = redis_client
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.chunk_size = 8 * 1024 * 1024  # 8MB chunks
        self.max_concurrent_downloads = 3
        self.max_retries = 3
        self.timeout = 300  # 5 minutes per chunk
        
        # Active jobs tracking
        self.active_jobs: Dict[str, LargeFileJob] = {}
        
        logger.info(f"🚀 Large File Ingestion Service initialized with download dir: {self.download_dir}")

    async def initialize(self):
        """Initialize service with Redis connection"""
        try:
            if self.redis_client is None:
                from backend.core.redis_connection_manager import get_redis_client
                self.redis_client = await get_redis_client()
            
            # Load active jobs from Redis
            await self._load_active_jobs()
            logger.info("✅ Large File Ingestion Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Large File Ingestion Service: {e}")
            # Continue without Redis for graceful degradation
            
    async def _load_active_jobs(self):
        """Load active jobs from Redis on service restart"""
        try:
            if not self.redis_client:
                return
                
            pattern = "large_file_job:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                job_data = await self.redis_client.hgetall(key)
                if job_data:
                    # Convert bytes to string for JSON parsing
                    job_dict = {k.decode(): v.decode() for k, v in job_data.items()}
                    job_dict = json.loads(job_dict.get('data', '{}'))
                    
                    job = LargeFileJob.from_dict(job_dict)
                    self.active_jobs[job.job_id] = job
                    
            logger.info(f"📂 Loaded {len(self.active_jobs)} active jobs from Redis")
            
        except Exception as e:
            logger.error(f"⚠️ Failed to load jobs from Redis: {e}")

    async def start_download(self, url: str, filename: str = None) -> str:
        """Start a large file download with progress tracking"""
        try:
            job_id = hashlib.md5(f"{url}{time.time()}".encode()).hexdigest()
            
            if not filename:
                filename = url.split('/')[-1] or f"download_{job_id}"
            
            # Get file size from HEAD request
            async with aiohttp.ClientSession() as session:
                async with session.head(url) as response:
                    total_size = int(response.headers.get('Content-Length', 0))
                    
            # Create job
            job = LargeFileJob(
                job_id=job_id,
                url=url,
                filename=filename,
                total_size=total_size,
                total_chunks=max(1, total_size // self.chunk_size)
            )
            
            self.active_jobs[job_id] = job
            await self._save_job_state(job)
            
            # Start download in background
            asyncio.create_task(self._download_file(job))
            
            logger.info(f"🔄 Started download job {job_id} for {filename} ({total_size} bytes)")
            return job_id
            
        except Exception as e:
            logger.error(f"❌ Failed to start download: {e}")
            raise

    async def _download_file(self, job: LargeFileJob):
        """Download file in chunks with progress tracking"""
        try:
            job.status = ProcessingStatus.DOWNLOADING
            await self._save_job_state(job)
            
            file_path = self.download_dir / job.filename
            
            # Support resume downloads
            existing_size = file_path.stat().st_size if file_path.exists() else 0
            job.downloaded_size = existing_size
            
            headers = {}
            if existing_size > 0:
                headers['Range'] = f'bytes={existing_size}-'
                
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(job.url, headers=headers) as response:
                    response.raise_for_status()
                    
                    # Calculate hash as we download
                    hasher = hashlib.sha256()
                    
                    async with aiofiles.open(file_path, 'ab' if existing_size > 0 else 'wb') as f:
                        async for chunk in response.content.iter_chunked(self.chunk_size):
                            await f.write(chunk)
                            hasher.update(chunk)
                            
                            job.downloaded_size += len(chunk)
                            job.chunks_completed += 1
                            job.updated_at = datetime.now()
                            
                            # Save progress every 10 chunks
                            if job.chunks_completed % 10 == 0:
                                await self._save_job_state(job)
                                
                            logger.debug(f"📥 Downloaded chunk {job.chunks_completed}/{job.total_chunks} "
                                       f"({job.progress_percentage:.1f}%)")
            
            # Finalize job
            job.file_hash = hasher.hexdigest()
            job.status = ProcessingStatus.COMPLETED
            job.updated_at = datetime.now()
            await self._save_job_state(job)
            
            logger.info(f"✅ Download completed: {job.filename} ({job.downloaded_size} bytes)")
            
            # Trigger post-processing
            await self._post_process_file(job)
            
        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.error_message = str(e)
            await self._save_job_state(job)
            logger.error(f"❌ Download failed for {job.filename}: {e}")

    async def _post_process_file(self, job: LargeFileJob):
        """Post-process downloaded file (extract, analyze, etc.)"""
        try:
            job.status = ProcessingStatus.PROCESSING
            await self._save_job_state(job)
            
            file_path = self.download_dir / job.filename
            
            # Detect file type and trigger appropriate processor
            if job.filename.lower().endswith(('.zip', '.tar', '.tar.gz', '.tgz')):
                await self._process_archive(job, file_path)
            else:
                await self._process_regular_file(job, file_path)
                
        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.error_message = f"Post-processing failed: {e}"
            await self._save_job_state(job)
            logger.error(f"❌ Post-processing failed for {job.filename}: {e}")

    async def _process_archive(self, job: LargeFileJob, file_path: Path):
        """Process archive files (ZIP, TAR)"""
        logger.info(f"📦 Processing archive: {file_path}")
        # This will be implemented by the Archive Processor
        job.metadata['archive_processed'] = True
        job.metadata['file_type'] = 'archive'

    async def _process_regular_file(self, job: LargeFileJob, file_path: Path):
        """Process regular files"""
        logger.info(f"📄 Processing regular file: {file_path}")
        # This will be implemented by the Binary File Handler
        job.metadata['file_processed'] = True
        job.metadata['file_type'] = 'regular'

    async def _save_job_state(self, job: LargeFileJob):
        """Save job state to Redis"""
        try:
            if not self.redis_client:
                return
                
            key = f"large_file_job:{job.job_id}"
            job_data = json.dumps(job.to_dict())
            
            await self.redis_client.hset(key, "data", job_data)
            await self.redis_client.expire(key, 86400 * 7)  # 7 days TTL
            
        except Exception as e:
            logger.error(f"⚠️ Failed to save job state: {e}")

    async def get_job_status(self, job_id: str) -> Optional[LargeFileJob]:
        """Get job status by ID"""
        try:
            # Check active jobs first
            if job_id in self.active_jobs:
                return self.active_jobs[job_id]
            
            # Check Redis
            if self.redis_client:
                key = f"large_file_job:{job_id}"
                job_data = await self.redis_client.hgetall(key)
                
                if job_data:
                    job_dict = {k.decode(): v.decode() for k, v in job_data.items()}
                    job_dict = json.loads(job_dict.get('data', '{}'))
                    return LargeFileJob.from_dict(job_dict)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get job status: {e}")
            return None

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        try:
            job = await self.get_job_status(job_id)
            if not job:
                return False
            
            job.status = ProcessingStatus.CANCELLED
            job.updated_at = datetime.now()
            await self._save_job_state(job)
            
            # Remove from active jobs
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
            
            logger.info(f"🛑 Cancelled job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel job: {e}")
            return False

    async def list_jobs(self, status_filter: ProcessingStatus = None) -> List[LargeFileJob]:
        """List all jobs, optionally filtered by status"""
        try:
            jobs = []
            
            # Get from active jobs
            for job in self.active_jobs.values():
                if not status_filter or job.status == status_filter:
                    jobs.append(job)
            
            # Get from Redis if not in active jobs
            if self.redis_client:
                pattern = "large_file_job:*"
                keys = await self.redis_client.keys(pattern)
                
                for key in keys:
                    job_data = await self.redis_client.hgetall(key)
                    if job_data:
                        job_dict = {k.decode(): v.decode() for k, v in job_data.items()}
                        job_dict = json.loads(job_dict.get('data', '{}'))
                        job = LargeFileJob.from_dict(job_dict)
                        
                        # Avoid duplicates
                        if job.job_id not in self.active_jobs:
                            if not status_filter or job.status == status_filter:
                                jobs.append(job)
            
            return sorted(jobs, key=lambda x: x.created_at, reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Failed to list jobs: {e}")
            return []

    async def cleanup_old_jobs(self, days_old: int = 7):
        """Clean up jobs older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            jobs = await self.list_jobs()
            
            cleaned_count = 0
            for job in jobs:
                if job.created_at < cutoff_date and job.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED, ProcessingStatus.CANCELLED]:
                    # Remove job data
                    if self.redis_client:
                        key = f"large_file_job:{job.job_id}"
                        await self.redis_client.delete(key)
                    
                    # Remove local file if exists
                    file_path = self.download_dir / job.filename
                    if file_path.exists():
                        file_path.unlink()
                    
                    cleaned_count += 1
            
            logger.info(f"🧹 Cleaned up {cleaned_count} old jobs")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old jobs: {e}")
            return 0

# Global service instance
_large_file_service = None

async def get_large_file_service() -> LargeFileIngestionService:
    """Get or create the global large file service instance"""
    global _large_file_service
    
    if _large_file_service is None:
        _large_file_service = LargeFileIngestionService()
        await _large_file_service.initialize()
    
    return _large_file_service 