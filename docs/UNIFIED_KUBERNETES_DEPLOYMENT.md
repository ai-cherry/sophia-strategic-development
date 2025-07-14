# Unified Kubernetes Deployment Guide

## Overview

Sophia AI now uses a **single, unified Kubernetes deployment approach** for all environments.

## Quick Start

```bash
# Deploy to Kubernetes
./scripts/deploy_unified_kubernetes.sh deploy

# Check status
./scripts/deploy_unified_kubernetes.sh status

# Upgrade deployment
./scripts/deploy_unified_kubernetes.sh upgrade

# Rollback if needed
./scripts/deploy_unified_kubernetes.sh rollback
```

## Architecture

- **Orchestration**: Kubernetes (via Helm)
- **Container Registry**: Docker Hub (scoobyjava15)
- **Secret Management**: Pulumi ESC → Kubernetes Secrets
- **LLM Gateway**: Portkey with OpenRouter fallback
- **GPU Support**: NVIDIA device plugin with node selectors
- **Monitoring**: Prometheus + Grafana
- **GitOps**: ArgoCD (optional)

## Configuration

All configuration is in `kubernetes/helm/sophia-platform/values.yaml`

### LLM Configuration

```yaml
llmGateway:
  provider: portkey
  portkey:
    endpoint: https://api.portkey.ai/v1
  openrouter:
    endpoint: https://openrouter.ai/api/v1
    models:
      - gpt-4o
      - claude-3-5-sonnet-20241022
      - deepseek-v3
      - gemini-2.0-flash-exp
```

### GPU Node Selection

```yaml
nodeSelector:
  gpu-type: GH200  # or RTX6000, A6000, A100, A10
```

## Removed Files

The following redundant files have been removed:
- Multiple docker-compose variants
- Duplicate deployment scripts
- Conflicting configuration files
- Old infrastructure code

## Best Practices

1. **Single Deployment Pattern**: Use only the unified Kubernetes approach
2. **GitOps**: All changes through Git, deployed via CI/CD
3. **No Manual Deployments**: Everything automated
4. **GPU Optimization**: Proper node selectors and resource limits
5. **Cost Management**: Resource quotas and monitoring

## Support

For issues or questions, check:
- Deployment logs: `kubectl logs -n sophia-ai`
- Helm status: `helm status sophia-platform -n sophia-ai`
- Pod status: `kubectl get pods -n sophia-ai`
