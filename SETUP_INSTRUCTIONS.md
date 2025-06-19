# Sophia AI Setup Instructions

This document provides comprehensive instructions for setting up the Sophia AI system, including environment configuration, secret management, and troubleshooting common issues.

## Prerequisites

Before setting up Sophia AI, ensure you have the following prerequisites installed:

1. **Python 3.11+**: Required for running the Sophia AI backend
2. **Docker**: Required for running the MCP servers
3. **Docker Compose**: Required for orchestrating the MCP servers
4. **Git**: Required for version control
5. **Pulumi CLI**: Required for infrastructure management (optional)
6. **GitHub CLI**: Required for GitHub integration (optional)

## Initial Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sophia-main
```

### 2. Create a Virtual Environment

```bash
python -m venv sophia_venv
source sophia_venv/bin/activate  # On Windows: sophia_venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file with the required environment variables:

```bash
# Generate a template .env file
./secrets_manager.py generate-template

# Edit the template file with your secrets
cp env.template .env
nano .env  # or use your preferred editor
```

### 5. Fix SSL Certificate Issues

If you encounter SSL certificate verification issues, run the SSL certificate fix script:

```bash
./fix_ssl_certificates.py
```

This will:
- Create a wrapper script (`run_with_ssl_fix.py`) for running Python scripts with SSL certificate verification
- Update your `.env` file with the SSL certificate path
- Update your shell profile with the SSL certificate path

### 6. Validate Configuration

```bash
./secrets_manager.py validate
```

This will check if all required environment variables are set and display a summary of the configuration.

### 7. Start the MCP Servers

```bash
./start_mcp_servers.py
```

This will:
- Check if Docker and Docker Compose are installed
- Validate the Docker Compose configuration
- Fix common issues in the Docker Compose file
- Start the MCP servers
- Check the health of the MCP servers

## Secret Management

Sophia AI uses a comprehensive secret management system to handle sensitive information across different environments and repositories.

### Required Environment Variables

The following environment variables are required for Sophia AI to function properly:

#### Core API Keys

- `ANTHROPIC_API_KEY`: Claude API key for AI capabilities
- `OPENAI_API_KEY`: OpenAI API key for AI capabilities (optional)
- `PULUMI_ACCESS_TOKEN`: Pulumi access token for infrastructure management

#### Slack Integration

- `SLACK_BOT_TOKEN`: Slack bot token for Slack integration
- `SLACK_APP_TOKEN`: Slack app token for Slack integration
- `SLACK_SIGNING_SECRET`: Slack signing secret for Slack integration

#### Linear Integration

- `LINEAR_API_TOKEN`: Linear API token for project management integration
- `LINEAR_WORKSPACE_ID`: Linear workspace ID for project management integration

#### Gong Integration

- `GONG_CLIENT_ID`: Gong client ID for call analysis integration
- `GONG_CLIENT_SECRET`: Gong client secret for call analysis integration

#### Database Credentials

- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: PostgreSQL database name

#### Vercel Integration

- `VERCEL_ACCESS_TOKEN`: Vercel access token for deployment integration
- `VERCEL_TEAM_ID`: Vercel team ID for deployment integration

#### Lambda Labs Integration

- `LAMBDA_LABS_API_KEY`: Lambda Labs API key for compute resources

#### Vector Database Integration

- `PINECONE_API_KEY`: Pinecone API key for vector database
- `WEAVIATE_API_KEY`: Weaviate API key for vector database

#### Snowflake Integration

- `SNOWFLAKE_ACCOUNT`: Snowflake account identifier
- `SNOWFLAKE_USER`: Snowflake username
- `SNOWFLAKE_PASSWORD`: Snowflake password
- `SNOWFLAKE_DATABASE`: Snowflake database name

#### Estuary Integration

- `ESTUARY_API_KEY`: Estuary API key for data flow management

#### Airbyte Integration

- `AIRBYTE_API_KEY`: Airbyte API key for data integration

#### Environment Configuration

