# 📅 Sophia AI - Week 0 Implementation Plan

## Overview
First week implementation plan to transition from successful cleanup to active development. This week focuses on architecture validation, environment setup, and initial scaffolding.

**Week Start**: 2025-07-03
**Week End**: 2025-07-10
**Team Size**: 2-4 developers

---

## Day 1: Architecture Review & Tech Stack Lock-in (Wednesday)

### Morning Session (9 AM - 12 PM)
**Architecture Review Meeting**
- [ ] Review current system components:
  ```
  Backend Services:
  - 31 MCP server directories (validated)
  - FastAPI unified backend (port 8000)
  - 9 configured MCP servers in cursor_enhanced_mcp_config.json

  Frontend:
  - React/TypeScript dashboard
  - Vercel deployment ready
  - UnifiedDashboard.tsx as main component

  Infrastructure:
  - Docker Swarm configuration (docker-compose.cloud.yml)
  - Lambda Labs instance (104.171.202.64)
  - Pulumi ESC with GitHub sync
  ```

- [ ] Document architecture decisions:
  ```bash
  # Create ADR template
  mkdir -p docs/architecture/decisions
  cat > docs/architecture/decisions/001-multi-tier-memory.md << EOF
  # ADR-001: Multi-Tier Memory Architecture

  ## Status
  Proposed

  ## Context
  Need sub-50ms response times for executive queries

  ## Decision
  Implement 3-tier memory system:
  - L1: Redis cache (<50ms)
  - L2: Snowflake Cortex (<100ms)
  - L3: Snowflake persistent (<500ms)

  ## Consequences
  - Improved response times
  - Increased complexity
  - Additional infrastructure cost
  EOF
  ```

### Afternoon Session (1 PM - 5 PM)
**Tech Stack Validation**
- [ ] Lock versions in pyproject.toml:
  ```toml
  [project]
  requires-python = "==3.12.*"

  [tool.poetry.dependencies]
  python = "3.12.*"
  fastapi = "0.115.0"
  uvicorn = "0.32.0"
  pydantic = "2.5.0"
  snowflake-connector-python = "3.6.0"
  redis = "5.0.1"
  mcp = "0.5.0"
  fastmcp = "0.1.0"
  langchain = "0.1.0"
  ```

- [ ] Create Node version file:
  ```bash
  echo "20.11.0" > .nvmrc
  echo "use_nvm() { nvm use; }" >> .envrc
  ```

- [ ] Update Docker base images:
  ```dockerfile
  # Standardize base images
  ARG PYTHON_VERSION=3.12
  ARG NODE_VERSION=20-alpine
  ```

---

## Day 2: Pulumi Stack Configuration (Thursday)

### Morning Session
**Create Environment Stacks**
```bash
# Initialize Pulumi stacks
cd infrastructure/pulumi

# Development stack
pulumi stack init sophia-ai-dev
pulumi config set environment dev
pulumi config set kubernetes:kubeconfig ~/.kube/config-dev

# Staging stack
pulumi stack init sophia-ai-staging
pulumi config set environment staging
pulumi config set kubernetes:kubeconfig ~/.kube/config-staging

# Production stack (already exists)
pulumi stack select sophia-ai-production
pulumi config set lambdaLabs:instance sophia-ai-production
pulumi config set lambdaLabs:ip 104.171.202.64
```

### Afternoon Session
**Create Stack-Specific Configurations**
```typescript
// infrastructure/pulumi/stacks/dev.ts
export const devConfig = {
  replicas: {
    orchestrator: 1,
    mcpServers: 1,
    frontend: 1
  },
  resources: {
    cpu: "500m",
    memory: "1Gi"
  },
  features: {
    monitoring: false,
    tracing: true,
    autoscaling: false
  }
};

// infrastructure/pulumi/stacks/staging.ts
export const stagingConfig = {
  replicas: {
    orchestrator: 2,
    mcpServers: 2,
    frontend: 2
  },
  resources: {
    cpu: "1000m",
    memory: "2Gi"
  },
  features: {
    monitoring: true,
    tracing: true,
    autoscaling: true
  }
};
```

