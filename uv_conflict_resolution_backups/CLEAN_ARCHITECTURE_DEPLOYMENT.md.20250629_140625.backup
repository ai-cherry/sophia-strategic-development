# Clean Architecture Deployment Guide

This guide explains how to deploy the Clean Architecture implementation on Lambda Labs infrastructure.

## Prerequisites

- Lambda Labs Kubernetes cluster access
- Pulumi CLI installed and configured
- Docker registry access
- Pulumi ESC configured with secrets

## Deployment Architecture

```
Lambda Labs Kubernetes Cluster
├── Namespace: sophia-ai
├── Deployment: sophia-api-clean-arch (3 replicas)
├── Service: sophia-api-service
├── Secrets: Managed by Pulumi ESC
├── ConfigMap: Application configuration
├── PVC: Model cache storage
└── HPA: Auto-scaling configuration
```

## Step 1: Build Optimized Docker Image

```bash
# Build the optimized Clean Architecture image
docker build -f Dockerfile.optimized \
  --target production \
  --build-arg PYTHON_VERSION=3.11 \
  --build-arg NODE_VERSION=18 \
  -t sophia-ai:clean-arch-optimized .

# Tag for your registry
docker tag sophia-ai:clean-arch-optimized \
  your-registry.com/sophia-ai:clean-arch-optimized

# Push to registry
docker push your-registry.com/sophia-ai:clean-arch-optimized
```

## Step 2: Configure Pulumi Stack

```bash
# Navigate to Pulumi directory
cd infrastructure/pulumi

# Select or create stack
pulumi stack select sophia-clean-arch-prod

# Set configuration
pulumi config set lambdaLabsKubeconfig --secret < ~/.kube/lambda-labs-config
pulumi config set dockerRegistry your-registry.com
pulumi config set dockerUsername your-username
pulumi config set dockerPassword --secret your-password

# Set all required secrets (from Pulumi ESC)
pulumi config set openaiApiKey --secret $OPENAI_API_KEY
pulumi config set anthropicApiKey --secret $ANTHROPIC_API_KEY
pulumi config set portkeyApiKey --secret $PORTKEY_API_KEY
pulumi config set snowflakeAccount --secret $SNOWFLAKE_ACCOUNT
pulumi config set snowflakeUsername --secret $SNOWFLAKE_USER
pulumi config set snowflakePassword --secret $SNOWFLAKE_PASSWORD
# ... set all other required secrets
```

## Step 3: Deploy with Pulumi

```bash
# Preview changes
pulumi preview

# Deploy
pulumi up --yes

# Monitor deployment
kubectl get pods -n sophia-ai -w
```

## Step 4: Verify Deployment

```bash
# Check pod status
kubectl get pods -n sophia-ai

# Check service
kubectl get svc -n sophia-ai

# Check logs
kubectl logs -n sophia-ai -l app=sophia-api --tail=100

# Test health endpoint
kubectl port-forward -n sophia-ai svc/sophia-api-service 8080:80
curl http://localhost:8080/health
```

## Step 5: Configure Ingress (Optional)

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sophia-api-ingress
  namespace: sophia-ai
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.sophia-intel.ai
    secretName: sophia-api-tls
  rules:
  - host: api.sophia-intel.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sophia-api-service
            port:
              number: 80
```

## Environment-Specific Configuration

### Production
- 3 replicas minimum
- GPU enabled for ML workloads
- 4-8GB memory per pod
- Auto-scaling enabled

### Staging
- 2 replicas
- GPU optional
- 2-4GB memory per pod
- Lower resource limits

### Development
- 1 replica
- No GPU required
- 1-2GB memory
- Minimal resources

## Monitoring and Observability

### Prometheus Metrics
```yaml
# Add to deployment
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

### Logging
- All logs sent to stdout/stderr
- Collected by cluster logging solution
- Structured JSON format

### Health Checks
- `/health` - Liveness probe
- `/ready` - Readiness probe
- `/metrics` - Prometheus metrics

## Troubleshooting

### Pod Not Starting
```bash
# Check events
kubectl describe pod -n sophia-ai <pod-name>

# Check logs
kubectl logs -n sophia-ai <pod-name> --previous
```

### Secret Issues
```bash
# Verify secrets exist
kubectl get secrets -n sophia-ai

# Check secret content (base64 encoded)
kubectl get secret -n sophia-ai sophia-api-secrets -o yaml
```

### Performance Issues
```bash
# Check resource usage
kubectl top pods -n sophia-ai

# Check HPA status
kubectl get hpa -n sophia-ai
```

## Rollback Procedure

```bash
# List Pulumi stack history
pulumi stack history

# Rollback to previous version
pulumi stack export | pulumi stack import --previous

# Or use kubectl
kubectl rollout undo deployment/sophia-api-clean-arch -n sophia-ai
```

## Security Considerations

1. **Secrets Management**
   - All secrets via Pulumi ESC
   - No hardcoded values
   - Regular rotation

2. **Network Policies**
   - Restrict pod-to-pod communication
   - Egress only to required services

3. **RBAC**
   - Service account with minimal permissions
   - No cluster-admin access

4. **Image Security**
   - Regular vulnerability scanning
   - Non-root user in container
   - Minimal base image

## Performance Optimization

1. **GPU Utilization**
   - Ensure GPU drivers installed
   - Monitor GPU usage
   - Batch ML operations

2. **Connection Pooling**
   - Snowflake connection pool configured
   - Redis connection reuse
   - HTTP client pooling

3. **Caching**
   - Model cache on SSD storage
   - Redis for application cache
   - CDN for static assets

## Maintenance

### Regular Tasks
- Update base images monthly
- Rotate secrets quarterly
- Review resource usage weekly
- Update dependencies as needed

### Backup Strategy
- Persistent volume snapshots
- Configuration backups in Git
- Secret backups in Pulumi

## Cost Optimization

1. **Right-sizing**
   - Monitor actual resource usage
   - Adjust requests/limits accordingly
   - Use spot instances where possible

2. **Auto-scaling**
   - Configure HPA properly
   - Set appropriate thresholds
   - Schedule scaling for known patterns

3. **Storage**
   - Clean old model cache
   - Use appropriate storage classes
   - Compress large files 