---
title: Sentry MCP Integration Guide for Sophia AI
description: 
tags: mcp, security, monitoring, docker, agent
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Sentry MCP Integration Guide for Sophia AI


## Table of Contents

- [Overview](#overview)
- [What You Need](#what-you-need)
  - [1. Sentry Issue ID](#1.-sentry-issue-id)
    - [How to Find a Sentry Issue ID:](#how-to-find-a-sentry-issue-id:)
  - [2. Project Slug](#2.-project-slug)
  - [3. Organization Slug](#3.-organization-slug)
- [Environment Variables Required](#environment-variables-required)
- [Webhook Configuration](#webhook-configuration)
  - [Alert Rule Action Configuration](#alert-rule-action-configuration)
- [Testing the Integration](#testing-the-integration)
  - [1. Update the Test Script](#1.-update-the-test-script)
  - [2. Run the Test](#2.-run-the-test)
- [Using Sentry MCP in Sophia AI](#using-sentry-mcp-in-sophia-ai)
  - [Available MCP Tools](#available-mcp-tools)
  - [Natural Language Commands](#natural-language-commands)
- [Deployment](#deployment)
  - [1. Deploy with Docker Compose](#1.-deploy-with-docker-compose)
  - [2. Verify Deployment](#2.-verify-deployment)
  - [3. Test MCP Connection](#3.-test-mcp-connection)
- [Integration with Sophia Agents](#integration-with-sophia-agents)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debug Commands](#debug-commands)
- [Next Steps](#next-steps)
- [Security Notes](#security-notes)

## Overview

This guide helps you set up and use the Sentry MCP (Model Context Protocol) integration with Sophia AI for error tracking, monitoring, and automated debugging.

## What You Need

### 1. Sentry Issue ID
A Sentry Issue ID is a unique identifier for each error/exception tracked in Sentry. 

#### How to Find a Sentry Issue ID:

**Method 1: From Sentry Web UI**
1. Go to: `https://sentry.io/organizations/pay-ready/issues/`
2. Click on any issue in your project
3. Look at the URL - it will be something like:
   ```python
# Example usage:
python
```bash
curl -H "Authorization: Bearer YOUR_SENTRY_API_TOKEN" \
  "https://sentry.io/api/0/projects/pay-ready/YOUR_PROJECT_SLUG/issues/"
```python
# Example usage:
python
```python
https://your-sophia-domain.com/webhooks/sentry
```python
# Example usage:
python
```python
# Replace these with your actual values
PROJECT_SLUG = "pay-ready"  # Your project slug
ISSUE_ID = "1234567890"     # Replace with a real issue ID from Sentry
```python
# Example usage:
python
```bash
python scripts/test/test_sentry_agent.py
```python
# Example usage:
python
```bash
# Deploy the Sentry MCP server
docker-compose -f docker-compose.sentry.yml up -d

# Or include it with your main deployment
docker-compose -f docker-compose.yml -f docker-compose.sentry.yml up -d
```python
# Example usage:
python
```bash
# Check if the container is running
docker ps | grep sentry-mcp

# Check logs
docker logs sentry-mcp
```python
# Example usage:
python
```bash
# Test the MCP server is responding
curl http://localhost:9006/health
```python
# Example usage:
python
```bash
# Check environment variables
docker exec sentry-mcp env | grep SENTRY

# Test API connection
docker exec sentry-mcp python -c "
import os
import httpx
token = os.getenv('SENTRY_API_TOKEN')
org = os.getenv('SENTRY_ORGANIZATION_SLUG')
resp = httpx.get(f'https://sentry.io/api/0/organizations/{org}/', 
                 headers={'Authorization': f'Bearer {token}'})
print(f'Status: {resp.status_code}')
"
```python

## Next Steps

1. Find a real Issue ID from your Sentry dashboard
2. Update the test script with your Issue ID
3. Run the test to verify the integration works
4. Deploy the Sentry MCP server
5. Start using natural language commands to interact with Sentry through Sophia AI

## Security Notes

- Never commit API tokens to version control
- Use GitHub Actions secrets for all sensitive data
- Rotate API tokens regularly
- Monitor API usage in Sentry settings