- `SOPHIA_ENVIRONMENT`: Environment name (development, staging, production)
- `PULUMI_ORGANIZATION`: Pulumi organization name
- `PULUMI_PROJECT`: Pulumi project name

### Secret Management Commands

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

## MCP Server Management

Sophia AI uses MCP (Model Context Protocol) servers to provide additional capabilities to the system. These servers are managed using Docker Compose.

### Starting MCP Servers

```bash
./start_mcp_servers.py
```

This command will start the MCP servers defined in the `mcp_config.json` file.

### Checking MCP Server Status

```bash
docker-compose -f docker-compose.mcp.yml ps
```

This command will display the status of the MCP servers.

### Viewing MCP Server Logs

```bash
docker-compose -f docker-compose.mcp.yml logs
```

This command will display the logs of the MCP servers.

### Stopping MCP Servers

```bash
docker-compose -f docker-compose.mcp.yml down
```

This command will stop the MCP servers.

## Troubleshooting

### SSL Certificate Issues

If you encounter SSL certificate verification issues, run the SSL certificate fix script:

```bash
./fix_ssl_certificates.py
```

This will:
- Create a wrapper script (`run_with_ssl_fix.py`) for running Python scripts with SSL certificate verification
- Update your `.env` file with the SSL certificate path
- Update your shell profile with the SSL certificate path

You can also run Python scripts with the SSL certificate fix applied:

```bash
./run_with_ssl_fix.py <script> [args...]
```

For example:

```bash
./run_with_ssl_fix.py automated_health_check.py
```

### Missing Environment Variables

If you encounter missing environment variables, use the `detect-missing` command to identify them:

```bash
./secrets_manager.py detect-missing
```

Then, add the missing variables to your `.env` file or import them from another source.

### Docker Compose Issues

If you encounter issues with Docker Compose, check the Docker Compose configuration:

```bash
docker-compose -f docker-compose.mcp.yml config
```

This will validate the Docker Compose configuration and display any errors.

You can also try to fix common issues in the Docker Compose file:

```bash
./start_mcp_servers.py
```

This script will attempt to fix common issues in the Docker Compose file before starting the MCP servers.

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

### Python Package Compatibility Issues

If you encounter Python package compatibility issues, check your `requirements.txt` for version pins and update as needed.

For example, if you encounter an error like:

```
ImportError: cannot import name 'eval_type_backport' from 'pydantic._internal._typing_extra'
```

This is likely due to a version mismatch between your `mcp` package and `pydantic`. You can fix this by upgrading/downgrading `pydantic` and `mcp` to compatible versions.

### Database Connection Issues

If you encounter database connection issues, ensure that:

1. The database credentials are set correctly in your `.env` file
2. The database server is running and accessible
3. The database exists and has the correct permissions

### API Endpoint Issues

If you encounter API endpoint issues, ensure that:

1. The API server is running and accessible
2. The API endpoint URL is correct
3. You have the necessary permissions to access the API

## Setting Up a New Repository

If you need to set up a new Sophia AI repository, you can use the `setup_new_repo.py` script:

```bash
./setup_new_repo.py --name sophia-new-repo
```

This will:
- Create a new directory for the repository
- Initialize a Git repository
- Copy the secrets_manager.py script
- Set up the necessary configuration files
- Create a README.md file with setup instructions

You can also import secrets from a master .env file:

```bash
./setup_new_repo.py --name sophia-new-repo --source-env /path/to/master.env
```

Or import secrets from Pulumi ESC:

```bash
./setup_new_repo.py --name sophia-new-repo --from-pulumi
```

## Additional Resources

For more information, refer to the following resources:

- [Secrets Management Guide](SECRETS_MANAGEMENT_GUIDE.md): Comprehensive guide for managing secrets and environment variables
- [MCP Server Documentation](docs/mcp_server_documentation.md): Documentation for the MCP servers
- [API Documentation](docs/API_DOCUMENTATION.md): Documentation for the Sophia AI API
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md): Guide for deploying Sophia AI
- [Troubleshooting Guide](docs/TROUBLESHOOTING_GUIDE.md): Guide for troubleshooting common issues
