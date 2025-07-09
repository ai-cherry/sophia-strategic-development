# Sophia AI Deployment Documentation Restructuring Plan

## Executive Summary

This plan provides a comprehensive strategy to restructure, update, and consolidate all deployment-related documentation and processes for Sophia AI. The goal is to create a single source of truth for deployment procedures while ensuring security, alignment with latest strategies, and elimination of outdated content.

## Current State Analysis

### Problems Identified
1. **Fragmented Documentation**: 40+ deployment-related files scattered across multiple directories
2. **Outdated Content**: References to deprecated services (Airbyte), old models, and obsolete workflows
3. **Security Risks**: Exposed credentials in scripts and documentation
4. **Inconsistent Strategies**: Multiple conflicting deployment approaches
5. **Missing Documentation**: Lambda Labs deployment details incomplete

### Key Findings
- 15+ GitHub workflows with overlapping functionality
- Multiple Docker compose files (cloud, prod, unified, etc.)
- Scattered secret management approaches
- Incomplete Lambda Labs instance documentation

## Restructuring Strategy

### 1. Documentation Hierarchy

```
docs/
├── deployment/
│   ├── README.md                    # Master deployment index
│   ├── DEPLOYMENT_GUIDE.md          # Primary deployment guide
│   ├── SECRET_MANAGEMENT.md         # Comprehensive secrets guide
│   ├── LAMBDA_LABS_GUIDE.md         # Lambda Labs specifics
│   ├── INFRASTRUCTURE_GUIDE.md      # Infrastructure overview
│   ├── MCP_SERVERS_GUIDE.md         # MCP deployment guide
│   ├── MONITORING_GUIDE.md          # Monitoring & health checks
│   ├── TROUBLESHOOTING.md           # Common issues & solutions
│   └── archive/                     # Deprecated docs (reference only)
```

### 2. Workflow Consolidation

#### Primary Workflows (Keep)
```yaml
.github/workflows/
├── main-deployment.yml       # Primary production deployment
├── mcp-deployment.yml        # MCP servers deployment
├── secret-sync.yml           # Secret synchronization
├── infrastructure.yml        # Infrastructure management
└── monitoring.yml            # Health checks & monitoring
```

#### Archive/Delete
- production-deployment.yml (duplicate)
- sophia-prod.yml (outdated)
- deploy-phase2.yml (deprecated)
- 30+ other redundant workflows

### 3. Script Organization

```
scripts/
├── deployment/
│   ├── deploy.py                    # Master deployment script
│   ├── lambda_labs_manager.py       # Lambda Labs management
│   ├── docker_build.py              # Docker image building
│   └── health_check.py              # Health validation
├── security/
│   ├── secret_validator.py          # Secret validation
│   ├── credential_scanner.py        # Pre-commit scanner
│   └── secret_rotation.py           # Secret rotation
└── validation/
    ├── pre_deployment.py            # Pre-deployment checks
    ├── post_deployment.py           # Post-deployment validation
    └── infrastructure_test.py       # Infrastructure testing
```

## Implementation Plan

### Phase 1: Security Audit & Cleanup (Day 1)

1. **Scan for Exposed Secrets**
   ```bash
   # Run comprehensive secret scan
   python scripts/security/scan_for_secrets.py
   
   # Remove any exposed credentials
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch <files-with-secrets>' \
     --prune-empty --tag-name-filter cat -- --all
   ```

2. **Update .gitignore**
   ```gitignore
   # Security
   *.pem
   *.key
   *_key
   *_key.pub
   .env*
   !.env.example
   secrets/
   credentials/
   ```

