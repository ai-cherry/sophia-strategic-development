---
title: Sophia AI Infrastructure Quick Start
description: 
tags: security
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Sophia AI Infrastructure Quick Start


## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Setup](#quick-setup)
  - [1. Clone and Setup](#1.-clone-and-setup)
  - [2. Configure Pulumi](#2.-configure-pulumi)
  - [3. Deploy Infrastructure](#3.-deploy-infrastructure)
- [Key Components](#key-components)
  - [Secret Management](#secret-management)
  - [Infrastructure Validation](#infrastructure-validation)
  - [Cleanup Legacy Files](#cleanup-legacy-files)
- [Deployment](#deployment)
  - [Manual Deploy](#manual-deploy)
  - [GitHub Actions Deploy](#github-actions-deploy)
- [Common Tasks](#common-tasks)
  - [Check Infrastructure Status](#check-infrastructure-status)
  - [Update Secrets](#update-secrets)
  - [Roll Back Changes](#roll-back-changes)
- [Troubleshooting](#troubleshooting)
  - [Secret Loading Issues](#secret-loading-issues)
  - [Deployment Failures](#deployment-failures)
- [Support](#support)

## Prerequisites
- Python 3.11+
- Pulumi CLI installed
- AWS credentials configured
- GitHub repository access

## Quick Setup

### 1. Clone and Setup
```bash
# Example usage:
bash
```python

### 2. Configure Pulumi
```bash
# Example usage:
bash
```python

### 3. Deploy Infrastructure
```bash
# Example usage:
bash
```python

## Key Components

### Secret Management
- All secrets stored in GitHub Organization (ai-cherry)
- Automatically synced to Pulumi ESC
- Backend loads secrets via `backend/core/auto_esc_config.py`

### Infrastructure Validation
```bash
# Example usage:
bash
```python

### Cleanup Legacy Files
```bash
# Example usage:
bash
```python

## Deployment

### Manual Deploy
```bash
# Example usage:
bash
```python

### GitHub Actions Deploy
- Push to main branch triggers automatic deployment
- Or manually trigger via GitHub Actions UI

## Common Tasks

### Check Infrastructure Status
```bash
# Example usage:
bash
```python

### Update Secrets
1. Update in GitHub Organization secrets
2. Secrets automatically sync to Pulumi ESC
3. Restart services to pick up new values

### Roll Back Changes
```bash
# Example usage:
bash
```python

## Troubleshooting

### Secret Loading Issues
- Ensure `PULUMI_ORG=scoobyjava-org` is set
- Check GitHub Actions has organization secret access
- Verify Pulumi ESC environment exists

### Deployment Failures
- Check AWS credentials are valid
- Ensure Pulumi stack exists
- Review GitHub Actions logs
- Run `pulumi preview` locally to debug

## Support
- Check existing documentation in `/docs`
- Review GitHub Actions workflows in `.github/workflows`
- Use `/reportbug` in Cursor AI for issues
