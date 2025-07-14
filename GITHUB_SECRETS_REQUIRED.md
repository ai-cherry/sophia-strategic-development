# 🔐 REQUIRED GITHUB ORGANIZATION SECRETS

**Organization**: `ai-cherry`
**Repository**: `sophia-main`

## Required Secrets for Production Deployment

### `PULUMI_ACCESS_TOKEN`
**Description**: Pulumi Cloud access token for infrastructure deployment
**Required**: ✅ Critical

### `LAMBDA_LABS_API_KEY`
**Description**: Lambda Labs API key for GPU instance management
**Required**: ✅ Critical

### `DOCKERHUB_USERNAME`
**Description**: Docker Hub username (scoobyjava15)
**Required**: ✅ Critical

### `DOCKER_TOKEN`
**Description**: Docker Hub personal access token
**Required**: ✅ Critical

### `LAMBDA_LABS_CONTROL_PLANE_IP`
**Description**: Lambda Labs control plane IP address
**Required**: 🟡 Important

### `LAMBDA_LABS_SSH_KEY_NAME`
**Description**: Lambda Labs SSH key name for instance access
**Required**: 🟡 Important

### `LAMBDA_SSH_PRIVATE_KEY`
**Description**: Lambda Labs SSH private key content
**Required**: 🟡 Important

### `OPENAI_API_KEY`
**Description**: OpenAI API key for AI services
**Required**: 🟡 Important

### `ANTHROPIC_API_KEY`
**Description**: Anthropic API key for Claude models
**Required**: 🟡 Important

### `GONG_ACCESS_KEY`
**Description**: Gong.io API access key
**Required**: 🟡 Important

### `HUBSPOT_ACCESS_TOKEN`
**Description**: HubSpot API access token
**Required**: 🟡 Important

### `SLACK_BOT_TOKEN`
**Description**: Slack bot token for notifications
**Required**: 🟡 Important

### `LINEAR_API_KEY`
**Description**: Linear API key for project management
**Required**: 🟡 Important

### `modern_stack_ACCOUNT`
**Description**: Modern Stack account identifier
**Required**: 🟡 Important

### `modern_stack_USER`
**Description**: Modern Stack username
**Required**: 🟡 Important

### `modern_stack_PASSWORD`
**Description**: Modern Stack password or PAT
**Required**: 🟡 Important

## How to Set GitHub Organization Secrets

1. Go to [GitHub ai-cherry Organization Settings](https://github.com/organizations/ai-cherry/settings/secrets/actions)
2. Click "New organization secret"
3. Add each secret above with its corresponding value
4. Ensure the secret is available to the `sophia-main` repository

## Verification

After setting all secrets, the GitHub Actions workflow will automatically:
- Deploy infrastructure with Pulumi
- Build and push Docker images
- Deploy MCP servers to Lambda Labs
- Configure ESC environment with secrets

## Local Development

For local development, create a `.env` file with these variables (use the generated template).