---

## Day 3: Lambda Labs & Dockcloud Setup (Friday)

### Morning Session
**Lambda Labs Kubernetes Provisioning**
```bash
# SSH into Lambda Labs instance
ssh ubuntu@104.171.202.64

# Install k3s (lightweight Kubernetes)
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644

# Configure GPU support
kubectl apply -f https://nvidia.github.io/gpu-operator/v1.11.1/gpu-operator.yaml

# Create namespaces
kubectl create namespace sophia-dev
kubectl create namespace sophia-staging
kubectl create namespace sophia-prod

# Label nodes
kubectl label nodes sophia-ai-production node-role=worker
kubectl label nodes sophia-ai-production gpu=true
kubectl label nodes sophia-ai-production storage=ssd
```

### Afternoon Session
**Dockcloud Project Setup**
```yaml
# .dockcloud.yml
version: 1.0
project: sophia-ai
registry: scoobyjava15

builds:
  orchestrator:
    context: ./services/orchestrator
    dockerfile: Dockerfile
    tags:
      - latest
      - ${GITHUB_SHA}

  mcp-servers:
    context: ./mcp-servers
    dockerfile: docker/Dockerfile.mcp-server
    matrix:
      - SERVICE: ai_memory
      - SERVICE: hubspot
      - SERVICE: gong
      - SERVICE: slack

hooks:
  pre-build:
    - scripts/validate_dockcloud_deployment.py

  post-build:
    - docker push ${REGISTRY}/${IMAGE}:${TAG}

notifications:
  slack:
    webhook: ${SLACK_WEBHOOK}
    events: [build_success, build_failure]
```

---

## Day 4: GitHub Actions Enhancement (Monday)

### Morning Session
**Create Unified CI/CD Pipeline**
```yaml
# .github/workflows/sophia-unified-pipeline.yml
name: Sophia AI Unified Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
  DOCKER_REGISTRY: scoobyjava15

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate Docker configs
        run: python scripts/validate_dockcloud_deployment.py

      - name: Check secrets
        run: |
          pulumi login
          pulumi stack select sophia-ai-${{ github.ref_name }}
          pulumi config get --path sophia

  build:
    needs: validate
    strategy:
      matrix:
        service: [orchestrator, memory, frontend]
    steps:
      - name: Build ${{ matrix.service }}
        run: |
          docker build -t $DOCKER_REGISTRY/sophia-${{ matrix.service }}:${{ github.sha }} \
            -f services/${{ matrix.service }}/Dockerfile \
            services/${{ matrix.service }}

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Lambda Labs
        run: |
          pulumi up --yes --stack sophia-ai-production
```

### Afternoon Session
**Secret Rotation Automation**
```yaml
# .github/workflows/secret-rotation.yml
name: Secret Rotation

on:
  schedule:
    - cron: '0 0 1 * *'  # Monthly
  workflow_dispatch:

jobs:
  rotate:
    runs-on: ubuntu-latest
    steps:
      - name: Rotate API Keys
        run: |
          # Rotate OpenAI key
          NEW_KEY=$(scripts/rotate_openai_key.sh)
          gh secret set OPENAI_API_KEY --body "$NEW_KEY"

          # Sync to Pulumi ESC
          pulumi config set --path sophia.ai.openai_api_key "$NEW_KEY"
```

---

## Day 5: Project Scaffolding (Tuesday)

### Morning Session
**Create Service Templates**
```bash
# Python service template
mkdir -p services/templates/python-service
cd services/templates/python-service

# Create cookiecutter template
cat > cookiecutter.json << EOF
{
  "service_name": "my_service",
  "service_port": "8080",
  "author": "Sophia AI Team",
  "python_version": "3.12"
}
EOF

# Template structure
mkdir -p {{cookiecutter.service_name}}/src/api
mkdir -p {{cookiecutter.service_name}}/tests
mkdir -p {{cookiecutter.service_name}}/k8s

# Dockerfile template
cat > {{cookiecutter.service_name}}/Dockerfile << 'EOF'
FROM python:{{cookiecutter.python_version}}-slim AS base
WORKDIR /app

FROM base AS dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

FROM base AS runtime
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .
EXPOSE {{cookiecutter.service_port}}
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "{{cookiecutter.service_port}}"]
EOF
```

