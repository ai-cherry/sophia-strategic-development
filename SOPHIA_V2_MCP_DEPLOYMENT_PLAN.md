# Sophia AI V2 MCP Server Deployment Plan

**Date:** January 14, 2025
**Scope:** Deploy 10 v2 MCP servers + supporting infrastructure
**Target:** Lambda Labs (192.222.58.232) via Docker Swarm
**Duration:** 3-4 hours (automated execution)

## 🎯 Executive Summary

Deploy 10 production-ready v2 MCP servers using our enhanced Docker Swarm infrastructure, with zero manual intervention following the Golden Rule of Deployment.

## 📋 Pre-Deployment Checklist

### Code Review & Validation
```bash
# Run from GitHub Actions only
python scripts/validate_environment.py
python scripts/mcp_version_validator.py
python scripts/optimize_swarm_resources.py --analyze
```

### V2 MCP Servers to Deploy
1. `ai_memory_v2` - Enhanced memory with Redis L1 cache
2. `gong_v2` - Gong integration with memory support
3. `snowflake_v2` - Snowflake operations with Cortex AI
4. `slack_v2` - Slack analysis with sentiment
5. `notion_v2` - Notion knowledge management
6. `linear_v2` - Linear project management
7. `github_v2` - GitHub integration
8. `codacy_v2` - Code quality analysis
9. `asana_v2` - Asana project tracking
10. `perplexity_v2` - Perplexity search integration

## 🚀 Phase 1: Build & Push Images (30 min)

### GitHub Action: `.github/workflows/build_v2_mcp_servers.yml`
```yaml
name: Build V2 MCP Servers
on:
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - 'infrastructure/mcp_servers/*_v2/**'

jobs:
  build-matrix:
    strategy:
      matrix:
        server: [ai_memory, gong, snowflake, slack, notion,
                linear, github, codacy, asana, perplexity]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build & Push
        env:
          DOCKER_REGISTRY: scoobyjava15
        run: |
          IMAGE_TAG="${DOCKER_REGISTRY}/sophia-${matrix.server}-v2:${GITHUB_SHA::7}"
          docker build \
            --build-arg ENVIRONMENT=prod \
            --build-arg PULUMI_ORG=scoobyjava-org \
            -f infrastructure/mcp_servers/${matrix.server}_v2/Dockerfile \
            -t $IMAGE_TAG \
            infrastructure/mcp_servers/${matrix.server}_v2/

          echo "${{ secrets.DOCKER_HUB_TOKEN }}" | docker login -u "${{ secrets.DOCKER_HUB_USERNAME }}" --password-stdin
          docker push $IMAGE_TAG

          # Save tag for deployment
          echo "${matrix.server}=$IMAGE_TAG" >> $GITHUB_OUTPUT
```

## 🚀 Phase 2: Deploy to Lambda Labs (45 min)

### Enhanced Docker Compose: `docker-compose.cloud.v2.yml`
```yaml
version: "3.8"

x-v2-defaults: &v2-defaults
  deploy:
    mode: replicated
    replicas: 2
    update_config:
      parallelism: 1
      delay: 30s
      failure_action: rollback
    restart_policy:
      condition: on-failure
      max_attempts: 5
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
      reservations:
        cpus: '1.0'
        memory: 2G
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 60s
  networks:
    - mcp-net
    - monitoring
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
      labels: "service,environment"

services:
  ai_memory_v2:
    <<: *v2-defaults
    image: ${AI_MEMORY_V2_IMAGE}
    ports:
      - "9010:8000"
    environment:
      ENVIRONMENT: prod
      REDIS_URL: redis://redis:6379/0
      SNOWFLAKE_WAREHOUSE: SOPHIA_AI_COMPUTE_WH
    secrets:
      - snowflake_creds
      - openai_key

  gong_v2:
    <<: *v2-defaults
    image: ${GONG_V2_IMAGE}
    ports:
      - "9011:8000"
    environment:
      ENVIRONMENT: prod
      MEMORY_SERVICE_URL: http://ai_memory_v2:8000
    secrets:
      - gong_api_key

  # ... similar for other 8 services ...

networks:
  mcp-net:
    driver: overlay
    encrypted: true
  monitoring:
    external: true

secrets:
  snowflake_creds:
    external: true
  openai_key:
    external: true
  gong_api_key:
    external: true
```

### Deployment Script: `scripts/deploy_v2_mcp_stack.sh`
```bash
#!/bin/bash
set -euo pipefail

# Source deployment functions
source scripts/deploy_enhanced.sh

# Deploy with monitoring
deploy_stack "sophia-v2-mcp" "docker-compose.cloud.v2.yml" \
  --with-monitoring \
  --health-check-timeout 300 \
  --rollback-on-failure
```

## 🚀 Phase 3: Infrastructure Services (30 min)