3. **Create Pre-commit Hooks**
   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/Yelp/detect-secrets
       rev: v1.4.0
       hooks:
         - id: detect-secrets
   ```

### Phase 2: Documentation Consolidation (Day 2-3)

1. **Create Master Deployment Guide**
   - Consolidate all deployment procedures
   - Remove outdated references
   - Add Lambda Labs specifics
   - Include security best practices

2. **Update Secret Management Guide**
   - Document GitHub → Pulumi ESC flow
   - Include all required secrets
   - Add rotation procedures
   - Include emergency access

3. **Create Infrastructure Guide**
   - Document all Lambda Labs instances
   - Include cost breakdown
   - Add scaling procedures
   - Include disaster recovery

### Phase 3: Workflow Modernization (Day 4-5)

1. **Create Unified Deployment Workflow**
   ```yaml
   name: Sophia AI Deployment
   
   on:
     push:
       branches: [main]
     workflow_dispatch:
       inputs:
         environment:
           type: choice
           options: [production, staging, development]
         components:
           type: choice
           options: [all, backend, mcp, frontend]
   ```

2. **Implement Security Checks**
   - Pre-deployment secret validation
   - Container vulnerability scanning
   - Infrastructure security audit

3. **Add Deployment Gates**
   - Automated testing
   - Manual approval for production
   - Rollback procedures

### Phase 4: Script Consolidation (Day 6-7)

1. **Create Master Deployment Script**
   ```python
   # scripts/deployment/deploy.py
   class SophiaDeploymentManager:
       def __init__(self):
           self.lambda_manager = LambdaLabsManager()
           self.docker_builder = DockerBuilder()
           self.secret_manager = SecretManager()
       
       def deploy(self, environment, components):
           # Comprehensive deployment logic
   ```

2. **Implement Validation Framework**
   - Pre-deployment validation
   - Post-deployment testing
   - Health check automation

### Phase 5: Testing & Validation (Day 8-9)

1. **Test Deployment Pipeline**
   - Deploy to development
   - Validate all components
   - Test rollback procedures

2. **Security Validation**
   - Run secret scans
   - Test access controls
   - Validate encryption

3. **Documentation Review**
   - Technical accuracy
   - Completeness check
   - User testing

### Phase 6: Cutover & Cleanup (Day 10)

1. **Archive Old Content**
   ```bash
   # Move deprecated files
   mkdir -p docs/deployment/archive
   mv docs/old-deployment-*.md docs/deployment/archive/
   ```

2. **Update References**
   - Update README.md
   - Update .cursorrules
   - Update CI/CD references

3. **Communication**
   - Team notification
   - Update procedures
   - Training if needed

## Security Guidelines

### Secret Management Best Practices

1. **Never Commit Secrets**
   - Use environment variables
   - Use Pulumi ESC
   - Use GitHub secrets

2. **Secret Rotation Schedule**
   - API keys: 90 days
   - Passwords: 60 days
   - SSH keys: Annual
   - Certificates: Before expiry

3. **Access Control**
   - Principle of least privilege
   - Role-based access
   - Audit logging

### Pre-commit Security Checks

```bash
#!/bin/bash
# scripts/security/pre-commit-security.sh

# Check for secrets
detect-secrets scan --baseline .secrets.baseline

# Check for private keys
if grep -r "BEGIN.*PRIVATE KEY" . --exclude-dir=.git; then
    echo "ERROR: Private key detected!"
    exit 1
fi

# Check for API keys
if grep -rE "(api_key|apikey|api-key)" . --exclude-dir=.git | grep -v example; then
    echo "WARNING: Possible API key detected"
fi
```

## Lambda Labs Documentation

### Instance Inventory
```yaml
instances:
  - name: sophia-ai-main
    ip: 192.222.51.151
    type: GH200
    gpu: 96GB
    cost: $1.49/hour
    purpose: Main backend, MCP servers
    
  - name: sophia-ai-worker-1
    ip: 192.222.51.122
    type: RTX6000
    gpu: 24GB
    cost: $0.50/hour
    purpose: MCP orchestration
    
  - name: sophia-ai-worker-2
    ip: 192.222.58.232
    type: A6000
    gpu: 48GB
    cost: $0.80/hour
    purpose: AI workloads
    
  - name: sophia-ai-dev
    ip: 104.171.202.103
    type: A100
    gpu: 40GB
    cost: $1.29/hour
    purpose: Development
    
  - name: sophia-ai-monitor
    ip: 155.248.194.183
    type: A10
    gpu: 24GB
    cost: $0.75/hour
    purpose: Monitoring
```

### Deployment Commands
```bash
# Deploy to specific instance
./scripts/deployment/deploy.py --instance sophia-ai-main --component backend

# Deploy all MCP servers
./scripts/deployment/deploy.py --instance sophia-ai-main --component mcp --parallel

# Health check
./scripts/deployment/health_check.py --all-instances
```

## Monitoring & Alerting

### Health Check Endpoints
```yaml
endpoints:
  - name: Backend API
    url: http://192.222.51.151:8000/health
    expected: 200
    
  - name: MCP Gateway
    url: http://192.222.51.151:8080/health
    expected: 200
    
  - name: Prometheus
    url: http://155.248.194.183:9090/-/healthy
    expected: 200
```

### Alerting Rules
```yaml
alerts:
  - name: InstanceDown
    condition: up == 0
    severity: critical
    
  - name: HighMemoryUsage
    condition: memory_usage > 90
    severity: warning
    
  - name: DeploymentFailed
    condition: deployment_status != "success"
    severity: critical
```

## Success Metrics

### Documentation Quality
- [ ] All deployment procedures documented
- [ ] No outdated references
- [ ] Security best practices included
- [ ] Lambda Labs specifics complete

### Security Compliance
- [ ] No exposed secrets in repository
- [ ] Pre-commit hooks active
- [ ] Secret rotation documented
- [ ] Access controls implemented

### Operational Excellence
- [ ] Single deployment command
- [ ] Automated health checks
- [ ] Rollback procedures tested
- [ ] Monitoring active

## Timeline

- **Week 1**: Security audit, documentation consolidation
- **Week 2**: Workflow modernization, script consolidation
- **Week 3**: Testing, validation, cutover

## Conclusion

This restructuring plan will transform Sophia AI's deployment infrastructure from a fragmented, security-risk-prone system to a streamlined, secure, and well-documented deployment pipeline. The focus on security, Lambda Labs integration, and operational excellence will ensure reliable and safe deployments going forward. 