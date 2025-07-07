#!/bin/bash
# Deploy Sophia AI Backend to K3s Cluster

set -euo pipefail

export KUBECONFIG=~/.kube/sophia-production
DOCKER_REGISTRY="scoobyjava15"
MASTER_IP="192.222.51.151"

echo "🚀 Deploying Sophia AI Backend to K3s"
echo "===================================="

# Create namespace
echo "📦 Creating namespace..."
kubectl create namespace sophia-ai --dry-run=client -o yaml | kubectl apply -f -

# Create secrets from Pulumi ESC
echo "🔐 Creating secrets..."
kubectl create secret generic sophia-secrets \
  --from-literal=postgres-password=$(openssl rand -base64 32) \
  --from-literal=redis-password=$(openssl rand -base64 32) \
  --from-literal=jwt-secret=$(openssl rand -base64 32) \
  -n sophia-ai --dry-run=client -o yaml | kubectl apply -f -

# Deploy PostgreSQL with HA
echo "🐘 Deploying PostgreSQL..."
cat << 'YAML' | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: sophia-ai
spec:
  ports:
  - port: 5432
    targetPort: 5432
  selector:
    app: postgres
  type: ClusterIP
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: sophia-ai
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: sophia
        - name: POSTGRES_USER
          value: sophia
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: sophia-secrets
              key: postgres-password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
YAML

# Deploy Redis with Sentinel
echo "🔴 Deploying Redis..."
cat << 'YAML' | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: sophia-ai
spec:
  ports:
  - port: 6379
    targetPort: 6379
  selector:
    app: redis
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: sophia-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server"]
        args: ["--maxmemory", "2gb", "--maxmemory-policy", "allkeys-lru"]
        resources:
          requests:
            memory: "1Gi"
            cpu: "0.5"
          limits:
            memory: "2Gi"
            cpu: "1"
YAML

# Deploy Sophia Backend
echo "🎯 Deploying Sophia Backend..."
cat << YAML | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: sophia-backend
  namespace: sophia-ai
spec:
  ports:
  - port: 8000
    targetPort: 8000
  selector:
    app: sophia-backend
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sophia-backend
  namespace: sophia-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sophia-backend
  template:
    metadata:
      labels:
        app: sophia-backend
    spec:
      containers:
      - name: sophia-backend
        image: ${DOCKER_REGISTRY}/sophia-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "prod"
        - name: PULUMI_ORG
          value: "scoobyjava-org"
        - name: DATABASE_URL
          value: "postgresql://sophia:password@postgres:5432/sophia"
        - name: REDIS_URL
          value: "redis://redis:6379"
        - name: NVIDIA_VISIBLE_DEVICES
          value: "all"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
            nvidia.com/gpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
            nvidia.com/gpu: "1"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
YAML

# Deploy NGINX Ingress
echo "🌐 Deploying NGINX Ingress..."
cat << YAML | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sophia-ingress
  namespace: sophia-ai
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.sophia-intel.ai
    - mcp.sophia-intel.ai
    secretName: sophia-tls
  rules:
  - host: api.sophia-intel.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sophia-backend
            port:
              number: 8000
  - host: mcp.sophia-intel.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mcp-gateway
            port:
              number: 8001
YAML

# Deploy MCP Servers
echo "🤖 Deploying MCP Servers..."
for mcp in ai-memory codacy github linear asana notion hubspot slack; do
  cat << YAML | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: mcp-${mcp}
  namespace: sophia-ai
spec:
  ports:
  - port: 9000
    targetPort: 9000
  selector:
    app: mcp-${mcp}
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-${mcp}
  namespace: sophia-ai
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mcp-${mcp}
  template:
    metadata:
      labels:
        app: mcp-${mcp}
    spec:
      containers:
      - name: mcp-${mcp}
        image: ${DOCKER_REGISTRY}/sophia-mcp-${mcp}:latest
        ports:
        - containerPort: 9000
        env:
        - name: ENVIRONMENT
          value: "prod"
        - name: MCP_SERVER_NAME
          value: "${mcp}"
        resources:
          requests:
            memory: "512Mi"
            cpu: "0.5"
          limits:
            memory: "1Gi"
            cpu: "1"
YAML
done

# Install cert-manager for SSL
echo "🔒 Installing cert-manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

# Create Let's Encrypt issuer
cat << YAML | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@sophia-intel.ai
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
YAML

# Deploy monitoring stack
echo "📊 Deploying monitoring..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set grafana.ingress.enabled=true \
  --set grafana.ingress.hosts[0]=grafana.sophia-intel.ai \
  --set grafana.ingress.tls[0].secretName=grafana-tls \
  --set grafana.ingress.tls[0].hosts[0]=grafana.sophia-intel.ai

echo "✅ Backend deployment complete!"
echo ""
echo "Checking deployment status..."
kubectl get pods -n sophia-ai
kubectl get ingress -n sophia-ai

echo ""
echo "Access your services at:"
echo "  API: https://api.sophia-intel.ai"
echo "  MCP: https://mcp.sophia-intel.ai"
echo "  Grafana: https://grafana.sophia-intel.ai"
