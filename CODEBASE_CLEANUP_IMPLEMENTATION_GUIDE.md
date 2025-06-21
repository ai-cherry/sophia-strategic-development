# Sophia AI Codebase Cleanup Implementation Guide

## Overview
This guide provides a complete implementation plan for cleaning up the Sophia AI codebase based on the comprehensive review findings. The cleanup addresses technical debt, removes duplicates, and establishes consistent patterns throughout the codebase.

## Quick Start

### 1. Review the Plan
Read `OPENAI_CODEX_INTEGRATION_PROMPT.md` for detailed cleanup instructions.

### 2. Create Feature Branch
```bash
git checkout -b feature/codebase-cleanup
```

### 3. Run Cleanup Script (Dry Run First)
```bash
# First, do a dry run to see what will change
python scripts/execute_codebase_cleanup.py --dry-run

# Review the output, then run for real
python scripts/execute_codebase_cleanup.py
```

### 4. Validate Changes
```bash
python scripts/execute_codebase_cleanup.py --validate-only
```

## Implementation Phases

### Phase 1: Critical Cleanup (Immediate - Day 1)
**Goal**: Remove vendored dependencies and fix critical issues

1. **Remove Vendored Dependencies**
   ```bash
   # This will save ~226MB of repository size
   git rm -r --cached frontend/node_modules
   git rm -r --cached sophia_admin_api/venv
   git rm -r --cached **/.npm
   ```

2. **Update .gitignore**
   - Add all necessary exclusions
   - Prevent future vendoring

3. **Fix Malformed Directory Names**
   - Rename `backend/agents/core/agent_framework.py and infrastructure`
   - Remove spaces from directory names

4. **Consolidate Main Entry Points**
   - Keep only `backend/main.py`
   - Add feature flags for dashboard/simplified modes

### Phase 2: Architecture Standardization (Days 2-3)
**Goal**: Establish consistent patterns

1. **Standardize Secret Management**
   - Keep only `backend/core/auto_esc_config.py`
   - Remove legacy implementations
   - Update all imports

2. **Consolidate Integrations**
   - Merge duplicate Gong integrations
   - Merge duplicate vector store integrations
   - Preserve unique functionality

3. **Unify API Routes**
   - Move all to `backend/app/routes/`
   - Remove `backend/app/routers/` and `backend/api/`
   - Update all route imports

4. **Standardize MCP Servers**
   - Ensure all inherit from `BaseMCPServer`
   - Fix async/sync inconsistencies

### Phase 3: Documentation & Testing (Days 4-5)
**Goal**: Clean documentation and test structure

1. **Reorganize Documentation**
   ```
   docs/
   ├── README.md
   ├── api/
   ├── architecture/
   ├── deployment/
   └── development/
   ```

2. **Clean Scripts Directory**
   - Move test scripts to `tests/`
   - Archive fix scripts after applying
   - Keep only active utilities

3. **Set Up Test Structure**
   ```
   tests/
   ├── unit/
   ├── integration/
   ├── e2e/
   └── scripts/
   ```

## Detailed Task Checklist

### Vendored Dependencies
- [ ] Remove `frontend/node_modules` from Git
- [ ] Remove `sophia_admin_api/venv` from Git
- [ ] Remove all `.npm` directories
- [ ] Update `.gitignore` with comprehensive exclusions
- [ ] Verify no vendored deps in Git history

### Main Entry Points
- [ ] Analyze unique features in each main*.py
- [ ] Merge features into single `backend/main.py`
- [ ] Add environment-based feature flags
- [ ] Remove duplicate main files
- [ ] Update all references

### Duplicate Integrations
- [ ] Compare Gong integration implementations
- [ ] Merge unique Gong features
- [ ] Remove duplicate Gong files
- [ ] Compare vector store implementations
- [ ] Merge vector store features
- [ ] Remove duplicate vector files

### Secret Management
- [ ] Identify all secret management patterns
- [ ] Ensure auto_esc_config.py handles all cases
- [ ] Remove `backend/core/pulumi_esc.py`
- [ ] Remove `backend/config/secure_config.py`
- [ ] Update all secret references

### Directory Structure
- [ ] Fix malformed directory names
- [ ] Remove spaces from paths
- [ ] Update all import statements
- [ ] Verify no broken imports

### API Routes
- [ ] List all routes in routers/ and api/
- [ ] Move routes to app/routes/
- [ ] Update route imports in main.py
- [ ] Remove empty directories
- [ ] Test all API endpoints

### MCP Servers
- [ ] Audit all MCP server implementations
- [ ] Ensure base class inheritance
- [ ] Standardize async patterns
- [ ] Update MCP configuration

### Documentation
- [ ] Create new docs structure
- [ ] Move guides to appropriate subdirs
- [ ] Consolidate duplicate docs
- [ ] Update main README
- [ ] Create migration guide

