# Unified System - Final Action Plan

**Date:** July 10, 2025  
**Priority:** CRITICAL - Foundation must be fixed before any feature work

## Executive Summary

We have identified that the root cause of all current issues is the broken secrets pipeline. The Pulumi ESC contains placeholder values (`FROM_GITHUB`) instead of real secrets because the sync workflow has never been run successfully.

## Immediate Actions (TODAY)

### 1. Fix Secrets Pipeline (30 minutes)

**Option A: Trigger GitHub Actions (Preferred)**
```bash
# Go to GitHub Actions UI
# Navigate to: https://github.com/ai-cherry/sophia-main/actions/workflows/sync_secrets.yml
# Click "Run workflow" > "Run workflow"
# Monitor the run for success
```

**Option B: Manual Sync (If Actions fail)**
```bash
# Step 1: Set credentials
export GITHUB_TOKEN=<your-github-pat>
export PULUMI_ACCESS_TOKEN=<your-pulumi-access-token>

# Step 2: Make manual script executable
chmod +x scripts/manual_sync_secrets.py

# Step 3: Run manual sync
python scripts/manual_sync_secrets.py

# Step 4: Verify
pulumi env open scoobyjava-org/default/sophia-ai-production
```

### 2. Enable Degraded Mode (1 hour)

Once secrets are synced, implement graceful degradation:

```python
# backend/services/service_factory.py
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ServiceFactory:
    """Factory for creating services with graceful degradation"""
    
    @staticmethod
    def create_memory_service() -> 'UnifiedMemoryService':
        """Create memory service with fallback to degraded mode"""
        from backend.services.unified_memory_service import UnifiedMemoryService
        
        try:
            # Try with Snowflake required
            service = UnifiedMemoryService(require_snowflake=True)
            logger.info("✅ Created memory service with full capabilities")
            return service
        except Exception as e:
            logger.warning(f"⚠️ Creating memory service in degraded mode: {e}")
            # Fall back to degraded mode
            return UnifiedMemoryService(require_snowflake=False)
    
    @staticmethod
    def create_orchestrator() -> 'SophiaUnifiedOrchestrator':
        """Create orchestrator with available services"""
        from backend.services.sophia_unified_orchestrator import SophiaUnifiedOrchestrator
        
        memory_service = ServiceFactory.create_memory_service()
        
        # Create orchestrator with degraded mode awareness
        orchestrator = SophiaUnifiedOrchestrator()
        orchestrator.memory_service = memory_service
        orchestrator.degraded_mode = memory_service.degraded_mode
        
        return orchestrator
```

### 3. Test the System (30 minutes)

```bash
# Step 1: Set environment
export PULUMI_ORG=scoobyjava-org
export ENVIRONMENT=prod

# Step 2: Start backend
python backend/app/unified_chat_backend.py

# Step 3: Run tests
python scripts/test_v4_orchestrator_integration.py

# Step 4: Test frontend
cd frontend
npm start
```

## This Week Actions

### Day 1: Fix Syntax-Blocked Files

Files to fix:
1. `sophia_workflow_runner.py`
2. `snowflake_config_manager.py`
3. `enhanced_snowflake_config.py`
4. Gong ETL scripts

```bash
# Use ruff to auto-fix what we can
ruff check --fix backend/
ruff format backend/

# Manually fix remaining syntax errors
# Then re-run the codemod
python scripts/fix_remaining_getenv.py
```

### Day 2: Implement Service Factory Pattern

1. Create `backend/services/service_factory.py` (code above)
2. Update `backend/app/unified_chat_backend.py`:
```python
from backend.services.service_factory import ServiceFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize with graceful degradation"""
    
    # Create services with fallbacks
    orchestrator = ServiceFactory.create_orchestrator()
    
    # Report capabilities
    if orchestrator.degraded_mode:
        logger.warning("🟡 Running in degraded mode - limited capabilities")
    else:
        logger.info("🟢 Running with full capabilities")
    
    app.state.orchestrator = orchestrator
    yield
```

### Day 3: Create Unified Dashboard

1. Create `frontend/src/components/UnifiedDashboard.tsx`:
```typescript
import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { UnifiedChatDashboard } from './UnifiedChatDashboard';
import { ProjectsDashboard } from './ProjectsDashboard';
import { SalesIntelligence } from './SalesIntelligence';

export const UnifiedDashboard: React.FC = () => {
  return (
    <div className="w-full h-screen">
      <Tabs defaultValue="chat" className="w-full h-full">
        <TabsList>
          <TabsTrigger value="chat">Unified Chat</TabsTrigger>
          <TabsTrigger value="projects">Projects & OKRs</TabsTrigger>
          <TabsTrigger value="sales">Sales Intelligence</TabsTrigger>
          <TabsTrigger value="executive">Executive Dashboard</TabsTrigger>
        </TabsList>
        
        <TabsContent value="chat" className="h-full">
          <UnifiedChatDashboard />
        </TabsContent>
        
        <TabsContent value="projects">
          <ProjectsDashboard />
        </TabsContent>
        
        <TabsContent value="sales">
          <SalesIntelligence />
        </TabsContent>
        
        <TabsContent value="executive">
          <ExecutiveDashboard />
        </TabsContent>
      </Tabs>
    </div>
  );
};
```

### Day 4-5: Testing & Documentation

1. Create integration tests for degraded mode
2. Update documentation to reflect actual architecture
3. Create developer onboarding guide

## Validation Checklist

- [ ] GitHub → Pulumi ESC sync successful
- [ ] Backend starts without Snowflake credentials
- [ ] Frontend connects to v4 API endpoints
- [ ] Degraded mode provides basic chat functionality
- [ ] System reports available capabilities
- [ ] No hardcoded credentials or placeholders
- [ ] Documentation reflects reality

## Long-term Improvements

1. **Automated Secret Rotation** (Week 2)
   - Implement secret rotation workflow
   - Add expiration monitoring

2. **Enhanced Monitoring** (Week 3)
   - Add capability dashboard
   - Service health monitoring
   - Degraded mode alerts

3. **Progressive Enhancement** (Week 4)
   - Dynamic service discovery
   - Feature flags for capabilities
   - Graceful feature degradation

## Success Metrics

- Time to start backend: < 30 seconds
- Services available in degraded mode: > 50%
- Test coverage including degraded mode: > 80%
- Zero hardcoded secrets or placeholders
- All developers can run system locally

## Conclusion

The path forward is clear:
1. Fix the secrets pipeline (TODAY)
2. Enable degraded mode (TODAY)
3. Build on stable foundation (THIS WEEK)

No more workarounds, no more placeholders - just a properly architected system that degrades gracefully when services are unavailable. 