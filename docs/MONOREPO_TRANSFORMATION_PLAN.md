# Sophia AI Monorepo Transformation Plan

## Executive Summary

This document outlines the comprehensive plan to transform the Sophia AI repository into a unified, multi-language workspace with standardized tooling, CI/CD, and documentation. The transformation will be executed over 7 weeks with clear phases for planning, coding, and review.

## Goals & Benefits

- **Unified Workspace**: Single source of truth for all services and libraries
- **Standardized Tooling**: Consistent development experience across Python and JavaScript
- **Optimized CI/CD**: Reusable workflows with intelligent caching
- **Enhanced Security**: Integrated dependency auditing and vulnerability management
- **Improved Developer Experience**: Faster builds, better dependency management

## Technology Stack

- **Monorepo Framework**: Turborepo + PNPM
- **Python Management**: UV (unified dependency management)
- **JavaScript Management**: PNPM workspaces
- **CI/CD**: GitHub Actions with reusable templates
- **Security**: pip-audit + safety integrated scanning

## Timeline Overview

- **Phase 0**: Preparation & Kickoff (Days 0-2)
- **Phase 1**: Detailed Planning & Design (Days 3-7)
- **Phase 2**: Coding & Implementation (Weeks 1-4)
- **Phase 3**: Code Review & QA (Weeks 5-6)
- **Phase 4**: Documentation & Training (Week 7)
- **Phase 5**: Monitoring & Continuous Improvement (Ongoing)

---

## Phase 0: Preparation & Kickoff (Days 0-2)

### Objectives
- Establish cross-functional task force
- Align on goals, roles, and timeline
- Set up project management infrastructure

### Tasks

#### Day 0
- [ ] Form task force with representatives from:
  - Backend Engineering
  - Frontend Engineering
  - DevOps
  - QA
  - Security Team
- [ ] Create GitHub Project Board for tracking
- [ ] Set up communication channels (Slack channel, meeting cadence)

#### Day 1
- [ ] Conduct 1-hour kickoff meeting
  - Review transformation goals
  - Assign phase owners
  - Confirm timeline
  - Address initial concerns
- [ ] Create project epics and milestones
- [ ] Define "Definition of Done" for each milestone

#### Day 2
- [ ] Document current state inventory
- [ ] Identify key stakeholders and reviewers
- [ ] Schedule weekly check-ins
- [ ] Create risk register

### Deliverables
- Task force roster with roles
- GitHub Project Board with epics/milestones
- Communication plan
- Risk register

---

## Phase 1: Detailed Planning & Design (Days 3-7)

### Objectives
- Complete requirements gathering
- Design target architecture
- Create detailed task breakdown
- Get stakeholder approval

### Tasks

#### Requirements Gathering (Days 3-4)
- [ ] Inventory existing tools and workflows
  - Current CI/CD pipelines
  - Dependency management approaches
  - Build and test processes
- [ ] Document pain points and inefficiencies
- [ ] Confirm technology selection: Turborepo + PNPM
- [ ] Identify integration requirements

#### Architecture Design (Days 5-6)
- [ ] Draft monorepo directory structure:
  ```
  sophia-ai/
  ├── apps/
  │   ├── api/            # FastAPI backend
  │   ├── frontend/       # React frontend
  │   ├── n8n-bridge/     # N8N integration
  │   └── mcp-servers/    # MCP server apps
  ├── libs/
  │   ├── ui/             # Shared UI components
  │   ├── utils/          # Shared utilities
  │   ├── types/          # Shared TypeScript types
  │   └── core/           # Core business logic
  ├── config/
  │   ├── eslint/
  │   ├── prettier/
  │   ├── typescript/
  │   └── ruff/
  ├── scripts/
  ├── docs/
  └── [root config files]
  ```
- [ ] Update System Handbook with proposed structure
- [ ] Create migration mapping (old → new locations)
- [ ] Design CI/CD template architecture

#### Task Breakdown (Day 7)
- [ ] Create granular GitHub issues for:
  - Each service migration (2-4 hours per service)
  - Configuration setup tasks
  - CI/CD workflow updates
  - Documentation updates
- [ ] Assign owners and reviewers
- [ ] Estimate effort and dependencies
- [ ] Create critical path analysis

### Deliverables
- Requirements document
- Architecture diagram
- Updated System Handbook section
- Task breakdown with assignments
- Approved transformation plan

---

## Phase 2: Coding & Implementation (Weeks 1-4)

### Week 1: Workspace Bootstrapping

#### Objectives
- Set up monorepo foundation
- Configure build tools
- Validate basic operations

#### Tasks
- [ ] Initialize root workspace:
  ```bash
  # Create root package.json
  npm init -y

  # Install PNPM
  npm install -g pnpm

  # Create pnpm-workspace.yaml
  echo "packages:
    - 'apps/*'
    - 'libs/*'
    - 'config/*'" > pnpm-workspace.yaml

  # Install Turborepo
  pnpm add -D turbo
  ```
