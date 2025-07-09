# Lambda Labs Deployment Infrastructure Update Plan

## Executive Summary

This plan provides a comprehensive update to all Lambda Labs deployment infrastructure to ensure:
1. Correct IP addresses and instance mappings
2. Proper SSH key management
3. Secure API key handling via Pulumi ESC
4. No exposed credentials in code or documentation
5. Modern CI/CD workflows with GitHub Actions

## Current State Analysis

### Active Lambda Labs Instance
- **Primary Instance**: GH200 at `192.222.51.151` (confirmed active)
- **SSH Key**: `~/.ssh/lynn_sophia_h200_key` (exists locally)
- **API Keys**: Stored in GitHub Secrets and Pulumi ESC

### Problems Identified

1. **Outdated IP References**:
   - Old IPs still referenced: `146.235.200.1`, `137.131.6.213`, `104.171.202.103`, etc.
   - Multiple conflicting instance mappings

2. **Hardcoded Credentials**:
   - API keys exposed in `scripts/lambda_labs_manager.py`
   - SSH key paths inconsistent across scripts

3. **Inconsistent Key Names**:
   - Mix of `lynn_sophia_h200_key`, `lambda_labs_sophia_key`, `lambda_labs_key`
   - GitHub secrets vs Pulumi ESC naming mismatches

## Implementation Plan

### Phase 1: Secure Credential Management

#### 1.1 Update Lambda Labs Manager
```python
# Remove hardcoded credentials from scripts/lambda_labs_manager.py
class LambdaLabsManager:
    def __init__(self):
        # Use Pulumi ESC for credentials
        from backend.core.auto_esc_config import get_config_value
        
        self.cloud_api_key = get_config_value("lambda_cloud_api_key")
        self.regular_api_key = get_config_value("lambda_api_key")
        self.api_endpoint = get_config_value("lambda_api_endpoint", "https://cloud.lambda.ai/api/v1")
        
        # Standardize SSH key path
        self.ssh_key_path = os.path.expanduser(
            get_config_value("lambda_ssh_key_path", "~/.ssh/lynn_sophia_h200_key")
        )
```

#### 1.2 Standardize Secret Names
```yaml
# Pulumi ESC Configuration (infrastructure/esc/sophia-ai-production.yaml)
infrastructure:
  lambda_labs:
    api_key: ${secrets.LAMBDA_API_KEY}
    cloud_api_key: ${secrets.LAMBDA_CLOUD_API_KEY}
    api_endpoint: "https://cloud.lambda.ai/api/v1"
    ssh_key_path: "~/.ssh/lynn_sophia_h200_key"
    instances:
      production:
        name: "sophia-main"
        ip: "192.222.51.151"
        type: "GH200"
```

### Phase 2: Update All Scripts and Documentation

#### 2.1 Scripts to Update
1. `scripts/lambda_labs_manager.py` - Remove hardcoded credentials
2. `scripts/deploy_sophia_complete.py` - Update IP and SSH key
3. `scripts/deploy_production_complete.py` - Update all references
4. `scripts/setup_github_secrets.sh` - Ensure correct secret names
5. `scripts/lambda_labs_api_integration.py` - Use Pulumi ESC

#### 2.2 Documentation Updates
1. Remove all references to old IPs
2. Update deployment guides with current instance
3. Create single source of truth for Lambda Labs config

### Phase 3: GitHub Actions Workflow Updates

#### 3.1 Main Deployment Workflow
```yaml
# .github/workflows/main-deployment.yml
env:
  LAMBDA_LABS_IP: "192.222.51.151"
  LAMBDA_SSH_KEY_NAME: "lynn_sophia_h200_key"
  
jobs:
  deploy:
    steps:
      - name: Configure SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.LAMBDA_SSH_KEY }}" > ~/.ssh/lynn_sophia_h200_key
          chmod 600 ~/.ssh/lynn_sophia_h200_key
```

### Phase 4: Infrastructure as Code Updates

#### 4.1 Pulumi Configuration
```typescript
// infrastructure/pulumi/lambda-labs.ts
export const lambdaLabsConfig = {
  instances: {
    production: {
      name: "sophia-main",
      ip: "192.222.51.151",
      type: "GH200",
      region: "us-west",
      sshKeyName: "lynn_sophia_h200_key"
    }
  },
  monitoring: {
    prometheusPort: 9090,
    grafanaPort: 3000
  }
};
```

### Phase 5: Security Scanning and Cleanup

