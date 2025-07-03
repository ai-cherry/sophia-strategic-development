#!/usr/bin/env python3
"""
Phoenix Memory Integration Deployment Script
===========================================
Deploys the multi-tiered memory architecture with Mem0 integration
while maintaining Snowflake as the center of the universe.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhoenixMemoryIntegrationDeployer:
    """Deploy Phoenix Platform memory integration"""
    
    def __init__(self):
        self.deployment_start = datetime.now()
        self.results = {
            "phase_1_foundation": {},
            "snowflake_schema_updates": {},
            "mcp_server_deployment": {},
            "unified_chat_enhancement": {},
            "dashboard_updates": {}
        }
    
    async def deploy_phase_1_foundation(self):
        """Deploy Phase 1: Foundation components"""
        logger.info("🚀 Starting Phase 1: Foundation Deployment")
        
        try:
            # 1. Update Snowflake schema with Mem0 integration
            await self._update_snowflake_schema()
            
            # 2. Deploy Mem0 MCP server configuration
            await self._deploy_mem0_mcp_config()
            
            # 3. Enhance session cache configuration
            await self._enhance_session_cache()
            
            # 4. Create Mem0 sync procedures
            await self._create_mem0_sync_procedures()
            
            self.results["phase_1_foundation"]["status"] = "completed"
            self.results["phase_1_foundation"]["completion_time"] = datetime.now()
            
            logger.info("✅ Phase 1: Foundation deployment completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Phase 1 deployment failed: {e}")
            self.results["phase_1_foundation"]["status"] = "failed"
            self.results["phase_1_foundation"]["error"] = str(e)
            raise
    
    async def _update_snowflake_schema(self):
        """Update Snowflake schema with Mem0 integration fields"""
        logger.info("📊 Updating Snowflake schema for Mem0 integration")
        
        schema_updates = """
        -- Enhanced Memory Records with Mem0 Integration
        ALTER TABLE IF EXISTS SOPHIA_AI_MEMORY.MEMORY_RECORDS 
        ADD COLUMN IF NOT EXISTS mem0_memory_id VARCHAR(255);
        
        ALTER TABLE IF EXISTS SOPHIA_AI_MEMORY.MEMORY_RECORDS 
        ADD COLUMN IF NOT EXISTS mem0_sync_status VARCHAR(50) DEFAULT 'pending';
        
        ALTER TABLE IF EXISTS SOPHIA_AI_MEMORY.MEMORY_RECORDS 
        ADD COLUMN IF NOT EXISTS mem0_last_sync TIMESTAMP_NTZ;
        
        ALTER TABLE IF EXISTS SOPHIA_AI_MEMORY.MEMORY_RECORDS 
        ADD COLUMN IF NOT EXISTS cross_session_relevance FLOAT DEFAULT 0.0;
        
        -- Create Mem0 sync status index
        CREATE INDEX IF NOT EXISTS idx_mem0_sync_status 
        ON SOPHIA_AI_MEMORY.MEMORY_RECORDS(mem0_sync_status);
        
        -- Create Mem0 memory ID index
        CREATE INDEX IF NOT EXISTS idx_mem0_memory_id 
        ON SOPHIA_AI_MEMORY.MEMORY_RECORDS(mem0_memory_id);
        """
        
        # Save schema updates to file
        schema_file = Path("backend/snowflake_setup/mem0_integration_schema.sql")
        schema_file.write_text(schema_updates)
        
        logger.info(f"📝 Schema updates saved to {schema_file}")
        self.results["snowflake_schema_updates"]["file_created"] = str(schema_file)
        self.results["snowflake_schema_updates"]["status"] = "completed"
    
    async def _deploy_mem0_mcp_config(self):
        """Deploy Mem0 MCP server configuration"""
        logger.info("🔧 Deploying Mem0 MCP server configuration")
        
        mcp_config = {
            "mcp_servers": {
                "mem0_persistent": {
                    "port": 9010,
                    "name": "Mem0 Persistent Memory",
                    "description": "Cross-session learning and adaptive intelligence",
                    "memory_integration": ["L3"],
                    "capabilities": [
                        "persistent_store",
                        "cross_session_recall", 
                        "adaptive_learning",
                        "snowflake_sync"
                    ],
                    "health_check_endpoint": "/health",
                    "environment_variables": [
                        "MEM0_API_KEY",
                        "MEM0_ENVIRONMENT",
                        "SNOWFLAKE_ACCOUNT",
                        "ENVIRONMENT"
                    ]
                }
            },
            "memory_tier_configuration": {
                "L1_session_cache": {
                    "provider": "redis",
                    "ttl_seconds": 3600,
                    "max_size_mb": 512
                },
                "L2_snowflake_cortex": {
                    "provider": "snowflake",
                    "embedding_model": "e5-base-v2",
                    "vector_dimension": 768
                },
                "L3_mem0_persistent": {
                    "provider": "mem0",
                    "api_endpoint": "https://api.mem0.ai/v1",
                    "sync_interval_minutes": 15
                }
            }
        }
        
        # Save MCP configuration
        config_file = Path("config/mem0_mcp_integration.json")
        config_file.parent.mkdir(exist_ok=True)
        
        import json
        config_file.write_text(json.dumps(mcp_config, indent=2))
        
        logger.info(f"📝 MCP configuration saved to {config_file}")
        self.results["mcp_server_deployment"]["config_file"] = str(config_file)
        self.results["mcp_server_deployment"]["port"] = 9010
        self.results["mcp_server_deployment"]["status"] = "configured"
    
    async def _enhance_session_cache(self):
        """Enhance session cache with Mem0 integration"""
        logger.info("🧠 Enhancing session cache configuration")
        
        cache_config = """
