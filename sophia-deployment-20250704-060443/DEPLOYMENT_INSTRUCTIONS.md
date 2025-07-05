# Sophia AI Deployment Instructions

## Prerequisites
1. SSH access to Lambda Labs (146.235.200.1)
2. Docker Swarm initialized
3. Required secrets set as environment variables

## Deployment Steps

### 1. Upload deployment package
```bash
# From your local machine
scp sophia-deployment-*.tar.gz ubuntu@146.235.200.1:~/
```

### 2. Connect to Lambda Labs
```bash
ssh ubuntu@146.235.200.1
```

### 3. Extract deployment package
```bash
tar -xzf sophia-deployment-*.tar.gz
cd sophia-deployment-*
```

### 4. Set required environment variables
```bash
# Set these with your actual values
export POSTGRES_PASSWORD="your-postgres-password"
export GRAFANA_PASSWORD="your-grafana-password"
export PULUMI_ACCESS_TOKEN="your-pulumi-token"
export MEM0_API_KEY="your-mem0-key"
export SNOWFLAKE_ACCOUNT="your-snowflake-account"
export SNOWFLAKE_USER="your-snowflake-user"
export SNOWFLAKE_PASSWORD="your-snowflake-password"
export VERCEL_V0DEV_API_KEY="your-vercel-key"
```

### 5. Run the deployment
```bash
# Make scripts executable
chmod +x *.sh

# Deploy the stack
./deploy_sophia_stack.sh
```

### 6. Monitor deployment
```bash
# Check service status
docker service ls

# Monitor performance
./monitor_swarm_performance.sh
```

## Post-Deployment

### Access URLs
- Dashboard: https://api.sophia-ai.lambda.cloud/dashboard
- Chat: https://chat-mcp.sophia-ai.lambda.cloud
- API Docs: https://api.sophia-ai.lambda.cloud/docs
- Grafana: https://sophia-ai.lambda.cloud:3000
- Prometheus: https://sophia-ai.lambda.cloud:9090

### Troubleshooting
- Check logs: `docker service logs <service-name>`
- Scale service: `docker service scale sophia-ai_backend=3`
- Update service: `docker service update --force <service-name>`
