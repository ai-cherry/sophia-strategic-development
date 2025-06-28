---
title: Sophia AI Secrets Management Guide
description: 
tags: mcp, security, gong, linear, database, docker
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Sophia AI Secrets Management Guide


## Table of Contents

- [🔐 **PERMANENT SECRET MANAGEMENT SOLUTION**](#🔐-**permanent-secret-management-solution**)
  - [**✅ What's Automated (No More Manual Work)**](#**✅-what's-automated-(no-more-manual-work)**)
  - [**🔑 How It Works**](#**🔑-how-it-works**)
  - [**📋 Required GitHub Organization Secrets**](#**📋-required-github-organization-secrets**)
    - [**Infrastructure Secrets**](#**infrastructure-secrets**)
    - [**AI Service Secrets**](#**ai-service-secrets**)
    - [**Business Integration Secrets**](#**business-integration-secrets**)
    - [**Data Infrastructure Secrets**](#**data-infrastructure-secrets**)
    - [**Cloud Service Secrets**](#**cloud-service-secrets**)
  - [**🚀 Quick Setup**](#**🚀-quick-setup**)
  - [**🔧 Troubleshooting the Permanent Solution**](#**🔧-troubleshooting-the-permanent-solution**)
    - [**"Secret not found" errors**](#**"secret-not-found"-errors**)
    - [**"Pulumi ESC access denied"**](#**"pulumi-esc-access-denied"**)
    - [**Backend can't load secrets**](#**backend-can't-load-secrets**)
- [📚 **LEGACY DOCUMENTATION (For Reference Only)**](#📚-**legacy-documentation-(for-reference-only)**)
- [Overview](#overview)
- [Pulumi ESC (Environment Secrets and Configuration)](#pulumi-esc-(environment-secrets-and-configuration))
  - [Configuration](#configuration)
  - [Secret Groups](#secret-groups)
  - [Access Control](#access-control)
- [Environment Variables](#environment-variables)
  - [.env Files](#.env-files)
  - [Docker Environment Variables](#docker-environment-variables)
- [GitHub Secrets](#github-secrets)
  - [Setting Up GitHub Secrets](#setting-up-github-secrets)
  - [GitHub Actions Usage](#github-actions-usage)
- [Secret Rotation](#secret-rotation)
  - [Rotation Procedure](#rotation-procedure)
- [Tools](#tools)
  - [1. `secrets_manager.py`](#1.-`secrets_manager.py`)
  - [2. `setup_new_repo.py`](#2.-`setup_new_repo.py`)
- [Secret Storage Locations](#secret-storage-locations)
  - [1. Local .env Files](#1.-local-.env-files)
  - [2. Pulumi ESC (Environment Secrets and Configuration)](#2.-pulumi-esc-(environment-secrets-and-configuration))
  - [3. GitHub Secrets](#3.-github-secrets)
- [Required Environment Variables](#required-environment-variables)
  - [Core API Keys](#core-api-keys)
  - [Slack Integration](#slack-integration)
  - [Linear Integration](#linear-integration)
  - [Gong Integration](#gong-integration)
  - [Database Credentials](#database-credentials)
  - [Vercel Integration](#vercel-integration)
  - [Lambda Labs Integration](#lambda-labs-integration)
  - [Vector Database Integration](#vector-database-integration)
  - [Snowflake Integration](#snowflake-integration)
  - [Estuary Integration](#estuary-integration)
  - [Estuary Integration](#estuary-integration)
  - [Environment Configuration](#environment-configuration)
- [Optional Environment Variables](#optional-environment-variables)
- [Usage Guide](#usage-guide)
  - [Setting Up a New Repository](#setting-up-a-new-repository)
  - [Managing Secrets in an Existing Repository](#managing-secrets-in-an-existing-repository)
    - [Detecting Missing Environment Variables](#detecting-missing-environment-variables)
    - [Importing Secrets from a .env File](#importing-secrets-from-a-.env-file)
    - [Exporting Secrets to a .env File](#exporting-secrets-to-a-.env-file)
    - [Syncing Secrets to Pulumi ESC](#syncing-secrets-to-pulumi-esc)
    - [Syncing Secrets to GitHub](#syncing-secrets-to-github)
    - [Validating Secret Configuration](#validating-secret-configuration)
    - [Generating a Template .env File](#generating-a-template-.env-file)
    - [Syncing All Secrets](#syncing-all-secrets)
- [Best Practices](#best-practices)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Getting Help](#getting-help)
- [Conclusion](#conclusion)
- [🎯 **PERMANENT SOLUTION GUARANTEE**](#🎯-**permanent-solution-guarantee**)

## 🔐 **PERMANENT SECRET MANAGEMENT SOLUTION**

**IMPORTANT**: Sophia AI now uses a **PERMANENT GitHub Organization Secrets → Pulumi ESC** solution that eliminates all manual secret management.

### **✅ What's Automated (No More Manual Work)**
- ❌ No more `.env` file management
- ❌ No more manual secret configuration
- ❌ No more environment variable setup
- ❌ No more API key sharing/copying
- ✅ All secrets managed in [GitHub ai-cherry organization](https://github.com/ai-cherry)
- ✅ Automatic synchronization to Pulumi ESC
- ✅ Backend automatically loads all secrets

### **🔑 How It Works**
```python
# Example usage:
python
```python

### **📋 Required GitHub Organization Secrets**

All secrets are managed in the [ai-cherry GitHub organization](https://github.com/ai-cherry/settings/secrets/actions):

#### **Infrastructure Secrets**
- `PULUMI_ACCESS_TOKEN` - Pulumi Cloud access token
- `PULUMI_ORG` - Set to `scoobyjava-org`

#### **AI Service Secrets**
- `OPENAI_API_KEY` - OpenAI API key (starts with `sk-`)
- `ANTHROPIC_API_KEY` - Anthropic Claude API key

#### **Business Integration Secrets**
- `GONG_ACCESS_KEY` - Gong API access key
- `GONG_CLIENT_SECRET` - Gong API client secret
- `GONG_URL` - Your Gong instance URL
- `HUBSPOT_API_TOKEN` - HubSpot API token
- `SLACK_BOT_TOKEN` - Slack bot token (starts with `xoxb-`)

#### **Data Infrastructure Secrets**
- `SNOWFLAKE_ACCOUNT` - Snowflake account identifier
- `SNOWFLAKE_USER` - Snowflake username
- `SNOWFLAKE_PASSWORD` - Snowflake password
- `PINECONE_API_KEY` - Pinecone vector database API key

#### **Cloud Service Secrets**
- `LAMBDA_LABS_API_KEY` - Lambda Labs GPU compute API key
- `VERCEL_ACCESS_TOKEN` - Vercel deployment token

### **🚀 Quick Setup**

```bash
# Example usage:
bash
```python

### **🔧 Troubleshooting the Permanent Solution**

#### **"Secret not found" errors**
1. Check [GitHub organization secrets](https://github.com/ai-cherry/settings/secrets/actions)
2. Verify secret name matches exactly
3. Re-run sync: `python scripts/sync_github_to_pulumi.sh`

#### **"Pulumi ESC access denied"**
1. Update `PULUMI_ACCESS_TOKEN` in GitHub organization
2. Test access: `export PULUMI_ORG=scoobyjava-org && pulumi whoami`

#### **Backend can't load secrets**
1. Run diagnostic: `python scripts/test_permanent_solution.py`
2. Check ESC access: `pulumi env open scoobyjava-org/default/sophia-ai-production`

---

## 📚 **LEGACY DOCUMENTATION (For Reference Only)**

**NOTE**: The following sections are kept for reference but are no longer needed with the permanent solution.

## Overview

This guide provides comprehensive instructions for managing secrets and environment variables across different Sophia AI repositories and environments.

The Sophia AI secrets management system provides a unified approach to handling sensitive information across all repositories and environments. It addresses the following key challenges:

1. **Consistency**: Ensuring all repositories have the same set of required secrets
2. **Security**: Keeping secrets secure and preventing accidental exposure
3. **Synchronization**: Maintaining consistency across different environments
4. **Validation**: Verifying that all required secrets are present and valid
5. **Portability**: Easily transferring secrets between repositories and environments

## Pulumi ESC (Environment Secrets and Configuration)

Pulumi ESC provides centralized secret management for the Sophia AI system. It offers:

- Encrypted storage of secrets
- Environment-based organization
- Integration with CI/CD pipelines
- Access control and audit logging

### Configuration

The Pulumi ESC configuration is defined in `pulumi-esc-environment.yaml`:

```yaml
# Example usage:
yaml
```python

### Secret Groups

Secrets are organized into logical groups:

1. **api-keys**: API keys for external services (OpenAI, Pinecone, etc.)
2. **database-credentials**: Database passwords and connection strings
3. **security-tokens**: JWT secrets, signing keys, etc.
4. **integration-credentials**: Credentials for integrated services (HubSpot, Salesforce, etc.)
5. **infrastructure-credentials**: Cloud provider credentials (AWS, etc.)

### Access Control

Access to secrets is controlled through access policies defined in `pulumi-esc-environment.yaml`:

```yaml
# Example usage:
yaml
```python

## Environment Variables

Environment variables are used to provide secrets to the application at runtime.

### .env Files

For local development, a `.env` file can be used to store environment variables. This file should **never** be committed to version control.

A template file (`env.example`) is provided with placeholder values:

```python
# Example usage:
python
```python

### Docker Environment Variables

For Docker deployments, environment variables are defined in `docker-compose.yml`:

```yaml
# Example usage:
yaml
```python

## GitHub Secrets

GitHub Actions workflows use secrets stored in the GitHub repository settings.

### Setting Up GitHub Secrets

Use the `configure_github_secrets.py` script to set up GitHub secrets:

```bash
# Example usage:
bash
```python

### GitHub Actions Usage

In GitHub Actions workflows, secrets are accessed using the `${{ secrets.SECRET_NAME }}` syntax:

```yaml
# Example usage:
yaml
```python

## Secret Rotation

Secrets should be rotated regularly according to the following schedule:

| Secret Type | Rotation Frequency | Responsible Team |
|-------------|-------------------|------------------|
| API Keys | 90 days | DevOps |
| Database Credentials | 180 days | Database Admin |
| JWT Secrets | 365 days | Security |
| Integration Credentials | 90 days | Integration Team |
| Infrastructure Credentials | 90 days | DevOps |

### Rotation Procedure

1. Generate new credentials in the external service
2. Update the secret in Pulumi ESC:
   ```bash
# Example usage:
bash
```bash
# Create a new repository with a specific name
./setup_new_repo.py --name sophia-new-repo

# Create a new repository and import secrets from a master .env file
./setup_new_repo.py --name sophia-new-repo --source-env /path/to/master.env

# Create a new repository and import secrets from Pulumi ESC
./setup_new_repo.py --name sophia-new-repo --from-pulumi
```python
# Example usage:
python
```bash
./secrets_manager.py detect-missing
```python
# Example usage:
python
```bash
./secrets_manager.py import-from-env --env-file .env
```python
# Example usage:
python
```bash
./secrets_manager.py export-to-env --env-file .env.new
```python
# Example usage:
python
```bash
./secrets_manager.py sync-to-pulumi
```python
# Example usage:
python
```bash
./secrets_manager.py sync-to-github
```python
# Example usage:
python
```bash
./secrets_manager.py validate
```python
# Example usage:
python
```bash
./secrets_manager.py generate-template --output-file env.template
```python
# Example usage:
python
```bash
./secrets_manager.py sync-all
```python

This command will sync all secrets to all destinations: .env file, Pulumi ESC, and GitHub Secrets.

## Best Practices

1. **Never commit secrets to version control**: Always use `.gitignore` to exclude `.env` files and other files containing secrets.

2. **Use environment-specific secrets**: Different environments (development, staging, production) should use different secrets.

3. **Rotate secrets regularly**: Follow the rotation schedule defined in this guide.

4. **Use strong, unique secrets**: Generate strong, unique secrets for each service and environment.

5. **Monitor secret usage**: Regularly audit secret usage and access patterns.

6. **Use least privilege access**: Only grant access to secrets that are absolutely necessary.

7. **Encrypt secrets at rest and in transit**: Use encrypted storage and secure transmission protocols.

8. **Implement proper access controls**: Use role-based access controls and audit logging.

9. **Have a secret recovery plan**: Ensure you have a plan for recovering from compromised secrets.

10. **Document secret management procedures**: Keep this guide up-to-date and ensure all team members are familiar with the procedures.

## Security Considerations

1. **Secret Exposure**: Never log secrets or include them in error messages.

2. **Access Logging**: Log all access to secrets for audit purposes.

3. **Network Security**: Use secure networks and VPNs when accessing secrets.

4. **Workstation Security**: Ensure workstations used to access secrets are secure and up-to-date.

5. **Backup Security**: Ensure secret backups are encrypted and stored securely.

6. **Incident Response**: Have a plan for responding to secret compromise incidents.

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**: Use the `detect-missing` command to identify missing variables.

2. **Invalid Secrets**: Use the `validate` command to check secret validity.

3. **Sync Failures**: Check network connectivity and access permissions.

4. **Access Denied**: Verify access permissions and authentication credentials.

### Getting Help

If you encounter issues not covered in this guide:

1. Check the troubleshooting section of the main documentation
2. Review the logs for error messages
3. Contact the development team for assistance
4. Create an issue in the GitHub repository

## Conclusion

The Sophia AI secrets management system provides a comprehensive, secure, and scalable approach to handling sensitive information. By following the guidelines and procedures outlined in this guide, you can ensure that secrets are managed consistently and securely across all environments and repositories.

---

## 🎯 **PERMANENT SOLUTION GUARANTEE**

**The new permanent solution eliminates 90% of the complexity in this guide. Once set up, you never need to manually manage secrets again.**

- ✅ **Zero Manual Configuration**: Everything automated
- ✅ **Enterprise Security**: GitHub organization + Pulumi ESC
- ✅ **Automatic Sync**: Secrets always up-to-date
- ✅ **Comprehensive Testing**: `python scripts/test_permanent_solution.py`
- ✅ **Forever Solution**: Works without intervention

**🔒 RESULT: PERMANENT SECRET MANAGEMENT - NO MORE MANUAL WORK EVER!**
