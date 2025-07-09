sophia-platform-prod: 192.222.58.232 (gpu_1x_a10)
sophia-mcp-prod: 165.1.69.44 (gpu_1x_a10)
sophia-ai-prod: 192.222.58.232 (gpu_1x_a100_sxm4)# Codacy MCP Servers Consolidation, Deployment & Testing Plan

**Date:** July 4, 2025
**Author:** Sophia AI / Cline

## 1. Objective
Merge the four existing Codacy MCP servers into a single, unified, production-grade FastAPI server (`codacy_server.py`), extract and preserve best features, then deploy and validate end-to-end.

## 2. Background
Current servers:
1. `codacy_mcp_server.py` (Original MCP protocol; unused)
2. `simple_codacy_server.py` (Basic FastAPI; minimal features)
3. `production_codacy_server.py` (Enterprise-grade; gold standard)
4. `enhanced_codacy_server.py` (Redundant extended features)

**Decision:** Retain `production_codacy_server.py` as base and rename to `codacy_server.py`.

## 3. Feature Extraction & Mapping
| Feature                                     | Source Server           | Action                          |
|---------------------------------------------|-------------------------|---------------------------------|
| Bandit integration                          | Original MCP            | Extract into `analyzers/security_analyzer.py` |
| AST & Radon complexity analysis             | Original MCP            | Extract into `analyzers/complexity_analyzer.py` |
| Lightweight pattern matching                | Simple FastAPI         | Extract shared utils as needed  |
| Background tasks / advanced analyzers       | Enhanced FastAPI        | Extract into `analyzers/performance_analyzer.py` and `utils/analysis_utils.py` |
| FastAPI best practices (lifespan, DI)       | Production FastAPI      | Keep core structure             |
| Comprehensive metrics & health endpoints    | Production FastAPI      | Keep and extend                 |

## 4. Repository Restructure
```text
mcp-servers/codacy/
├── codacy_server.py            # Renamed production server
├── analyzers/
│   ├── security_analyzer.py
│   ├── complexity_analyzer.py
│   └── performance_analyzer.py
├── models/
│   └── analysis_models.py      # Pydantic schemas
├── utils/
│   └── analysis_utils.py       # Shared helper functions
└── Dockerfile                  # Updated build for unified server
```
Remove:
- `simple_codacy_server.py`
- `enhanced_codacy_server.py`
- `codacy_mcp_server.py`

## 5. Implementation Steps

### 5.1 Branch & Environment
1. Create feature branch: `feature/consolidate-codacy-server`
2. Ensure local environment:
   ```bash
   cd mcp-servers/codacy
   git checkout -b feature/consolidate-codacy-server
   ```

### 5.2 Code Consolidation
1. Copy `production_codacy_server.py` → `codacy_server.py`
2. Delete three redundant server files.
3. Create directories `analyzers/`, `models/`, `utils/`.
4. Scan `codacy_mcp_server.py`, `enhanced_codacy_server.py`, `simple_codacy_server.py` to extract:
   - Security checks → `security_analyzer.py`
   - Complexity analysis → `complexity_analyzer.py`
   - Performance/background tasks → `performance_analyzer.py`
   - Shared helpers → `analysis_utils.py`
5. Define Pydantic models in `models/analysis_models.py` for request/response schemas.
6. Update `codacy_server.py` imports and route handlers to use new modules.
7. Adjust FastAPI lifespan and DI to initialize analyzers:
   ```python
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       app.state.security = SecurityAnalyzer()
       app.state.complexity = ComplexityAnalyzer()
       app.state.performance = PerformanceAnalyzer()
       yield
   ```
8. Add endpoints for each analyzer under `/api/v1/analysis/security`, `/complexity`, `/performance`.

### 5.3 Configuration & CI
1. Update `Dockerfile` to copy new directories and install required dependencies (bandit, radon, astor).
2. Update `docker-compose.mcp.yml` to point to `codacy_server:3008`.
3. Add a GitHub Actions workflow `.github/workflows/codacy-consolidation.yml`:
   - Build Docker image
   - Run lint (flake8, pylint)
   - Run unit tests
   - Deploy to staging environment

## 6. Deployment Plan

### 6.1 Staging Deployment
1. Push feature branch and open PR.
2. CI builds and pushes Docker image tagged `codacy:staging`.
3. Deploy to staging via:
   ```bash
   docker stack deploy -c docker-compose.mcp.yml sophia-mcp-staging
   ```
4. Smoke test health endpoint:
   ```bash
   curl http://staging.example.com:3008/health
   ```

### 6.2 Production Deployment
1. After QA approval, merge to `main`.
2. CI builds and pushes Docker image tagged `codacy:latest`.
3. Deploy to production:
   ```bash
   docker stack deploy -c docker-compose.mcp.yml sophia-mcp
   ```
4. Monitor logs and metrics:
   ```bash
   docker service logs codacy_server --follow
   ```

## 7. Testing Strategy

### 7.1 Unit & Integration Tests
- Write pytest unit tests for analyzers (`tests/analyzers/`).
- Mock FastAPI test client to exercise each endpoint.
- Validate schema serialization and error handling.

### 7.2 Functional & Performance Tests
- Use `locust` or `k6` to simulate load (1000 RPS) on `/health` and analysis endpoints.
- Validate response times (<50ms for simple analysis, <200ms for radon scans).

### 7.3 End-to-End Tests
- Simulate CLI:
  ```bash
  curl -X POST http://localhost:3008/api/v1/analysis/security -d '{"code": "..." }'
  ```
- Verify correct analyzer output and HTTP status codes.

## 8. Rollback Plan
1. Keep previous Docker tag `codacy:previous`.
2. If issues detected, roll back:
   ```bash
   docker service update --image codacy:previous codacy_server
   ```
3. Revert PR and re-run CI for hotfix.

## 9. Timeline & Milestones
- **Day 1:** Branch, consolidation coding, basic smoke tests.
- **Day 2:** Feature extraction, unit tests, CI pipeline.
- **Day 3:** Staging deployment, integration testing.
- **Day 4:** Production deployment, load testing, finalize documentation.

---

**End of Plan**
