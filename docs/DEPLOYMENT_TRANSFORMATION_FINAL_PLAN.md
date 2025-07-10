# 🚀 Sophia AI Deployment Transformation - Final Execution Plan

**Date:** July 10, 2025  
**Current State:** Hybrid (Docker Swarm + Partial K3s)  
**Target State:** Unified K3s + GitOps  
**Timeline:** 10 days focused execution

## 🎯 Mission Statement

Transform Sophia AI's deployment from fragmented, manual processes to a unified, fully automated Kubernetes-native platform. This plan builds on:
- ✅ Memory Ecosystem (83% complete)
- ✅ Code Quality (improved, 60 syntax errors remaining)
- ✅ Lambda Labs Infrastructure (5 instances running)
- ⚠️ Partial K3s Implementation (needs completion)

## 📊 Current State Analysis

### What's Working Well
1. **Core Services Running** on Lambda Labs
2. **GitHub Actions** exist (but fragmented)
3. **Pulumi ESC** for secrets management
4. **Docker Registry** (scoobyjava15) configured

### What Needs Transformation
1. **Mixed Deployment** (Docker Swarm + manual K3s)
2. **Multiple Workflows** (need unification)
3. **No GitOps** (manual kubectl commands)
4. **Legacy Scripts** cluttering repository

## 🏗️ Phase 1: Foundation Cleanup (Days 1-2)

### Day 1: Repository Organization
```bash
# 1. Create clean structure
mkdir -p {archive,kubernetes}/{base,overlays,helm}
mkdir -p scripts/{quality,deployment,monitoring}

# 2. Archive legacy files
python scripts/deployment/archive_legacy.py

# 3. Fix remaining code issues
python scripts/quality/fix_remaining_issues.py
```

### Day 2: Standardize Configuration
- Convert all YAML to consistent format
- Ensure all services use Pulumi ESC
- Document service dependencies

## 🏗️ Phase 2: K3s Migration (Days 3-5)

### Day 3: Core Services
1. **API Service**
   ```yaml
   # kubernetes/base/api-deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: sophia-api
   spec:
     replicas: 3
     template:
       spec:
         containers:
         - name: api
           image: scoobyjava15/sophia-api:latest
           env:
           - name: ENVIRONMENT
             value: "prod"
   ```

2. **Supporting Services** (Redis, PostgreSQL)

### Day 4: MCP Server Fleet
- Convert 11 MCP servers to K8s deployments
- Implement service discovery
- Add health checks

### Day 5: Ingress & Networking
- Configure Traefik ingress
- Set up internal service mesh
- SSL/TLS certificates

## 🏗️ Phase 3: GitHub Actions Unification (Days 6-7)

### Day 6: Single Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to K3s
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build & Deploy
      run: |
        # Quality checks
        uv run ruff check .
        uv run pytest
        
        # Build images
        docker buildx build --push -t scoobyjava15/sophia:${{ github.sha }} .
        
        # Deploy to K3s
        kubectl set image deployment/sophia-api api=scoobyjava15/sophia:${{ github.sha }}
```

### Day 7: Archive Old Workflows
- Move all old workflows to archive/
- Document migration path
- Test new unified workflow

## 🏗️ Phase 4: GitOps Implementation (Days 8-9)

### Day 8: Flux Setup
```bash
# Install Flux
flux bootstrap github \
  --owner=ai-cherry \
  --repository=sophia-main \
  --branch=main \
  --path=./kubernetes
```

### Day 9: Application Sync
- Configure Flux to watch repository
- Set up automated deployments
- Implement rollback mechanisms

## 🏗️ Phase 5: Validation & Cutover (Day 10)

### Morning: Final Testing
- [ ] All services healthy in K3s
- [ ] Monitoring shows normal metrics
- [ ] No manual steps required

### Afternoon: Cutover
1. Scale down Docker Swarm
2. Verify K3s handling all traffic
3. Archive Docker Swarm configs
4. Update documentation

### Evening: Celebration 🎉

## 📋 Quick Reference Commands

### Check Current State
```bash
# Docker Swarm status
docker service ls

# K3s status
kubectl get all -n sophia-ai-prod

# GitHub Actions status
gh workflow list
```

### Emergency Rollback
```bash
# Revert to previous image
kubectl rollout undo deployment/sophia-api

# Scale up Docker Swarm (if needed)
docker service scale sophia_api=3
```

## 🎯 Success Criteria

1. **Zero Manual Deployments** - Everything via git push
2. **Single Source of Truth** - All config in Git
3. **< 5 min Deployments** - From commit to production
4. **100% Automated** - No SSH, no manual commands

## 🚨 Critical Path Items

1. **Fix Code Quality** - Must pass CI/CD checks
2. **Migrate Stateful Services** - Redis needs PVC
3. **Update DNS** - Point to K3s ingress
4. **Document Everything** - For future reference

## 📊 Progress Tracking

### Daily Checklist
- [ ] Morning: Review overnight alerts
- [ ] Midday: Check migration progress
- [ ] Evening: Update progress report
- [ ] EOD: Commit all changes

### Key Metrics
- Services Migrated: 0/15
- Workflows Unified: 0/8
- Documentation Updated: 0/10
- Quality Gates Passing: 70%

## 🎬 Next Immediate Actions

1. **Right Now:**
   ```bash
   # Check current deployment state
   docker service ls
   kubectl get pods -A
   ```

2. **Next Hour:**
   ```bash
   # Start repository cleanup
   python scripts/deployment/start_cleanup.py
   ```

3. **Today:**
   - Review and approve this plan
   - Begin Phase 1 execution
   - Set up progress tracking

---

**Remember:** This is a transformation, not just a migration. We're building a world-class deployment pipeline that will serve Sophia AI for years to come. Every decision should optimize for clarity, automation, and reliability.

**Contact:** For questions or blockers, immediate escalation to the team via Slack #sophia-deployment channel. 