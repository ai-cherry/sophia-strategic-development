# GitHub Secrets Setup for Sophia AI

## Required Secrets

Add these secrets to your GitHub repository settings:

### 1. Docker Hub Credentials
- **DOCKER_HUB_USERNAME**: Your Docker Hub username
- **DOCKER_HUB_ACCESS_TOKEN**: Docker Hub access token (not password)

### 2. Lambda Labs Kubeconfig
- **LAMBDA_LABS_KUBECONFIG**: Base64 encoded kubeconfig

To encode your kubeconfig:
```bash
cat ~/.kube/lambda-labs-k3s | base64 -w 0
```

## Adding Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret with the exact names above

## Verification

After adding secrets, the deployment workflow will trigger automatically on push to main.

Monitor the deployment:
- GitHub Actions tab in your repository
- Lambda Labs K3s cluster: `kubectl get pods -n sophia-ai-prod`
