# OpenAI Codex Implementation Prompt for Sophia AI Codebase Cleanup

## Context
You are tasked with cleaning up and optimizing the Sophia AI codebase, which is a centralized AI platform for orchestrating agents and business integrations for Pay Ready company. The codebase has accumulated technical debt through rapid development, resulting in duplicate code, conflicting patterns, and architectural inconsistencies.

## Repository Information
- **Repository**: https://github.com/ai-cherry/sophia-ai
- **Primary Language**: Python 3.11 with FastAPI
- **Frontend**: React/Vite with TypeScript
- **Infrastructure**: Pulumi ESC for secrets, Docker, Lambda Labs deployment
- **Secret Management**: GitHub Organization Secrets → Pulumi ESC (PERMANENT solution)

## Critical Issues to Address

### 1. Remove Vendored Dependencies (High Priority)
**Issue**: Large vendored directories committed to Git
- `frontend/node_modules/` (~202 MB)
- `sophia_admin_api/venv/` (~24 MB)
- `.npm` cache files in Git history

**Actions**:
```bash
# Remove from Git tracking
git rm -r --cached frontend/node_modules
git rm -r --cached sophia_admin_api/venv
git rm -r --cached **/.npm

# Add to .gitignore
echo "node_modules/" >> .gitignore
echo "venv/" >> .gitignore
echo ".npm/" >> .gitignore
echo "**/venv/" >> .gitignore
echo "**/node_modules/" >> .gitignore
```

### 2. Consolidate Main Entry Points
**Issue**: Multiple main.py files with overlapping functionality
- `backend/main.py` - Keep as primary
- `backend/main_simple.py` - Remove
- `backend/main_dashboard.py` - Remove
- `backend/main_simplified.py` - Remove

**Actions**:
1. Merge functionality into `backend/main.py` with environment-based configuration
2. Use environment variables to control features:
   ```python
   # backend/main.py
   import os
   from backend.core.auto_esc_config import config
   
   # Feature flags from environment
   ENABLE_DASHBOARD = os.getenv("ENABLE_DASHBOARD", "true").lower() == "true"
   ENABLE_MCP = os.getenv("ENABLE_MCP", "true").lower() == "true"
   ```

### 3. Fix Duplicate Integrations
**Consolidate these duplicates**:

#### Gong Integration
- Keep: `backend/integrations/gong_integration.py`
- Remove: `backend/integrations/gong/enhanced_gong_integration.py`
- Remove: `backend/analytics/gong_analytics.py`

#### Vector Store Integration  
- Keep: `backend/vector/vector_integration.py`
- Remove: `backend/vector/vector_integration_updated.py`

### 4. Standardize Secret Management
**Keep ONLY**:
- `backend/core/auto_esc_config.py` - Primary config loader
- `infrastructure/esc/` - ESC secret definitions

**Remove**:
- `backend/core/pulumi_esc.py` - Legacy
- `backend/config/secure_config.py` - Legacy
- Any direct environment variable usage

### 5. Fix Directory Structure Issues
**Rename/Fix**:
- `backend/agents/core/agent_framework.py and infrastructure` → Fix this malformed directory name
- Remove any directories with spaces or special characters in names

### 6. Unify Dependency Management
**Decision**: Use Poetry (pyproject.toml)
- Remove `requirements.txt`
- Update `pyproject.toml` with correct versions
- Generate lock file: `poetry lock`

### 7. Consolidate API Routes
**Move all routes to**: `backend/app/routes/`
- Remove `backend/app/routers/` directory
- Remove `backend/api/` directory
- Update all imports

### 8. Standardize MCP Servers
**Pattern to enforce**:
```python
# All MCP servers must inherit from base
from backend.mcp.base_mcp_server import BaseMCPServer

class YourMCPServer(BaseMCPServer):
    async def initialize(self):
        # Implementation
        pass
```

### 9. Clean Up Scripts Directory
**Evaluate and categorize**:
- `scripts/dev/` - Development utilities (keep)
- `scripts/ci/` - CI/CD scripts (keep)
- `scripts/fix_*.py` - Remove after fixes applied
- `scripts/test_*.py` - Move to `tests/`

