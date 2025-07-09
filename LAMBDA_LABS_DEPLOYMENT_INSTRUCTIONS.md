# 🚀 SOPHIA AI LAMBDA LABS DEPLOYMENT INSTRUCTIONS
**Date**: July 5, 2025
**Target**: sophia-platform-prod (192.222.58.232)
**Status**: Ready for Manual Deployment

## 📋 DEPLOYMENT SUMMARY

### ✅ COMPLETED PREPARATIONS
- **Docker Image**: `scoobyjava15/sophia-ai:latest` (3.19GB) - Successfully built and pushed
- **Deployment Script**: `SOPHIA_LAMBDA_DEPLOYMENT_SCRIPT.sh` - Comprehensive production deployment
- **Lambda Labs API**: Working and instance verified active
- **Environment**: Production-ready with all configurations

### 🎯 DEPLOYMENT TARGET
- **Instance**: sophia-platform-prod
- **ID**: 959035912afe4b52b9c126b138a52ab5
- **IP**: 192.222.58.232
- **Private IP**: 10.19.50.155
- **Status**: Active
- **SSH Key**: sophia2025 (configured)

## 🔧 MANUAL DEPLOYMENT METHODS

### METHOD 1: Lambda Labs Web Interface (Recommended)

1. **Access Lambda Labs Console**
   - Go to https://cloud.lambdalabs.com/
   - Navigate to your instances
   - Click on "sophia-platform-prod"

2. **Open Web Terminal**
   - Click "Connect" or "Terminal" button
   - This opens a browser-based terminal

3. **Upload Deployment Script**
   - Copy the contents of `SOPHIA_LAMBDA_DEPLOYMENT_SCRIPT.sh`
   - In the terminal, create the file:
     ```bash
     nano /tmp/deploy-sophia.sh
     ```
   - Paste the script content
   - Save with Ctrl+X, Y, Enter

4. **Execute Deployment**
   ```bash
   chmod +x /tmp/deploy-sophia.sh
   sudo /tmp/deploy-sophia.sh
   ```

### METHOD 2: Copy-Paste Deployment Commands

If the web interface has limitations, run these commands one by one:

```bash
# 1. System update
sudo apt-get update -y && sudo apt-get upgrade -y

# 2. Install Docker (if needed)
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# 3. Clean up existing containers
sudo docker stop sophia-ai-production 2>/dev/null || true
sudo docker rm sophia-ai-production 2>/dev/null || true

# 4. Pull latest image
sudo docker pull scoobyjava15/sophia-ai:latest

# 5. Create environment file
sudo tee /opt/sophia-ai-production.env << EOF
ENVIRONMENT=production
PULUMI_ORG=scoobyjava-org
PORT=8000
LAMBDA_LABS_INSTANCE_TYPE=gpu_1x_a10
LAMBDA_LABS_REGION=us-west-1
LAMBDA_LABS_DEPLOYMENT_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SOPHIA_AI_VERSION=3.0.0
SOPHIA_AI_DEPLOYMENT_ID=lambda-production-$(date +%s)
SOPHIA_AI_LOG_LEVEL=info
EOF

# 6. Deploy container
sudo docker run -d \
  --name sophia-ai-production \
  --restart always \
  -p 80:8000 \
  -p 443:8000 \
  --env-file /opt/sophia-ai-production.env \
  --memory="6g" \
  --cpus="3.0" \
  --health-cmd="curl -f http://localhost:8000/api/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-start-period=40s \
  --health-retries=3 \
  scoobyjava15/sophia-ai:latest

# 7. Wait and check
sleep 30
sudo docker ps | grep sophia-ai-production
curl -f http://localhost:8000/api/health
```

### METHOD 3: Alternative SSH Approach

If you have the correct private key:

