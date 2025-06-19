# Sophia AI Secrets Management Guide

This guide provides comprehensive instructions for managing secrets and environment variables across different Sophia AI repositories and environments.

## Overview

The Sophia AI secrets management system provides a unified approach to handling sensitive information across all repositories and environments. It addresses the following key challenges:

1. **Consistency**: Ensuring all repositories have the same set of required secrets
2. **Security**: Keeping secrets secure and preventing accidental exposure
3. **Synchronization**: Maintaining consistency across different environments
4. **Validation**: Verifying that all required secrets are present and valid
5. **Portability**: Easily transferring secrets between repositories and environments

## Tools

The secrets management system includes the following tools:

### 1. `secrets_manager.py`

A comprehensive script for managing secrets and environment variables. It can:

- Detect missing environment variables
- Import secrets from various sources (.env files, Pulumi ESC, GitHub)
- Export secrets to various destinations (.env files, Pulumi ESC, GitHub)
- Validate secret configurations
- Generate template .env files
- Sync secrets across different environments

### 2. `setup_new_repo.py`

A script to automate the setup of a new Sophia AI repository with all the necessary secrets and configurations. It:

- Creates a new directory for the repository
- Initializes a Git repository
- Copies the secrets_manager.py script
- Imports secrets from a master .env file or Pulumi ESC
- Sets up the necessary configuration files
- Creates a README.md file with setup instructions

## Secret Storage Locations

The secrets management system supports multiple storage locations:

### 1. Local .env Files

- **Purpose**: Development environments and local testing
- **Format**: Key-value pairs in a .env file
- **Security**: Not committed to Git (included in .gitignore)
- **Usage**: Loaded by the application at runtime

### 2. Pulumi ESC (Environment Secrets and Configuration)

- **Purpose**: Centralized secret management for all environments
- **Format**: JSON object stored in Pulumi's secure storage
- **Security**: Encrypted at rest and in transit
- **Usage**: Accessed via Pulumi API or CLI

### 3. GitHub Secrets

- **Purpose**: CI/CD pipelines and GitHub Actions
- **Format**: Key-value pairs stored in GitHub repository settings
- **Security**: Encrypted at rest and masked in logs
- **Usage**: Accessed via GitHub Actions environment variables

## Required Environment Variables

The following environment variables are required for Sophia AI to function properly:

### Core API Keys

- `ANTHROPIC_API_KEY`: Claude API key for AI capabilities
- `OPENAI_API_KEY`: OpenAI API key for AI capabilities (optional)
- `PULUMI_ACCESS_TOKEN`: Pulumi access token for infrastructure management

### Slack Integration

- `SLACK_BOT_TOKEN`: Slack bot token for Slack integration
- `SLACK_APP_TOKEN`: Slack app token for Slack integration
- `SLACK_SIGNING_SECRET`: Slack signing secret for Slack integration

### Linear Integration

- `LINEAR_API_TOKEN`: Linear API token for project management integration
- `LINEAR_WORKSPACE_ID`: Linear workspace ID for project management integration

### Gong Integration

- `GONG_CLIENT_ID`: Gong client ID for call analysis integration
- `GONG_CLIENT_SECRET`: Gong client secret for call analysis integration

### Database Credentials

- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: PostgreSQL database name

### Vercel Integration

- `VERCEL_ACCESS_TOKEN`: Vercel access token for deployment integration
- `VERCEL_TEAM_ID`: Vercel team ID for deployment integration

### Lambda Labs Integration

- `LAMBDA_LABS_API_KEY`: Lambda Labs API key for compute resources

### Vector Database Integration

- `PINECONE_API_KEY`: Pinecone API key for vector database
- `WEAVIATE_API_KEY`: Weaviate API key for vector database

### Snowflake Integration

- `SNOWFLAKE_ACCOUNT`: Snowflake account identifier
- `SNOWFLAKE_USER`: Snowflake username
- `SNOWFLAKE_PASSWORD`: Snowflake password
- `SNOWFLAKE_DATABASE`: Snowflake database name

### Estuary Integration

- `ESTUARY_API_KEY`: Estuary API key for data flow management

### Airbyte Integration

- `AIRBYTE_API_KEY`: Airbyte API key for data integration

### Environment Configuration

- `SOPHIA_ENVIRONMENT`: Environment name (development, staging, production)
- `PULUMI_ORGANIZATION`: Pulumi organization name
- `PULUMI_PROJECT`: Pulumi project name

## Optional Environment Variables

The following environment variables are optional and have default values:

