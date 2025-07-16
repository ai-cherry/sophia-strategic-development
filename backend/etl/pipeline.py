"""
ETL Pipeline for Sophia AI
Orchestrates data extraction, transformation, and loading
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime

from backend.etl.adapters.unified_etl_adapter import UnifiedETLAdapter, ETLJob

logger = logging.getLogger(__name__)

class ETLPipeline:
    """ETL pipeline orchestrator"""
    
    def __init__(self):
        self.adapter = UnifiedETLAdapter()
        self.running_jobs: Dict[str, ETLJob] = {}
        
    async def initialize(self):
        """Initialize ETL pipeline"""
        await self.adapter.initialize()
        logger.info("✅ ETL Pipeline initialized")
        
    async def run_etl_job(self, job: ETLJob) -> bool:
        """Run a complete ETL job"""
        logger.info(f"Starting ETL job: {job.job_id}")
        job.status = "running"
        self.running_jobs[job.job_id] = job
        
        try:
            # Extract
            extracted_data = await self.adapter.extract_data(job.source, {})
            
            # Transform
            transformed_data = await self.adapter.transform_data(extracted_data, job.transformation_rules)
            
            # Load
            success = await self.adapter.load_data(transformed_data, job.destination)
            
            if success:
                job.status = "completed"
                logger.info(f"✅ ETL job {job.job_id} completed successfully")
            else:
                job.status = "failed"
                logger.error(f"❌ ETL job {job.job_id} failed")
                
            return success
            
        except Exception as e:
            job.status = "error"
            logger.error(f"❌ ETL job {job.job_id} error: {e}")
            return False
        finally:
            if job.job_id in self.running_jobs:
                del self.running_jobs[job.job_id]
    
    async def schedule_job(self, source: str, destination: str, transformation_rules: Dict[str, Any]) -> str:
        """Schedule a new ETL job"""
        job_id = f"etl_{int(datetime.utcnow().timestamp())}"
        
        job = ETLJob(
            job_id=job_id,
            source=source,
            destination=destination,
            transformation_rules=transformation_rules
        )
        
        # Run job asynchronously
        asyncio.create_task(self.run_etl_job(job))
        
        logger.info(f"Scheduled ETL job: {job_id}")
        return job_id
