# Comprehensive Remediation Plan for Sophia AI
Date: July 4, 2025

## Executive Summary

This plan addresses critical architectural drift, documentation chaos, and the vision-reality gap in the Sophia AI project. We will execute a 4-phase remediation over 15 days, followed by ongoing governance measures to prevent future drift.

## Critical Findings Summary

1. **Documentation Chaos**: 75+ planning documents creating conflicting guidance
2. **Architecture Gap**: System Handbook describes Phoenix architecture; reality is minimal FastAPI with mocks
3. **Backend Complexity**: 28 directories in backend/ with overlapping responsibilities
4. **Tool Proliferation**: 50+ dependencies, multiple vector DBs, unused MCP servers

## Phase 1: Documentation Unification (Days 1-2)

### Day 1: Document Audit & Triage

**Morning (4 hours)**
1. Create `/docs/archive/2025-07-cleanup/` directory
2. Inventory all 75+ documents in `/docs/`
3. Categorize each document:
   - **KEEP**: Core operational documents (max 5)
   - **ARCHIVE**: Historical/superseded documents
   - **DELETE**: Truly obsolete/duplicate content

**Afternoon (4 hours)**
1. Execute document moves:
   ```bash
   # Archive superseded plans
   mv docs/*_PLAN.md docs/archive/2025-07-cleanup/plans/
   mv docs/*_STATUS*.md docs/archive/2025-07-cleanup/status/
   mv docs/*_COMPLETE*.md docs/archive/2025-07-cleanup/completed/
   ```

2. Create `docs/archive/2025-07-cleanup/INDEX.md` documenting:
   - What was archived and why
   - Key decisions from archived docs
   - Migration to new structure

### Day 2: Documentation Consolidation

**Morning (4 hours)**
1. Retain only these core documents:
   - `00_SOPHIA_AI_SYSTEM_HANDBOOK.md` (authoritative architecture)
   - `API_DOCUMENTATION.md` (current API specs)
   - `DEPLOYMENT_CHECKLIST.md` (operational procedures)
   - `APPLICATION_STRUCTURE.md` (current app structure)
   - `DEVELOPMENT_QUICKSTART.md` (new - to be created)