- `CLAUDE_MODEL`: Claude model to use (default: claude-3-5-sonnet-20241022)
- `CLAUDE_MAX_TOKENS`: Maximum tokens for Claude responses (default: 4096)
- `CLAUDE_ORGANIZATION_ID`: Claude organization ID (default: sophia-ai)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4-turbo)
- `OPENAI_MAX_TOKENS`: Maximum tokens for OpenAI responses (default: 4096)
- `REDIS_URL`: Redis URL (default: redis://localhost:6379)
- `POSTGRES_HOST`: PostgreSQL host (default: localhost)
- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `LOG_LEVEL`: Logging level (default: INFO)
- `SSL_CERT_FILE`: SSL certificate file path

## Usage Guide

### Setting Up a New Repository

To set up a new repository with all the necessary secrets and configurations:

```bash
# Create a new repository with a specific name
./setup_new_repo.py --name sophia-new-repo

# Create a new repository and import secrets from a master .env file
./setup_new_repo.py --name sophia-new-repo --source-env /path/to/master.env

# Create a new repository and import secrets from Pulumi ESC
./setup_new_repo.py --name sophia-new-repo --from-pulumi
```

### Managing Secrets in an Existing Repository

#### Detecting Missing Environment Variables

```bash
./secrets_manager.py detect-missing
```

This command will check for missing required environment variables and display them with their descriptions.

#### Importing Secrets from a .env File

```bash
./secrets_manager.py import-from-env --env-file .env
```

This command will import environment variables from a .env file and add them to the current environment.

#### Exporting Secrets to a .env File

```bash
./secrets_manager.py export-to-env --env-file .env.new
```

This command will export the current environment variables to a .env file, organized by category.

#### Syncing Secrets to Pulumi ESC

```bash
./secrets_manager.py sync-to-pulumi
```

This command will sync the current environment variables to Pulumi ESC, making them available to all repositories and environments.

#### Syncing Secrets to GitHub

```bash
./secrets_manager.py sync-to-github
```

This command will sync the current environment variables to GitHub Secrets, making them available to GitHub Actions.

#### Validating Secret Configuration

```bash
./secrets_manager.py validate
```

This command will validate the current configuration, checking for missing required variables and displaying a summary of the configuration.

#### Generating a Template .env File

```bash
./secrets_manager.py generate-template --output-file env.template
```

This command will generate a template .env file with all required and optional variables, with sensitive values masked.

#### Syncing All Secrets

```bash
./secrets_manager.py sync-all
```

This command will sync all secrets to all destinations: .env file, Pulumi ESC, and GitHub Secrets.

## Best Practices

### 1. Use a Master .env File

Maintain a master .env file with all required secrets in a secure location (e.g., password manager). Use this file as the source of truth for all repositories.

### 2. Sync to Pulumi ESC

Sync all secrets to Pulumi ESC to make them available to all repositories and environments. This provides a centralized location for secret management.

### 3. Validate Before Deployment

Always validate the secret configuration before deploying to ensure all required secrets are present and valid.

### 4. Use Template Files

Generate template .env files for new team members to fill in with their own secrets. This ensures consistency across all development environments.

### 5. Rotate Secrets Regularly

Rotate secrets regularly to maintain security. Update the master .env file and sync to all destinations.

### 6. Use Different Secrets for Different Environments

Use different secrets for development, staging, and production environments to maintain separation of concerns.

### 7. Limit Access to Secrets

Limit access to secrets to only those who need them. Use Pulumi ESC's access control features to restrict access to sensitive secrets.

## Troubleshooting

### Missing Environment Variables

If you encounter missing environment variables, use the `detect-missing` command to identify them:

```bash
./secrets_manager.py detect-missing
```

Then, add the missing variables to your .env file or import them from another source.

### Pulumi ESC Access Issues

If you encounter issues accessing Pulumi ESC, ensure that:

1. The `PULUMI_ACCESS_TOKEN` environment variable is set correctly
2. The Pulumi CLI is installed and configured
3. You have the necessary permissions to access the Pulumi organization and project

### GitHub Secrets Access Issues

If you encounter issues accessing GitHub Secrets, ensure that:

1. The GitHub CLI (gh) is installed and authenticated
2. You have the necessary permissions to access the GitHub repository
3. The repository URL is correctly configured in Git

### SSL Certificate Issues

If you encounter SSL certificate verification issues, run the SSL certificate fix script:

```bash
python3 fix_ssl_certificates.py
```

Then add the following line to your `.bashrc` or `.zshrc` file:

```bash
export SSL_CERT_FILE=/path/to/certifi/cacert.pem
```

Replace `/path/to/certifi/cacert.pem` with the path displayed by the SSL certificate fix script.

## Conclusion

The Sophia AI secrets management system provides a comprehensive solution for managing secrets and environment variables across different repositories and environments. By following the guidelines in this document, you can ensure that your secrets are secure, consistent, and easily manageable.
