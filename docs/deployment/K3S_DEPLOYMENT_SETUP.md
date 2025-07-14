# K3s Deployment Setup Instructions

## Prerequisites

1. **Lambda Labs Access**
   - Server IP: 192.222.58.232
   - SSH access configured
   - K3s installed and running

2. **Local Prerequisites**
   - kubectl installed
   - SSH key for Lambda Labs

## Setup Steps

### 1. Get K3s Kubeconfig

SSH into Lambda Labs and get the kubeconfig:

```bash
ssh user@192.222.58.232
sudo cat /etc/rancher/k3s/k3s.yaml
```

### 2. Configure Local kubectl

Save the kubeconfig locally and update the server address:

```bash
# Create .kube directory
mkdir -p ~/.kube

# Save kubeconfig (paste the content from step 1)
cat > ~/.kube/k3s-lambda-labs

# Update the server address in the file
# Change server: https://127.0.0.1:6443
# To: server: https://192.222.58.232:6443

# Set KUBECONFIG environment variable
export KUBECONFIG=~/.kube/k3s-lambda-labs
```

### 3. Test Connection

```bash
kubectl cluster-info
kubectl get nodes
```

### 4. Deploy Sophia AI

```bash
# Deploy using kustomize
kubectl apply -k kubernetes/overlays/production

# Check deployment
kubectl get all -n sophia-ai-prod
```

## GitHub Actions Setup

Add these secrets to your GitHub repository:

1. **DOCKER_HUB_USERNAME**: Your Docker Hub username
2. **DOCKER_HUB_ACCESS_TOKEN**: Docker Hub access token
3. **LAMBDA_LABS_KUBECONFIG**: Base64 encoded kubeconfig
   ```bash
   cat ~/.kube/k3s-lambda-labs | base64
   ```

## Monitoring

Check deployment status:
```bash
kubectl get pods -n sophia-ai-prod
kubectl logs -f deployment/sophia-api -n sophia-ai-prod
```

## Troubleshooting

If pods are not starting:
```bash
kubectl describe pod <pod-name> -n sophia-ai-prod
kubectl get events -n sophia-ai-prod
```
