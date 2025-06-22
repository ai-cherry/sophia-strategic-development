# Cursor AI: Phase 2 Improvement Prompts - Post-Merge Optimization

## 🎯 MISSION: Complete Remaining Critical Fixes & Optimize Architecture

After successfully merging 10 critical fixes, workflows are still failing due to remaining syntax errors and architectural issues. This phase focuses on completing the cleanup and optimizing the Sophia AI architecture for production readiness.

## 🚨 CRITICAL REMAINING ISSUES (Phase 2)

### 1. **Additional Syntax Errors in Multiple Files**
**Status**: CRITICAL - Blocking all workflows
**Files Affected**:
- `scripts/ingest_codebase.py` - Line 85: `"""try:.` (malformed docstring)
- `scripts/deploy_complete_system.py` - Line 123: Similar malformed docstring pattern
- Multiple other Python files with similar patterns

**Required Actions**:
```python
# Fix pattern: """docstring"""function_call().
# Should be: 
"""docstring"""
function_call()

# Scan ALL Python files for this pattern:
grep -r '""".*""".*\.' --include="*.py" .
```

### 2. **Import and Module Structure Issues**
**Status**: HIGH - Causing test collection failures
**Issues**:
- Circular import dependencies in agent modules
- Missing or incorrect module paths
- Import errors in test files

**Required Actions**:
- Fix circular imports in `backend/agents/` modules
- Ensure all agent imports follow consistent patterns
- Verify all test files can import required modules
- Add proper module initialization

### 3. **Workflow Configuration Optimization**
**Status**: MEDIUM - Reducing efficiency
**Issues**:
- Multiple duplicate workflows running simultaneously
- Inefficient workflow triggers
- Missing workflow dependencies

**Required Actions**:
- Consolidate similar workflows into single, efficient pipelines
- Add proper workflow dependencies and conditions
- Optimize workflow triggers to reduce unnecessary runs

### 4. **Architecture Standardization**
**Status**: MEDIUM - Long-term maintainability
**Issues**:
- Inconsistent agent inheritance patterns
- Multiple entry points for similar functionality
- Duplicate integrations (Gong, Vector Store, Estuary)

**Required Actions**:
- Standardize agent base classes and inheritance
- Consolidate duplicate integrations
- Create single source of truth for each functionality

## 🔧 SPECIFIC CURSOR AI PROMPTS

### **Prompt 1: Complete Syntax Error Cleanup**
```
Scan the entire Sophia AI codebase for malformed docstring patterns where docstrings are concatenated with function calls on the same line. The pattern to find and fix is:

"""docstring"""function_call().

This should be separated into:
"""docstring"""
function_call()

Files known to have this issue:
- scripts/ingest_codebase.py (line 85)
- scripts/deploy_complete_system.py (line 123)

Use this command to find all instances:
grep -r '""".*""".*\.' --include="*.py" .

Fix ALL instances found. Ensure proper Python syntax with docstrings on separate lines from code.
```

### **Prompt 2: Fix Import Dependencies and Module Structure**
```
Fix all import and module structure issues in the Sophia AI project:

1. Resolve circular import dependencies in backend/agents/ modules
2. Fix import errors causing test collection failures
3. Ensure consistent import patterns across all agent modules
4. Verify all modules can be imported without errors

Focus on:
- backend/agents/core/agent_framework.py
- backend/agents/nl_command_agent.py
- All test files in the project

Test the fixes by running:
python -c "import backend.agents.core.agent_framework"
pytest --collect-only
```

### **Prompt 3: Optimize and Consolidate Workflows**
```
Optimize the GitHub Actions workflows for the Sophia AI project:

1. Identify and consolidate duplicate workflows
2. Create efficient workflow dependencies
3. Optimize triggers to reduce unnecessary runs
4. Ensure workflows run in logical sequence

Current workflows to optimize:
- Deploy Sophia AI (Secure Production)
- Deploy with Organization Secrets
- Sophia AI - Automatic Deployment with Org Secrets
- SOPHIA AI System Deployment

Goal: Reduce from 10+ workflows to 3-5 efficient, well-orchestrated workflows.
```

### **Prompt 4: Standardize Agent Architecture**
```
Standardize the agent architecture in the Sophia AI project:

1. Create consistent base agent classes
2. Standardize inheritance patterns
3. Consolidate duplicate integrations:
   - Multiple Gong integrations
   - Duplicate Vector Store implementations
   - Multiple Estuary connections

4. Implement consistent patterns for:
   - Agent initialization
   - Configuration management
   - Error handling
   - Logging

Focus on backend/agents/ directory and ensure all agents follow the same architectural patterns.
```

### **Prompt 5: Enhance Testing Infrastructure**
```
Build comprehensive testing infrastructure for Sophia AI:

1. Fix all test collection errors
2. Create test suites for each major component:
   - Agent functionality
   - MCP server integration
   - Vector operations
   - Secret management

3. Add integration tests for:
   - End-to-end workflows
   - API endpoints
   - Database operations

4. Ensure tests can run in CI/CD pipeline without failures

Target: 80%+ test coverage with all tests passing.
```

## 🏗️ ARCHITECTURE ALIGNMENT REQUIREMENTS

### **Secret Management Flow**
```
GitHub Organization Secrets → Pulumi ESC → Application Runtime
```
- Ensure all secrets follow this flow
- Remove any hardcoded credentials
- Implement proper secret rotation capabilities

### **MCP Integration Standards**
```
Cursor IDE ↔ MCP Gateway ↔ Specialized MCP Servers
```
- Standardize MCP server implementations
- Ensure proper MCP client initialization
- Optimize MCP server deployment patterns

### **Infrastructure as Code Structure**
```
Pulumi ESC (Config) → Pulumi IaC (Infrastructure) → Application Deployment
```
- Fix all Pulumi stack references
- Ensure proper IaC structure
- Align with production-first deployment approach

## 📋 EXECUTION PRIORITY

### **Phase 2A: Critical Fixes (Immediate)**
1. **Fix all remaining syntax errors** (Prompt 1)
2. **Resolve import dependencies** (Prompt 2)
3. **Test basic functionality** (verify fixes work)

### **Phase 2B: Optimization (Short-term)**
1. **Consolidate workflows** (Prompt 3)
2. **Standardize agent architecture** (Prompt 4)
3. **Enhance testing** (Prompt 5)

### **Phase 2C: Production Readiness (Medium-term)**
1. **Performance optimization**
2. **Security hardening**
3. **Documentation completion**
4. **Monitoring and alerting setup**

## 🎯 SUCCESS CRITERIA

### **Immediate Goals**
- ✅ All Python files compile without syntax errors
- ✅ All tests can be collected and run
- ✅ Basic workflows pass (>50% success rate)

### **Short-term Goals**
- ✅ Workflow success rate >80%
- ✅ Consistent agent architecture
- ✅ Consolidated, efficient CI/CD pipeline

### **Medium-term Goals**
- ✅ Production-ready deployment
- ✅ Comprehensive test coverage
- ✅ Optimized performance
- ✅ Complete documentation

## 💡 IMPLEMENTATION NOTES

- **Incremental Approach**: Fix critical issues first, then optimize
- **Test-Driven**: Verify each fix with automated tests
- **Architecture-First**: Ensure all changes align with Sophia AI principles
- **Production-Ready**: Focus on scalability and maintainability
- **Documentation**: Update docs as changes are made

---

**Execute these prompts in sequence to transform Sophia AI from current state to a fully operational, production-ready system with robust CI/CD and clean architecture.**