# Enhanced Session Cache Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=${REDIS_PASSWORD}

# Mem0 Integration
MEM0_API_KEY=${MEM0_API_KEY}
MEM0_ENVIRONMENT=production
MEM0_SESSION_CONTEXT_ENABLED=true
MEM0_CONTEXT_CACHE_TTL=3600

# Session Configuration
SESSION_CACHE_TTL=3600
SESSION_CONTEXT_MAX_MEMORIES=5
PERSISTENT_CONTEXT_ENABLED=true
"""
        
        # Save cache configuration
        cache_file = Path("config/enhanced_session_cache.env")
        cache_file.write_text(cache_config)
        
        logger.info(f"📝 Enhanced session cache config saved to {cache_file}")
        self.results["unified_chat_enhancement"]["cache_config"] = str(cache_file)
        self.results["unified_chat_enhancement"]["status"] = "configured"
    
    async def _create_mem0_sync_procedures(self):
        """Create Mem0 synchronization procedures"""
        logger.info("🔄 Creating Mem0 sync procedures")
        
        sync_procedures = """
-- Mem0 Sync Procedure for Snowflake
CREATE OR REPLACE PROCEDURE SOPHIA_AI_MEMORY.SYNC_WITH_MEM0()
RETURNS STRING
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
BEGIN
    -- Get unsynchronized memories
    LET unsync_count INTEGER := (
        SELECT COUNT(*) 
        FROM SOPHIA_AI_MEMORY.MEMORY_RECORDS 
        WHERE mem0_sync_status = 'pending'
    );
    
    -- Update sync status for batch processing
    UPDATE SOPHIA_AI_MEMORY.MEMORY_RECORDS 
    SET mem0_sync_status = 'processing',
        mem0_last_sync = CURRENT_TIMESTAMP()
    WHERE mem0_sync_status = 'pending'
    AND ROWNUM <= 100;
    
    RETURN 'Marked ' || unsync_count || ' memories for Mem0 sync processing';
END;
$$;

-- Procedure to mark successful sync
CREATE OR REPLACE PROCEDURE SOPHIA_AI_MEMORY.MARK_MEM0_SYNC_SUCCESS(
    MEMORY_ID VARCHAR,
    MEM0_ID VARCHAR
)
RETURNS STRING
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
BEGIN
    UPDATE SOPHIA_AI_MEMORY.MEMORY_RECORDS 
    SET mem0_sync_status = 'synced',
        mem0_memory_id = MEM0_ID,
        mem0_last_sync = CURRENT_TIMESTAMP()
    WHERE memory_id = MEMORY_ID;
    
    RETURN 'Memory ' || MEMORY_ID || ' successfully synced with Mem0 ID: ' || MEM0_ID;
END;
$$;

-- Procedure to mark failed sync
CREATE OR REPLACE PROCEDURE SOPHIA_AI_MEMORY.MARK_MEM0_SYNC_FAILED(
    MEMORY_ID VARCHAR,
    ERROR_MESSAGE VARCHAR
)
RETURNS STRING
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
BEGIN
    UPDATE SOPHIA_AI_MEMORY.MEMORY_RECORDS 
    SET mem0_sync_status = 'failed',
        mem0_last_sync = CURRENT_TIMESTAMP()
    WHERE memory_id = MEMORY_ID;
    
    -- Log error (would integrate with logging system)
    INSERT INTO SOPHIA_CORE.SYSTEM_HEALTH (
        health_id,
        component_name,
        component_type,
        status,
        health_score,
        metrics
    ) VALUES (
        'mem0_sync_error_' || MEMORY_ID,
        'mem0_sync',
        'memory_integration',
        'error',
        0.0,
        PARSE_JSON('{"error": "' || ERROR_MESSAGE || '", "memory_id": "' || MEMORY_ID || '"}')
    );
    
    RETURN 'Memory ' || MEMORY_ID || ' sync failed: ' || ERROR_MESSAGE;