### Snowflake Setup
```sql
-- Apply via Pulumi Snowflake provider
CREATE WAREHOUSE IF NOT EXISTS SOPHIA_AI_V2_WH
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_PROD.MCP_V2;

-- Grant permissions
GRANT USAGE ON WAREHOUSE SOPHIA_AI_V2_WH TO ROLE SOPHIA_MCP_ROLE;
GRANT ALL ON SCHEMA SOPHIA_AI_PROD.MCP_V2 TO ROLE SOPHIA_MCP_ROLE;
```

### Estuary Flows
```bash
# Deploy via GitHub Action
flowctl apply --source config/estuary/v2_flows.yaml --yes
```

## 🚀 Phase 4: Gateway & Routing (20 min)

### Update MCP Gateway Configuration
```json
{
  "servers": {
    "ai_memory_v2": {
      "url": "http://ai_memory_v2:8000",
      "port": 9010,
      "healthcheck": "/health",
      "version": "2.0.0"
    },
    // ... other servers
  }
}
```

### Nginx Update for External Access
```nginx
upstream mcp_v2_servers {
    server ai_memory_v2:8000 weight=10;
    server gong_v2:8000 weight=5;
    # ... other servers
}
```

## 🚀 Phase 5: Monitoring & Alerting (20 min)

### Deploy Enhanced Monitoring Stack
```bash
docker stack deploy -c monitoring-stack.yml monitoring
```

### Grafana Dashboard Import
```bash
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @configs/grafana_v2_mcp_dashboard.json
```

## 🚀 Phase 6: Validation & Testing (30 min)

### Automated Validation Suite
```python
# scripts/validate_v2_deployment.py
import asyncio
from typing import Dict, List

async def validate_deployment():
    servers = [
        ("ai_memory_v2", 9010),
        ("gong_v2", 9011),
        # ... other servers
    ]

    results = {}
    for server, port in servers:
        # Health check
        health = await check_health(f"http://192.222.58.232:{port}/health")

        # Performance test
        perf = await test_performance(f"http://192.222.58.232:{port}/tools")

        # Integration test
        integration = await test_integration(server)

        results[server] = {
            "health": health,
            "performance": perf,
            "integration": integration
        }

    return results
```

## 🚀 Phase 7: Frontend Integration (15 min)

### Update Vercel Environment
```bash
# Via GitHub Action only
vercel env add MCP_GATEWAY_URL https://192.222.58.232:8080 production
vercel env add MCP_V2_ENABLED true production
```

### Deploy Frontend
```bash
vercel deploy --prod
```

## 📊 Success Metrics

### Performance Targets
- **Response Time:** p95 < 200ms
- **Availability:** 99.9% uptime
- **Resource Usage:** < 60% CPU, < 70% memory
- **Error Rate:** < 0.1%

### Monitoring Alerts
- Service down > 2 minutes
- Response time > 500ms for 5 minutes
- Memory usage > 80%
- Error rate > 1%

## 🔧 Rollback Plan

```bash
# Automatic rollback via Docker Swarm
docker service rollback sophia-v2-mcp_ai_memory_v2

# Full stack rollback
docker stack rm sophia-v2-mcp
docker stack deploy -c docker-compose.cloud.previous.yml sophia-mcp
```

## 📝 Post-Deployment Tasks

1. **Update Documentation**
   ```bash
   python scripts/generate_deployment_docs.py --version v2
   ```

2. **Performance Report**
   ```bash
   python scripts/generate_performance_report.py --duration 24h
   ```

3. **Security Scan**
   ```bash
   docker run --rm aquasec/trivy image scoobyjava15/sophia-ai-memory-v2:latest
   ```

## 🚨 Important Notes

1. **NO LOCAL DEPLOYMENT** - Everything via GitHub Actions
2. **NO MANUAL SECRETS** - All via Pulumi ESC
3. **PRODUCTION FIRST** - Default environment is always prod
4. **AUTOMATED ROLLBACK** - On any failure
5. **COMPREHENSIVE MONITORING** - Every service tracked

## 🎯 Execution Timeline

| Phase | Duration | Automated | Manual Steps |
|-------|----------|-----------|--------------|
| Pre-checks | 10 min | ✅ | None |
| Build & Push | 30 min | ✅ | Trigger workflow |
| Deploy Stack | 45 min | ✅ | None |
| Infrastructure | 30 min | ✅ | None |
| Gateway | 20 min | ✅ | None |
| Monitoring | 20 min | ✅ | None |
| Validation | 30 min | ✅ | None |
| Frontend | 15 min | ✅ | None |
| **Total** | **3.5 hours** | **100%** | **1 trigger** |

## 🚀 Start Deployment

```bash
# From GitHub UI or CLI
gh workflow run deploy_v2_mcp_servers.yml
```

This plan leverages our enhanced Docker Swarm deployment tools and follows all established patterns for zero-manual-intervention deployment.
