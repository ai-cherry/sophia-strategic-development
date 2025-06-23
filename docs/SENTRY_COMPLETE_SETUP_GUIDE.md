---
title: Sentry Integration Setup Guide for Sophia AI
description: This guide provides step-by-step instructions for setting up Sentry integration with the Sophia AI project, including GitHub secrets management and Pulumi ESC synchronization.
tags: mcp, monitoring, security, agent
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Sentry Integration Setup Guide for Sophia AI


## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step 1: Set Up GitHub Organization Secrets](#step-1:-set-up-github-organization-secrets)
- [Step 2: Create Sentry Project](#step-2:-create-sentry-project)
- [Step 3: Set Sentry DSN Secret](#step-3:-set-sentry-dsn-secret)
- [Step 4: Sync Secrets to Pulumi ESC](#step-4:-sync-secrets-to-pulumi-esc)
- [Step 5: Verify Configuration](#step-5:-verify-configuration)
- [Configuration Structure](#configuration-structure)
- [Testing the Integration](#testing-the-integration)
- [MCP Server Integration](#mcp-server-integration)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Manual Verification Scripts](#manual-verification-scripts)
- [Security Considerations](#security-considerations)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Support](#support)
- [Related Files](#related-files)

This guide provides step-by-step instructions for setting up Sentry integration with the Sophia AI project, including GitHub secrets management and Pulumi ESC synchronization.

## Overview

The Sentry integration follows the Sophia AI secret management architecture:
- **GitHub Organization Secrets** → **Pulumi ESC** → **Application Runtime**

## Prerequisites

1. Access to the `ai-cherry` GitHub organization
2. GitHub CLI (`gh`) installed and authenticated
3. Access to the Sentry organization `pay-ready`
4. Pulumi CLI installed and authenticated

## Step 1: Set Up GitHub Organization Secrets

Run the provided script to set up all required GitHub secrets:

```bash
# Example usage:
bash
```python

This script sets the following secrets in the `ai-cherry` organization:
- `SENTRY_AUTH_TOKEN` - Personal Access Token for Sentry API
- `SENTRY_API_TOKEN` - API token for Sentry integration
- `SENTRY_CLIENT_SECRET` - Client secret for Sentry OAuth
- `SENTRY_ORGANIZATION_SLUG` - Organization slug (`pay-ready`)
- `SENTRY_PROJECT_SLUG` - Project slug (`sophia-ai`)

## Step 2: Create Sentry Project

1. Log in to [Sentry](https://sentry.io)
2. Navigate to the `pay-ready` organization
3. Create a new project:
   - **Platform**: Python
   - **Project Name**: `sophia-ai`
   - **Team**: Select appropriate team
4. Copy the DSN from the project settings

## Step 3: Set Sentry DSN Secret

After creating the Sentry project, set the DSN secret:

```bash
# Example usage:
bash
```python

## Step 4: Sync Secrets to Pulumi ESC

Trigger the sync workflow to push all secrets to Pulumi ESC:

```bash
# Example usage:
bash
```python

## Step 5: Verify Configuration

Check that secrets were properly synced:

```bash
# Example usage:
bash
```python

## Configuration Structure

The Sentry configuration is accessible in the application via:

```python
# Example usage:
python
```python

## Testing the Integration

1. **Local Testing**:
   ```bash
# Example usage:
bash
```bash
gh workflow run deploy-sentry-mcp.yml --repo ai-cherry/sophia-main
```python
# Example usage:
python
```bash
# Verify Pulumi ESC secrets
./scripts/verify_sentry_pulumi_secrets.sh

# Manual sync if needed
./scripts/manual_sync_sentry_to_pulumi.sh
```python

## Security Considerations

- All secrets are stored as encrypted GitHub organization secrets
- Secrets are marked as `--secret` in Pulumi ESC for additional encryption
- No secrets are hardcoded in the application code
- Regular rotation of tokens is recommended

## Monitoring and Maintenance

1. **Regular Health Checks**:
   - Monitor Sentry error rates
   - Check MCP server status
   - Verify secret sync workflow runs

2. **Token Rotation**:
   - Update GitHub secrets when tokens expire
   - Re-run sync workflow after updates
   - Test integration after rotation

3. **Documentation Updates**:
   - Keep this guide updated with any changes
   - Document any custom configurations
   - Update troubleshooting section as needed

## Support

For issues with this integration:
1. Check the troubleshooting section above
2. Review GitHub Actions workflow logs
3. Check Sentry project configuration
4. Contact the DevOps team for Pulumi ESC issues

## Related Files

- `backend/core/sentry_setup.py` - Sentry SDK initialization
- `backend/core/auto_esc_config.py` - Configuration management
- `backend/agents/specialized/sentry_agent.py` - Sentry agent implementation
- `mcp-servers/sentry/sentry_mcp_server.py` - MCP server for Sentry
- `.github/workflows/sync-sentry-secrets.yml` - Secret sync workflow
- `.github/workflows/deploy-sentry-mcp.yml` - MCP deployment workflow