- [ ] Create `turbo.json` configuration:
  ```json
  {
    "$schema": "https://turbo.build/schema.json",
    "pipeline": {
      "build": {
        "dependsOn": ["^build"],
        "outputs": ["dist/**", ".next/**"]
      },
      "test": {
        "dependsOn": ["build"],
        "outputs": ["coverage/**"]
      },
      "lint": {},
      "dev": {
        "cache": false
      }
    }
  }
  ```
- [ ] Scaffold directory structure
- [ ] Create initial `.gitignore` updates
- [ ] Validate with simple echo task: `turbo run echo`
- [ ] Commit initial monorepo structure

### Week 2: Python App Migration

#### Objectives
- Migrate all Python services to UV
- Refactor Dockerfiles
- Validate Python builds

#### Tasks
- [ ] Audit all `requirements.txt` files
- [ ] Create backup branch: `archive/pre-uv-requirements`
- [ ] Consolidate Python dependencies:
  ```bash
  # Import runtime dependencies
  uv add -r apps/api/requirements.txt
  uv add -r apps/mcp-servers/requirements.txt

  # Add dev dependencies
  uv add --group dev pytest black ruff mypy httpx
  uv add --group test pytest-cov pytest-asyncio
  ```
- [ ] Update all Python Dockerfiles:
  ```dockerfile
  FROM python:3.12-slim

  # Install UV
  COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

  # Copy dependency files
  COPY pyproject.toml uv.lock ./

  # Install production dependencies only
  RUN uv sync --no-dev --frozen

  # Copy application code
  COPY apps/api ./apps/api

  # Run with UV
  CMD ["uv", "run", "python", "-m", "apps.api.main"]
  ```
- [ ] Test each service build and startup
- [ ] Update Python service documentation

### Week 3: JavaScript Workspace Migration

#### Objectives
- Convert frontend to PNPM workspace
- Extract shared libraries
- Centralize configs

#### Tasks
- [ ] Convert `apps/frontend` to PNPM:
  ```bash
  cd apps/frontend
  rm -rf node_modules package-lock.json
  pnpm install
  ```
- [ ] Extract shared UI components:
  ```bash
  # Create shared UI library
  mkdir -p libs/ui
  cd libs/ui
  pnpm init

  # Move shared components
  mv apps/frontend/src/components/shared/* libs/ui/src/
  ```
- [ ] Update imports to use workspace protocol:
  ```json
  {
    "dependencies": {
      "@sophia-ai/ui": "workspace:*"
    }
  }
  ```
- [ ] Centralize configurations:
  - Move ESLint config to `/config/eslint`
  - Move Prettier config to `/config/prettier`
  - Move TSConfig to `/config/typescript`
- [ ] Update all package.json files to extend root configs
- [ ] Validate builds: `pnpm turbo run build --filter=frontend`

### Week 4: CI/CD Consolidation & Security

#### Objectives
- Extract reusable workflows
- Implement security scanning
- Clean up legacy CI files

#### Tasks
- [ ] Create workflow templates:
  ```yaml
  # .github/workflow-templates/python-test.yml
  name: Python Test Template
  on:
    workflow_call:
      inputs:
        service-path:
          required: true
          type: string

  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: Install UV
          run: curl -LsSf https://astral.sh/uv/install.sh | sh
        - name: Run tests
          run: |
            cd ${{ inputs.service-path }}
            uv run pytest
  ```
- [ ] Update service workflows to use templates:
  ```yaml
  name: API Tests
  on: [push, pull_request]

  jobs:
    test:
      uses: ./.github/workflow-templates/python-test.yml
      with:
        service-path: apps/api
  ```
- [ ] Enhance security scanning (already implemented):
  - Integrate pip-audit in UV CI
  - Add nightly baseline scans
  - Configure vulnerability reporting
- [ ] Remove legacy CI files in cleanup PR
- [ ] Document CI/CD patterns

---

## Phase 3: Code Review & Quality Assurance (Weeks 5-6)

### Objectives
- Ensure code quality standards
- Validate functionality
- Measure performance improvements

### Pull Request Standards
- [ ] Implement PR template with checklist:
  - Descriptive title with issue link
  - Tests pass locally
  - Lint/format checks pass
  - Security scan completed
  - Documentation updated
- [ ] Require reviews from:
  - Code owner
  - Cross-team reviewer (backend/frontend)
  - Security team (for dependency changes)

### Automated Quality Gates
- [ ] CI pipeline must pass:
  - Linting (Ruff/ESLint)
  - Type checking (MyPy/TypeScript)
  - Unit tests (Pytest/Jest)
  - Security scans (pip-audit/safety)
  - Build validation
- [ ] Block merge on:
  - Test failures
  - New critical vulnerabilities
  - Coverage regression >5%

### Manual QA Testing
- [ ] QA team validation:
  - API health endpoints
  - Frontend rendering
  - End-to-end user flows
  - Database migrations
  - MCP server functionality
- [ ] Document any regressions
- [ ] Create fix tickets with priority

### Performance Benchmarking
- [ ] Measure before/after metrics:
  - Local build times
  - CI job duration
  - Docker image sizes
  - Memory usage
  - API response times