### 10. Consolidate Documentation
**Structure**:
```
docs/
├── README.md (main documentation)
├── api/
│   └── API_REFERENCE.md
├── architecture/
│   ├── SYSTEM_DESIGN.md
│   └── AGENT_ARCHITECTURE.md
├── deployment/
│   ├── DEPLOYMENT_GUIDE.md
│   └── INFRASTRUCTURE.md
└── development/
    ├── SETUP_GUIDE.md
    └── CONTRIBUTING.md
```

## Implementation Steps

### Phase 1: Critical Cleanup (Immediate)
1. Remove vendored dependencies
2. Fix `.gitignore`
3. Consolidate main entry points
4. Fix malformed directory names

### Phase 2: Architecture Standardization (Short-term)
1. Unify secret management
2. Consolidate duplicate integrations
3. Standardize MCP server implementations
4. Fix API route organization

### Phase 3: Documentation & Testing (Medium-term)
1. Reorganize documentation
2. Set up comprehensive test structure
3. Clean up scripts directory
4. Update README with accurate information

## Git Workflow

### Branch Strategy
```bash
# Create feature branch
git checkout -b feature/codebase-cleanup

# Make changes in logical commits
git add -p  # Stage changes selectively
git commit -m "chore: remove vendored dependencies"
git commit -m "refactor: consolidate main entry points"
git commit -m "refactor: unify secret management"
# ... etc
```

### Pull Request Structure
**Title**: "Major Codebase Cleanup: Remove Duplicates and Standardize Architecture"

**Description**:
```markdown
## Summary
This PR addresses technical debt accumulated during rapid development by:
- Removing vendored dependencies (reduces repo size by ~226MB)
- Consolidating duplicate code and conflicting patterns
- Standardizing architecture according to best practices
- Implementing the permanent GitHub Org → Pulumi ESC secret solution

## Changes
### Removed
- [ ] Vendored dependencies (node_modules, venv)
- [ ] Duplicate main.py files
- [ ] Legacy secret management code
- [ ] Duplicate integration files

### Consolidated
- [ ] Single main.py with environment-based configuration
- [ ] Unified secret management through auto_esc_config
- [ ] Standardized MCP server implementations
- [ ] API routes under backend/app/routes/

### Added
- [ ] Comprehensive .gitignore
- [ ] Updated documentation structure
- [ ] Proper test organization

## Testing
- [ ] All existing tests pass
- [ ] Manual testing of consolidated features
- [ ] Deployment verification

## Breaking Changes
- Import paths updated for consolidated modules
- Environment variables standardized
- Some deprecated APIs removed

## Migration Guide
See `docs/MIGRATION_GUIDE.md` for details on updating existing code.
```

## Code Quality Checks

### Pre-commit Hooks
Ensure these pass:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88']
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ['--profile', 'black']
```

### Validation Script
Create `scripts/validate_cleanup.py`:
```python
#!/usr/bin/env python3
"""Validate codebase cleanup was successful."""

import os
import sys
from pathlib import Path

def check_no_vendored_deps():
    """Ensure no vendored dependencies exist."""
    vendored = [
        "frontend/node_modules",
        "sophia_admin_api/venv",
    ]
    for path in vendored:
        if Path(path).exists():
            print(f"ERROR: Vendored dependency still exists: {path}")
            return False
    return True

def check_single_main():
    """Ensure only one main.py exists."""
    main_files = list(Path("backend").glob("main*.py"))
    if len(main_files) != 1:
        print(f"ERROR: Multiple main files found: {main_files}")
        return False
    return True

def check_no_duplicate_integrations():
    """Check for duplicate integration files."""
    # Add checks for known duplicates
    pass

if __name__ == "__main__":
    checks = [
        check_no_vendored_deps,
        check_single_main,
        check_no_duplicate_integrations,
    ]
    
    all_passed = all(check() for check in checks)
    sys.exit(0 if all_passed else 1)
```

## Success Criteria
1. Repository size reduced by at least 200MB
2. No duplicate functionality
3. All tests passing
4. Clear, consistent architecture
5. Single source of truth for configuration
6. Standardized patterns throughout codebase

## Notes for Implementation
- Preserve all business logic during consolidation
- Maintain backward compatibility where possible
- Document all breaking changes
- Test thoroughly before merging
- Consider using feature flags for gradual rollout

## Additional Considerations
- After cleanup, set up GitHub Actions to prevent vendored dependencies
- Implement size limits for pull requests
- Add architecture decision records (ADRs) for future changes
- Create developer onboarding documentation

This cleanup will transform Sophia AI into a maintainable, scalable platform ready for continued development and deployment.
