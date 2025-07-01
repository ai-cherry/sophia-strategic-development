# Sophia AI GitHub Actions Workflow Hierarchy

## Primary Workflows

### 1. sophia-main.yml (Production Deployment)
- **Purpose**: Primary production deployment workflow
- **Triggers**: Push to main branch, manual dispatch
- **Environment**: Production only
- **Features**: 
  - Pulumi ESC integration
  - Backend + Frontend + Infrastructure deployment
  - Security scanning
  - Automated testing

### 2. deploy-sophia-platform.yml (Multi-Environment)
- **Purpose**: Comprehensive multi-environment deployment
- **Triggers**: Push to main/develop, pull requests
- **Environment**: dev/staging/prod
- **Features**:
  - Preview deployments for PRs
  - Environment-specific configurations
  - Comprehensive testing suite

## Specialized Workflows

### MCP Operations
- `mcp-integration-test.yml` - MCP server testing
- `mcp-security-audit.yml` - Security validation
- `sync-mcp-submodules.yml` - Submodule management

### Infrastructure
- `infrastructure-deploy.yml` - Infrastructure only
- `infrastructure-tests.yml` - Infrastructure validation
- `sync_secrets.yml` - Secret management

### Development
- `cursor-integration.yml` - IDE integration
- `documentation-quality.yml` - Documentation checks
- `test-suite.yml` - Test execution

## Deprecated Workflows
- `production_deployment.yml` - Superseded by sophia-main.yml
- `deploy-phase2.yml` - DATABASE_URL dependency issues

## Usage Guidelines

### For Production Deployments
```bash
# Automatic on push to main
git push origin main

# Manual deployment
gh workflow run "Sophia AI Production Deployment"
```

### For Development
```bash
# Create PR for preview deployment
git push origin feature-branch
# Creates PR which triggers preview deployment
```

### For Infrastructure Changes
```bash
# Manual infrastructure deployment
gh workflow run "Deploy Infrastructure" --ref main
```

## Environment Variables

All workflows use centralized environment configuration:
- `PULUMI_ORG: scoobyjava-org`
- `ENVIRONMENT: prod` (default)
- Secrets managed via Pulumi ESC
- No DATABASE_URL dependencies (use Snowflake via ESC)

## Monitoring

Check workflow status:
```bash
gh run list --limit 10
gh run view <run-id>
```
