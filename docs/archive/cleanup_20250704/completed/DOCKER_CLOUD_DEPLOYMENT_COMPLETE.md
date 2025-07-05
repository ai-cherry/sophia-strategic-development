# Docker Cloud Deployment Complete Guide

## 🚀 Everything is Docker Cloud Ready!

As requested, **everything** in Sophia AI is now configured for Docker Cloud deployment on Lambda Labs.

## 📦 What's Ready

### 1. **Docker Compose Cloud Configuration**
- `docker-compose.production.yml` - Main production configuration
- Optimized for Docker Swarm on Lambda Labs
- All services use Docker secrets (no .env files)
- Health checks on all services
- Resource limits configured
- Auto-scaling ready

### 2. **MCP Servers Dockerized**
All MCP servers have Docker configurations:
- Dashboard MCP (port 9100)
- Chat MCP (port 9101)
- Codacy MCP (port 3008)
- AI Memory MCP (port 9001)
- Prompt Optimizer MCP (port 9030)
- And 20+ more...

### 3. **Monitoring Stack**
- Prometheus (metrics collection)
- Grafana (dashboards)
- Node Exporter (system metrics)
- cAdvisor (container metrics)

### 4. **Deployment Scripts**
- `scripts/prepare_deployment_package.sh` - Creates deployment package
- `scripts/one_command_deploy.sh` - Single command deployment on Lambda Labs
- `scripts/monitor_swarm_performance.sh` - Performance monitoring

## 🎯 One-Command Deployment

### Step 1: Create Deployment Package (on your local machine)
```bash
./scripts/prepare_deployment_package.sh
```

This creates `sophia-deployment-<timestamp>.tar.gz` with everything needed.

### Step 2: Upload to Lambda Labs
```bash
scp sophia-deployment-*.tar.gz ubuntu@146.235.200.1:~/
```

### Step 3: SSH to Lambda Labs and Deploy
```bash
ssh ubuntu@146.235.200.1

# Extract and run one-command deployment
tar -xzf sophia-deployment-*.tar.gz
cd sophia-deployment-*
./one_command_deploy.sh
```

That's it! The script handles everything:
- ✅ Docker Swarm initialization check
- ✅ Environment variable setup
- ✅ Docker secrets creation
- ✅ Stack deployment
- ✅ MCP server deployment
- ✅ Health monitoring
- ✅ Status reporting

## 🔧 What the Deployment Includes

### Core Services
```yaml
- Backend API (3 replicas, auto-scaling)
- Frontend (2 replicas)
- PostgreSQL (with persistent volume)
- Redis (with persistence)
- Nginx (load balancer)
```

### AI Services
```yaml
- Mem0 Server (persistent memory)
- Snowflake Cortex integration
- LangGraph orchestration
- Unified Chat service
```

### MCP Servers
```yaml
- 25+ specialized MCP servers
- All with health checks
- Resource limits configured
- Auto-restart on failure
```

### Monitoring
```yaml
- Prometheus (metrics)
- Grafana (visualization)
- Custom dashboards
- Alert rules
```

## 🌐 Access Points

### Immediate Access (Using IP Address)
After deployment, you can immediately access your services at:

- **Backend API**: http://146.235.200.1:8000
- **Frontend Dashboard**: http://146.235.200.1:3000
- **API Documentation**: http://146.235.200.1:8000/docs
- **Grafana Monitoring**: http://146.235.200.1:3000 (port 3000 for Grafana)
- **Prometheus Metrics**: http://146.235.200.1:9090
- **Dashboard MCP**: http://146.235.200.1:9100
- **Chat MCP**: http://146.235.200.1:9101
- **Codacy MCP**: http://146.235.200.1:3008

### Future Access (After DNS Setup)
Once you configure DNS (see instructions below), you'll access via:

- **Dashboard**: https://api.sophia-ai.lambda.cloud/dashboard
- **Chat Interface**: https://chat-mcp.sophia-ai.lambda.cloud
- **API Documentation**: https://api.sophia-ai.lambda.cloud/docs

## 🔗 DNS Configuration

To use the custom domain names, you need to:

1. **Own a domain** (e.g., sophia-ai.lambda.cloud)
2. **Configure DNS records** pointing to Lambda Labs IP (146.235.200.1)
3. **Set up SSL certificates** (Let's Encrypt recommended)

### Example DNS Records:
```
Type  Name                          Value
A     api.sophia-ai.lambda.cloud    146.235.200.1
A     chat-mcp.sophia-ai.lambda.cloud  146.235.200.1
A     *.sophia-ai.lambda.cloud      146.235.200.1
```

## 🔒 Security

All deployed with enterprise security:
- Docker secrets (no exposed credentials)
- Network isolation (overlay networks)
- Resource limits (prevent DoS)
- Health checks (auto-recovery)
- TLS/SSL ready (with Nginx)

## 📊 Monitoring Your Deployment

### Check Service Status
```bash
docker service ls
```

### View Logs
```bash
docker service logs sophia-ai_backend
docker service logs sophia-ai_frontend
```

### Monitor Performance
```bash
./monitor_swarm_performance.sh
```

### Scale Services
```bash
docker service scale sophia-ai_backend=5
docker service scale sophia-ai_chat-mcp=5
```

## 🚨 Troubleshooting

### If Services Don't Start
1. Check logs: `docker service logs <service-name>`
2. Verify secrets: `docker secret ls`
3. Check resources: `docker node ls`

### Common Issues
- **Port conflicts**: Ensure ports are free
- **Memory limits**: Adjust in docker-compose.production.yml
- **Network issues**: Check overlay network: `docker network ls`

## 🎉 Success Indicators

You know deployment is successful when:
- ✅ All services show desired replicas
- ✅ Health checks passing (green in Grafana)
- ✅ Can access services via IP address
- ✅ API docs load at http://146.235.200.1:8000/docs
- ✅ No error logs in services

## 📈 Next Steps

1. **Test with IP addresses first** - Verify everything works
2. **Configure DNS**: Point your domain to Lambda Labs IP
3. **Set up SSL**: Use Let's Encrypt with Nginx
4. **Configure Backups**: Set up automated PostgreSQL backups
5. **Fine-tune Scaling**: Adjust replicas based on load
6. **Set up Alerts**: Configure Grafana alerts

## 🔄 Updates and Maintenance

To update the deployment:

1. Build new images locally
2. Push to Docker Hub
3. On Lambda Labs: `docker service update --image <new-image> <service>`

Or use the full redeployment:
```bash
./one_command_deploy.sh
```

## 💡 Key Benefits of Docker Cloud Deployment

- **High Availability**: Multi-replica services
- **Auto-scaling**: Based on CPU/memory
- **Self-healing**: Automatic container restart
- **Load Balancing**: Built-in with Swarm
- **Rolling Updates**: Zero-downtime deployments
- **Resource Efficiency**: Optimized container usage
- **Centralized Logs**: All logs in one place
- **Unified Networking**: Secure overlay networks

## 🎯 Summary

Everything in Sophia AI is now:
- ✅ Dockerized with production configs
- ✅ Optimized for Lambda Labs infrastructure
- ✅ Ready for one-command deployment
- ✅ Monitored with Prometheus/Grafana
- ✅ Secured with Docker secrets
- ✅ Scalable with Docker Swarm

Just run `./one_command_deploy.sh` on Lambda Labs and you're live! 🚀
