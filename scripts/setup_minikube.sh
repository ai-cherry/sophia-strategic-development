#!/bin/bash
# Setup Minikube for local Sophia AI testing

echo "🚀 Setting up Minikube for Sophia AI testing..."

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ Minikube not installed. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install minikube
    else
        # Linux
        curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
        sudo install minikube-linux-amd64 /usr/local/bin/minikube
    fi
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not installed. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install kubectl
    else
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        sudo install kubectl /usr/local/bin/kubectl
    fi
fi

# Start minikube with adequate resources
echo "🔧 Starting Minikube with GPU-ready config..."
minikube start \
    --cpus=4 \
    --memory=8192 \
    --disk-size=50g \
    --driver=docker \
    --kubernetes-version=v1.28.0

# Enable necessary addons
echo "📦 Enabling addons..."
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Create namespaces
echo "🏗️ Creating namespaces..."
kubectl create namespace sophia-ai-prod || true
kubectl create namespace mcp-servers || true
kubectl create namespace monitoring || true

# Set default namespace
kubectl config set-context --current --namespace=sophia-ai-prod

# Create secrets for Docker registry
echo "🔐 Creating Docker registry secret..."
kubectl create secret docker-registry regcred \
    --docker-server=docker.io \
    --docker-username=scoobyjava15 \
    --docker-password=${DOCKER_HUB_TOKEN} \
    --namespace=sophia-ai-prod || true

# Deploy local storage class
echo "💾 Creating storage class..."
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: k8s.io/minikube-hostpath
parameters:
  type: pd-ssd
reclaimPolicy: Delete
volumeBindingMode: Immediate
EOF

# Deploy Redis for local testing
echo "🔴 Deploying Redis..."
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: sophia-ai-prod
spec:
  replicas: 1
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
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: sophia-ai-prod
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
EOF

# Deploy PostgreSQL for local testing
echo "🐘 Deploying PostgreSQL..."
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgresql
  namespace: sophia-ai-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
      - name: postgresql
        image: pgvector/pgvector:pg16
        env:
        - name: POSTGRES_DB
          value: sophia
        - name: POSTGRES_USER
          value: sophia
        - name: POSTGRES_PASSWORD
          value: sophia
        ports:
        - containerPort: 5432
---
apiVersion: v1
kind: Service
metadata:
  name: postgresql
  namespace: sophia-ai-prod
spec:
  selector:
    app: postgresql
  ports:
  - port: 5432
    targetPort: 5432
EOF

# Deploy Weaviate for local testing
echo "🔍 Deploying Weaviate..."
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weaviate
  namespace: sophia-ai-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: weaviate
  template:
    metadata:
      labels:
        app: weaviate
    spec:
      containers:
      - name: weaviate
        image: semitechnologies/weaviate:1.25.4
        env:
        - name: AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED
          value: "true"
        - name: PERSISTENCE_DATA_PATH
          value: "/var/lib/weaviate"
        - name: DEFAULT_VECTORIZER_MODULE
          value: "none"
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: weaviate
  namespace: sophia-ai-prod
spec:
  selector:
    app: weaviate
  ports:
  - port: 8080
    targetPort: 8080
EOF

# Wait for services
echo "⏳ Waiting for services to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/redis -n sophia-ai-prod
kubectl wait --for=condition=available --timeout=300s deployment/postgresql -n sophia-ai-prod
kubectl wait --for=condition=available --timeout=300s deployment/weaviate -n sophia-ai-prod

# Display status
echo "✅ Minikube setup complete!"
echo ""
echo "📊 Cluster Status:"
kubectl get nodes
echo ""
echo "🚀 Services:"
kubectl get svc -n sophia-ai-prod
echo ""
echo "📦 Pods:"
kubectl get pods -n sophia-ai-prod
echo ""
echo "🔗 Access Services:"
echo "  Redis: $(minikube service redis -n sophia-ai-prod --url)"
echo "  PostgreSQL: $(minikube service postgresql -n sophia-ai-prod --url)"
echo "  Weaviate: $(minikube service weaviate -n sophia-ai-prod --url)"
echo ""
echo "📊 Dashboard: minikube dashboard" 