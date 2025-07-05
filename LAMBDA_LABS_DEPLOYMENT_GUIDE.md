# Lambda Labs Docker Cloud Deployment Guide

## 🚀 Complete Deployment Solution

Everything is ready for Docker Cloud deployment on Lambda Labs. Here's what we've prepared:

## 📦 What's Ready

### 1. **Deployment Scripts**
- `scripts/quick_lambda_deploy.sh` - Quick deployment with minimal setup
- `scripts/deploy_lambda_labs_complete.sh` - Full deployment with all MCP servers
- `scripts/setup_lambda_deployment.sh` - Interactive setup wizard
- `scripts/one_command_deploy.sh` - Single command deployment

### 2. **Docker Images**
All services are configured to use Docker images from Docker Hub:
- Backend: `scoobyjava15/sophia-backend:latest`
- Frontend: `scoobyjava15/sophia-frontend:latest`
- MCP Servers: `scoobyjava15/sophia-*-mcp:latest`

### 3. **Docker Compose Configurations**
- Optimized for Docker Swarm
- All services configured with health checks
- Resource limits and auto-scaling
- Docker secrets for security

## 🔑 Prerequisites

### 1. **Lambda Labs Access**
You need:
- Lambda Labs API key
- SSH access to your Lambda Labs instance (146.235.200.1)
- The correct SSH private key that matches your Lambda Labs instance

### 2. **Set Up SSH Key**
Save your Lambda Labs SSH private key:
```bash
# Create the key file
cat > ~/.ssh/lambda_labs_sophia << 'EOF'
[PASTE YOUR ACTUAL SSH PRIVATE KEY HERE]
EOF

# Set correct permissions
chmod 600 ~/.ssh/lambda_labs_sophia

# Test connection
ssh -i ~/.ssh/lambda_labs_sophia ubuntu@146.235.200.1 'echo "Connected!"'
```

## 🚀 Deployment Steps

### Option 1: Quick Deployment (Recommended)
```bash
# Set up environment
export LAMBDA_API_KEY="your-lambda-api-key"
export LAMBDA_SSH_KEY_PATH=~/.ssh/lambda_labs_sophia

# Run quick deployment
./scripts/quick_lambda_deploy.sh
```

### Option 2: Full Deployment with All Services
```bash
# Set up environment
export LAMBDA_API_KEY="your-lambda-api-key"
export PULUMI_ACCESS_TOKEN="your-pulumi-token"

# Run setup wizard
./scripts/setup_lambda_deployment.sh
# Choose option 5 (Do everything)

# Deploy
./scripts/deploy_lambda_labs_complete.sh
```

### Option 3: Manual Deployment
```bash
# 1. Create deployment package
./scripts/prepare_deployment_package.sh

# 2. Upload to Lambda Labs
scp -i ~/.ssh/lambda_labs_sophia sophia-deployment-*.tar.gz ubuntu@146.235.200.1:~/

# 3. SSH to Lambda Labs
ssh -i ~/.ssh/lambda_labs_sophia ubuntu@146.235.200.1

# 4. On Lambda Labs, extract and deploy
tar -xzf sophia-deployment-*.tar.gz
cd sophia-deployment-*
./deploy.sh
```

## 🌐 Access Your Services

After deployment, access your services at:

### Direct IP Access (Immediate)
- **Backend API**: http://146.235.200.1:8000
- **Frontend**: http://146.235.200.1:3000
- **API Documentation**: http://146.235.200.1:8000/docs
- **Grafana**: http://146.235.200.1:3001
- **Prometheus**: http://146.235.200.1:9090

### MCP Servers
- **AI Memory**: http://146.235.200.1:9001
- **Dashboard**: http://146.235.200.1:9100
- **Chat**: http://146.235.200.1:9101
- **Codacy**: http://146.235.200.1:3008
- **Prompt Optimizer**: http://146.235.200.1:9030

## 🔧 Managing Your Deployment

### Check Service Status
```bash
ssh -i ~/.ssh/lambda_labs_sophia ubuntu@146.235.200.1 'docker service ls'
```

### View Logs
```bash
ssh -i ~/.ssh/lambda_labs_sophia ubuntu@146.235.200.1 'docker service logs sophia-ai_backend'
```

### Scale Services
```bash
ssh -i ~/.ssh/lambda_labs_sophia ubuntu@146.235.200.1 'docker service scale sophia-ai_backend=5'
```

### Update Services
```bash
# Build and push new image
docker build -t scoobyjava15/sophia-backend:latest .
docker push scoobyjava15/sophia-backend:latest

# Update on Lambda Labs
ssh -i ~/.ssh/lambda_labs_sophia ubuntu@146.235.200.1 \
  'docker service update --image scoobyjava15/sophia-backend:latest sophia-ai_backend'
```

## 🔒 Security Notes

1. **Never commit credentials** - Use environment variables
2. **Use Docker secrets** - All sensitive data goes through Docker secrets
3. **Pulumi ESC integration** - Secrets are managed centrally
4. **Network isolation** - Services communicate through overlay networks

## 🚨 Troubleshooting

### SSH Connection Issues
```bash
# Check your SSH key
ls -la ~/.ssh/lambda_labs_sophia

# Test with verbose output
ssh -vvv -i ~/.ssh/lambda_labs_sophia ubuntu@146.235.200.1
```

### Docker Swarm Issues
```bash
# Initialize Swarm if needed
ssh -i ~/.ssh/lambda_labs_sophia ubuntu@146.235.200.1 \
  'docker swarm init --advertise-addr 146.235.200.1'
```

### Service Not Starting
```bash
# Check service status
ssh -i ~/.ssh/lambda_labs_sophia ubuntu@146.235.200.1 \
  'docker service ps sophia-ai_backend --no-trunc'
```

## 📊 Lambda Labs API Usage

Check your instance status:
```bash
export LAMBDA_API_KEY="your-api-key"
curl -u "${LAMBDA_API_KEY}:" https://cloud.lambda.ai/api/v1/instances | jq
```

## 🎯 Summary

1. **Everything is containerized** - All services run in Docker
2. **Swarm orchestration** - High availability and scaling
3. **Secure by default** - Docker secrets and network isolation
4. **Easy deployment** - Single script deployment
5. **Full monitoring** - Prometheus and Grafana included

Just set up your SSH key correctly and run the deployment scripts!