### Afternoon Session
**Initialize Core Services**
```bash
# Create orchestrator service
cookiecutter services/templates/python-service \
  --no-input \
  service_name=orchestrator \
  service_port=8000

# Create memory service
cookiecutter services/templates/python-service \
  --no-input \
  service_name=memory \
  service_port=8001

# Initialize service code
cat > services/orchestrator/src/main.py << 'EOF'
from fastapi import FastAPI
from src.core.config import settings
from src.api.routes import router

app = FastAPI(
    title="Sophia AI Orchestrator",
    version="1.0.0",
    docs_url="/api/docs"
)

app.include_router(router)

@app.on_event("startup")
async def startup():
    # Initialize connections
    pass

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "orchestrator"}
EOF
```

---

## Deliverables Checklist

### Documentation
- [ ] Architecture Decision Records (ADRs)
- [ ] Updated System Handbook
- [ ] API specification (OpenAPI)
- [ ] Deployment runbook

### Code Artifacts
- [ ] Service templates (Python/React)
- [ ] Pulumi stack configurations
- [ ] Enhanced GitHub workflows
- [ ] Docker configurations

### Infrastructure
- [ ] 3 Pulumi stacks (dev/staging/prod)
- [ ] Lambda Labs k3s cluster
- [ ] Dockcloud project
- [ ] Secret rotation automation

### Testing
- [ ] Unit test templates
- [ ] E2E test framework
- [ ] Load test scenarios
- [ ] Security scan baseline

---

## Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Stack provisioning | 3 stacks | 0 | 🔴 |
| Service templates | 2 templates | 0 | 🔴 |
| CI/CD pipeline | Unified | Multiple | 🟡 |
| Documentation | 4 docs | 1 | 🟡 |
| Test coverage | >80% | TBD | 🔴 |

---

## Risk Mitigation

### Technical Risks
1. **Lambda Labs GPU availability**
   - Mitigation: Reserve instances in advance
   - Fallback: Use CPU-only nodes initially

2. **Snowflake Cortex compatibility**
   - Mitigation: Test with sample data first
   - Fallback: Use traditional embeddings

3. **Service mesh complexity**
   - Mitigation: Start with simple LoadBalancer
   - Fallback: Use Kubernetes native features

### Process Risks
1. **Team onboarding**
   - Mitigation: Daily standups
   - Solution: Pair programming sessions

2. **Scope creep**
   - Mitigation: Strict sprint planning
   - Solution: Weekly scope reviews

---

## Daily Standup Template

```markdown
## Date: YYYY-MM-DD

### Yesterday
- What was completed
- Blockers resolved

### Today
- Planned tasks
- Pair programming sessions

### Blockers
- Technical challenges
- Resource needs

### Metrics
- Lines of code: X
- Tests written: Y
- Docs updated: Z
```

---

## Commands Cheat Sheet

```bash
# Pulumi operations
pulumi up --yes --stack sophia-ai-dev
pulumi destroy --yes --stack sophia-ai-dev
pulumi config set --path sophia.feature.enabled true

# Docker operations
docker build -t sophia-orchestrator .
docker push scoobyjava15/sophia-orchestrator:latest
docker stack deploy -c docker-compose.cloud.yml sophia

# Kubernetes operations
kubectl get pods -n sophia-dev
kubectl logs -f deployment/orchestrator -n sophia-dev
kubectl port-forward svc/orchestrator 8000:8000 -n sophia-dev

# Development
pytest tests/ -v --cov=src
black src/ --check
ruff check src/
mypy src/
```

---

**Week 0 Complete**: Ready for Phase 2 Foundation Layer implementation!
