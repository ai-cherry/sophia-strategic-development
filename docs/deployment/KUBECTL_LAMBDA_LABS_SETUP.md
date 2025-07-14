# 🚀 Kubectl Configuration for Lambda Labs K3s

This guide will help you configure kubectl to connect to your Lambda Labs K3s cluster for Sophia AI deployment.

## Prerequisites

1. **kubectl installed** on your local machine
   ```bash
   # macOS
   brew install kubectl
   
   # Or download directly
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl"
   chmod +x kubectl
   sudo mv kubectl /usr/local/bin/
   ```

2. **Lambda Labs instance** with K3s installed
   - Instance IP: 192.222.58.232
   - SSH access configured

## Step 1: Get K3s Kubeconfig from Lambda Labs

1. SSH into your Lambda Labs instance:
   ```bash
   ssh ubuntu@192.222.58.232
   ```

2. Get the K3s kubeconfig:
   ```bash
   sudo cat /etc/rancher/k3s/k3s.yaml
   ```

3. Copy the entire output (it's a YAML file)

## Step 2: Configure Local Kubeconfig

1. Create/edit your local kubeconfig:
   ```bash
   mkdir -p ~/.kube
   nano ~/.kube/k3s-lambda-labs
   ```

2. Paste the K3s config and modify the server URL:
   - Change `server: https://127.0.0.1:6443` to `server: https://192.222.58.232:6443`
   - Save the file

3. Example kubeconfig structure:
   ```yaml
   apiVersion: v1
   clusters:
   - cluster:
       certificate-authority-data: [BASE64_CERT_DATA]
       server: https://192.222.58.232:6443  # Changed from 127.0.0.1
     name: default
   contexts:
   - context:
       cluster: default
       user: default
     name: k3s-lambda-labs
   current-context: k3s-lambda-labs
   kind: Config
   preferences: {}
   users:
   - name: default
     user:
       client-certificate-data: [BASE64_CLIENT_CERT]
       client-key-data: [BASE64_CLIENT_KEY]
   ```

## Step 3: Set KUBECONFIG Environment Variable

1. Add to your shell profile (`~/.zshrc` or `~/.bashrc`):
   ```bash
   export KUBECONFIG=$HOME/.kube/k3s-lambda-labs
   ```

2. Reload your shell:
   ```bash
   source ~/.zshrc  # or ~/.bashrc
   ```

## Step 4: Verify Connection

1. Test kubectl connection:
   ```bash
   kubectl get nodes
   ```
   
   Expected output:
   ```
   NAME               STATUS   ROLES                  AGE   VERSION
   lambda-labs-node   Ready    control-plane,master   7d    v1.27.3+k3s1
   ```

2. Check cluster info:
   ```bash
   kubectl cluster-info
   ```

## Step 5: Create Sophia AI Namespace

```bash
kubectl create namespace sophia-ai-prod
kubectl config set-context --current --namespace=sophia-ai-prod
```

## Step 6: Add GitHub Secrets for Automated Deployment

1. Go to your GitHub repository settings:
   https://github.com/ai-cherry/sophia-main/settings/secrets/actions

2. Add these repository secrets:

   **DOCKER_HUB_USERNAME**
   ```
   scoobyjava15
   ```

   **DOCKER_HUB_ACCESS_TOKEN**
   ```
   [Your Docker Hub Personal Access Token]
   ```

   **LAMBDA_LABS_KUBECONFIG**
   ```bash
   # Base64 encode your kubeconfig
   base64 < ~/.kube/k3s-lambda-labs | tr -d '\n'
   ```
   Copy the output and paste as the secret value

## Step 7: Deploy Sophia AI

### Option 1: Automated Deployment (Recommended)
Push to main branch to trigger the GitHub Actions workflow:
```bash
git push origin main
```

The workflow will:
1. Build Docker images
2. Push to Docker Hub
3. Deploy to K3s cluster

### Option 2: Manual Deployment
```bash
# Apply all K8s manifests
kubectl apply -k k8s/overlays/production

# Check deployment status
kubectl get all -n sophia-ai-prod

# Watch pods starting
kubectl get pods -n sophia-ai-prod -w
```

## Step 8: Verify Deployment

1. Check pod status:
   ```bash
   kubectl get pods -n sophia-ai-prod
   ```

2. Check services:
   ```bash
   kubectl get svc -n sophia-ai-prod
   ```

3. Get ingress URL:
   ```bash
   kubectl get ingress -n sophia-ai-prod
   ```

4. Port forward for local testing:
   ```bash
   # Backend API
   kubectl port-forward -n sophia-ai-prod svc/sophia-api 8001:8001
   
   # Frontend
   kubectl port-forward -n sophia-ai-prod svc/sophia-frontend 3000:3000
   ```

## Troubleshooting

### Connection Refused
- Ensure Lambda Labs instance firewall allows port 6443
- Verify the IP address is correct
- Check K3s is running: `sudo systemctl status k3s`

### Certificate Issues
- Ensure the certificate-authority-data is not corrupted
- Try using `--insecure-skip-tls-verify` flag for testing

### Permission Denied
- Ensure your user has proper RBAC permissions
- Check the service account token is valid

## Next Steps

1. Set up monitoring with Prometheus/Grafana
2. Configure automatic backups
3. Set up log aggregation
4. Configure SSL/TLS ingress

## Quick Reference

```bash
# Switch to Sophia namespace
kubectl config set-context --current --namespace=sophia-ai-prod

# Get all resources
kubectl get all

# Describe a pod
kubectl describe pod <pod-name>

# Check logs
kubectl logs -f <pod-name>

# Execute into a pod
kubectl exec -it <pod-name> -- /bin/bash

# Scale deployment
kubectl scale deployment sophia-api --replicas=3

# Update deployment
kubectl set image deployment/sophia-api sophia-api=scoobyjava15/sophia-ai:latest
```

---

**Important**: Keep your kubeconfig secure. It provides full access to your cluster. 