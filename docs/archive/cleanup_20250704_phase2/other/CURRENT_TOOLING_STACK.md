# Current Tooling Stack - Authoritative List

**Last Updated**: January 2025

This is the authoritative list of tools currently in use at Sophia AI. Any tool not on this list should NOT be referenced as part of our stack.

## Core Infrastructure

### Container Orchestration
- **Kubernetes** (on Lambda Labs) - Primary orchestration
- **Docker** - Container runtime
- **Helm** - Kubernetes package management

### Infrastructure as Code
- **Pulumi** - IaC management
- **Pulumi ESC** - Secret management (NO .env files)

### CI/CD
- **GitHub Actions** - ONLY CI/CD platform

### Reverse Proxy/Load Balancing
- **Traefik** - ONLY reverse proxy

## Development Tools

### Code Quality
- **Codacy** (via MCP server) - Primary code analysis
- **Pre-commit hooks** - Local development (Black, Ruff, Bandit)
- **pytest** - Testing framework

### Dependency Management
- **UV** - Python dependency management (NOT pip)
- **Dependabot** - Automated dependency updates

### Version Control
- **Git** / **GitHub** - Source control

## Data & Analytics

### Databases
- **PostgreSQL** - Primary database
- **Redis** - Caching and sessions
- **Snowflake** - Data warehouse

### Vector Databases
- **Pinecone** - Primary vector store
- **Weaviate** - Secondary vector store

### ELT/Data Pipeline
- **Estuary** - ONLY ELT tool (NOT Airflow/Dagster/Prefect)

## AI/ML Stack

### LLM Routing
- **UnifiedLLMService** - Central LLM routing
- **Portkey** - Primary model gateway
- **OpenRouter** - Experimental models
- **Snowflake Cortex** - Data-local operations

### Agent Orchestration
- **LangGraph** - ONLY orchestration framework (NOT LangChain)

### Memory System
- **Mem0** - Persistent memory with RLHF

## Monitoring & Observability

### Metrics
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization (dashboards in Phase 4)

### Logging
- **Python logging** - Standard logging (NOT ELK stack)

### Alerts
- **Slack webhooks** - Alert routing (Phase 4)

## Frontend

### Framework
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool

### UI Components
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library

## MCP Servers (Active)

1. **ai_memory** (port 9000) - Memory and context
2. **codacy** (port 9003) - Code analysis
3. **github** (port 9005) - Repository integration
4. **sophia_infrastructure** - Infrastructure operations
5. **snowflake_admin** (port 9012) - Database administration
6. **sophia_data** - Data operations

## What We DON'T Use

These tools are mentioned in various places but are NOT part of our stack:

- ❌ **SonarQube** - Use Codacy instead
- ❌ **Airflow/Dagster/Prefect** - Use Estuary instead
- ❌ **LangChain** - Use LangGraph instead
- ❌ **pip** - Use UV instead
- ❌ **.env files** - Use Pulumi ESC instead
- ❌ **ELK Stack** - Current logging is sufficient
- ❌ **Jenkins/CircleCI** - Use GitHub Actions instead
- ❌ **NGINX** - Use Traefik instead

## Planned Additions (Phase 4-5)

These are the ONLY new tools under consideration:

1. **Jaeger** - Distributed tracing (Phase 5+, only if needed)
2. **Grafana dashboards** - Already have Prometheus, just need dashboards
3. **Slack webhook integration** - For centralized alerts

## Key Principle

> **Only add new tools when there's a clear gap that existing tools cannot fill.**

Before proposing any new tool:
1. Check this list
2. Identify the specific gap
3. Verify existing tools can't handle it
4. Document the justification

This list is maintained as the single source of truth for our tooling decisions.
