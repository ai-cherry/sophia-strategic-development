---
title: Sophia AI - Production Deployment Guide
description: 
tags: security, gong, monitoring, database, docker
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Sophia AI - Production Deployment Guide


## Table of Contents

- [🚀 Quick Start](#🚀-quick-start)
- [📋 Prerequisites](#📋-prerequisites)
  - [Required API Keys (Minimal Setup)](#required-api-keys-(minimal-setup))
  - [Optional Integrations (Add as Needed)](#optional-integrations-(add-as-needed))
- [🔑 Setting Up GitHub Secrets](#🔑-setting-up-github-secrets)
  - [Step 1: Add Organization Secrets](#step-1:-add-organization-secrets)
  - [Step 2: Verify Secrets](#step-2:-verify-secrets)
- [🏗️ Architecture Overview](#🏗️-architecture-overview)
- [📦 Deployment Process](#📦-deployment-process)
  - [Automatic Deployment (Recommended)](#automatic-deployment-(recommended))
  - [Manual Deployment](#manual-deployment)
- [🔧 Configuration](#🔧-configuration)
  - [LLM Gateway Setup](#llm-gateway-setup)
  - [Environment Variables](#environment-variables)
  - [Pulumi ESC Secret Loading](#pulumi-esc-secret-loading)
  - [Feature Flags](#feature-flags)
- [🚨 Production Checklist](#🚨-production-checklist)
  - [Security](#security)
  - [Performance](#performance)
  - [Backup](#backup)
- [📊 Monitoring](#📊-monitoring)
  - [Health Checks](#health-checks)
  - [Logs](#logs)
- [🆘 Troubleshooting](#🆘-troubleshooting)
  - [Deployment Fails](#deployment-fails)
  - [LLM Gateway Issues](#llm-gateway-issues)
  - [Integration Problems](#integration-problems)
- [📞 Support](#📞-support)
- [🔄 Updates](#🔄-updates)

## 🚀 Quick Start

This guide covers deploying Sophia AI to production using GitHub Actions, Vercel (frontend), and Lambda Labs (backend).

## 📋 Prerequisites

### Required API Keys (Minimal Setup)
1. **LLM Gateway** (2 keys for 100+ models):
   - `PORTKEY_API_KEY` - Get from [portkey.ai](https://portkey.ai)
   - `OPENROUTER_API_KEY` - Get from [openrouter.ai](https://openrouter.ai)

2. **Deployment Targets**:
   - `VERCEL_ACCESS_TOKEN` - For frontend deployment
   - `LAMBDA_LABS_API_KEY` - For backend deployment

3. **Security**:
   - `SECRET_KEY` - Generate a random 32+ character string
   - `ADMIN_USERNAME` - Admin dashboard username
   - `ADMIN_PASSWORD` - Strong admin password

### Optional Integrations (Add as Needed)
- **Business**: `HUBSPOT_API_KEY`, `GONG_API_KEY`, `SLACK_BOT_TOKEN`
- **Vector DBs**: `PINECONE_API_KEY`, `WEAVIATE_API_KEY`
- **AI Discovery**: `HUGGINGFACE_API_TOKEN`

## 🔑 Setting Up GitHub Secrets

### Step 1: Add Organization Secrets
Navigate to your GitHub organization settings → Secrets → Actions

Add these secrets:
```yaml
# Example usage:
yaml
```python

### Step 2: Verify Secrets
The deployment workflow will automatically report which features are enabled based on available secrets.

## 🏗️ Architecture Overview

```mermaid
# Example usage:
mermaid
```python

## 📦 Deployment Process

### Automatic Deployment (Recommended)
1. Push to `main` branch
2. GitHub Actions automatically:
   - Builds Docker images
   - Deploys frontend to Vercel
   - Deploys backend to Lambda Labs
   - Reports deployment status

### Manual Deployment
```bash
# Example usage:
bash
```python

## 🔧 Configuration

### LLM Gateway Setup
Sophia uses Portkey + OpenRouter for unified LLM access:

```python
# Example usage:
python
```python

### Environment Variables
Create `.env` from the provided example:
```bash
cp .env.example .env
# Add your API keys
```python

### Pulumi ESC Secret Loading
All GitHub organization secrets are automatically synchronized to **Pulumi ESC**.
During deployment the containers load these secrets at runtime, so manual secret
management is not required.

### Feature Flags
Features auto-enable based on available API keys:
- ✅ AI Chat (if Portkey configured)
- ✅ CRM Sync (if HubSpot configured)
- ✅ Call Analysis (if Gong configured)
- ✅ Notifications (if Slack configured)
- ✅ Vector Search (if Pinecone/Weaviate configured)

## 🚨 Production Checklist

### Security
- [ ] Change default `SECRET_KEY`
- [ ] Set strong `ADMIN_PASSWORD`
- [ ] Enable HTTPS on Lambda Labs
- [ ] Configure CORS origins
- [ ] Review firewall rules

### Performance
- [ ] Enable Redis caching
- [ ] Configure CDN for frontend
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure rate limiting

### Backup
- [ ] PostgreSQL automated backups
- [ ] Redis persistence enabled
- [ ] Configuration backups

## 📊 Monitoring

### Health Checks
- Frontend: `https://your-app.vercel.app/health`
- Backend: `https://your-api.lambda-labs.com/health`
- API Status: `https://your-api.lambda-labs.com/api/v1/status`

### Logs
- Frontend: Vercel dashboard
- Backend: Lambda Labs console
- Application: `/logs` directory

## 🆘 Troubleshooting

### Deployment Fails
1. Check GitHub Actions logs
2. Verify all required secrets are set
3. Ensure Docker builds locally

### LLM Gateway Issues
1. Verify Portkey and OpenRouter keys
2. Check rate limits
3. Review fallback configuration

### Integration Problems
1. Test API keys individually
2. Check network connectivity
3. Review error logs

## 📞 Support

- Documentation: `/docs`
- Issues: GitHub Issues
- Community: Discord/Slack

## 🔄 Updates

To update Sophia:
1. Pull latest changes
2. Review migration notes
3. Push to main (auto-deploys)

---

**Note**: This guide assumes you're using GitHub organization secrets. For personal repos, add secrets to repository settings instead.
