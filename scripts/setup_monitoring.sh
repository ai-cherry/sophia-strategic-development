#!/bin/bash
set -e

echo "📊 Setting up monitoring and health checks"

# Install Prometheus and Grafana
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring

# Install Grafana dashboards for Sophia AI
kubectl apply -f k8s/monitoring/

echo "✅ Monitoring setup complete!"
echo "📊 Grafana: http://localhost:3000 (port-forward required)"
echo "📈 Prometheus: http://localhost:9090 (port-forward required)"