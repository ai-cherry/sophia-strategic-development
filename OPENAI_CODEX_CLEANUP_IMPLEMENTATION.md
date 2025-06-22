# OpenAI Codex Implementation Prompt for Sophia AI Cleanup

## Context
You are tasked with cleaning up the Sophia AI repository, a centralized AI platform for orchestrating agents and business integrations. The codebase has several issues that need to be addressed to improve maintainability and reduce repository size.

## Current State Analysis

### Repository Overview
- **Purpose**: AI orchestrator for Pay Ready company with agent pooling, performance metrics, and feature-based architecture
- **Tech Stack**: Python 3.11, FastAPI, React/Vite, Pulumi ESC for secrets
- **Size Issues**: ~226MB repository with vendored dependencies

### Critical Issues to Fix

1. **Vendored Dependencies** (HIGH PRIORITY)
   - `frontend/node_modules/` (~202 MB) - Should not be in version control
   - `sophia_admin_api/venv/` (~24 MB) - Virtual environment committed
   - Large .npm cache files in Git history

2. **Erroneous Directory Names**
   - `backend/agents/core/agent_framework.py and infrastructure/` - Likely copy error
   - Other misnamed directories with special characters

3. **Mixed Dependency Management**
   - Both `pyproject.toml` (Poetry) and `requirements.txt` (pip) present
   - Version conflicts: openai 1.3.7 vs 1.28.0
   - No lockfiles for reproducible builds

4. **Dead Code and Scripts**
   - Numerous `fix_*` scripts in `scripts/` directory
   - Test scripts that may be obsolete
   - Duplicate implementations

5. **Virtual Environment Issues**
   - `sophia_venv/` directory committed
   - Poetry configured to use external venv

## Implementation Tasks

### Phase 1: Remove Vendored Dependencies
```bash
# Add to .gitignore
echo "frontend/node_modules/" >> .gitignore
echo "sophia_admin_api/venv/" >> .gitignore
echo "sophia_venv/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".npm/" >> .gitignore

# Remove from tracking
git rm -r --cached frontend/node_modules/
git rm -r --cached sophia_admin_api/venv/
git rm -r --cached sophia_venv/
```

### Phase 2: Fix Directory Names
```bash
# Rename erroneous directories
mv "backend/agents/core/agent_framework.py and infrastructure" "backend/agents/core/infrastructure"
# Update any imports accordingly
```

### Phase 3: Consolidate Dependencies
Choose either Poetry or pip (recommend Poetry for better dependency resolution):

```python
# If choosing Poetry:
# 1. Update pyproject.toml with all dependencies
# 2. Generate poetry.lock
# 3. Remove requirements.txt
# 4. Update CI/CD to use Poetry

# If choosing pip:
# 1. Consolidate all dependencies in requirements.txt
# 2. Remove pyproject.toml
# 3. Use pip-compile for lockfile
```

### Phase 4: Clean Dead Code
Analyze and remove obsolete scripts:
```python
scripts_to_evaluate = [
    "scripts/fix_*.py",  # Numerous syntax fix scripts
    "scripts/test_*.py",  # Standalone test scripts
    "scripts/*_old.py",   # Any old versions
]
```

### Phase 5: Git History Cleanup (Optional but Recommended)
Use BFG Repo-Cleaner or git filter-branch to remove large files from history:
```bash
# Remove large files from history
bfg --delete-files '*.{pyc,pyo}' --no-blob-protection
bfg --strip-blobs-bigger-than 10M
```

## Safety Considerations

### Never Modify
- `backend/core/auto_esc_config.py` - Critical for secret management
- `.github/workflows/` - CI/CD pipelines
- `infrastructure/esc/` - Pulumi ESC configurations
- `docker-compose.yml` - Service orchestration

### Test Before Removing
- Run full test suite after each phase
- Verify Docker builds still work
- Check that all imports resolve correctly
- Ensure CI/CD pipelines pass

## Pull Request Structure

Create separate PRs for each phase:

1. **PR 1: Remove Vendored Dependencies**
   - Update .gitignore
   - Remove node_modules, venv directories
   - Update documentation

2. **PR 2: Fix Directory Structure**
   - Rename erroneous directories
   - Update import statements
   - Fix any broken references

3. **PR 3: Consolidate Dependencies**
   - Choose dependency manager
   - Create lockfiles
   - Update CI/CD

4. **PR 4: Remove Dead Code**
   - Analyze script usage
   - Remove obsolete files
   - Update documentation

## Validation Steps

After each PR:
1. Run `pytest` for backend tests
2. Run `npm test` for frontend tests
3. Build Docker images: `docker-compose build`
4. Verify secret loading works
5. Check that all MCP servers start correctly

## Expected Outcomes

- Repository size reduced from ~226MB to ~20MB
- Clear dependency management
- No vendored dependencies in version control
- Clean directory structure
- Improved maintainability

## Additional Recommendations

1. **Add Pre-commit Hooks**
   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/pre-commit/pre-commit-hooks
       hooks:
         - id: check-added-large-files
           args: ['--maxkb=1000']
         - id: check-yaml
         - id: end-of-file-fixer
   ```

2. **Create Development Setup Script**
   ```python
   # scripts/setup_dev_environment.py
   """One-command development environment setup."""
   ```

3. **Document Dependency Management**
   Update README with clear instructions on:
   - How to install dependencies
   - How to add new dependencies
   - Virtual environment management

## Implementation Order

1. Start with Phase 1 (vendored dependencies) - Highest impact
2. Phase 2 (directory names) - Quick fix
3. Phase 3 (dependencies) - Improves development workflow
4. Phase 4 (dead code) - Ongoing maintenance
5. Phase 5 (git history) - Optional, coordinate with team

Remember: Each change should be atomic, tested, and reversible. Use feature branches and thorough PR reviews.
