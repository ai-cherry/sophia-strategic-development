# Sophia AI Production Deployment Quick Guide

## 🚀 Quick Deployment (Automated)

Run the complete automated deployment:
```bash
./scripts/deploy_sophia_production_complete.sh
```

This will:
1. Build and deploy frontend to nginx
2. Configure nginx for React app serving
3. Deploy all MCP servers
4. Set up monitoring
5. Run verification tests
6. Generate deployment report

## 🔧 Manual Deployment Steps

### 1. Deploy Frontend (PRIORITY)
```bash
# Build frontend locally
cd frontend
npm run build
tar -czf sophia-frontend.tar.gz dist/*

# Copy to server
scp -i ~/.ssh/sophia_correct_key sophia-frontend.tar.gz ubuntu@192.222.58.232:/tmp/

# SSH to server
ssh -i ~/.ssh/sophia_correct_key ubuntu@192.222.58.232

# Deploy frontend
sudo mkdir -p /var/www/sophia-frontend
cd /var/www/sophia-frontend
sudo tar -xzf /tmp/sophia-frontend.tar.gz --strip-components=1
sudo chown -R www-data:www-data /var/www/sophia-frontend
```

### 2. Update Nginx Configuration
```bash
# On server
sudo nano /etc/nginx/sites-available/sophia-intel-ai

# Replace with the configuration from nginx-sophia-production.conf
# Key change: Set root to /var/www/sophia-frontend

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Deploy MCP Servers
```bash
# On server
cd ~/sophia-main
source venv/bin/activate

# Start MCP servers
python -m mcp_servers.ai_memory.ai_memory_mcp_server &
python -m mcp_servers.codacy.codacy_mcp_server &
python -m mcp_servers.github.github_mcp_server &
python -m mcp_servers.linear.linear_mcp_server &
python -m mcp_servers.slack.slack_mcp_server &
python -m mcp_servers.hubspot.hubspot_mcp_server &
```

## ✅ Verification

Run the verification script:
```bash
python scripts/verify_sophia_production.py
```

Or manually check:
- Frontend: https://sophia-intel.ai (should show React app)
- API: https://api.sophia-intel.ai/health
- Docs: https://api.sophia-intel.ai/docs

## 📊 Current Status

| Component | Status | URL |
|-----------|--------|-----|
| Backend API | ✅ Running | https://api.sophia-intel.ai |
| SSL Certificates | ✅ Active | Valid until Oct 2025 |
| DNS | ✅ Configured | All pointing to 192.222.58.232 |
| Frontend | ⚠️ Needs deployment | https://sophia-intel.ai |
| MCP Servers | ⚠️ Need verification | Ports 9000-9006 |

## 🔍 Monitoring

Check system health:
```bash
ssh -i ~/.ssh/sophia_correct_key ubuntu@192.222.58.232
./check_sophia_health.sh
```

View logs:
```bash
# Backend logs
sudo journalctl -u sophia-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# MCP server logs
tail -f ~/sophia-main/logs/*.log
```

## 🚨 Troubleshooting

### Frontend shows backend JSON
- Check nginx root directory points to `/var/www/sophia-frontend`
- Verify frontend files exist in that directory
- Check nginx error logs

### MCP servers not running
- Check if ports are already in use: `sudo lsof -i :9000`
- Check Python environment is activated
- Review logs in `~/sophia-main/logs/`

### SSL issues
- Certificates are valid until October 2025
- Auto-renewal is configured via cron
- Check with: `sudo certbot certificates`

## 📝 Post-Deployment

1. **Monitor for 24 hours** - Check logs and performance
2. **Set up backups** - Database and configuration backups
3. **Configure alerts** - Slack/email notifications for downtime
4. **Document issues** - Update runbooks with any problems found
5. **Performance tuning** - Optimize based on real usage

---

**Need help?** The full deployment plan is in `SOPHIA_AI_FULL_PRODUCTION_DEPLOYMENT_PLAN.md` 