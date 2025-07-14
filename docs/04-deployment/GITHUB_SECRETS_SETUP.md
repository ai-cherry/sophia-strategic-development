# GitHub Secrets Setup Guide

## Overview

This guide documents how to set up GitHub secrets for the Sophia AI project, including Docker Hub authentication and other critical secrets.

## Required Secrets

### Docker Hub Authentication

1. **DOCKER_TOKEN**
   - Type: Personal Access Token (PAT)
   - Purpose: Authenticate with Docker Hub for pushing images
   - How to create:
     1. Go to https://hub.docker.com/settings/security
     2. Click "New Access Token"
     3. Give it a descriptive name (e.g., "Sophia AI GitHub Actions")
     4. Copy the token immediately (it won't be shown again)

### Setting Up Secrets in GitHub

1. Navigate to your repository: https://github.com/ai-cherry/sophia-main
2. Go to Settings → Secrets and variables → Actions
3. Click "New repository secret"

### Critical Secrets to Add

```yaml
# Docker Hub
DOCKER_TOKEN: Your Docker Personal Access Token

# Pulumi
PULUMI_ACCESS_TOKEN: Your Pulumi access token

# Cloud Providers
LAMBDA_LABS_API_KEY: Lambda Labs API key

# AI Services
OPENAI_API_KEY: OpenAI API key
ANTHROPIC_API_KEY: Anthropic API key

# Database
SNOWFLAKE_ACCOUNT: Your Modern Stack account
SNOWFLAKE_USER: Modern Stack username
SNOWFLAKE_PASSWORD: Modern Stack password

# Other Services
GONG_ACCESS_KEY: Gong API access key
HUBSPOT_API_KEY: HubSpot API key
PINECONE_API_KEY: Pinecone API key
```

## GitHub Actions Workflow Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: scoobyjava15
          password: ${{ secrets.DOCKER_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile.simple
          push: true
          tags: |
            scoobyjava15/sophia-backend:latest
            scoobyjava15/sophia-backend:${{ github.sha }}

      - name: Configure Pulumi
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
        run: |
          pulumi login
          pulumi stack select sophia-ai-production
```

## Security Best Practices

### 1. Secret Rotation
- Rotate secrets quarterly
- Document rotation dates
- Update all dependent systems

### 2. Access Control
- Limit who can view/modify secrets
- Use environment-specific secrets
- Enable audit logging

### 3. Secret Naming Convention
```
SERVICE_TYPE_ENVIRONMENT

Examples:
DOCKER_TOKEN_PROD
SNOWFLAKE_PASSWORD_DEV
OPENAI_API_KEY_STAGING
```

### 4. Never Commit Secrets
```bash
# Add to .gitignore
.env
.env.*
*.key
*.pem
secrets/
```

## Verifying Secrets

### Check Secret Availability in Actions

```yaml
- name: Verify secrets are available
  run: |
    if [ -z "${{ secrets.DOCKER_TOKEN }}" ]; then
      echo "ERROR: DOCKER_TOKEN secret is not set"
      exit 1
    fi
    echo "✅ Docker token is configured"
```

### Debug Secret Issues

```yaml
- name: Debug secrets (safe)
  run: |
    echo "Docker token length: ${#DOCKER_TOKEN}"
    echo "First 4 chars: ${DOCKER_TOKEN:0:4}..."
  env:
    DOCKER_TOKEN: ${{ secrets.DOCKER_TOKEN }}
```

## Organization Secrets

For organization-wide secrets:

1. Go to https://github.com/organizations/ai-cherry/settings/secrets
2. Add secrets that should be available to all repositories
3. Configure repository access:
   - All repositories
   - Private repositories
   - Selected repositories

## Troubleshooting

### Secret Not Available
- Check secret name matches exactly (case-sensitive)
- Verify repository has access to organization secrets
- Ensure workflow has proper permissions

### Authentication Failures
- Regenerate tokens/keys
- Check expiration dates
- Verify correct environment

### Debugging Tips
```yaml
# List available secrets (names only)
- name: List secret names
  run: |
    echo "Available secrets:"
    echo "${{ toJSON(secrets) }}" | jq 'keys'
```

## Maintenance Checklist

- [ ] Monthly: Review secret usage
- [ ] Quarterly: Rotate all tokens
- [ ] Semi-annually: Audit access logs
- [ ] Annually: Full security review

## Emergency Procedures

If a secret is compromised:

1. **Immediately revoke** the compromised credential
2. **Generate new** credential
3. **Update** GitHub secret
4. **Deploy** changes to all environments
5. **Audit** logs for unauthorized usage
6. **Document** the incident

## Related Documentation

- [Docker Hub Deployment Guide](./DOCKER_HUB_DEPLOYMENT.md)
- [Pulumi ESC Integration](./PULUMI_ESC_INTEGRATION.md)
- [CI/CD Pipeline](./CI_CD_PIPELINE.md)
