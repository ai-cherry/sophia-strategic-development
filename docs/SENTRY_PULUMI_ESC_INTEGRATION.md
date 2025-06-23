---
title: Sentry Integration with Pulumi ESC and GitHub Actions
description: 
tags: mcp, docker, security
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Sentry Integration with Pulumi ESC and GitHub Actions


## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Required GitHub Organization Secrets](#required-github-organization-secrets)
- [Automatic Synchronization](#automatic-synchronization)
  - [GitHub Actions Workflow](#github-actions-workflow)
  - [Manual Sync](#manual-sync)
- [Pulumi ESC Configuration](#pulumi-esc-configuration)
  - [Environment Path](#environment-path)
  - [Stored Secrets](#stored-secrets)
  - [Access in Code](#access-in-code)
    - [Python Backend](#python-backend)
    - [MCP Server](#mcp-server)
- [Docker Deployment](#docker-deployment)
  - [Environment Variables](#environment-variables)
  - [Automatic Configuration](#automatic-configuration)
- [Local Development](#local-development)
  - [Setup](#setup)
  - [Testing](#testing)
- [Security Benefits](#security-benefits)
- [Troubleshooting](#troubleshooting)
  - [Secret Not Available?](#secret-not-available?)
  - [MCP Server Can't Access Secrets?](#mcp-server-can't-access-secrets?)
  - [Sync Workflow Failing?](#sync-workflow-failing?)
- [Best Practices](#best-practices)
- [Integration Points](#integration-points)
  - [1. Backend Initialization](#1.-backend-initialization)
  - [2. MCP Server](#2.-mcp-server)
  - [3. Docker Compose](#3.-docker-compose)
  - [4. GitHub Actions](#4.-github-actions)
- [Summary](#summary)

## Overview

This document describes how Sentry is integrated with Sophia AI using:
- **GitHub Organization Secrets** (ai-cherry org)
- **Pulumi ESC** (Environment Secrets Configuration)
- **Automatic Secret Synchronization**

## Architecture

```python
# Example usage:
python
```python

## Required GitHub Organization Secrets

Add these secrets at the organization level in GitHub (ai-cherry):

1. **SENTRY_DSN** - Your Sentry Data Source Name
   - Get from: Sentry → Settings → Client Keys (DSN)
   - Format: `https://xxxxx@o123456.ingest.sentry.io/123456`

2. **SENTRY_API_TOKEN** - Sentry API authentication token
   - Get from: https://sentry.io/settings/account/api/auth-tokens/
   - Required scopes: `project:read`, `project:write`, `issue:read`, `issue:write`

3. **SENTRY_ORGANIZATION_SLUG** - Your Sentry organization identifier
   - Value: `pay-ready`

4. **SENTRY_PROJECT_SLUG** - Your Sentry project identifier
   - Value: `pay-ready`

5. **SENTRY_CLIENT_SECRET** - Optional webhook verification secret
   - For webhook signature verification

## Automatic Synchronization

### GitHub Actions Workflow

The workflow `.github/workflows/sync-sentry-secrets.yml`:
- Runs every 6 hours automatically
- Can be triggered manually
- Syncs all Sentry secrets from GitHub to Pulumi ESC
- Verifies configuration after sync
- Triggers Sentry MCP deployment on success

### Manual Sync

To manually sync secrets:
1. Go to Actions tab in GitHub
2. Select "Sync Sentry Secrets to Pulumi ESC"
3. Click "Run workflow"

## Pulumi ESC Configuration

### Environment Path
```python
# Example usage:
python
```python

### Stored Secrets
- `SENTRY_DSN` (encrypted)
- `SENTRY_API_TOKEN` (encrypted)
- `SENTRY_ORGANIZATION_SLUG`
- `SENTRY_PROJECT_SLUG`
- `SENTRY_CLIENT_SECRET` (encrypted)

### Access in Code

#### Python Backend
```python
# Example usage:
python
```python

#### MCP Server
The Sentry MCP server automatically retrieves secrets using Pulumi CLI:
```python
# Example usage:
python
```python

## Docker Deployment

### Environment Variables
The Docker Compose configuration includes:
```yaml
# Example usage:
yaml
```python

### Automatic Configuration
1. Container starts with Pulumi CLI installed
2. Retrieves secrets from Pulumi ESC
3. Falls back to environment variables if needed

## Local Development

### Setup
```bash
# Example usage:
bash
```python

### Testing
```bash
# Example usage:
bash
```python

## Security Benefits

1. **No Hardcoded Secrets** - All secrets managed centrally
2. **Automatic Rotation** - Update in GitHub → Auto-sync to Pulumi
3. **Audit Trail** - All secret access logged
4. **Environment Isolation** - Different secrets per environment
5. **Zero Manual Management** - Fully automated workflow

## Troubleshooting

### Secret Not Available?
1. Check GitHub Actions workflow ran successfully
2. Verify secret exists in GitHub organization
3. Check Pulumi ESC environment:
   ```bash
# Example usage:
bash
```python
# backend/core/sentry_setup.py
from backend.core.auto_esc_config import config

sentry_dsn = config.sentry_dsn
sentry_sdk.init(dsn=sentry_dsn)
```python
# Example usage:
python
```python
# mcp-servers/sentry/sentry_mcp_server.py
self.api_token = get_pulumi_esc_value("SENTRY_API_TOKEN")
```python
# Example usage:
python
```yaml
# docker-compose.sentry.yml
environment:
  - PULUMI_ACCESS_TOKEN=${PULUMI_ACCESS_TOKEN}
```python
# Example usage:
python
```yaml
# .github/workflows/sync-sentry-secrets.yml
pulumi env set scoobyjava-org/default/sophia-ai-production SENTRY_API_TOKEN "$SENTRY_API_TOKEN" --secret
```python

## Summary

The Sentry integration leverages:
- **GitHub Organization Secrets** for centralized secret management
- **Pulumi ESC** for secure secret distribution
- **GitHub Actions** for automatic synchronization
- **Docker** with Pulumi CLI for runtime configuration

This provides a secure, automated, and maintainable approach to managing Sentry credentials across the Sophia AI platform.
