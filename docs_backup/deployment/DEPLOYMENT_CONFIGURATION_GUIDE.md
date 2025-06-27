---
title: Sophia AI Platform - Deployment Configuration Guide
description: 
tags: mcp, security, kubernetes, deployment, monitoring, database, docker
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Sophia AI Platform - Deployment Configuration Guide


## Table of Contents

- [Overview](#overview)
- [Current Infrastructure Configuration](#current-infrastructure-configuration)
  - [Lambda Labs Server Specifications](#lambda-labs-server-specifications)
  - [SSH Key Strategy](#ssh-key-strategy)
    - [Current Active Configuration](#current-active-configuration)
    - [Available SSH Keys](#available-ssh-keys)
    - [Key Management Best Practices](#key-management-best-practices)
- [Pulumi Configuration](#pulumi-configuration)
  - [Current Stack Configuration](#current-stack-configuration)
  - [Required Configuration Values](#required-configuration-values)
  - [Deployment Commands](#deployment-commands)
- [GitHub Organization Secrets](#github-organization-secrets)
  - [Verified Access](#verified-access)
  - [Key Secrets for Sophia AI](#key-secrets-for-sophia-ai)
  - [Secret Management Flow](#secret-management-flow)
- [MCP Server Integrations](#mcp-server-integrations)
  - [Configured MCP Servers](#configured-mcp-servers)
  - [Service Integration Registry](#service-integration-registry)
  - [Integration Configuration](#integration-configuration)
- [Performance Optimization Opportunities](#performance-optimization-opportunities)
  - [Current Server Analysis](#current-server-analysis)
  - [Upgrade Options Available](#upgrade-options-available)
  - [Optimization Recommendations](#optimization-recommendations)
- [Deployment Verification Checklist](#deployment-verification-checklist)
  - [Pre-Deployment](#pre-deployment)
  - [Post-Deployment](#post-deployment)
  - [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)
  - [Secret Management](#secret-management)
  - [Access Control](#access-control)
  - [Network Security](#network-security)
- [Maintenance Schedule](#maintenance-schedule)
  - [Weekly](#weekly)
  - [Monthly](#monthly)
  - [Quarterly](#quarterly)
- [Contact and Support](#contact-and-support)
  - [Team Responsibilities](#team-responsibilities)
  - [Emergency Procedures](#emergency-procedures)

## Overview

This document provides comprehensive configuration details for the Sophia AI platform deployment on Lambda Labs infrastructure with integrated MCP servers and service connections.

## Current Infrastructure Configuration

### Lambda Labs Server Specifications
- **Server Name**: sophia-ai-production
- **IP Address**: 170.9.9.253 (Public), 10.19.48.242 (Private)
- **Instance Type**: gpu_1x_a10 (1x A10 24GB PCIe)
- **Specifications**:
  - vCPUs: 30
  - Memory: 200 GiB
  - Storage: 1,400 GiB
  - GPUs: 1x A10 (24GB)
  - Cost: $0.75/hour
- **Region**: us-west-1 (California, USA)
- **Status**: Active

### SSH Key Strategy

#### Current Active Configuration
- **Primary SSH Key**: `cherry-ai-key`
- **Key Location**: Lambda Labs account (ID: 3e20c3328eff43e9aaadfade649ed9c3)
- **Pulumi Configuration**: `LAMBDA_SSH_KEY_NAME=cherry-ai-key`

#### Available SSH Keys
1. **cherry-ai-key** (ACTIVE)
   - Currently deployed on sophia-ai-production server
   - Used by Pulumi for deployment automation

2. **sophia-deployment-key-20250621** (AVAILABLE)
   - Added to Lambda Labs account (ID: 8562fdb75c544db39c04d23addef2dfd)
   - Ready for future deployments or manual server updates

#### Key Management Best Practices
- All SSH keys are managed through Lambda Labs API
- Private keys are stored securely in Pulumi ESC
- Public keys are registered in Lambda Labs account
- Key rotation should be performed quarterly

## Pulumi Configuration

### Current Stack Configuration
- **Stack Name**: sophia-prod-on-lambda
- **Organization**: scoobyjava-org
- **Project**: sophia-infra

### Required Configuration Values
```bash
# Example usage:
bash
```python

### Deployment Commands
```bash
# Example usage:
bash
```python

## GitHub Organization Secrets

### Verified Access
- **Organization**: ai-cherry
- **PAT Access**: Confirmed with full organization permissions
- **Total Secrets**: 158 configured secrets

### Key Secrets for Sophia AI
- `ANTHROPIC_API_KEY`: AI model access
- `SNOWFLAKE_*`: Data warehouse credentials
- `PINECONE_API_KEY`: Vector database access
- `DOCKER_PERSONAL_ACCESS_TOKEN`: Container registry access
- `DOCKER_USER_NAME`: Docker Hub username
- `LAMBDA_API_KEY`: Lambda Labs API access
- `PULUMI_ACCESS_TOKEN`: Infrastructure management

### Secret Management Flow
1. **Primary Storage**: GitHub Organization Secrets
2. **Distribution**: Pulumi ESC for deployment
3. **Runtime Access**: Environment variables in containers
4. **Automatic Loading**: Containers pull secrets from Pulumi ESC at startup
5. **Rotation**: Automated through GitHub Actions

## MCP Server Integrations

### Configured MCP Servers
1. **Snowflake MCP Server**
   - Location: `mcp-servers/snowflake/`
   - Purpose: Data warehouse operations
   - Authentication: Username/password + MFA support
   - Configuration: Environment variables from Pulumi ESC

2. **Pulumi MCP Server**
   - Location: `mcp-servers/pulumi/`
   - Purpose: Infrastructure management
   - Authentication: Pulumi access token
   - Configuration: Stack and organization settings

### Service Integration Registry
Located in `infrastructure/integration_registry.json`:
- **Snowflake**: Database integration with 90-day key rotation
- **Pinecone**: Vector database for AI embeddings
- **OpenAI/Anthropic**: AI model providers
- **Airbyte**: Data pipeline integration
- **Estuary**: Real-time data streaming

### Integration Configuration
- **Config Manager**: `backend/core/integration_config.py`
- **Registry**: `backend/core/integration_registry.py`
- **Multi-DB Integration**: `backend/integration/multi_database_integration.py`

## Performance Optimization Opportunities

### Current Server Analysis
The current gpu_1x_a10 instance provides:
- Adequate compute for development and testing
- Sufficient memory for moderate AI workloads
- Good cost-effectiveness at $0.75/hour

### Upgrade Options Available
1. **gpu_1x_gh200** ($1.49/hour)
   - 64 vCPUs, 432 GiB RAM, 96GB GPU
   - 2x cost, 4x performance improvement

2. **gpu_4x_h100_sxm5** ($12.36/hour)
   - 104 vCPUs, 900 GiB RAM, 4x 80GB GPUs
   - 16x cost, 10x+ performance for AI workloads

### Optimization Recommendations
1. **Current Setup**: Suitable for development and moderate production
2. **Scale-Up Trigger**: When AI workloads exceed 24GB GPU memory
3. **Cost Monitoring**: Current $540/month is cost-effective
4. **Performance Monitoring**: Track GPU utilization and memory usage

## Deployment Verification Checklist

### Pre-Deployment
- [ ] Pulumi configuration verified
- [ ] SSH key access confirmed
- [ ] GitHub secrets accessible
- [ ] Docker authentication configured

### Post-Deployment
- [ ] Kubernetes cluster operational
- [ ] MCP servers responding
- [ ] Service integrations connected
- [ ] Monitoring and logging active

### Troubleshooting
- **SSH Issues**: Verify key name matches Lambda Labs configuration
- **Pulumi Errors**: Check ESC environment and stack configuration
- **Service Failures**: Validate GitHub secrets and API keys
- **Performance Issues**: Monitor resource utilization

## Security Best Practices

### Secret Management
1. Never commit secrets to version control
2. Use Pulumi ESC for centralized secret management
3. Rotate keys quarterly or after security incidents
4. Monitor secret access and usage

### Access Control
1. Limit SSH key access to authorized personnel
2. Use GitHub organization-level secrets
3. Implement least-privilege access principles
4. Regular access reviews and audits

### Network Security
1. Use private IPs for internal communication
2. Implement proper firewall rules
3. Monitor network traffic and access patterns
4. Regular security updates and patches

## Maintenance Schedule

### Weekly
- Monitor server performance and costs
- Check deployment pipeline health
- Review error logs and alerts

### Monthly
- Update dependencies and packages
- Review and optimize resource usage
- Backup critical configurations

### Quarterly
- Rotate SSH keys and API tokens
- Review and update security policies
- Performance optimization review
- Cost analysis and optimization

## Contact and Support

### Team Responsibilities
- **Infrastructure**: DevOps team
- **Security**: Security team
- **Applications**: Development team
- **Data**: Data engineering team

### Emergency Procedures
1. Server issues: Check Lambda Labs status
2. Deployment failures: Review Pulumi logs
3. Security incidents: Rotate affected keys immediately
4. Performance issues: Scale resources as needed

---

**Last Updated**: June 21, 2025
**Version**: 1.0
**Maintained By**: Sophia AI Platform Team