2. Create `DEVELOPMENT_QUICKSTART.md`:
   ```markdown
   # Sophia AI Development Quickstart

   ## Prerequisites
   - Python 3.12+
   - UV package manager
   - Docker Desktop
   - Snowflake account

   ## Setup (5 minutes)
   1. Clone: `git clone https://github.com/ai-cherry/sophia-main.git`
   2. Install: `uv pip install -e .`
   3. Configure: `cp .env.example .env` and add credentials
   4. Run: `uvicorn backend.app.app:app --reload`

   ## Architecture Overview
   See System Handbook section 3

   ## Common Tasks
   - Add endpoint: See API_DOCUMENTATION.md
   - Deploy: See DEPLOYMENT_CHECKLIST.md
   ```

**Afternoon (4 hours)**
1. Update System Handbook with:
   - Documentation governance section
   - ADR (Architecture Decision Record) template
   - Document lifecycle process

2. Create `.github/CODEOWNERS` for documentation:
   ```
   # Documentation ownership
   /docs/00_SOPHIA_AI_SYSTEM_HANDBOOK.md @lead-architect @cto
   /docs/API_DOCUMENTATION.md @backend-lead
   /docs/DEPLOYMENT_CHECKLIST.md @devops-lead
   ```

## Phase 2: Backend Architecture Alignment (Days 3-7)

### Day 3: Backend Structure Consolidation

**Morning (4 hours)**
1. Map current 28 directories to new 5-module structure:
   ```
   Current → Target Mapping:
   /api/, /presentation/, /application/ → /api/
   /services/, /domain/, /agents/ → /services/
   /integrations/, /mcp_servers/ → /integrations/
   /core/, /utils/, /security/ → /core/
   /database/, /snowflake_setup/ → /database/

   Archive/Delete:
   /rag/, /etl/, /websocket/, /n8n_bridge/ → /archive/legacy/
   /prompts/, /orchestration/, /monitoring/ → merge into relevant modules
   ```

2. Create migration script:
   ```python
   # scripts/consolidate_backend_structure.py
   import shutil
   import os

   MIGRATIONS = {
       'backend/presentation': 'backend/api/routes',
       'backend/application': 'backend/api/handlers',
       'backend/domain': 'backend/services/domain',
       # ... etc
   }

   def migrate_structure():
       for old, new in MIGRATIONS.items():
           if os.path.exists(old):
               os.makedirs(new, exist_ok=True)
               shutil.move(old, new)
   ```

**Afternoon (4 hours)**
1. Execute structure migration
2. Update all imports in moved files
3. Run tests to ensure nothing broke
4. Update `backend/__init__.py` with new structure

### Day 4-5: Implement Phoenix Core Architecture

**Day 4 Morning (4 hours)**
1. Implement real `UnifiedChatService`:
   ```python
   # backend/services/unified_chat_service.py
   class UnifiedChatService:
       def __init__(self):
           self.snowflake = SnowflakeCortexService()
           self.mcp_gateway = MCPGatewayService()
           self.memory = ConversationMemoryService()

       async def process_message(self, message: ChatMessage) -> ChatResponse:
           # 1. Classify intent
           intent = await self.snowflake.classify_intent(message.content)

           # 2. Retrieve context
           context = await self.snowflake.retrieve_context(
               message.content,
               message.user_id
           )

           # 3. Route to appropriate service
           if intent.requires_tool:
               response = await self.mcp_gateway.execute(
                   intent.tool,
                   message,
                   context
               )
           else:
               response = await self.snowflake.generate_response(
                   message,
                   context
               )

           # 4. Store in memory
           await self.memory.store(message, response)

           return response
   ```

**Day 4 Afternoon (4 hours)**
1. Replace mock responses in `backend/app/app.py`
2. Wire up real Snowflake Cortex integration
3. Test end-to-end chat flow

**Day 5 Morning (4 hours)**
1. Implement MCP Gateway Service:
   ```python
   # backend/services/mcp_gateway_service.py
   class MCPGatewayService:
       def __init__(self):
           self.servers = self._discover_servers()
           self.router = CapabilityRouter()

       async def execute(self, tool: str, message: ChatMessage, context: dict):
           # Route to appropriate MCP server
           server = self.router.get_server_for_capability(tool)
           return await server.execute(message, context)
   ```

**Day 5 Afternoon (4 hours)**
1. Validate each MCP server configuration
2. Remove unused MCP servers
3. Create health check endpoint for MCP servers

### Day 6-7: Database and Integration Layer

**Day 6 (8 hours)**
1. Consolidate database operations:
   ```python
   # backend/database/snowflake_manager.py
   class SnowflakeManager:
       """Single point of entry for all Snowflake operations"""

       def __init__(self):
           self.connector = SnowflakeConnector()
           self.cortex = SnowflakeCortexService()

       async def execute_query(self, query: str):
           # Centralized query execution with logging
           pass

       async def store_conversation(self, conversation: dict):
           # Store chat history in Snowflake
           pass
   ```

2. Remove redundant database connectors
3. Standardize on Snowflake for all data operations

**Day 7 (8 hours)**
1. Clean up integrations:
   - Keep: HubSpot, Gong, Slack (actively used)
   - Remove: Unused webhook handlers
   - Consolidate: Multiple notification services

2. Create integration health dashboard

## Phase 3: Tool & Dependency Consolidation (Days 8-10)

### Day 8: Dependency Audit

**Morning (4 hours)**
1. Run comprehensive dependency analysis:
   ```bash
   # Create dependency usage report
   pip-audit
   vulture backend/ --min-confidence 80

   # Find unused imports
   autoflake --check --remove-all-unused-imports -r backend/
   ```

2. Create dependency removal list:
   - Remove: pinecone-client, weaviate-client, chromadb
   - Remove: Unused AI frameworks
   - Keep: Core dependencies only

**Afternoon (4 hours)**
1. Update `pyproject.toml` with cleaned dependencies
2. Run `uv lock --refresh`
3. Test all functionality

### Day 9: Docker and Deployment Cleanup

**Morning (4 hours)**
1. Consolidate to single Dockerfile:
   ```dockerfile
   # Dockerfile
   FROM python:3.12-slim

   WORKDIR /app

   # Install UV
   RUN pip install uv

   # Copy and install dependencies
   COPY pyproject.toml uv.lock ./
   RUN uv pip install --system -e .

   # Copy application
   COPY backend/ ./backend/

   # Run
   CMD ["uvicorn", "backend.app.app:app", "--host", "0.0.0.0"]
   ```

2. Single docker-compose.yml:
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       env_file: .env
       depends_on:
         - redis

     redis:
       image: redis:alpine
       ports:
         - "6379:6379"
   ```

**Afternoon (4 hours)**
1. Remove all other Dockerfiles and compose files
2. Update deployment documentation
3. Test complete deployment flow

### Day 10: MCP Server Validation

**Full Day (8 hours)**
1. Create MCP validation script:
   ```python
   # scripts/validate_mcp_servers.py
   async def validate_all_servers():
       results = {}
       for server in MCP_SERVERS:
           try:
               health = await server.health_check()
               capabilities = await server.list_capabilities()
               results[server.name] = {
                   'healthy': health.status == 'ok',
                   'capabilities': len(capabilities),
                   'used': check_usage_in_codebase(server.name)
               }
           except Exception as e:
               results[server.name] = {'error': str(e)}

       return results
   ```

2. Remove unused MCP servers
3. Document remaining MCP servers and their purposes

## Phase 4: Reality Check & Stabilization (Days 11-15)

### Day 11-12: End-to-End Testing

**Day 11 (8 hours)**
1. Write comprehensive integration tests:
   ```python
   # tests/integration/test_chat_flow.py
   async def test_complete_chat_flow():
       # Test intent classification
       # Test context retrieval
       # Test response generation
       # Test memory storage
       # Test streaming responses
   ```

