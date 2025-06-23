# Sophia AI Platform

A comprehensive AI platform with MCP (Model Context Protocol) integration, deployed on Lambda Labs infrastructure.

> **Note**
> The repository contains references to an experimental Agno integration.
> That integration is not included in the codebase at this time.

## 🚀 AI-First Codebase: Optimized for AI Coding Agents

**This repository is designed for AI-first development.**
- All core logic, agent orchestration, and performance monitoring are structured for seamless collaboration between human and AI coders.
 - The codebase references an `AgnoPerformanceOptimizer`, but the actual integration is not included.
- Live agent performance metrics are available via API and the CEO dashboard.

## 🧠 Quickstart for AI Coders

- **Agent Instantiation:**
  - Use the `pooled` classmethod for all major agents (e.g., `await SalesCoachAgent.pooled(config)`).
  - All agents were originally expected to register with `AgnoPerformanceOptimizer` for pooling and tracking, but that system is not implemented.
- **Performance Metrics:**
  - The `/api/metrics/agno-performance` endpoint is not available since the Agno integration is missing.
- **Code Structure:**
  - Feature-based, vertical slice architecture for easy navigation by AI tools.
  - All business logic, integrations, and workflows are grouped by feature.
- **API Integration:**
  - All endpoints are documented with clear input/output schemas.
  - Use the FastAPI OpenAPI docs at `/docs` for live API exploration.

## 🏗️ Agent Pooling & Performance

- **AgnoPerformanceOptimizer (not implemented):**
  - Documentation references this component, but it is not available in the repository.
  - Metrics and pooling features tied to Agno are therefore not functional.
- **How to Use:**
  - When the integration becomes available, register agent classes with the optimizer for pooling.
  - Use the `pooled` classmethod for agent instantiation once Agno is integrated.

## 📊 Live Monitoring & CEO Dashboard

- **CEO Dashboard:**
  - View live agent performance metrics, business KPIs, and system health in one place.
  - Accessible at `/ceo-dashboard` (see frontend for details).
  - **API Metrics:**
  - The `/api/metrics/agno-performance` endpoint is referenced in older docs but is not implemented.

## 📚 Documentation for AI & Human Developers

- **AI-First Documentation:**
  - All docstrings, comments, and guides are structured for easy parsing by AI coding agents.
  - Key integration points, agent APIs, and performance hooks are clearly marked.
- **Human-Friendly Guides:**
  - See `docs/AGNO_VSA_IMPLEMENTATION_PLAN.md` and `docs/AGNO_VSA_IMPLEMENTATION_ROADMAP.md` for architecture and migration details.
  - All configuration files are YAML/JSON and include inline comments for clarity.
- **API Reference:**
  - FastAPI OpenAPI docs at `/docs`.
  - Agent pooling and performance API endpoints will be documented once Agno integration is available.

## 📝 Contributing (AI & Human)

- All code contributions should use the pooled agent pattern and follow the vertical slice architecture.
- Document new agents, endpoints, and performance hooks with clear, AI-readable docstrings and comments.
- Use the CEO dashboard and API metrics to monitor performance impact of changes.

## 🛡️ Security & Best Practices

- All secrets and credentials are managed via Pulumi ESC and GitHub Organization Secrets.
- Never hardcode secrets or credentials in code or configuration files.
- See `backend/core/auto_esc_config.py` for secure secret loading patterns.

## 📦 Deployment & Rollout

- All changes are feature-flagged and can be rolled out safely.
- Use the deployment checklist in `docs/AGNO_VSA_IMPLEMENTATION_ROADMAP.md` before going live.
- Monitor live metrics and system health via the CEO dashboard during and after deployment.

## 📚 Current Infrastructure

### Server Configuration
- **Provider**: Lambda Labs
- **Instance**: gpu_1x_a10 (1x A10 24GB, 30 vCPUs, 200GB RAM)
- **IP**: 170.9.9.253
- **Cost**: $0.75/hour (~$540/month)
- **SSH Key**: cherry-ai-key

### Key Components
- **Kubernetes**: K3s cluster for container orchestration
- **MCP Servers**: Snowflake, Pulumi, and custom integrations
- **Data Pipeline**: Airbyte + Snowflake + Pinecone
- **AI Models**: Anthropic Claude, OpenAI GPT
- **Monitoring**: Comprehensive logging and metrics

## 📋 Architecture