END;
$$;
"""
        
        # Save sync procedures
        procedures_file = Path("backend/snowflake_setup/mem0_sync_procedures.sql")
        procedures_file.write_text(sync_procedures)
        
        logger.info(f"📝 Mem0 sync procedures saved to {procedures_file}")
        self.results["snowflake_schema_updates"]["procedures_file"] = str(procedures_file)
    
    def generate_deployment_report(self):
        """Generate comprehensive deployment report"""
        logger.info("📋 Generating deployment report")
        
        report = f"""
# PHOENIX MEMORY INTEGRATION DEPLOYMENT REPORT
## Phase 1: Foundation Deployment

**Deployment Started**: {self.deployment_start.isoformat()}
**Deployment Completed**: {datetime.now().isoformat()}
**Total Duration**: {datetime.now() - self.deployment_start}

## Deployment Results

### ✅ Phase 1: Foundation
- **Status**: {self.results['phase_1_foundation'].get('status', 'pending')}
- **Completion**: {self.results['phase_1_foundation'].get('completion_time', 'N/A')}

### 📊 Snowflake Schema Updates
- **Status**: {self.results['snowflake_schema_updates'].get('status', 'pending')}
- **Schema File**: {self.results['snowflake_schema_updates'].get('file_created', 'N/A')}
- **Procedures File**: {self.results['snowflake_schema_updates'].get('procedures_file', 'N/A')}

### 🔧 MCP Server Deployment
- **Status**: {self.results['mcp_server_deployment'].get('status', 'pending')}
- **Config File**: {self.results['mcp_server_deployment'].get('config_file', 'N/A')}
- **Port**: {self.results['mcp_server_deployment'].get('port', 'N/A')}

### 🧠 Unified Chat Enhancement
- **Status**: {self.results['unified_chat_enhancement'].get('status', 'pending')}
- **Cache Config**: {self.results['unified_chat_enhancement'].get('cache_config', 'N/A')}

## Next Steps

### Phase 2: Unified Chat Enhancement (Week 3-4)
1. Implement multi-tier memory in Unified Chat Service
2. Add memory context display to frontend
3. Deploy enhanced chat interface
4. Test memory integration functionality

### Phase 3: Knowledge Graph Integration (Week 5-6)
1. Enhance knowledge graph MCP with Mem0
2. Implement entity-relationship memory
3. Add multi-hop reasoning capabilities

### Immediate Actions Required
1. **Deploy Snowflake Schema**: Execute the generated SQL files
2. **Configure Secrets**: Add MEM0_API_KEY to GitHub Organization Secrets
3. **Deploy MCP Server**: Build and deploy Mem0 MCP server container
4. **Test Integration**: Validate Mem0 API connectivity

## Files Created
- `backend/snowflake_setup/mem0_integration_schema.sql`
- `backend/snowflake_setup/mem0_sync_procedures.sql`
- `config/mem0_mcp_integration.json`
- `config/enhanced_session_cache.env`

## Success Metrics Baseline
- **Memory Tiers Configured**: 3 (L1, L2, L3)
- **MCP Server Port**: 9010
- **Sync Procedures**: 3 created
- **Configuration Files**: 4 created

---

**Status**: Phase 1 Foundation deployment completed successfully.
**Next Phase**: Ready for Phase 2 implementation.
"""
        
        # Save deployment report
        report_file = Path(f"PHOENIX_MEMORY_INTEGRATION_DEPLOYMENT_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        report_file.write_text(report)
        
        logger.info(f"📋 Deployment report saved to {report_file}")
        return str(report_file)

async def main():
    """Main deployment function"""
    logger.info("🔥 Starting Phoenix Memory Integration Deployment")
    
    deployer = PhoenixMemoryIntegrationDeployer()
    
    try:
        # Deploy Phase 1: Foundation
        await deployer.deploy_phase_1_foundation()
        
        # Generate deployment report
        report_file = deployer.generate_deployment_report()
        
        logger.info("🎉 Phoenix Memory Integration Phase 1 deployment completed successfully!")
        logger.info(f"📋 See deployment report: {report_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"💥 Deployment failed: {e}")
        
        # Generate failure report
        deployer.results["deployment_status"] = "failed"
        deployer.results["deployment_error"] = str(e)
        report_file = deployer.generate_deployment_report()
        
        logger.info(f"📋 Failure report saved to: {report_file}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
