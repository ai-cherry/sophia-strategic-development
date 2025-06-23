# Gong Webhook Service - Kubernetes Deployment Guide

## Overview

The Gong Webhook Service is a production-ready FastAPI application that processes Gong webhooks in real-time, enhances data via API calls, and stores processed data in Snowflake. This guide covers the Kubernetes deployment of the service within the Sophia AI platform.

## Architecture

```
Internet → Ingress (TLS) → Service → Deployment (3 replicas) → Pods
                                 ↓
                           Auto-scaling (HPA)
                                 ↓
                          Monitoring (Prometheus)
```

### Components Deployed

1. **Namespace**: `sophia-ai` - Isolated environment for Sophia AI services
2. **Deployment**: 3-replica deployment with rolling updates
3. **Service**: ClusterIP service for internal communication
4. **Ingress**: NGINX ingress with TLS termination
5. **ConfigMap**: Non-sensitive configuration values
6. **Secret**: Sensitive credentials from Pulumi ESC
7. **HPA**: Horizontal Pod Autoscaler (3-10 replicas)
8. **ServiceMonitor**: Prometheus monitoring configuration
9. **NetworkPolicy**: Security policies for network traffic
10. **PodDisruptionBudget**: High availability guarantees

## Prerequisites

### Required Tools
- `kubectl` - Kubernetes CLI
- `docker` - Container management
- `pulumi` - Infrastructure as Code and secret management
- `curl` - API testing

### Required Access
- Kubernetes cluster admin access
- Pulumi ESC environment access (`sophia-ai-production`)
- Docker registry access (for image pushing)

### Required Infrastructure
- Kubernetes cluster (1.21+)
- NGINX Ingress Controller
- Prometheus Operator (for monitoring)
- cert-manager (for TLS certificates)

## Configuration

### Environment Variables (ConfigMap)
```yaml
HOST: "0.0.0.0"
PORT: "8080"
WORKERS: "4"
GONG_API_BASE_URL: "https://api.gong.io"
GONG_API_RATE_LIMIT: "2.5"
GONG_API_BURST_LIMIT: "10"
SNOWFLAKE_WAREHOUSE: "COMPUTE_WH"
SNOWFLAKE_DATABASE: "SOPHIA_AI"
SNOWFLAKE_SCHEMA: "GONG_WEBHOOKS"
REDIS_URL: "redis://redis-service:6379"
MAX_RETRY_ATTEMPTS: "5"
INITIAL_RETRY_DELAY: "1.0"
MAX_RETRY_DELAY: "300.0"
WEBHOOK_TIMEOUT_SECONDS: "30"
```

### Secrets (Kubernetes Secret)
Managed by Pulumi ESC and automatically injected:
- `GONG_API_KEY` - Gong API authentication
- `GONG_WEBHOOK_SECRETS` - JWT verification secrets
- `SNOWFLAKE_ACCOUNT` - Snowflake account identifier
- `SNOWFLAKE_USER` - Snowflake username
- `SNOWFLAKE_PASSWORD` - Snowflake password

## Deployment

### Quick Deployment
```bash
# Full deployment with secret injection
./scripts/deploy-gong-webhook-k8s.sh deploy

# Build image only
./scripts/deploy-gong-webhook-k8s.sh build

# Apply secrets only
./scripts/deploy-gong-webhook-k8s.sh secrets
```

### Step-by-Step Deployment

1. **Prepare Environment**
   ```bash
   export PULUMI_ORG=scoobyjava-org
   pulumi login
   pulumi env open scoobyjava-org/default/sophia-ai-production
   ```

2. **Build Docker Image**
   ```bash
   docker build -f Dockerfile.gong-webhook -t sophia-ai/gong-webhook-service:latest .
   ```

3. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f infrastructure/kubernetes/manifests/gong-webhook-service.yaml
   ```

4. **Inject Secrets**
   ```bash
   # Load ESC environment
   eval "$(pulumi env get scoobyjava-org/default/sophia-ai-production --format shell)"
   
   # Create secret
   kubectl create secret generic gong-webhook-secrets \
     --namespace=sophia-ai \
     --from-literal=GONG_API_KEY="${GONG_ACCESS_KEY}" \
     --from-literal=GONG_WEBHOOK_SECRETS="${GONG_CLIENT_SECRET}" \
     --from-literal=SNOWFLAKE_ACCOUNT="${SNOWFLAKE_ACCOUNT}" \
     --from-literal=SNOWFLAKE_USER="${SNOWFLAKE_USER}" \
     --from-literal=SNOWFLAKE_PASSWORD="${SNOWFLAKE_PASSWORD}"
   ```

5. **Verify Deployment**
   ```bash
   kubectl get pods -l app=gong-webhook-service -n sophia-ai
   kubectl logs -l app=gong-webhook-service -n sophia-ai -f
   ```

## Resource Specifications

### Pod Resources
```yaml
requests:
  memory: "512Mi"
  cpu: "250m"
  ephemeral-storage: "1Gi"
limits:
  memory: "2Gi"
  cpu: "1000m"
  ephemeral-storage: "2Gi"
