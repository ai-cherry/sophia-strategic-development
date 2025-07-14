# Deployment Infrastructure Action Items - July 2025

**Priority:** CRITICAL  
**Deadline:** July 12, 2025 (Strategic Decision)

## 🚨 Immediate Actions (This Week)

### 1. STOP Current Development
- [ ] **Pause all MCP server development** until deployment is fixed
- [ ] Document current MCP migration status (56.25% complete)
- [ ] Preserve work done on 9 migrated servers

### 2. Execute Strategic Decision
- [ ] **Confirmed direction**: Kubernetes via K3s migration path
- [ ] Review existing migration plan in ORCHESTRATION_MIGRATION.md
- [ ] Confirm 16-week timeline with stakeholders

### 3. Fix Critical Gaps
- [ ] Fix broken GitHub Actions that reference non-existent files:
  - `production-deployment.yml` → Missing `scripts/unified_lambda_labs_deployment.py`
  - `sophia-unified-deployment.yml` → Missing `docker-compose.unified.yml`

### 4. Consolidate Configurations
- [ ] Rename `docker-compose.cloud.yml` → `docker-compose.unified.yml`
- [ ] Delete conflicting Docker Compose files
- [ ] Remove unused GitHub workflows

## 📋 Week 1 Tasks (Foundation)

### Infrastructure Gap
- [ ] Update Pulumi to include Docker Swarm initialization in cloud-init
- [ ] Add orchestrator setup to infrastructure provisioning
- [ ] Ensure Swarm manager IP is output from Pulumi

### Cleanup
- [ ] Remove all Kubernetes artifacts if choosing Swarm
- [ ] Delete manual deployment scripts after automation works
- [ ] Remove hardcoded IPs (104.171.202.103, 192.222.58.232, etc.)

## 📋 Week 2 Tasks (Automation)

### Fix GitHub Actions
- [ ] Update workflows to use Pulumi outputs (not hardcoded IPs)
- [ ] Create missing deployment scripts referenced in workflows
- [ ] Test end-to-end automated deployment

### Complete MCP Migration
- [ ] Finish migrating remaining 7 MCP servers to official SDK:
  - figma_context
  - lambda_labs_cli
  - linear_v2
  - notion_v2
  - postgres
  - portkey_admin
  - openrouter_search

### Containerize MCP Servers
- [ ] Create base Docker image for MCP servers
- [ ] Build individual server images
- [ ] Add to docker-compose.unified.yml

## 📋 Week 3 Tasks (Integration)

### Deploy & Test
- [ ] Deploy all MCP servers via chosen orchestrator
- [ ] Implement health monitoring for all services
- [ ] Performance test the complete system
- [ ] Update all documentation

## 🎯 Success Metrics

1. **Deployment Success Rate**: 100% via automation
2. **Time to Deploy**: < 10 minutes
3. **Hardcoded IPs**: 0
4. **MCP Servers Migrated**: 16/16 (100%)
5. **Documentation Accuracy**: 100%

## ⚠️ Risks if Not Addressed

- **Development Velocity**: -40% ongoing impact
- **Production Failures**: Manual deployments increase error risk
- **Technical Debt**: Compounding daily
- **Team Morale**: Confusion and frustration

## 💡 Quick Wins Available

1. **Fix workflow file references** (1 hour) - Immediate improvement
2. **Consolidate Docker Compose** (30 minutes) - Reduce confusion
3. **Document current deployment** (2 hours) - Help team today

---

**Owner:** Platform Team  
**Escalation:** CTO if blocked  
**Next Review:** July 17, 2025 