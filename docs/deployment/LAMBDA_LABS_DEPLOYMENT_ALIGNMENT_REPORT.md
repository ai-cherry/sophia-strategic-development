# Lambda Labs Deployment Alignment Report

## Executive Summary

A comprehensive review of the Sophia AI codebase reveals significant misalignments between the current deployment strategy and the requested "all Lambda Labs serverless" approach. This report details all misalignments and provides corrective actions.

## Current vs. Required Deployment Strategy

### 1. Frontend Deployment

| Aspect | Current State | Required State | Misalignment Level |
|--------|--------------|----------------|-------------------|
| Platform | Vercel (3rd party) | Lambda Labs | **CRITICAL** |
| Type | Serverless SaaS | Lambda Labs VPS | Major |
| Configuration | `frontend/vercel.json` | Nginx on Lambda Labs | Major |
| CI/CD | Manual/Vercel GitHub App | GitHub Actions to Lambda Labs | Major |

**Evidence of Misalignment:**
- `frontend/vercel.json` exists and is actively used
- Multiple Vercel deployment scripts in `scripts/`
- Documentation references Vercel throughout
- `.cursorrules` explicitly states frontend uses Vercel
- No active CI/CD pipeline for frontend to Lambda Labs

### 2. Backend Deployment

| Aspect | Current State | Required State | Misalignment Level |
|--------|--------------|----------------|-------------------|
| Platform | Lambda Labs K3s | Lambda Labs "serverless" | **MEDIUM** |
| IP Address | 192.222.58.232 | Same or different | Minor |
| Type | Containerized K8s | True serverless unclear | Medium |
| CI/CD | Partial (image updates only) | Full deployment | Major |

**Evidence of Misalignment:**
- Backend is on Lambda Labs (correct platform)
- Using K3s/Kubernetes (not serverless functions)
- `.github/workflows/deploy-k3s.yml` only updates images
- No Lambda Labs Serverless Inference API integration

### 3. MCP Servers Deployment

| Aspect | Current State | Required State | Misalignment Level |
|--------|--------------|----------------|-------------------|
| Target IP | 192.222.58.232 | 104.171.202.117 | **CRITICAL** |
| Platform | K3s on backend server | K3s on MCP server | Major |
| Node Selection | None | Required nodeSelector | Major |
| CI/CD | Manual kubectl apply | Automated deployment | Major |

**Evidence of Misalignment:**
- All MCP deployment manifests lack nodeSelector
- No configuration targets 104.171.202.117
- MCP servers deploy to same cluster as backend
- No automated MCP deployment in CI/CD

## Misaligned Files and Scripts

### Frontend Misalignments
1. **Configuration Files:**
   - `frontend/vercel.json` - Vercel-specific config
   - `frontend/.env.production` - References Vercel URLs
   - `infrastructure/vercel/` - Entire directory for Vercel

2. **Deployment Scripts:**
   - `scripts/deploy_to_vercel.py`
   - `scripts/deploy_frontend_vercel.py`
   - `scripts/deploy_backend_serverless_vercel.py`
   - Multiple scripts reference Vercel deployment

3. **Documentation:**
   - `docs/04-deployment/VERCEL_DEPLOYMENT_GUIDE.md`
   - `docs/deployment/DEPLOYMENT_GUIDE.md` - References Vercel
   - `docs/04-deployment/PRODUCTION_DEPLOYMENT_ARCHITECTURE.md` - States Vercel

### Backend Misalignments
1. **Terminology Issues:**
   - User requests "serverless" but infrastructure is K3s
   - Lambda Labs offers GPU inference API, not function-as-a-service
   - Current setup is containerized, not serverless

2. **CI/CD Limitations:**
   - `.github/workflows/deploy-k3s.yml` only updates backend image
   - No deployment of other services
   - No initial deployment automation

### MCP Server Misalignments
1. **Kubernetes Manifests:**
   - All files in `kubernetes/production/mcp-*.yaml` lack nodeSelector
   - No targeting of 104.171.202.117
   - Examples:
     - `mcp-ai-memory-deployment.yaml`
     - `mcp-slack-deployment.yaml`
     - `mcp-github-deployment.yaml`
     - etc.

2. **Missing Automation:**
   - No MCP deployment in CI/CD
   - Manual `kubectl apply` required
   - No health checks or monitoring

## Corrective Actions Required

### 1. Frontend Migration to Lambda Labs
- Remove all Vercel dependencies and configurations
- Setup Nginx on Lambda Labs instance (104.171.202.103)
- Create deployment pipeline to Lambda Labs
- Update all environment variables and documentation
- Remove `frontend/vercel.json`

### 2. Backend Alignment
- Clarify "serverless" requirement:
  - If true serverless needed, redesign for Lambda Labs Inference API
  - If K3s acceptable, update terminology in documentation
- Expand CI/CD to deploy all services
- Add proper health checks and monitoring

### 3. MCP Server Targeting
- Add nodeSelector to all MCP deployment manifests:
  ```yaml
  nodeSelector:
    kubernetes.io/hostname: mcp-node
  ```
- Label the 104.171.202.117 node appropriately
- Update CI/CD to deploy MCP servers
- Add inter-node networking configuration

### 4. CI/CD Pipeline Enhancement
- Create comprehensive GitHub Actions workflow
- Deploy all components (frontend, backend, MCP servers)
- Add proper staging/production environments
- Implement rollback capabilities

## Implementation Script

I've created `scripts/deploy_lambda_labs_aligned.py` that:
1. Deploys frontend to Lambda Labs (104.171.202.103)
2. Deploys backend to Lambda Labs K3s (192.222.58.232)
3. Deploys MCP servers to dedicated instance (104.171.202.117)
4. Configures proper ingress and networking

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Frontend migration breaking changes | High | Gradual migration with testing |
| MCP server network isolation | Medium | Proper K3s multi-node setup |
| Loss of Vercel features | Medium | Implement equivalent on Lambda Labs |
| Increased operational complexity | High | Comprehensive automation |

## Recommendations

1. **Immediate Actions:**
   - Run `scripts/deploy_lambda_labs_aligned.py` to test aligned deployment
   - Update all documentation to reflect Lambda Labs strategy
   - Remove Vercel configurations

2. **Short-term (1 week):**
   - Enhance CI/CD pipeline for full automation
   - Implement monitoring and alerting
   - Test multi-node K3s configuration

3. **Long-term (1 month):**
   - Consider true serverless architecture if needed
   - Implement proper GitOps with ArgoCD
   - Add comprehensive observability

## Conclusion

The current deployment strategy has significant misalignments with the requested "all Lambda Labs serverless" approach. The frontend is on Vercel (wrong platform), the backend is on Lambda Labs but not serverless (terminology issue), and MCP servers are not targeted to the correct instance (configuration issue). The provided alignment script addresses these issues, but careful migration planning is required to avoid service disruption. 