#### 5.1 Remove Exposed Credentials
1. Scan entire codebase for exposed keys
2. Remove hardcoded IPs and credentials
3. Update `.gitignore` to prevent future exposures

#### 5.2 Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: check-lambda-labs-secrets
      name: Check for Lambda Labs secrets
      entry: scripts/security/scan_for_secrets.py
      language: python
      files: \.(py|sh|yml|yaml|md|ts|js)$
```

## Migration Steps

### Step 1: Backup Current Configuration
```bash
# Create backup of current config
mkdir -p backups/lambda-labs-$(date +%Y%m%d)
cp -r scripts/lambda_labs_* backups/lambda-labs-$(date +%Y%m%d)/
cp -r infrastructure/pulumi/* backups/lambda-labs-$(date +%Y%m%d)/
```

### Step 2: Update Pulumi ESC
```bash
# Set correct values in Pulumi ESC
pulumi env set scoobyjava-org/default/sophia-ai-production \
  lambda_labs.api_key "secret_sophia5apikey_a404a99d985d41828d7020f0b9a122a2.PjbWZb0lLubKu1nmyWYLy9Ycl3vyL18o" \
  --secret

pulumi env set scoobyjava-org/default/sophia-ai-production \
  lambda_labs.cloud_api_key "secret_sophiacloudapi_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y" \
  --secret

pulumi env set scoobyjava-org/default/sophia-ai-production \
  lambda_labs.instances.production.ip "192.222.51.151"
```

### Step 3: Update GitHub Secrets
```bash
# Ensure GitHub secrets are correctly set
gh secret set LAMBDA_API_KEY --body "$LAMBDA_API_KEY" --org ai-cherry
gh secret set LAMBDA_CLOUD_API_KEY --body "$LAMBDA_CLOUD_API_KEY" --org ai-cherry
gh secret set LAMBDA_SSH_KEY --body "$(cat ~/.ssh/lynn_sophia_h200_key)" --org ai-cherry
```

### Step 4: Run Security Scan
```bash
# Scan for any remaining exposed credentials
python scripts/security/scan_for_secrets.py --fix
```

### Step 5: Test Deployment
```bash
# Test with updated configuration
python scripts/lambda_labs_manager.py health --instance production
```

## Validation Checklist

- [ ] No hardcoded API keys in any scripts
- [ ] All scripts use Pulumi ESC for credentials
- [ ] Single IP address (192.222.51.151) used consistently
- [ ] SSH key path standardized to `~/.ssh/lynn_sophia_h200_key`
- [ ] GitHub Actions workflows updated
- [ ] Documentation reflects current state
- [ ] Security scan passes
- [ ] Deployment test successful

## Files to Delete/Archive

1. **Delete Outdated Scripts**:
   - Old deployment scripts with hardcoded IPs
   - Duplicate Lambda Labs managers
   - Scripts with exposed credentials

2. **Archive Historical Docs**:
   - Move old deployment guides to `docs/archive/`
   - Keep only current deployment documentation

## Final Configuration

### Lambda Labs Instance
```yaml
production:
  name: sophia-main
  ip: 192.222.51.151
  type: GH200
  gpu: 96GB
  memory: 480GB
  cost_per_hour: $1.49
  ssh_key: ~/.ssh/lynn_sophia_h200_key
  services:
    - backend: 8000
    - mcp_servers: 9000-9100
    - prometheus: 9090
    - grafana: 3000
    - postgres: 5432
    - redis: 6379
```

### Access URLs
- Backend API: http://192.222.51.151:8000
- API Docs: http://192.222.51.151:8000/docs
- Grafana: http://192.222.51.151:3000
- Prometheus: http://192.222.51.151:9090

## Success Criteria

1. **Security**: Zero exposed credentials in codebase
2. **Consistency**: Single source of truth for Lambda Labs config
3. **Automation**: All deployments via GitHub Actions
4. **Monitoring**: Health checks and alerts configured
5. **Documentation**: Clear, updated deployment guides

## Timeline

- **Phase 1**: Immediate - Secure credential management (1 hour)
- **Phase 2**: Update scripts and docs (2 hours)
- **Phase 3**: GitHub Actions updates (1 hour)
- **Phase 4**: Infrastructure as Code (1 hour)
- **Phase 5**: Security scan and cleanup (1 hour)

Total estimated time: 6 hours

## Next Steps

1. Execute this plan systematically
2. Test each phase before proceeding
3. Document any issues or changes
4. Create automated tests for deployment
5. Set up monitoring and alerting 