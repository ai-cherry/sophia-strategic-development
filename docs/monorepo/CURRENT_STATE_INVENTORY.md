# Current State Inventory - Sophia AI

## Repository Structure

### Current Directory Layout
```
sophia-main/
├── backend/               # Python backend services
│   ├── agents/           # AI agent implementations
│   ├── api/              # API routes
│   ├── app/              # FastAPI applications
│   ├── core/             # Core utilities
│   ├── etl/              # ETL pipelines
│   ├── integrations/     # External service integrations
│   ├── mcp_servers/      # MCP server implementations
│   ├── monitoring/       # Monitoring services
│   ├── services/         # Business logic services
│   └── utils/            # Utility functions
├── frontend/              # React frontend
│   ├── src/
│   └── knowledge-admin/
├── mcp-servers/          # Standalone MCP servers
├── infrastructure/        # Pulumi IaC
├── kubernetes/           # K8s manifests
├── scripts/              # Utility scripts
├── docs/                 # Documentation
├── tests/                # Test files
└── external/             # External dependencies

Total directories: ~50+
Total Python files: ~400+
Total TypeScript/JavaScript files: ~100+
```

### Dependency Management

#### Python Dependencies
- **Current Method**: `pyproject.toml` with UV (recently migrated)
- **Lock File**: `uv.lock` (419 packages resolved)
- **Virtual Environment**: `.venv` managed by UV
- **Package Groups**:
  - Main dependencies: 110+ packages
  - Dev dependencies: 30+ packages
  - Optional groups: ui, docs, security, performance

#### JavaScript Dependencies
- **Frontend**: 
  - Method: npm with `package-lock.json`
  - Location: `frontend/package.json`
  - Framework: React with Vite
- **Knowledge Admin**:
  - Separate `package.json`
  - Duplicate dependencies

### CI/CD Pipelines

#### Current Workflows (`.github/workflows/`)
1. **uv-ci-cd.yml** - Main Python CI/CD with UV
2. **security-baseline-scan.yml** - Nightly security scans
3. **deploy-sophia-platform.yml** - Platform deployment
4. **sync_secrets.yml** - Secret synchronization
5. **test_integrations.yml** - Integration tests
6. Multiple service-specific workflows

**Total workflows**: 15+ YAML files
**Duplication**: High - similar steps repeated across workflows

### Build & Test Processes

#### Python Services
- **Build**: Docker with multi-stage builds
- **Test**: pytest with coverage
- **Lint**: Ruff
- **Format**: Black
- **Type Check**: MyPy

#### JavaScript Services
- **Build**: Vite for frontend
- **Test**: Jest (limited coverage)
- **Lint**: ESLint (multiple configs)
- **Format**: Prettier

### Docker Configuration

#### Dockerfiles
- **Count**: 20+ Dockerfiles
- **Patterns**: Inconsistent base images, build processes
- **Locations**: Scattered throughout codebase

#### Docker Compose
- `docker-compose.cloud.yml` - Production
- `docker-compose.prod.yml` - Legacy production
- Multiple service-specific compose files

### Configuration Files

#### Root Level
- `pyproject.toml` - Python project config
- `uv.lock` - Python lock file
- `.python-version` - Python version (3.12)
- `.cursorrules` - AI coding rules
- `Pulumi.yaml` - Infrastructure config

#### Scattered Configs
- Multiple `.eslintrc` files
- Multiple `tsconfig.json` files
- Service-specific `.env.example` files
- Inconsistent `.gitignore` patterns

## Pain Points & Inefficiencies

### 1. Dependency Management
- **Problem**: Separate dependency files for each service
- **Impact**: Version conflicts, duplicate dependencies
- **Time Lost**: ~2 hours/week resolving conflicts

### 2. CI/CD Duplication
- **Problem**: 15+ workflow files with repeated logic
- **Impact**: Maintenance overhead, inconsistent updates
- **Time Lost**: ~4 hours/week updating workflows

### 3. Build Times
- **Problem**: No shared caching between services
- **Impact**: Full rebuilds for each service
- **Current Build Time**: ~15-20 minutes
- **Potential Savings**: 50-70% with proper caching

### 4. Configuration Sprawl
- **Problem**: Configs scattered across services
- **Impact**: Inconsistent standards, hard to update
- **Time Lost**: ~1 hour/week on config issues

### 5. Testing Challenges
- **Problem**: Tests run in isolation per service
- **Impact**: Can't run full test suite easily
- **Current Test Time**: ~10 minutes per service

### 6. Local Development
- **Problem**: Complex setup for full stack
- **Impact**: New developer onboarding takes 2-3 days
- **Desired**: <2 hours for full setup

## Current Tools & Versions

### Languages & Runtimes
- Python: 3.12
- Node.js: 18.x (assumed from workflows)
- TypeScript: 5.x

### Key Dependencies
- FastAPI: 0.115.0
- React: 18.x
- Turborepo: Not used
- PNPM: Not used

### Infrastructure
- Docker: Multi-stage builds
- Kubernetes: EKS deployment ready
- Pulumi: Infrastructure as Code
- GitHub Actions: CI/CD

## Migration Requirements

### Must Maintain
1. Pulumi infrastructure compatibility
2. Docker deployment structure
3. GitHub Actions (can refactor)
4. Environment variable structure
5. Database connections

### Can Change
1. Directory structure (with mapping)
2. Build processes
3. Test execution
4. Local development setup
5. Configuration organization

## Success Metrics Baseline

### Current Performance
- **Local Build Time**: 15-20 minutes (full)
- **CI Build Time**: 20-25 minutes
- **Test Execution**: 10 minutes per service
- **Docker Image Size**: 1.5-2GB average
- **Dependency Install**: 3-5 minutes

### Target Performance
- **Local Build Time**: <5 minutes (with cache)
- **CI Build Time**: <10 minutes
- **Test Execution**: <5 minutes (parallel)
- **Docker Image Size**: <500MB
- **Dependency Install**: <1 minute

## Integration Points

### External Services
1. **Snowflake** - Data warehouse
2. **HubSpot** - CRM
3. **Gong** - Call analytics
4. **Slack** - Communications
5. **Linear** - Project management
6. **GitHub** - Source control
7. **Vercel** - Frontend hosting
8. **Lambda Labs** - GPU infrastructure

### Internal Services
1. **MCP Servers** - 28+ microservices
2. **AI Agents** - 15+ specialized agents
3. **ETL Pipelines** - Multiple data flows
4. **Monitoring** - Prometheus/Grafana

## Security Considerations

### Current State
- Dependency scanning: Recently implemented
- Secret management: Pulumi ESC
- Vulnerabilities: 45 known (being addressed)

### Requirements
- Maintain security scanning in new structure
- Preserve secret management flow
- Enhance with monorepo-wide scanning

## Next Steps for Planning

1. **Prioritize Services**: Which to migrate first
2. **Define Standards**: Naming, structure, configs
3. **Create Templates**: Service templates for consistency
4. **Plan Phases**: Logical grouping of migrations
5. **Risk Assessment**: Per-service migration risks

---

*This inventory will be used to create the detailed migration plan in Phase 1.* 