```

### Auto-scaling
- **Min replicas**: 3
- **Max replicas**: 10
- **CPU target**: 70%
- **Memory target**: 80%
- **Scale-up policy**: 100% increase, max 2 pods per minute
- **Scale-down policy**: 10% decrease per minute with 5-minute stabilization

### High Availability
- **Pod anti-affinity**: Spreads pods across nodes
- **Pod disruption budget**: Minimum 2 pods available during disruptions
- **Rolling updates**: Max 1 surge, 0 unavailable
- **Health checks**: Startup, readiness, and liveness probes

## Security Features

### Container Security
- Non-root user (UID/GID 1000)
- Read-only root filesystem
- No privilege escalation
- Dropped capabilities (ALL)
- Security context enforcement

### Network Security
- NetworkPolicy restricting ingress/egress
- TLS termination at ingress
- Internal service communication only
- Prometheus metrics endpoint protection

### Secret Management
- Pulumi ESC integration for secret rotation
- Kubernetes secrets with proper annotations
- No hardcoded credentials
- Secret rotation schedule (90 days)

## Monitoring and Observability

### Health Endpoints
- **Health check**: `GET /health`
- **Metrics**: `GET /metrics` (Prometheus format)

### Prometheus Metrics
- Request count and duration
- API call metrics
- Rate limit metrics
- Data quality scores
- Background task metrics

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking with context
- Request ID correlation

## Troubleshooting

### Common Issues

1. **Pod Startup Failures**
   ```bash
   kubectl describe pod -l app=gong-webhook-service -n sophia-ai
   kubectl logs -l app=gong-webhook-service -n sophia-ai --previous
   ```

2. **Secret Access Issues**
   ```bash
   kubectl get secret gong-webhook-secrets -n sophia-ai -o yaml
   pulumi env get scoobyjava-org/default/sophia-ai-production
   ```

3. **Network Connectivity**
   ```bash
   kubectl exec -it deployment/gong-webhook-service -n sophia-ai -- curl -v https://api.gong.io
   ```

4. **Health Check Failures**
   ```bash
   kubectl port-forward service/gong-webhook-service 8080:80 -n sophia-ai
   curl http://localhost:8080/health
   ```

### Debugging Commands
```bash
# View all resources
kubectl get all -l app=gong-webhook-service -n sophia-ai

# Check pod events
kubectl get events --field-selector involvedObject.name=<pod-name> -n sophia-ai

# Access pod shell
kubectl exec -it deployment/gong-webhook-service -n sophia-ai -- /bin/bash

# View configuration
kubectl get configmap gong-webhook-config -n sophia-ai -o yaml

# Check ingress
kubectl describe ingress gong-webhook-ingress -n sophia-ai
```

## Maintenance

### Updates
```bash
# Update image
kubectl set image deployment/gong-webhook-service \
  gong-webhook=sophia-ai/gong-webhook-service:v1.1.0 \
  -n sophia-ai

# Monitor rollout
kubectl rollout status deployment/gong-webhook-service -n sophia-ai
```

### Scaling
```bash
# Manual scaling
kubectl scale deployment gong-webhook-service --replicas=5 -n sophia-ai

# Update HPA
kubectl patch hpa gong-webhook-hpa -n sophia-ai -p '{"spec":{"maxReplicas":15}}'
```

### Secret Rotation
```bash
# Rotate secrets via Pulumi ESC
pulumi env set scoobyjava-org/default/sophia-ai-production GONG_ACCESS_KEY new-value

# Restart deployment to pick up new secrets
kubectl rollout restart deployment/gong-webhook-service -n sophia-ai
```

## Performance Optimization

### Tuning Parameters
- **Worker processes**: Adjust based on CPU cores
- **Connection pooling**: Optimize database connections
- **Rate limiting**: Tune based on Gong API limits
- **Caching**: Configure Redis appropriately

### Monitoring Metrics
- Response time percentiles
- Request rate
- Error rates
- Resource utilization
- Queue depth

## Integration Points

### Upstream Services
- **Gong API**: External webhook source
- **Load balancer**: Traffic distribution

### Downstream Services
- **Snowflake**: Data storage
- **Redis**: Background task queue
- **Prometheus**: Metrics collection
- **Slack**: Notification delivery

## Disaster Recovery

### Backup Strategy
- Configuration stored in Git
- Secrets managed by Pulumi ESC
- Data backed up in Snowflake
- Container images in registry

### Recovery Procedures
1. Restore from Git repository
2. Apply Kubernetes manifests
3. Inject secrets from ESC
4. Verify service functionality
5. Resume traffic routing

## Support and Documentation

### Additional Resources
- [Gong API Documentation](https://us-66463.app.gong.io/settings/api/documentation)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Pulumi ESC Documentation](https://www.pulumi.com/docs/esc/)
- [Prometheus Monitoring](https://prometheus.io/docs/)

### Contact Information
- **Team**: Sophia AI Platform Team
- **Repository**: `sophia-main`
- **Monitoring**: Grafana dashboards
- **Alerts**: Prometheus AlertManager 