### MCP Integration
The platform uses Model Context Protocol (MCP) for standardized AI-tool communication:
- **Snowflake MCP**: Data warehouse operations
- **Pulumi MCP**: Infrastructure management
- **Custom MCPs**: Business-specific integrations

### Data Flow
```
External APIs → Airbyte → Snowflake → Vector Processing → Pinecone → AI Models
```

### Service Integrations
- **CRM**: HubSpot integration for customer data
- **Sales**: Gong.io for conversation intelligence
- **Communication**: Slack for team collaboration
- **Analytics**: Arize for AI model monitoring

## 📋 Configuration Management

### Secret Management
- **Primary**: GitHub Organization Secrets (158 configured)
- **Distribution**: Pulumi ESC
- **Runtime**: Environment variables
- **Rotation**: Quarterly automated rotation

### Key Secrets
- `ANTHROPIC_API_KEY`: AI model access
- `SNOWFLAKE_*`: Data warehouse credentials
- `PINECONE_API_KEY`: Vector database
- `LAMBDA_API_KEY`: Infrastructure management

## 📋 Development

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt
# Or run the helper script which installs Python packages for you
# ./setup.sh
npm install

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Start development server
make dev
```

### MCP Server Development
```bash
cd mcp-servers/[server-name]
python main.py
```

## 📋 Deployment

### Infrastructure Deployment
```bash
cd infrastructure
pulumi stack select sophia-prod-on-lambda
pulumi up
```

### Application Deployment
Applications are automatically deployed via Kubernetes manifests when infrastructure is updated.

### Monitoring
- **Logs**: Centralized logging via Kubernetes
- **Metrics**: Prometheus + Grafana
- **Alerts**: Automated alerting for critical issues

## 📋 Security

### Access Control
- SSH key-based authentication
- GitHub organization-level secrets
- Least-privilege access principles
- Regular access reviews

### Best Practices
- No secrets in code
- Encrypted communication
- Regular security updates
- Audit logging

## 📋 Performance

### Current Capacity
- **AI Workloads**: Up to 24GB GPU memory
- **Concurrent Users**: 50-100 users
- **Data Processing**: 1TB+ daily throughput
- **Response Time**: <2s for most operations

### Scaling Options
- **Vertical**: Upgrade to H100 instances
- **Horizontal**: Multi-instance deployment
- **Auto-scaling**: Kubernetes HPA

## 📋 Troubleshooting

### Common Issues
1. **SSH Connection Failed**: Verify SSH key configuration
2. **Pulumi Deployment Failed**: Check ESC environment
3. **MCP Server Down**: Restart via Kubernetes
4. **High Costs**: Monitor resource usage

### Support
- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues
- **Emergency**: Contact platform team

## 📋 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Deploy after review

### Code Standards
- Python: Black formatting, type hints
- JavaScript: ESLint + Prettier
- Infrastructure: Pulumi best practices
- Documentation: Markdown with clear examples

## 📋 License

This project is proprietary to AI-Cherry organization.

---

**Status**: Production Ready
**Last Updated**: June 21, 2025
**Maintained By**: Sophia AI Platform Team

For detailed configuration information, see [DEPLOYMENT_CONFIGURATION_GUIDE.md](./DEPLOYMENT_CONFIGURATION_GUIDE.md)

# Sophia AI - Local Development with Pulumi ESC Secrets

## Pulumi ESC Secrets Workflow

All secrets and sensitive configuration for Sophia AI are managed in Pulumi ESC. For local development, follow this workflow to ensure your containers have the correct environment variables:

1. **Fetch secrets from Pulumi ESC:**
   ```sh
   ./scripts/dev/fetch-secrets.sh
   ```
   This will create or update a `.env.local` file in the project root with all required secrets in dotenv format.

2. **Start your stack with Docker Compose:**
   ```sh
   docker compose up
   ```
   Docker Compose will automatically load environment variables from `.env.local` and inject them into your containers.

3. **Security Note:**
   - `.env.local` is already in `.gitignore` and should never be committed to version control.
   - If secrets change in Pulumi ESC, re-run the fetch script to update your local environment.

4. **For CI/CD:**
   - Integrate the fetch script into your pipeline before any build or deploy steps that require secrets.

## Example Compose Service

```yaml
services:
  app:
    image: myapp:latest
    env_file:
      - .env.local
    ports:
      - "8080:8080"
```

---

For more details, see the Pulumi ESC documentation: https://www.pulumi.com/docs/esc/
