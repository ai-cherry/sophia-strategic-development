# MCP Server Kubernetes Deployment Patterns

**Date:** July 10, 2025  
**Purpose:** Standardized patterns for deploying MCP servers on K3s/Kubernetes

## 🎯 Overview

This document provides standardized deployment patterns for MCP servers as we migrate from Docker Swarm to Kubernetes. All patterns are designed to work with K3s initially and scale to full Kubernetes.

## 📋 Standard MCP Server Deployment

### 1. Deployment Manifest Template

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-{server-name}
  namespace: sophia-ai
  labels:
    app: mcp-{server-name}
    tier: mcp
    version: v{version}
spec:
  replicas: 2  # Default to 2 for HA
  selector:
    matchLabels:
      app: mcp-{server-name}
  template:
    metadata:
      labels:
        app: mcp-{server-name}
        tier: mcp
        version: v{version}
    spec:
      containers:
      - name: {server-name}
        image: scoobyjava15/mcp-{server-name}:v{version}
        ports:
        - containerPort: {port}
          name: mcp
        env:
        - name: ENVIRONMENT
          value: "prod"
        - name: PULUMI_ORG
          value: "scoobyjava-org"
        - name: SERVER_PORT
          value: "{port}"
        envFrom:
        - secretRef:
            name: mcp-{server-name}-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
        livenessProbe:
          httpGet:
            path: /health
            port: mcp
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: mcp
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: mcp-{server-name}-config
```

### 2. Service Manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mcp-{server-name}
  namespace: sophia-ai
  labels:
    app: mcp-{server-name}
spec:
  type: ClusterIP
  ports:
  - port: {port}
    targetPort: mcp
    protocol: TCP
    name: mcp
  selector:
    app: mcp-{server-name}
```

### 3. ConfigMap for Server Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-{server-name}-config
  namespace: sophia-ai
data:
  server-config.json: |
    {
      "name": "{server-name}",
      "version": "{version}",
      "port": {port},
      "tools": {tool-count},
      "description": "{description}"
    }
```

### 4. Secret Management with External Secrets Operator

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: mcp-{server-name}-secrets
  namespace: sophia-ai
spec:
  secretStoreRef:
    name: pulumi-esc
    kind: SecretStore
  target:
    name: mcp-{server-name}-secrets
  data:
  - secretKey: API_KEY
    remoteRef:
      key: sophia.{service}.api_key
```

## 🚀 GPU-Enabled MCP Servers

For AI/ML workloads requiring GPU:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-ai-memory
  namespace: sophia-ai
spec:
  replicas: 1  # GPU servers typically single replica
  template:
    spec:
      nodeSelector:
        nvidia.com/gpu: "true"
        gpu-type: "GH200"  # or A100, A6000, etc.
      containers:
      - name: ai-memory
        image: scoobyjava15/mcp-ai-memory:v2.0.0
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
            nvidia.com/gpu: 1
          limits:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: 1
```

## 📊 Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mcp-{server-name}-hpa
  namespace: sophia-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcp-{server-name}
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 🔌 Inter-MCP Communication

### Service Discovery Pattern

```yaml
# MCP servers communicate via Kubernetes DNS
# Format: {service-name}.{namespace}.svc.cluster.local

# Example in Python code:
ELIMINATED_MCP_URL = "http://mcp-ELIMINATED.sophia-ai.svc.cluster.local:9001"
AI_MEMORY_MCP_URL = "http://mcp-ai-memory.sophia-ai.svc.cluster.local:9000"
```

### Network Policy for MCP Communication

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mcp-communication
  namespace: sophia-ai
spec:
  podSelector:
    matchLabels:
      tier: mcp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: mcp
    - podSelector:
        matchLabels:
          app: sophia-backend
    ports:
    - protocol: TCP
      port: 9000
      endPort: 9020  # MCP port range
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: mcp
    ports:
    - protocol: TCP
```

## 🎯 Deployment Order

### Phase 1: Core MCP Servers
1. ai_memory (GPU-enabled)
2. ELIMINATED_unified
3. github
4. slack

### Phase 2: Business Critical
5. gong_v2
6. hubspot_unified
7. linear_v2
8. codacy

### Phase 3: Extended Functionality
9. notion_v2
10. postgres
11. portkey_admin
12. figma_context

### Phase 4: Advanced Features
13. openrouter_search
14. lambda_labs_cli
15. asana
16. ui_ux_agent

## 🔧 Helm Chart Structure

```
helm/mcp-servers/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── externalsecret.yaml
│   ├── hpa.yaml
│   └── networkpolicy.yaml
└── values/
    ├── ai-memory.yaml
    ├── ELIMINATED.yaml
    ├── github.yaml
    └── ...
```

### Example values.yaml Override

```yaml
# values/gong.yaml
name: gong
port: 9005
replicas: 3
version: "2.0.0"
resources:
  requests:
    memory: "2Gi"
    cpu: "1"
  limits:
    memory: "4Gi"
    cpu: "2"
tools: 6
description: "Sales call analytics"
secrets:
  - name: GONG_API_KEY
    remoteRef: sophia.business.gong.api_key
```

## 📝 Migration Commands

```bash
# Convert existing MCP server to K8s
cd mcp-servers/{server-name}
kompose convert -f docker-compose.yml

# Deploy with kubectl
kubectl apply -f k8s/

# Deploy with Helm
helm install mcp-{server-name} ./helm/mcp-servers \
  -f ./helm/mcp-servers/values/{server-name}.yaml

# Check deployment
kubectl get pods -n sophia-ai -l tier=mcp
kubectl logs -n sophia-ai -l app=mcp-{server-name}
```

## 🚨 Important Notes

1. **Health Endpoints:** All MCP servers must implement `/health` and `/ready` endpoints
2. **Graceful Shutdown:** Handle SIGTERM for clean pod termination
3. **Logging:** Use structured JSON logging to stdout
4. **Metrics:** Expose Prometheus metrics on `/metrics`
5. **Secrets:** Never hardcode credentials - use External Secrets Operator

## ✅ Validation Checklist

Before deploying any MCP server to K8s:

- [ ] Docker image pushed to scoobyjava15 registry
- [ ] Health and ready endpoints implemented
- [ ] Resource requests/limits defined
- [ ] External secrets configured
- [ ] Network policies applied
- [ ] HPA configured (if applicable)
- [ ] Logging to stdout
- [ ] Graceful shutdown handling
- [ ] Inter-MCP communication tested
- [ ] Monitoring/metrics exposed 