### Scripts Cleanup
- [ ] Move test_*.py to tests/
- [ ] Archive applied fix scripts
- [ ] Organize remaining scripts
- [ ] Update script references

### Dependency Management
- [ ] Choose Poetry over pip
- [ ] Update pyproject.toml
- [ ] Remove requirements.txt
- [ ] Generate poetry.lock
- [ ] Update CI/CD configs

## Validation Steps

### Automated Validation
Run the validation script:
```bash
python scripts/validate_cleanup.py
```

This checks:
- No vendored dependencies exist
- Only one main.py file
- No duplicate integrations
- API routes consolidated
- Proper directory structure

### Manual Validation
1. **Test Application Startup**
   ```bash
   cd backend
   python main.py
   ```

2. **Run Test Suite**
   ```bash
   pytest tests/
   ```

3. **Check Import Resolution**
   ```bash
   python scripts/check_imports.py
   ```

4. **Verify API Endpoints**
   ```bash
   curl http://localhost:8000/health
   ```

## Git Workflow

### Commit Strategy
Make atomic commits for each major change:

```bash
# Remove vendored dependencies
git add .gitignore
git rm -r --cached frontend/node_modules
git commit -m "chore: remove vendored node_modules and update gitignore"

# Consolidate main files
git add backend/main.py
git rm backend/main_simple.py backend/main_dashboard.py
git commit -m "refactor: consolidate main entry points with feature flags"

# Fix secret management
git rm backend/core/pulumi_esc.py
git commit -m "refactor: remove legacy secret management"
```

### Pull Request Template
```markdown
## Summary
Major codebase cleanup addressing technical debt from rapid development.

## Changes Made
- ✅ Removed vendored dependencies (saves ~226MB)
- ✅ Consolidated 4 main.py files into 1
- ✅ Unified secret management
- ✅ Fixed duplicate integrations
- ✅ Standardized API routes
- ✅ Cleaned documentation structure

## Testing
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] No import errors
- [ ] API endpoints verified

## Breaking Changes
- Import paths changed for consolidated modules
- Environment variables for feature flags
- API route paths updated

## Migration Required
- Update imports in external scripts
- Set feature flag environment variables
- Update API client route paths
```

## Rollback Plan

If issues arise:

1. **Immediate Rollback**
   ```bash
   git checkout main
   git branch -D feature/codebase-cleanup
   ```

2. **Partial Rollback**
   ```bash
   # Revert specific commits
   git revert <commit-hash>
   ```

3. **Recovery Steps**
   - Restore vendored deps from backup
   - Revert to multiple main files
   - Restore legacy secret management

## Success Metrics

### Quantitative
- Repository size reduced by 200+ MB
- Build time improved by 30%
- Import resolution time reduced
- Zero duplicate code files

### Qualitative
- Clear, consistent architecture
- Single source of truth for configs
- Standardized patterns throughout
- Improved developer experience

## Post-Cleanup Actions

### Immediate
1. Update CI/CD pipelines
2. Notify team of changes
3. Update deployment scripts
4. Monitor for issues

### Short-term
1. Add pre-commit hooks to prevent vendoring
2. Document new architecture
3. Create onboarding guide
4. Set up code quality gates

### Long-term
1. Regular architecture reviews
2. Automated dependency updates
3. Performance monitoring
4. Technical debt tracking

## Troubleshooting

### Common Issues

**Import Errors After Cleanup**
```python
# Old import
from backend.app.routers import user_router

# New import
from backend.app.routes import user_router
```

**Missing Environment Variables**
```bash
export ENABLE_DASHBOARD=true
export ENABLE_MCP=true
export SIMPLIFIED_MODE=false
```

**Secret Loading Failures**
Ensure Pulumi ESC is configured:
```bash
export PULUMI_ORG=scoobyjava-org
pulumi env open sophia-ai-production
```

## Resources

- [OPENAI_CODEX_INTEGRATION_PROMPT.md](./OPENAI_CODEX_INTEGRATION_PROMPT.md) - Detailed cleanup instructions
- [CODEBASE_REVIEW_SUMMARY.md](./CODEBASE_REVIEW_SUMMARY.md) - Original findings
- [scripts/execute_codebase_cleanup.py](./scripts/execute_codebase_cleanup.py) - Automation script
- [PERMANENT_GITHUB_ORG_SECRETS_SOLUTION.md](./PERMANENT_GITHUB_ORG_SECRETS_SOLUTION.md) - Secret management

## Conclusion

This cleanup transforms Sophia AI from a rapidly-developed prototype into a production-ready platform. By following this guide, you'll establish a clean, maintainable codebase that supports the Pay Ready vision of AI-powered business intelligence.

Remember: Take backups, test thoroughly, and communicate changes clearly to the team.
