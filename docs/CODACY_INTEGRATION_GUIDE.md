# Codacy Integration Guide for Sophia AI

## Overview

This guide provides comprehensive instructions for integrating Codacy code quality and security analysis into the Sophia AI platform, optimized for macOS and Cursor IDE development workflows.

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Installation and Setup](#installation-and-setup)
- [Cursor IDE Integration](#cursor-ide-integration)
- [MCP Server Configuration](#mcp-server-configuration)
- [Usage Examples](#usage-examples)
- [Custom Rules for Sophia AI](#custom-rules-for-sophia-ai)
- [Dashboard Integration](#dashboard-integration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Quick Start

### Automated Setup (Recommended)

```bash
# Run the automated setup script
./scripts/setup_codacy_macos.sh

# Start the MCP server
docker-compose -f docker-compose.mcp-gateway.yml up -d codacy-mcp

# Verify installation
./scripts/codacy_health_check.sh
```

### Manual Setup

1. **Install Codacy CLI**:
   ```bash
   bash <(curl -Ls https://raw.githubusercontent.com/codacy/codacy-cli-v2/main/codacy-cli.sh)
   ```

2. **Configure Environment**:
   ```bash
   export CODACY_ACCOUNT_TOKEN="your_api_token"
   export CODACY_WORKSPACE_PATH="/Users/lynnmusil/sophia-main"
   ```

3. **Start MCP Server**:
   ```bash
   docker-compose -f docker-compose.mcp-gateway.yml up -d codacy-mcp
   ```

## Architecture Overview

### Integration Components

```
Cursor IDE
    ↓
Codacy MCP Server (Port 3008)
    ↓
┌─────────────────┬─────────────────┐
│   Codacy CLI    │   Codacy API    │
│   (Local)       │   (Cloud)       │
└─────────────────┴─────────────────┘
    ↓                   ↓
Code Analysis       Project Metrics
```

### Key Components

1. **Codacy MCP Server**: `mcp-servers/codacy/codacy_mcp_server.py`
2. **Backend API Routes**: `backend/api/codacy_integration_routes.py`
3. **Cursor Configuration**: `.cursor/mcp_settings.json`
4. **Docker Integration**: `docker-compose.mcp-gateway.yml`
5. **Custom Rules**: `.codacy/custom-rules/`

## Installation and Setup

### Prerequisites

- **macOS**: 10.15+ (Catalina or later)
- **Node.js**: 18.0+ (LTS recommended)
- **Python**: 3.11+
- **Docker**: Latest version
- **Cursor IDE**: Latest version

### Step-by-Step Installation

#### 1. System Prerequisites

```bash
# Verify system requirements
sw_vers                    # Check macOS version
node --version            # Check Node.js (should be 18+)
python3 --version         # Check Python (should be 3.11+)
docker --version          # Check Docker
```

#### 2. Install Codacy CLI

```bash
# Install via official script
bash <(curl -Ls https://raw.githubusercontent.com/codacy/codacy-cli-v2/main/codacy-cli.sh)

# Verify installation
codacy-cli --version
```

#### 3. Configure Codacy Account

1. **Create Codacy Account**: [codacy.com/signup](https://www.codacy.com/signup-codacy)
2. **Get API Token**:
   - Go to Account Settings → API Tokens
   - Create new token with appropriate scopes
   - Save securely

#### 4. Set Environment Variables

```bash
# Add to ~/.zshrc or ~/.bash_profile
export CODACY_ACCOUNT_TOKEN="your_api_token_here"
export CODACY_WORKSPACE_PATH="/Users/lynnmusil/sophia-main"

# Reload shell
source ~/.zshrc
```

#### 5. Configure Project

```bash
# Create Codacy configuration directory
mkdir -p .codacy/{config,tools,reports,cache,custom-rules}

# The setup script creates the configuration automatically
# Or manually create .codacy/config.yml (see Configuration section)
```

## Cursor IDE Integration

### MCP Server Configuration

The Codacy MCP server is automatically configured in `.cursor/mcp_settings.json`:

```json
{
  "mcpServers": {
    "codacy": {
      "command": "python",
      "args": ["-m", "mcp-servers.codacy.codacy_mcp_server"],
      "cwd": "/Users/lynnmusil/sophia-main",
      "env": {
        "CODACY_ACCOUNT_TOKEN": "${ESC_CODACY_ACCOUNT_TOKEN}",
        "CODACY_PROJECT_TOKEN": "${ESC_CODACY_PROJECT_TOKEN}",
        "CODACY_WORKSPACE_PATH": "/Users/lynnmusil/sophia-main"
      }
    }
  }
}
```

### Cursor Workspace Settings

Create `.vscode/settings.json` for optimal Cursor integration:

```json
{
  "codacy.enableRealTimeAnalysis": true,
  "codacy.autoFixOnSave": false,
  "codacy.showInlineIssues": true,
  "codacy.analysisTimeout": 60000,
  "codacy.excludePatterns": [
    "node_modules/**",
    "dist/**",
    "build/**",
    ".git/**",
    "docs_archive_*/**",
    "__pycache__/**"
  ]
}
```

### Cursor AI Commands

Use these natural language commands in Cursor:

```
@codacy analyze this file
@codacy security scan the project
@codacy fix issues automatically
@codacy generate executive report
@codacy check Sophia AI architecture compliance
```

## MCP Server Configuration

### Docker Deployment

The Codacy MCP server runs as a Docker container:

```yaml
# docker-compose.mcp-gateway.yml
codacy-mcp:
  build:
    context: ./mcp-servers/codacy
    dockerfile: Dockerfile
  environment:
    - CODACY_ACCOUNT_TOKEN=${CODACY_ACCOUNT_TOKEN}
    - CODACY_PROJECT_TOKEN=${CODACY_PROJECT_TOKEN}
    - CODACY_WORKSPACE_PATH=/workspace
    - MCP_TRANSPORT=sse
    - MCP_PORT=3008
  ports:
    - "3008:3008"
  volumes:
    - .:/workspace:ro
```

### Available MCP Tools

1. **analyze_project**: Comprehensive code analysis
2. **security_scan**: Security-focused analysis
3. **quality_metrics**: Code quality metrics
4. **fix_issues**: Automatic issue fixing
5. **get_project_status**: Overall project health
6. **coverage_analysis**: Code coverage analysis
7. **duplication_analysis**: Code duplication detection
8. **custom_rules**: Sophia AI specific rules
9. **integration_health**: Health monitoring
10. **generate_report**: Executive reporting

## Usage Examples

### Basic Analysis

```bash
# Run comprehensive analysis
curl -X POST http://localhost:8000/api/v1/integrations/codacy/analyze \
  -H "Content-Type: application/json" \
  -d '{"severity": "warning", "format": "json"}'

# Security scan
curl -X POST http://localhost:8000/api/v1/integrations/codacy/security-scan \
  -H "Content-Type: application/json"

# Quality metrics
curl -X GET http://localhost:8000/api/v1/integrations/codacy/quality-metrics
```

### Cursor AI Integration

```
# In Cursor AI chat:
@codacy What security issues are in this project?
@codacy Analyze the backend/agents/ directory for quality issues
@codacy Generate an executive report on code quality
@codacy Fix all automatically fixable issues
```

### API Integration

```python
# Python example
import aiohttp

async def analyze_code():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:8000/api/v1/integrations/codacy/analyze',
            json={'severity': 'error', 'format': 'json'}
        ) as response:
            result = await response.json()
            return result
```

## Custom Rules for Sophia AI

### Security Rules (`.codacy/custom-rules/sophia-security.yml`)

```yaml
rules:
  no-hardcoded-secrets:
    severity: error
    pattern: '(password|secret|key|token)\s*[:=]\s*["\'][^"\']*["\']'
    message: "Hardcoded secrets detected. Use Pulumi ESC for secret management."
    
  require-env-vars:
    severity: warning
    pattern: 'os\.getenv\(["\'][^"\']*["\'],\s*["\'][^"\']*["\']'
    message: "Consider using Pulumi ESC integration instead of default values."
    
  mcp-auth-required:
    severity: error
    pattern: 'mcp.*server.*without.*auth'
    message: "MCP servers must implement proper authentication."
```

### Performance Rules (`.codacy/custom-rules/sophia-performance.yml`)

```yaml
rules:
  async-await-required:
    severity: warning
    pattern: 'def.*api.*\(.*\):(?!.*async)'
    message: "API endpoints should use async/await for better performance."
    
  connection-pooling:
    severity: warning
    pattern: 'create_engine.*pool_size.*None'
    message: "Database connections should use connection pooling."
```

### Architecture Rules (`.codacy/custom-rules/sophia-architecture.yml`)

```yaml
rules:
  mcp-server-structure:
    severity: info
    pattern: 'class.*MCP.*Server.*:(?!.*def setup_handlers)'
    message: "MCP servers should follow the established pattern with setup_handlers method."
    
  agent-categorization:
    severity: warning
    pattern: 'class.*Agent.*:(?!.*category.*=)'
    message: "Agents should specify their category for proper routing."
```

## Dashboard Integration

### Executive Summary Endpoint

```http
GET /api/v1/integrations/codacy/dashboard/summary
```

Response:
```json
{
  "overall_health": "healthy",
  "total_files": 150,
  "python_files": 75,
  "typescript_files": 45,
  "security_status": "secure",
  "quality_grade": "A",
  "last_analysis": "2024-08-15T14:30:00Z",
  "recommendations": [
    "Continue following current code quality practices",
    "Consider adding more automated tests",
    "Review security configurations regularly"
  ]
}
```

### Cursor Integration Analysis

```http
POST /api/v1/integrations/codacy/cursor-integration
```

Response:
```json
{
  "cursor_optimization": {
    "architecture_compliance": {...},
    "security_compliance": {...},
    "performance_compliance": {...},
    "overall_score": 95,
    "cursor_ready": true
  },
  "recommendations_for_cursor": [
    "MCP server patterns are well implemented",
    "Agent categorization follows best practices"
  ]
}
```

## Troubleshooting

### Common Issues

#### 1. CLI Not Found

```bash
# Check PATH
echo $PATH

# Reinstall CLI
bash <(curl -Ls https://raw.githubusercontent.com/codacy/codacy-cli-v2/main/codacy-cli.sh)

# Add to PATH manually
export PATH="$HOME/.local/bin:$PATH"
```

#### 2. API Authentication Errors

```bash
# Verify token
curl -H "Accept: application/json" \
     -H "api-token: $CODACY_ACCOUNT_TOKEN" \
     https://app.codacy.com/api/v3/user

# Check environment variables
echo $CODACY_ACCOUNT_TOKEN
```

#### 3. MCP Server Connection Issues

```bash
# Check MCP server logs
docker logs codacy-mcp

# Restart MCP server
docker-compose -f docker-compose.mcp-gateway.yml restart codacy-mcp

# Test MCP connectivity
curl http://localhost:3008/health
```

#### 4. Analysis Timeout

```bash
# Increase timeout in configuration
# Edit .codacy/config.yml:
analysis:
  timeout: 300  # 5 minutes
```

### Health Check Script

```bash
# Run comprehensive health check
./scripts/codacy_health_check.sh

# Manual health checks
codacy-cli --version
curl http://localhost:8000/api/v1/integrations/codacy/health
docker ps | grep codacy-mcp
```

### Debug Mode

```bash
# Enable debug logging
export CODACY_LOG_LEVEL=debug

# Run with verbose output
codacy-cli analyze --verbose --directory . --format json
```

## Best Practices

### Development Workflow

1. **Pre-commit Analysis**:
   ```bash
   # Add to .git/hooks/pre-commit
   codacy-cli analyze --directory . --severity error --exit-code
   ```

2. **Continuous Integration**:
   ```yaml
   # GitHub Actions example
   - name: Codacy Analysis
     run: |
       codacy-cli analyze --format sarif --output codacy-results.sarif
       # Upload to GitHub Security tab
   ```

3. **Regular Monitoring**:
   ```bash
   # Weekly quality check
   codacy-cli analyze --format json --output weekly-report.json
   ```

### Configuration Management

1. **Environment-Specific Rules**:
   ```yaml
   # .codacy/config.yml
   environments:
     development:
       severity_threshold: info
     production:
       severity_threshold: error
   ```

2. **Team Standards**:
   ```yaml
   # Enforce team coding standards
   quality:
     maintainability_threshold: B
     security_threshold: A
     coverage_threshold: 80
   ```

### Performance Optimization

1. **Incremental Analysis**:
   ```bash
   # Analyze only changed files
   git diff --name-only HEAD~1 | xargs codacy-cli analyze --files
   ```

2. **Parallel Processing**:
   ```yaml
   # .codacy/config.yml
   analysis:
     parallel_jobs: 4
     timeout: 300
   ```

3. **Caching**:
   ```yaml
   # .codacy/config.yml
   cache:
     enabled: true
     directory: .codacy/cache
     ttl: 86400  # 24 hours
   ```

### Security Best Practices

1. **Secret Management**:
   - Never commit API tokens
   - Use Pulumi ESC for secret storage
   - Rotate tokens regularly

2. **Access Control**:
   - Limit API token permissions
   - Use project-specific tokens
   - Monitor token usage

3. **Data Privacy**:
   - Review data sharing policies
   - Exclude sensitive files from analysis
   - Use on-premises deployment if required

## Maintenance and Updates

### Regular Updates

```bash
# Update Codacy CLI
bash <(curl -Ls https://raw.githubusercontent.com/codacy/codacy-cli-v2/main/codacy-cli.sh)

# Update MCP server
docker-compose -f docker-compose.mcp-gateway.yml pull codacy-mcp
docker-compose -f docker-compose.mcp-gateway.yml up -d codacy-mcp

# Update custom rules
git pull origin main  # If rules are in version control
```

### Backup Configuration

```bash
# Create backup
tar -czf codacy-backup-$(date +%Y%m%d).tar.gz .codacy/

# Restore backup
tar -xzf codacy-backup-YYYYMMDD.tar.gz
```

### Monitoring

```bash
# Set up monitoring alerts
# Add to crontab:
0 9 * * * /path/to/sophia-main/scripts/codacy_health_check.sh | mail -s "Codacy Health Report" admin@payready.com
```

## Integration with Sophia AI Ecosystem

### MCP Server Ecosystem

Codacy integrates seamlessly with other Sophia AI MCP servers:

- **AI Memory**: Store code quality insights
- **GitHub**: Link issues to commits
- **Slack**: Send quality alerts
- **Pulumi**: Infrastructure compliance checks

### Business Intelligence

Code quality metrics feed into executive dashboards:

- **Technical Debt Tracking**: Quantify maintenance burden
- **Security Posture**: Track vulnerability trends
- **Development Velocity**: Correlate quality with delivery speed
- **Team Performance**: Individual and team quality metrics

### Continuous Improvement

- **Automated Fixes**: Integrate with CI/CD pipelines
- **Quality Gates**: Prevent deployment of low-quality code
- **Trend Analysis**: Track quality improvements over time
- **Best Practice Sharing**: Learn from high-quality code patterns

This comprehensive integration ensures that code quality is not just measured but actively improved as part of the Sophia AI development workflow. 