2. Test all API endpoints
3. Test MCP server integrations

**Day 12 (8 hours)**
1. Performance testing
2. Load testing with realistic data
3. Security scanning

### Day 13-14: Frontend Integration

**Day 13 (8 hours)**
1. Connect frontend to real backend endpoints
2. Remove all mock data from frontend
3. Test role-based access control

**Day 14 (8 hours)**
1. Full user acceptance testing
2. Fix any integration issues
3. Update user documentation

### Day 15: Deployment and Documentation

**Morning (4 hours)**
1. Execute full production deployment
2. Monitor all health endpoints
3. Verify MCP server connectivity

**Afternoon (4 hours)**
1. Create final status report
2. Update System Handbook with current state
3. Team handoff meeting

## Ongoing Governance & Future-Proofing

### 1. Documentation Governance

**ADR Process**
- Every architectural change requires an ADR
- Template location: `/docs/architecture/decisions/template.md`
- Review in weekly architecture meeting

**Documentation Rules**
1. No new "PLAN" documents without archiving old ones
2. Maximum 10 active documents in `/docs/` root
3. Quarterly documentation review and cleanup

### 2. Code Structure Governance

**CI/CD Checks**
```yaml
# .github/workflows/structure-check.yml
- name: Check Backend Structure
  run: |
    # Fail if new top-level directories added
    ALLOWED_DIRS="api services integrations core database"
    for dir in backend/*/; do
      basename=$(basename "$dir")
      if [[ ! " $ALLOWED_DIRS " =~ " $basename " ]]; then
        echo "Unauthorized directory: $dir"
        exit 1
      fi
    done
```

**Import Rules**
- No circular imports between modules
- Services can't import from API layer
- Core can't import from any other module

### 3. Dependency Management

**Monthly Audit**
```bash
# scripts/monthly_dependency_audit.sh
#!/bin/bash
echo "=== Dependency Audit $(date) ==="
pip-audit
uv pip list | wc -l
vulture backend/ --min-confidence 80
```

**Approval Process**
- New dependencies require architecture review
- Must justify why existing tools can't solve the problem
- Document in ADR

### 4. Architecture Review Board

**Weekly Meetings**
- Every Tuesday, 2pm
- Review proposed changes
- Approve new patterns
- Update System Handbook

**Participants**
- Lead Architect
- Backend Lead
- Frontend Lead
- DevOps Lead

### 5. Health Monitoring

**Automated Checks**
```python
# scripts/nightly_health_check.py
async def run_health_checks():
    checks = [
        check_unused_imports(),
        check_documentation_references(),
        check_mcp_server_health(),
        check_dependency_vulnerabilities(),
        check_code_complexity()
    ]

    results = await asyncio.gather(*checks)

    if any(r.has_issues for r in results):
        send_alert_to_team(results)
```

**Metrics Dashboard**
- Documentation freshness
- Code complexity trends
- Dependency count
- Test coverage
- MCP server uptime

## Success Metrics

### Phase 1 (Documentation)
- ✓ Reduce from 75+ to ≤10 active documents
- ✓ All documents have clear ownership
- ✓ No conflicting guidance

### Phase 2 (Architecture)
- ✓ Backend reduced from 28 to 5 core directories
- ✓ Phoenix architecture implemented
- ✓ No mock responses in production

### Phase 3 (Dependencies)
- ✓ Dependencies reduced by 50%
- ✓ Single vector DB (Snowflake Cortex)
- ✓ All MCP servers validated and used

### Phase 4 (Integration)
- ✓ All tests passing
- ✓ Frontend connected to real backend
- ✓ Successfully deployed to production

## Risk Mitigation

### Technical Risks
1. **Data Loss During Migration**
   - Mitigation: Complete backups before each phase
   - Rollback plan for each change

2. **Breaking Changes**
   - Mitigation: Comprehensive test suite
   - Gradual migration with feature flags

3. **Performance Degradation**
   - Mitigation: Performance benchmarks before/after
   - Load testing at each phase

### Organizational Risks
1. **Team Resistance**
   - Mitigation: Clear communication of benefits
   - Involve team in planning

2. **Scope Creep**
   - Mitigation: Strict phase boundaries
   - Change requests go through ARB

3. **Knowledge Loss**
   - Mitigation: Document all decisions
   - Pair programming during changes

## Timeline Summary

- **Days 1-2**: Documentation Unification
- **Days 3-7**: Backend Architecture Alignment
- **Days 8-10**: Tool & Dependency Consolidation
- **Days 11-15**: Reality Check & Stabilization
- **Ongoing**: Governance & Monitoring

Total Duration: 15 working days (3 weeks)

## Next Steps

1. Get stakeholder approval for this plan
2. Assign team members to each phase
3. Set up daily standup for remediation period
4. Create shared dashboard for progress tracking
5. Schedule architecture review board meetings

---

This remediation plan addresses all critical issues while establishing governance to prevent future drift. The key is not just fixing current problems but creating sustainable practices that keep the codebase aligned with our vision.
