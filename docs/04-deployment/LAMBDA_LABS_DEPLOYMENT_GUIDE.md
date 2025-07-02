# Lambda Labs Quick Deployment Guide

This guide explains how to deploy the Sophia AI platform on Lambda Labs using our one-click deployment script.

## Prerequisites

- Access to the Pulumi ESC or GitHub Organization Secrets that store the following credentials:
  - Docker Hub: `DOCKER_USER_NAME`, `DOCKER_PERSONAL_ACCESS_TOKEN`
  - Lambda Labs: `LAMBDA_LABS_API_KEY`
  - (Optional) Additional: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `PINECONE_API_KEY`, `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_PASSWORD`
- Tools installed: `bash`, `git`, `docker`, `docker-compose`, `python3`.

## Setup Credentials

1. Copy and fill in your credentials:
   ```bash
   cp deployment_credentials.env.example deployment_credentials.env
   ```

2. Source the credentials file:
   ```bash
   source deployment_credentials.env
   ```

   Or pull directly from Pulumi ESC:
   ```bash
   pulumi stack output --json | jq -r \
     '"export DOCKER_USER_NAME=\(.dockerUserName)"\n"export DOCKER_PERSONAL_ACCESS_TOKEN=\(.dockerPatToken)"\n"export LAMBDA_LABS_API_KEY=\(.lambdaLabsApiKey)"' \
     > deployment_credentials.env
   source deployment_credentials.env
   ```

## Clone & Deploy

```bash
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main
bash lambda_labs_quick_deploy.sh
```

## What Gets Deployed

- **Main Sophia AI Application** → `${DOCKER_USER_NAME}/sophia-ai:latest`
- **MCP Servers** → `${DOCKER_USER_NAME}/sophia-mcp-<server>:latest`
- **PostgreSQL**, **Redis**, **Nginx Reverse Proxy**
- **Monitoring Stack** (if enabled in `docker-compose.yml`)

## Post-Deployment Access

- Application: `http://<instance-ip>/`
- API: `http://<instance-ip>/api/`
- Grafana (if configured): `http://<instance-ip>:3000/`
- Health Check: `http://<instance-ip>/health`

## Cleanup

```bash
docker-compose down
``` 