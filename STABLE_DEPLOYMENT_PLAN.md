# Stable Core Coding Infrastructure Deployment Plan

## Executive Summary

Based on comprehensive infrastructure assessment, we have **4/10 healthy components** with critical gaps in secret management. This plan will systematically fix these issues to achieve stable deployment of core coding services.

## Current Status Analysis

### ✅ Working Components (4/10)
1. **Docker**: Available with Compose support
2. **Snowflake**: Connected (version 9.17.2) 
3. **MCP Servers**: 6/7 critical servers available
4. **Code Protection**: 50+ GitHub workflows, quality tools ready

### ❌ Critical Issues (6/10)
1. **Pulumi ESC**: Missing 4 critical secrets (GitHub, Lambda Labs, Vercel, Estuary)
2. **Kubernetes**: No cluster connection
3. **Lambda Labs**: Missing API credentials  
4. **Vercel**: Missing deployment token
5. **GitHub Integration**: Token missing
6. **Estuary**: No credentials configured

## Multi-Step Deployment Strategy

### Phase 1: Secret Management Foundation (IMMEDIATE - 30 minutes)

#### Step 1.1: Add Missing Secrets to GitHub Organization
```bash
# Go to: https://github.com/organizations/ai-cherry/settings/secrets/actions
# Add these secrets:
GITHUB_TOKEN=<personal_access_token>
LAMBDA_LABS_API_KEY=<lambda_labs_key>  
VERCEL_TOKEN=<vercel_deployment_token>
ESTUARY_ACCESS_TOKEN=<estuary_api_token>
```

#### Step 1.2: Trigger Secret Sync
```bash
# Run GitHub Actions workflow: "Sync Secrets to Pulumi ESC"
# Or manual sync:
python scripts/ci/sync_from_gh_to_pulumi.py
```

#### Step 1.3: Verify Secret Availability
```bash
python scripts/assess_core_infrastructure.py
# Target: 8/10 healthy components
```

### Phase 2: Core MCP Server Deployment (1 hour)

#### Step 2.1: Deploy Core MCP Servers
```bash
# Deploy critical coding infrastructure servers:
python scripts/deploy_core_mcp_servers.py

# Priority order:
# 1. AI Memory MCP Server (port 9000) - Development context
# 2. Codacy MCP Server (port 3008) - Code quality automation  
# 3. GitHub MCP Server (port 9003) - Repository integration
# 4. Linear MCP Server (port 9004) - Project management
```

### Phase 3: Integration Testing (30 minutes)

#### Step 3.1: End-to-End Testing
```bash
# Test all core components:
python scripts/test_core_infrastructure.py

# Manual health checks:
curl http://localhost:8000/health  # API Gateway
curl http://localhost:9000/health  # AI Memory
curl http://localhost:3008/health  # Codacy
curl http://localhost:9003/health  # GitHub
curl http://localhost:9004/health  # Linear
```

## Success Metrics

### Phase 1 Success: Secret Management
- [ ] All 4 missing secrets added to GitHub Organization
- [ ] Pulumi ESC showing 8/10 healthy components
- [ ] All critical API keys accessible via get_config_value()

### Phase 2 Success: MCP Deployment  
- [ ] 4/4 core MCP servers running and healthy
- [ ] All servers responding to health checks
- [ ] MCP orchestration service operational

### Phase 3 Success: Integration
- [ ] 80%+ end-to-end tests passing
- [ ] Code protection automation running
- [ ] Development workflow unblocked

## Deployment Commands

### Quick Start (Run in Order)
```bash
# 1. Run infrastructure assessment
python scripts/assess_core_infrastructure.py

# 2. Add missing secrets to GitHub Organization
# (Manual step - use GitHub UI)

# 3. Sync secrets to Pulumi ESC  
python scripts/ci/sync_from_gh_to_pulumi.py

# 4. Deploy core MCP servers
python scripts/deploy_core_mcp_servers.py

# 5. Run end-to-end tests
python scripts/test_core_infrastructure.py
```

### Monitoring Commands
```bash
# Check all services
curl http://localhost:8000/api/v1/status

# Check individual MCP servers
curl http://localhost:9000/health  # AI Memory
curl http://localhost:3008/health  # Codacy
curl http://localhost:9003/health  # GitHub
curl http://localhost:9004/health  # Linear

# Re-run assessment
python scripts/assess_core_infrastructure.py
```

## Expected Timeline

- **Phase 1**: 30 minutes (Secret management)
- **Phase 2**: 1 hour (MCP deployment)
- **Phase 3**: 30 minutes (Testing)

**Total**: 2 hours to core stability

## Success Definition

**Core coding infrastructure is considered stable when:**
- 8/10 infrastructure components healthy
- 4/4 critical MCP servers operational  
- End-to-end tests passing at 80%+
- Code protection automation running
- Development workflow unblocked

This plan provides a systematic approach to achieving stable deployment of all core coding services while maintaining the working foundation we've already established.

## Next Steps After Stability

Once core infrastructure is stable:
1. Add database connection to minimal API
2. Add chat endpoint with OpenAI integration
3. Expand to additional MCP servers
4. Deploy frontend to Vercel
5. Setup Lambda Labs compute infrastructure
6. Enable full system orchestration

The key is getting the foundation solid first, then building incrementally.
