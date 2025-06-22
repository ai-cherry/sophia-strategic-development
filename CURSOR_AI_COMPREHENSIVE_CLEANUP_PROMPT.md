# Cursor AI: Comprehensive Sophia AI Error Cleanup & CI/CD Fix

## 🎯 MISSION: Fix All GitHub Actions Failures & Codebase Issues

You are tasked with performing a comprehensive cleanup and fix of the Sophia AI project to resolve all GitHub Actions failures and codebase issues. Based on analysis of 80+ failed workflow runs, here are the critical error patterns that need immediate resolution:

## 🚨 CRITICAL ERROR PATTERNS IDENTIFIED

### 1. **Security Validation Failures**
**Problem**: Hardcoded API keys detected in security scans
**Files Affected**: 
- `.env.example` - Contains `sk-ant-api03-your_anthropic_key_here`
- `.github/workflows/deploy-simplified.yml` - Contains hardcoded key patterns
- `backend/core/secure_environment_validator.py` - Contains regex patterns triggering false positives

**Required Actions**:
- Remove all hardcoded API key examples from `.env.example`
- Update security scan exclusions to ignore example files
- Fix regex patterns in security validator to avoid false positives
- Ensure all workflows use proper secret management

### 2. **Python Syntax Errors**
**Problem**: Critical syntax errors breaking script execution
**Files Affected**:
- `scripts/ingest_codebase.py` - Line 62: Invalid syntax with missing function definition
- Multiple Python files with malformed docstrings and function definitions

**Required Actions**:
- Fix syntax error in `scripts/ingest_codebase.py` line 62
- Scan all Python files for syntax errors using `python -m py_compile`
- Fix malformed docstrings and function definitions
- Add proper error handling and logging

### 3. **Missing Dependencies & Requirements**
**Problem**: Workflows failing due to missing packages
**Missing Packages**:
- `pytest` - Required for testing workflows
- Various Python packages not in `requirements.txt`

**Required Actions**:
- Create/update comprehensive `requirements.txt` with all dependencies
- Add `pytest` and testing dependencies
- Ensure all MCP server dependencies are included
- Add development dependencies section

### 4. **Workflow Configuration Issues**
**Problem**: Multiple workflow failures due to configuration errors
**Issues**:
- Incorrect Pulumi stack references
- Missing environment variables
- Duplicate workflow definitions
- Conflicting secret management approaches

**Required Actions**:
- Consolidate duplicate workflows
- Fix Pulumi stack references to `scoobyjava-org/sophia-prod-on-lambda`
- Standardize secret management to GitHub Org Secrets → Pulumi ESC
- Remove conflicting workflow definitions

### 5. **Import and Module Errors**
**Problem**: Python import failures and module structure issues
**Issues**:
- Missing `__init__.py` files
- Circular import dependencies
- Incorrect module paths
- `agent_framework.py` filename conflicts

**Required Actions**:
- Add missing `__init__.py` files throughout the project
- Fix circular import dependencies
- Resolve `agent_framework.py` filename conflicts
- Standardize import paths and module structure

## 🔧 SPECIFIC FIXES REQUIRED

### A. Security & Secrets Management
```bash
# 1. Clean up .env.example
# Remove: ANTHROPIC_API_KEY=sk-ant-api03-your_anthropic_key_here
# Replace with: ANTHROPIC_API_KEY=your_anthropic_key_here

# 2. Update security scan exclusions
# Add proper exclusions for example files and documentation

# 3. Fix security validator regex patterns
# Ensure they don't trigger on legitimate code patterns
```

### B. Python Code Fixes
```python
# 1. Fix scripts/ingest_codebase.py line 62
# Current (broken): """Scans the repository for relevant files to ingest."""logging.info("Scanning repository for relevant files...").
# Fix to proper function definition with docstring

# 2. Add comprehensive error handling
# 3. Fix all syntax errors identified by py_compile
```

### C. Dependencies & Requirements
```txt
# Create comprehensive requirements.txt including:
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
redis==4.6.0
pulumi>=3.0.0,<4.0.0
docker==6.1.3
boto3==1.34.0
openai==1.6.1
pytest>=7.0.0
pytest-asyncio>=0.21.0
# ... (all other dependencies)
```

### D. Workflow Consolidation
```yaml
# 1. Merge duplicate deployment workflows
# 2. Standardize secret access patterns
# 3. Fix Pulumi stack references
# 4. Add proper error handling and retries
```

## 🏗️ ARCHITECTURE ALIGNMENT

Ensure all fixes align with Sophia AI architecture principles:

### 1. **Secret Management Flow**
```
GitHub Organization Secrets → Pulumi ESC → Application Runtime
```
- Remove all hardcoded secrets
- Standardize on Pulumi ESC for configuration management
- Ensure proper secret rotation capabilities

### 2. **MCP Server Integration**
- Fix all MCP server dependencies and configurations
- Ensure proper MCP client initialization
- Standardize MCP server deployment patterns

### 3. **Infrastructure as Code**
- Fix all Pulumi stack references
- Ensure proper IaC structure
- Align with production-first deployment approach

### 4. **Codebase Structure**
- Consolidate duplicate integrations (Gong, Vector Store, Estuary)
- Standardize agent inheritance patterns
- Fix route and database access patterns

## 📋 EXECUTION CHECKLIST

### Phase 1: Critical Fixes
- [ ] Fix `scripts/ingest_codebase.py` syntax error
- [ ] Clean up `.env.example` hardcoded keys
- [ ] Update security scan exclusions
- [ ] Create comprehensive `requirements.txt`

### Phase 2: Workflow Fixes
- [ ] Consolidate duplicate workflows
- [ ] Fix Pulumi stack references
- [ ] Standardize secret management
- [ ] Add missing dependencies to workflows

### Phase 3: Code Quality
- [ ] Fix all Python syntax errors
- [ ] Add missing `__init__.py` files
- [ ] Resolve import conflicts
- [ ] Fix `agent_framework.py` conflicts

### Phase 4: Testing & Validation
- [ ] Add comprehensive test coverage
- [ ] Ensure all workflows pass
- [ ] Validate secret management flow
- [ ] Test MCP server integrations

## 🎯 SUCCESS CRITERIA

1. **All GitHub Actions workflows pass** (currently 95%+ failure rate)
2. **No security scan failures** (remove hardcoded key detections)
3. **All Python files compile without syntax errors**
4. **Comprehensive test coverage** with passing tests
5. **Standardized secret management** via Pulumi ESC
6. **Clean codebase structure** with proper imports and modules

## 🚀 PRIORITY ORDER

1. **CRITICAL**: Fix syntax errors breaking basic functionality
2. **HIGH**: Resolve security validation failures
3. **HIGH**: Create proper requirements.txt and dependencies
4. **MEDIUM**: Consolidate workflows and fix configurations
5. **MEDIUM**: Standardize codebase structure and imports
6. **LOW**: Optimize and refactor for maintainability

## 💡 IMPLEMENTATION NOTES

- Use production-first approach (no sandbox environments)
- Maintain deep Infrastructure as Code structure
- Ensure centralized management via Pulumi ESC
- Follow existing Sophia AI architectural patterns
- Test each fix incrementally to avoid breaking changes
- Document all changes for future maintenance

---

**Execute this comprehensive cleanup to transform the Sophia AI project from a 95% failure rate to a fully operational, production-ready system with robust CI/CD pipelines and clean, maintainable code.**