1. **Save the private key** to `~/.ssh/lambda_labs_private_key`
2. **Set permissions**: `chmod 600 ~/.ssh/lambda_labs_private_key`
3. **Test connection**: `ssh -i ~/.ssh/lambda_labs_private_key ubuntu@192.222.58.232`
4. **Upload and run script**:
   ```bash
   scp -i ~/.ssh/lambda_labs_private_key SOPHIA_LAMBDA_DEPLOYMENT_SCRIPT.sh ubuntu@192.222.58.232:/tmp/
   ssh -i ~/.ssh/lambda_labs_private_key ubuntu@192.222.58.232 "chmod +x /tmp/SOPHIA_LAMBDA_DEPLOYMENT_SCRIPT.sh && sudo /tmp/SOPHIA_LAMBDA_DEPLOYMENT_SCRIPT.sh"
   ```

## 🔍 DEPLOYMENT VERIFICATION

After deployment, verify these endpoints:

### Health Checks
- **Internal Health**: `curl http://localhost:8000/api/health`
- **External Health**: `curl http://192.222.58.232/api/health`
- **Container Status**: `sudo docker ps | grep sophia-ai-production`
- **Container Health**: `sudo docker inspect --format='{{.State.Health.Status}}' sophia-ai-production`

### Access URLs
- **Main API**: http://192.222.58.232/
- **Health Check**: http://192.222.58.232/api/health
- **API Documentation**: http://192.222.58.232/docs

## 📊 MONITORING COMMANDS

### Container Monitoring
```bash
# View container logs
sudo docker logs sophia-ai-production

# Follow logs in real-time
sudo docker logs -f sophia-ai-production

# Container resource usage
sudo docker stats sophia-ai-production

# Container health
sudo docker inspect --format='{{.State.Health.Status}}' sophia-ai-production
```

### System Monitoring
```bash
# System resources
htop

# Disk usage
df -h

# Network connections
netstat -tlnp | grep :80

# Check if ports are open
sudo netstat -tlnp | grep :8000
```

## 🚨 TROUBLESHOOTING

### Container Won't Start
```bash
# Check logs
sudo docker logs sophia-ai-production

# Restart container
sudo docker restart sophia-ai-production

# Check environment file
cat /opt/sophia-ai-production.env
```

### Health Check Failures
```bash
# Test internal health
curl -v http://localhost:8000/api/health

# Check container processes
sudo docker exec sophia-ai-production ps aux

# Check environment variables
sudo docker exec sophia-ai-production env
```

### External Access Issues
```bash
# Check nginx status
sudo systemctl status nginx

# Check nginx configuration
sudo nginx -t

# Check firewall
sudo ufw status

# Test port accessibility
telnet localhost 8000
```

## 🎯 EXPECTED RESULTS

### Successful Deployment Indicators
- ✅ Container status: `running`
- ✅ Health status: `healthy`
- ✅ HTTP 200 response from health endpoint
- ✅ API documentation accessible
- ✅ Nginx reverse proxy working
- ✅ Monitoring script running

### Performance Targets
- **Container Memory**: ~6GB allocation
- **CPU Usage**: ~3.0 cores
- **Response Time**: <200ms for health checks
- **Startup Time**: <60 seconds
- **Health Check Interval**: 30 seconds

## 📈 POST-DEPLOYMENT ACTIONS

1. **Update DNS Records** (if using custom domain)
2. **Configure SSL Certificate** (if HTTPS required)
3. **Set up log rotation** for container logs
4. **Configure backup scripts** for container data
5. **Set up automated health monitoring**
6. **Configure firewall rules** for security

## 🎉 SUCCESS CONFIRMATION

When deployment is successful, you should see:
```
🎉 SOPHIA AI DEPLOYMENT COMPLETED!
==================================================
✅ Container deployed and running
✅ Nginx reverse proxy configured
✅ Health monitoring active
✅ External access configured

🌐 ACCESS URLS:
  - Main API: http://192.222.58.232/
  - Health Check: http://192.222.58.232/api/health
  - API Documentation: http://192.222.58.232/docs

🚀 Sophia AI is now live on Lambda Labs!
```

## 📞 SUPPORT

If you encounter issues:
1. Check the troubleshooting section above
2. Review container logs: `sudo docker logs sophia-ai-production`
3. Verify the deployment script execution logs
4. Ensure all prerequisites are met

---

**Ready to deploy!** Choose Method 1 (Web Interface) for the easiest approach, or Method 2 (Copy-Paste) for step-by-step control.
