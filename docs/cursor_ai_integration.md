# Sophia AI - Enhanced Cursor IDE Integration

## Infrastructure as Code Commands

### Pulumi ESC Operations
- **Get Secret**: `python infrastructure/esc/get_secret.py --secret-name <name> --environment production`
- **Rotate Secrets**: `python infrastructure/esc/secret_rotation_framework.py --service <service> --environment production`
- **Sync Secrets**: `python infrastructure/esc/github_sync_bidirectional.py --direction bidirectional --environment production`
- **Setup ESC**: `bash infrastructure/esc/setup_esc.sh --environment production`

### GitHub Actions Workflows
- **Deploy All**: Trigger `sophia-main.yml` workflow with manual dispatch
- **Test ESC**: Trigger `test_esc_integration.yml` workflow for validation
- **Rotate Secrets**: Trigger `rotate_secrets.yml` workflow for secret rotation
- **Sync Secrets**: Trigger `sync_secrets.yml` workflow for synchronization

### Natural Language Commands for Infrastructure
When working with infrastructure, use these patterns:

#### Secret Management
- "Get the Snowflake password" → `python infrastructure/esc/get_secret.py --secret-name snowflake_password --environment production`
- "Rotate all API keys" → `python infrastructure/esc/secret_rotation_framework.py --environment production`
- "Sync GitHub secrets to Pulumi" → `python infrastructure/esc/github_sync_bidirectional.py --direction github-to-pulumi`

#### Deployment Operations
- "Deploy to production" → Trigger GitHub Actions workflow `sophia-main.yml`
- "Test the infrastructure" → Trigger GitHub Actions workflow `test_esc_integration.yml`
- "Check deployment status" → Review GitHub Actions workflow runs

#### Service Configuration
- "Configure Gong integration" → Edit `infrastructure/integration_registry.json` and run sync
- "Update Vercel settings" → Use `python infrastructure/manage_integrations.py --service vercel --action update`
- "List all integrations" → `python infrastructure/manage_integrations.py --action list`

### MCP Server Integration Commands
- **Start MCP Servers**: `docker-compose -f docker-compose.mcp.yml up -d`
- **Check MCP Status**: `curl http://localhost:8000/snowflake/health`
- **Query via MCP**: Use the MCP client tools in `backend/mcp/`

### Development Workflow
1. **Local Development**: Use `.env` file with `env.minimal.example` as template
2. **Secret Management**: Always use Pulumi ESC for production secrets
3. **Testing**: Run ESC integration tests before deployment
4. **Deployment**: Use GitHub Actions for all production deployments

### Security Best Practices
- Never hardcode secrets in code
- Always use environment variables from Pulumi ESC
- Rotate secrets monthly using automated workflows
- Validate all secret operations with dry-run mode first

### Troubleshooting Commands
- **Check ESC Status**: `pulumi stack ls` and `pulumi config`
- **Validate Secrets**: `python infrastructure/esc/get_secret.py --test-mode`
- **Debug Workflows**: Check GitHub Actions logs and artifacts
- **MCP Debugging**: Check Docker logs with `docker-compose logs`



### Backend Configuration Integration Commands
When working with backend configuration, use these enhanced patterns:

#### Configuration Management
- "Check service configuration for Gong" → `python -c "import asyncio; from backend.core.config_manager import get_config; print(asyncio.run(get_config('gong')))"`
- "Validate all integrations" → `python -c "import asyncio; from backend.core.config_manager import list_services, health_check; services = asyncio.run(list_services()); [print(f'{s}: {asyncio.run(health_check(s))}') for s in services]"`
- "List registered services" → `python -c "import asyncio; from backend.core.config_manager import list_services; print(asyncio.run(list_services()))"`
- "Refresh configuration cache" → `python -c "import asyncio; from backend.core.config_manager import refresh_cache; asyncio.run(refresh_cache())"`

#### Secret Management with Backend Integration
- "Get Snowflake connection string" → `python -c "import asyncio; from backend.core.config_manager import get_connection_string; print(asyncio.run(get_connection_string('snowflake')))"`
- "Test Gong API client" → `python -c "import asyncio; from backend.core.config_manager import get_api_client; client = asyncio.run(get_api_client('gong')); print('Client ready' if client else 'Failed')"`
- "Check Pinecone health" → `python -c "import asyncio; from backend.core.config_manager import health_check; print(asyncio.run(health_check('pinecone')))"`

