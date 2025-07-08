# MCP V2+ Migration Summary

## Quick Start Guide

This summary provides the essential commands and checkpoints for executing the MCP V2+ migration.

## Pre-Flight Checklist

```bash
# 1. Create feature branch
git checkout -b feature/mcp-v2-consolidation

# 2. Run safety validation
python scripts/migration/validate_migration_safety.py

# 3. Generate inventory
python scripts/migration/inventory_mcp_servers.py

# 4. Allocate ports
python scripts/migration/allocate_ports.py

# 5. Check for import conflicts
python scripts/migration/detect_import_conflicts.py
```

## Migration Execution

### Phase 1: Core Infrastructure (Week 1)
```bash
# Dry run first
python scripts/migration/mcp_v2_migration_orchestrator.py --phase phase_1 --dry-run

# Execute migration
python scripts/migration/mcp_v2_migration_orchestrator.py --phase phase_1

# Servers migrated:
# - snowflake_v2 (port 9001)
# - ai_memory_v2 (port 9002)
# - postgres_v2 (port 9003)
# - redis_cache_v2 (port 9004)
# - infrastructure_management_v2 (port 9005)
# - lambda_labs_cli_v2 (port 9006)
```

### Phase 2: Business Intelligence (Week 2)
```bash
python scripts/migration/mcp_v2_migration_orchestrator.py --phase phase_2

# Servers migrated:
# - salesforce_v2 (port 9011)
# - hubspot_unified_v2 (port 9012)
# - gong_v2 (port 9013)
# - linear_v2 (port 9014)
# - asana_v2 (port 9015)
# - sophia_intelligence_v2 (port 9016)
```

### Phase 3: Communication & AI (Week 3)
```bash
python scripts/migration/mcp_v2_migration_orchestrator.py --phase phase_3

# Servers migrated:
# - slack_v2 (port 9021)
# - notion_v2 (port 9022)
# - github_v2 (port 9023)
# - graphiti_v2 (port 9024)
# - ai_operations_v2 (port 9025)
# - design_intelligence_v2 (port 9026)
# - code_management_v2 (port 9027)
```

### Phase 4: Data Integration (Week 4)
```bash
python scripts/migration/mcp_v2_migration_orchestrator.py --phase phase_4

# Servers migrated:
# - data_collection_v2 (port 9031)
# - playwright_v2 (port 9032)
# - huggingface_ai_v2 (port 9033)
# - estuary_v2 (port 9034)
# - airbyte_v2 (port 9035)
```

## Validation Commands

### After Each Phase
```bash
# Test all V2 servers
python scripts/ci/smoke_test_all_servers.py

# Check health endpoints
curl http://localhost:9001/health  # snowflake_v2
curl http://localhost:9002/health  # ai_memory_v2
# ... etc

# Run integration tests
uv run pytest infrastructure/mcp_servers/*/tests -v

# Check Docker builds
docker compose -f docker/docker-compose.cloud.yml --profile v2-only build
```

### CI/CD Validation
```bash
# Trigger CI for all V2 servers
gh workflow run mcp_unified_ci.yml

# Check deployment preview
pulumi preview -s sophia-ai-production
```

## Key Files to Monitor

1. **Port Registry**: `config/consolidated_mcp_ports.json`
2. **Migration Log**: `reports/migration_report_*.json`
3. **Safety Report**: `reports/migration_safety_report.json`
4. **Import Conflicts**: `reports/import_conflicts.json`

## Rollback Procedures

If issues arise:

```bash
# 1. Stop problematic server
docker stop sophia-{server_name}_v2

# 2. Revert to V1
docker start sophia-{server_name}

# 3. Update port mapping
# Edit config/consolidated_mcp_ports.json

# 4. Revert code if needed
git checkout HEAD~1 infrastructure/mcp_servers/{server_name}_v2
```

## Success Criteria

Each phase is complete when:

- [ ] All servers in phase migrated successfully
- [ ] All tests passing (`uv run pytest`)
- [ ] All health endpoints responding
- [ ] No import conflicts detected
- [ ] CI/CD pipeline green
- [ ] Pulumi preview shows no unexpected changes
- [ ] Performance metrics within acceptable range

## Common Issues & Solutions

### Port Already in Use
```bash
# Find process using port
lsof -i :9001

# Kill process if needed
kill -9 <PID>
```

### Import Conflicts
```bash
# Auto-fix imports
python scripts/migration/fix_imports.py

# Manual fix: Update imports to use shared libraries
# FROM: from mcp-servers.utils import X
# TO: from backend.core.utils import X
```

### Test Failures
```bash
# Run specific test with verbose output
uv run pytest infrastructure/mcp_servers/{server_name}_v2/tests -vvs

# Check test fixtures
uv run pytest --fixtures infrastructure/mcp_servers/{server_name}_v2/tests
```

### Docker Build Issues
```bash
# Build with no cache
docker build --no-cache -t {server_name}_v2 \
  -f infrastructure/mcp_servers/{server_name}_v2/Dockerfile .

# Check build context
docker build --progress=plain -t {server_name}_v2 \
  -f infrastructure/mcp_servers/{server_name}_v2/Dockerfile .
```

## Post-Migration Cleanup

After all phases complete:

```bash
# 1. Archive V1 servers
./scripts/migration/archive_v1_servers.sh

# 2. Update documentation
python scripts/generate_mcp_docs.py

# 3. Clean up old Docker images
docker image prune -a

# 4. Update monitoring dashboards
# Update Grafana dashboard IDs in monitoring configs

# 5. Merge to main
git checkout main
git merge feature/mcp-v2-consolidation
git push origin main
```

## Monitoring Post-Migration

```bash
# Check all services
curl http://localhost:9000/health | jq  # Gateway
for port in {9001..9035}; do
  echo "Checking port $port"
  curl -s http://localhost:$port/health | jq '.status' 2>/dev/null
done

# Check metrics
curl http://localhost:9000/metrics | grep request_seconds

# View logs
docker logs sophia-mcp-gateway -f
```

## Contact for Issues

- Slack: #sophia-ai-migration
- On-call: Check PagerDuty
- Documentation: This guide + detailed plans in `docs/implementation/`

---

Remember: **Take it slow, validate often, and always have a rollback plan!**