- [ ] Validate targets:
  - ≥2× throughput for FastAPI endpoints
  - ≥50% faster CI builds with caching
  - ≥30% smaller Docker images

---

## Phase 4: Documentation & Training (Week 7)

### Objectives
- Update all documentation
- Train development teams
- Create self-service resources

### Documentation Updates
- [ ] Update core docs:
  - README.md with new structure
  - Developer onboarding guide
  - System Handbook monorepo section
- [ ] Create migration guide:
  - Directory mapping (old → new)
  - Command translations
  - Common workflows
- [ ] Document new patterns:
  - Adding dependencies with UV/PNPM
  - Creating new services/libraries
  - Using CI/CD templates

### Quick-Start Scripts
- [ ] `scripts/setup-workspace.sh`:
  ```bash
  #!/bin/bash
  echo "🚀 Setting up Sophia AI monorepo..."

  # Install prerequisites
  curl -LsSf https://astral.sh/uv/install.sh | sh
  npm install -g pnpm

  # Clone and setup
  git clone https://github.com/ai-cherry/sophia-main.git
  cd sophia-main

  # Install dependencies
  uv sync
  pnpm install

  # Validate setup
  pnpm turbo run build
  ```
- [ ] `scripts/new-service.sh` - Scaffold new services
- [ ] `scripts/audit-all.sh` - Run security audits

### Training Program
- [ ] Workshop 1: Workspace Fundamentals (30 min)
  - Monorepo structure
  - UV commands for Python
  - PNPM commands for JavaScript
  - Running builds and tests
- [ ] Workshop 2: CI/CD & Security (30 min)
  - Using workflow templates
  - Security scanning
  - Troubleshooting builds
- [ ] Record workshop videos
- [ ] Create cheat sheets

### Self-Service Resources
- [ ] FAQ document
- [ ] Troubleshooting guide
- [ ] Video tutorials playlist
- [ ] Slack channel for questions

---

## Phase 5: Monitoring & Continuous Improvement (Ongoing)

### Objectives
- Track adoption and performance
- Gather feedback
- Continuously optimize

### Metrics Dashboard
- [ ] Set up Grafana panels:
  - Build duration trends
  - Cache hit rates
  - Vulnerability trends
  - CI success rates
- [ ] Configure alerts:
  - Build time regression >20%
  - New critical vulnerabilities
  - CI failure rate >10%

### Quarterly Reviews
- [ ] Dependency audit:
  ```bash
  # Remove unused dependencies
  uv show --only-deps | grep "unused"
  pnpm prune

  # Update outdated packages
  uv update --dry-run
  pnpm outdated
  ```
- [ ] CI/CD optimization:
  - Review workflow run times
  - Optimize caching strategies
  - Remove obsolete jobs

### Feedback Loop
- [ ] Monthly developer survey:
  - Build time satisfaction
  - Tool usability
  - Pain points
- [ ] Retrospective meetings
- [ ] Update processes based on feedback

### Success Metrics
- [ ] Target metrics:
  - 90% developer satisfaction
  - <5 min average build time
  - >80% cache hit rate
  - <2% CI failure rate
  - 100% security scan coverage

---

## Risk Management

### Identified Risks

1. **Dependency Conflicts**
   - Mitigation: Gradual migration with thorough testing
   - Owner: Backend Lead

2. **CI/CD Disruption**
   - Mitigation: Parallel run old/new pipelines
   - Owner: DevOps Lead

3. **Learning Curve**
   - Mitigation: Comprehensive training program
   - Owner: Tech Lead

4. **Performance Regression**
   - Mitigation: Benchmark before/after
   - Owner: Performance Engineer

### Contingency Plans
- Rollback procedures documented
- Feature flags for gradual rollout
- Backup branches maintained
- Emergency contacts list

---

## Success Criteria

The transformation will be considered successful when:

1. ✅ All services migrated to monorepo structure
2. ✅ UV managing all Python dependencies
3. ✅ PNPM managing all JavaScript dependencies
4. ✅ Turborepo orchestrating builds
5. ✅ CI/CD using reusable templates
6. ✅ Security scanning integrated
7. ✅ Documentation complete
8. ✅ Teams trained
9. ✅ Performance targets met
10. ✅ 90% developer satisfaction

---

## Appendix

### Command Reference

#### UV Commands
```bash
# Add dependency
uv add package-name

# Add dev dependency
uv add --group dev package-name

# Update dependencies
uv update

# Run scripts
uv run python script.py
```

#### PNPM Commands
```bash
# Install all dependencies
pnpm install

# Add dependency to workspace
pnpm add package-name --filter=frontend

# Run turbo pipeline
pnpm turbo run build

# Run specific app
pnpm --filter=frontend dev
```

#### Turbo Commands
```bash
# Run all builds
turbo run build

# Run with specific filter
turbo run test --filter=api

# Run in parallel
turbo run lint test --parallel

# Clear cache
turbo run build --force
```

### Resources
- [UV Documentation](https://github.com/astral-sh/uv)
- [PNPM Documentation](https://pnpm.io)
- [Turborepo Documentation](https://turbo.build)
- [GitHub Actions Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