#### Integration Registry Operations
- "Register new integration" → Use `backend/core/integration_registry.py` with proper service configuration
- "Get integration metadata" → `python -c "import asyncio; from backend.core.config_manager import get_service_metadata; print(asyncio.run(get_service_metadata('estuary')))"`
- "List integration types" → `python -c "import asyncio; from backend.core.config_manager import list_services, get_service_metadata; services = asyncio.run(list_services()); [print(f'{s}: {asyncio.run(get_service_metadata(s)).get(\"type\")}') for s in services]"`

#### Advanced Configuration Operations
- "Validate Estuary integration setup" → `python -c "import asyncio; from backend.integrations.estuary_flow_integration_updated import EstuaryFlowClient; client = EstuaryFlowClient(); asyncio.run(client.setup()); print('Setup complete')"`
- "Test vector database connections" → `python -c "import asyncio; from backend.vector.vector_integration_updated import VectorIntegration; vi = VectorIntegration(); asyncio.run(vi.setup()); print('Vector setup complete')"`

### Enhanced Natural Language Processing for Complex Operations
When using Cursor AI for complex infrastructure operations:

#### Multi-Service Operations
- "If Snowflake is down, check backup database status" → Conditional health checks with fallback logic
- "Rotate secrets for all API services except OpenAI" → Selective secret rotation with exclusions
- "Deploy backend only if all integrations pass health checks" → Conditional deployment with validation

#### Error Recovery and Troubleshooting
- "Check why Gong integration is failing" → `python -c "import asyncio; from backend.core.config_manager import health_check, get_service_metadata; print(f'Health: {asyncio.run(health_check(\"gong\"))}'); print(f'Config: {asyncio.run(get_service_metadata(\"gong\"))}')"` 
- "Show performance metrics for vector search" → Access vector integration performance stats
- "Diagnose secret rotation issues" → Check secret rotation logs and status

#### Configuration Validation and Testing
- "Validate all service configurations" → Comprehensive configuration validation across all services
- "Test all API connections" → Batch API connection testing
- "Check configuration completeness" → Validate required configuration keys are present

### MCP Server Integration with Backend Configuration
Enhanced MCP integration leveraging the new backend configuration system:

#### Dynamic MCP Server Discovery
- "List available MCP servers" → Query MCP server registry with backend integration
- "Start MCP servers for active integrations" → Dynamic MCP server startup based on configured services
- "Check MCP server health for all services" → Comprehensive MCP health monitoring

#### Natural Language MCP Queries
- "Query Gong for recent calls using MCP" → `curl -X POST http://localhost:8000/gong/query -d '{"query": "recent calls"}'`
- "Get Snowflake table schema via MCP" → `curl -X POST http://localhost:8000/snowflake/schema -d '{"table": "target_table"}'`
- "Deploy to Vercel using MCP agent" → `curl -X POST http://localhost:8000/vercel/deploy -d '{"project": "sophia-ai"}'`

#### Cross-Service MCP Operations
- "Sync data from Gong to Snowflake via MCP" → Multi-service MCP orchestration
- "Update vector embeddings from latest Snowflake data" → Data pipeline orchestration via MCP
- "Backup all service configurations to GitHub" → Configuration backup via MCP

### Performance Monitoring and Optimization
Enhanced monitoring capabilities with backend integration:

#### Performance Metrics
- "Show API response times for all services" → Performance monitoring dashboard
- "Check cache hit rates for configuration manager" → Cache performance analysis
- "Monitor secret rotation status" → Secret rotation monitoring

#### Optimization Commands
- "Optimize vector search performance" → Vector database optimization
- "Clear all configuration caches" → Cache management
- "Refresh stale connections" → Connection pool management

### Security and Compliance
Enhanced security operations with centralized configuration:

#### Security Validation
- "Audit all secret access patterns" → Security audit logging
- "Validate secret rotation schedules" → Compliance checking
- "Check for exposed secrets in logs" → Security scanning

#### Compliance Operations
- "Generate security compliance report" → Automated compliance reporting
- "Validate access control policies" → Access control validation
- "Check encryption status for all secrets" → Encryption validation

