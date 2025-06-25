#!/usr/bin/env python3
"""
Airbyte Gong Integration Setup Script

Automates the configuration of Gong source connector and Snowflake destination
for the Sophia AI data pipeline using the Airbyte API.

Usage:
    python backend/scripts/airbyte_gong_setup.py --mode setup
    python backend/scripts/airbyte_gong_setup.py --mode test
    python backend/scripts/airbyte_gong_setup.py --mode monitor

Features:
- Automated Gong source connector configuration
- Snowflake destination setup with proper schemas
- Connection configuration with incremental sync
- Monitoring and health checks
- Integration with Pulumi ESC secrets
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import argparse

import aiohttp
import structlog
from backend.core.auto_esc_config import get_config_value

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()


class AirbyteOperationMode(Enum):
    """Airbyte operation modes"""
    SETUP = "setup"
    TEST = "test"
    MONITOR = "monitor"
    SYNC = "sync"


@dataclass
class AirbyteConfig:
    """Airbyte configuration"""
    base_url: str
    username: str = "airbyte"
    password: str = "password"
    workspace_id: str = "default"


@dataclass
class GongSourceConfig:
    """Gong source connector configuration"""
    access_key: str
    access_key_secret: str
    start_date: str = "2024-01-01T00:00:00Z"
    call_types: List[str] = None
    include_transcripts: bool = True
    sync_mode: str = "incremental"
    
    def __post_init__(self):
        if self.call_types is None:
            self.call_types = ["inbound", "outbound"]


@dataclass
class SnowflakeDestinationConfig:
    """Snowflake destination connector configuration"""
    host: str
    role: str = "ROLE_SOPHIA_AIRBYTE_INGEST"
    warehouse: str = "WH_SOPHIA_ETL_TRANSFORM"
    database: str = "SOPHIA_AI_DEV"
    schema: str = "RAW_AIRBYTE"
    username: str = "SCOOBYJAVA15"
    password: str = ""
    jdbc_url_params: str = "CLIENT_SESSION_KEEP_ALIVE=true"


class AirbyteGongOrchestrator:
    """
    Orchestrates Airbyte setup for Gong data pipeline
    
    Capabilities:
    - Configure Gong source connector with proper API scopes
    - Set up Snowflake destination for RAW_AIRBYTE schema
    - Create and manage connections with incremental sync
    - Monitor sync jobs and provide health checks
    - Integration with Sophia AI infrastructure
    """

    def __init__(self, airbyte_config: AirbyteConfig):
        self.airbyte_config = airbyte_config
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Configuration from Pulumi ESC
        self.gong_config: Optional[GongSourceConfig] = None
        self.snowflake_config: Optional[SnowflakeDestinationConfig] = None
        
        # Airbyte resource IDs (will be populated during setup)
        self.gong_source_id: Optional[str] = None
        self.snowflake_destination_id: Optional[str] = None
        self.connection_id: Optional[str] = None

    async def initialize(self) -> None:
        """Initialize the orchestrator with configurations from Pulumi ESC"""
        try:
            # Load configurations from Pulumi ESC
            self.gong_config = GongSourceConfig(
                access_key=get_config_value("gong_access_key"),
                access_key_secret=get_config_value("gong_client_secret"),
                start_date=get_config_value("gong_sync_start_date", "2024-01-01T00:00:00Z"),
                include_transcripts=True,
                sync_mode="incremental"
            )
            
            self.snowflake_config = SnowflakeDestinationConfig(
                host=f"{get_config_value('snowflake_account')}.snowflakecomputing.com",
                username=get_config_value("snowflake_user", "SCOOBYJAVA15"),
                password=get_config_value("snowflake_password"),
                warehouse=get_config_value("snowflake_warehouse", "WH_SOPHIA_ETL_TRANSFORM"),
                database=get_config_value("snowflake_database", "SOPHIA_AI_DEV"),
                schema="RAW_AIRBYTE"
            )
            
            # Initialize HTTP session
            auth = aiohttp.BasicAuth(
                self.airbyte_config.username, 
                self.airbyte_config.password
            )
            self.session = aiohttp.ClientSession(
                auth=auth,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=60)
            )
            
            logger.info("✅ Airbyte Gong Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Airbyte orchestrator: {e}")
            raise

    async def setup_complete_pipeline(self) -> Dict[str, Any]:
        """Set up the complete Gong → Airbyte → Snowflake pipeline"""
        try:
            logger.info("🚀 Setting up complete Gong data pipeline...")
            
            # Step 1: Create Gong source connector
            gong_source = await self._create_gong_source()
            self.gong_source_id = gong_source["sourceId"]
            logger.info(f"✅ Gong source created: {self.gong_source_id}")
            
            # Step 2: Create Snowflake destination connector
            snowflake_dest = await self._create_snowflake_destination()
            self.snowflake_destination_id = snowflake_dest["destinationId"]
            logger.info(f"✅ Snowflake destination created: {self.snowflake_destination_id}")
            
            # Step 3: Create connection between source and destination
            connection = await self._create_connection()
            self.connection_id = connection["connectionId"]
            logger.info(f"✅ Connection created: {self.connection_id}")
            
            # Step 4: Configure sync schedule (hourly)
            await self._configure_sync_schedule()
            logger.info("✅ Sync schedule configured (hourly)")
            
            # Step 5: Test connection
            test_result = await self._test_connection()
            logger.info(f"✅ Connection test: {'PASSED' if test_result else 'FAILED'}")
            
            # Step 6: Trigger initial sync
            sync_job = await self._trigger_sync()
            logger.info(f"✅ Initial sync triggered: {sync_job.get('jobId')}")
            
            return {
                "success": True,
                "gong_source_id": self.gong_source_id,
                "snowflake_destination_id": self.snowflake_destination_id,
                "connection_id": self.connection_id,
                "sync_job_id": sync_job.get("jobId"),
                "setup_timestamp": datetime.utcnow().isoformat(),
                "next_steps": [
                    "Monitor sync job progress",
                    "Verify data landing in RAW_AIRBYTE tables",
                    "Activate Snowflake transformation tasks",
                    "Test AI Memory integration"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to set up Gong pipeline: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_setup": {
                    "gong_source_id": self.gong_source_id,
                    "snowflake_destination_id": self.snowflake_destination_id,
                    "connection_id": self.connection_id
                }
            }

    async def _create_gong_source(self) -> Dict[str, Any]:
        """Create Gong source connector with proper API scopes"""
        source_definition_id = await self._get_source_definition_id("Gong")
        
        source_config = {
            "sourceDefinitionId": source_definition_id,
            "connectionConfiguration": {
                "access_key": self.gong_config.access_key,
                "access_key_secret": self.gong_config.access_key_secret,
                "start_date": self.gong_config.start_date,
                
                # Gong API scopes and endpoints (based on Manus AI guidance)
                "api_endpoints": {
                    "calls": {
                        "enabled": True,
                        "endpoint": "/v2/calls",
                        "incremental_field": "metaData.started",
                        "sync_mode": "incremental_append_dedup"
                    },
                    "call_transcripts": {
                        "enabled": self.gong_config.include_transcripts,
                        "endpoint": "/v2/calls/{call_id}/transcript",
                        "incremental_field": "metaData.started",
                        "sync_mode": "incremental_append_dedup"
                    },
                    "users": {
                        "enabled": True,
                        "endpoint": "/v2/users",
                        "sync_mode": "full_refresh_overwrite"
                    },
                    "workspaces": {
                        "enabled": True,
                        "endpoint": "/v2/workspaces",
                        "sync_mode": "full_refresh_overwrite"
                    }
                },
                
                # API rate limiting and retry configuration
                "api_rate_limit": 2.5,  # requests per second
                "api_timeout": 30,
                "retry_attempts": 3,
                "retry_backoff_factor": 2,
                
                # Data filtering and transformation
                "call_types": self.gong_config.call_types,
                "include_internal_calls": False,
                "include_recorded_calls_only": True,
                "minimum_call_duration_seconds": 60,
                
                # Incremental sync configuration
                "lookback_window_days": 1,  # Re-sync last day to catch updates
                "cursor_field": "metaData.started",
                "dedupe_field": "id"
            },
            "workspaceId": self.airbyte_config.workspace_id,
            "name": "Gong Source - Sophia AI Production"
        }
        
        async with self.session.post(
            f"{self.airbyte_config.base_url}/api/v1/sources/create",
            json=source_config
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"Failed to create Gong source: {response.status} - {error_text}")

    async def monitor_sync_jobs(self) -> Dict[str, Any]:
        """Monitor sync job status and provide health metrics"""
        try:
            # Get recent jobs for the connection
            async with self.session.get(
                f"{self.airbyte_config.base_url}/api/v1/jobs/list",
                params={
                    "connectionId": self.connection_id,
                    "limit": 10
                }
            ) as response:
                if response.status == 200:
                    jobs_data = await response.json()
                    jobs = jobs_data.get("jobs", [])
                    
                    # Analyze job health
                    total_jobs = len(jobs)
                    successful_jobs = sum(1 for job in jobs if job.get("status") == "succeeded")
                    failed_jobs = sum(1 for job in jobs if job.get("status") == "failed")
                    running_jobs = sum(1 for job in jobs if job.get("status") == "running")
                    
                    # Get latest job details
                    latest_job = jobs[0] if jobs else None
                    
                    # Calculate success rate
                    success_rate = (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0
                    
                    return {
                        "connection_id": self.connection_id,
                        "total_jobs": total_jobs,
                        "successful_jobs": successful_jobs,
                        "failed_jobs": failed_jobs,
                        "running_jobs": running_jobs,
                        "success_rate": success_rate,
                        "latest_job": {
                            "job_id": latest_job.get("id") if latest_job else None,
                            "status": latest_job.get("status") if latest_job else None,
                            "started_at": latest_job.get("createdAt") if latest_job else None,
                            "records_synced": latest_job.get("recordsSynced", 0) if latest_job else 0
                        },
                        "health_status": "healthy" if success_rate > 80 else "degraded" if success_rate > 50 else "unhealthy",
                        "monitoring_timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return {"error": f"Failed to fetch jobs: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Failed to monitor sync jobs: {e}")
            return {"error": str(e)}

    async def cleanup(self) -> None:
        """Clean up resources"""
        if self.session:
            await self.session.close()


async def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description="Airbyte Gong Integration Setup")
    parser.add_argument("--mode", choices=["setup", "test", "monitor", "sync"], 
                       default="setup", help="Operation mode")
    parser.add_argument("--airbyte-url", default="http://localhost:8000", 
                       help="Airbyte server URL")
    parser.add_argument("--workspace-id", default="default", 
                       help="Airbyte workspace ID")
    
    args = parser.parse_args()
    
    # Initialize Airbyte configuration
    airbyte_config = AirbyteConfig(
        base_url=args.airbyte_url,
        workspace_id=args.workspace_id
    )
    
    orchestrator = AirbyteGongOrchestrator(airbyte_config)
    
    try:
        await orchestrator.initialize()
        
        if args.mode == "setup":
            result = await orchestrator.setup_complete_pipeline()
            print(json.dumps(result, indent=2))
            
        elif args.mode == "monitor":
            status = await orchestrator.monitor_sync_jobs()
            print(json.dumps(status, indent=2))
            
        elif args.mode == "test":
            test_result = await orchestrator._test_connection()
            print(f"Connection test: {'PASSED' if test_result else 'FAILED'}")
            
        elif args.mode == "sync":
            sync_result = await orchestrator._trigger_sync()
            print(json.dumps(sync_result, indent=2))
            
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)
        
    finally:
        await orchestrator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
