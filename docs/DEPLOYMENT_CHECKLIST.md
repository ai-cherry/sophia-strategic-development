# Sophia AI Deployment Checklist

## Pre-Deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Snowflake connection verified
- [ ] MCP servers health check

## Deployment Steps
1. Build Docker image: `docker build -t sophia-ai .`
2. Run health checks: `python scripts/health_check.py`
3. Deploy: `docker-compose up -d`
4. Verify: `curl http://localhost:8000/health`

## Post-Deployment
- [ ] Monitor logs for errors
- [ ] Test chat endpoint
- [ ] Verify MCP connectivity
- [ ] Check performance metrics
