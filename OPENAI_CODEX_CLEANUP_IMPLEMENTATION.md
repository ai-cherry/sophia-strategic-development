# OpenAI Codex Implementation Guide: Sophia AI Codebase Cleanup

## Overview
This guide provides the implementation steps for cleaning up the Sophia AI codebase based on the comprehensive review findings.

## Key Issues Identified

### 1. Vendored Dependencies (226+ MB)
- `frontend/node_modules` (~202 MB)
- `sophia_admin_api/venv` (~24 MB)
- `.npm` cache files in git history

### 2. Structural Issues
- Malformed directory: `backend/agents/core/agent_framework.py and infrastructure`
- Mixed dependency management (Poetry vs pip)
- Numerous obsolete scripts in `scripts/` directory

### 3. Configuration Issues
- Missing comprehensive `.gitignore`
- Vendored dependencies tracked in git

## Implementation Steps

### Step 1: Run the Cleanup Script
```bash
cd /Users/lynnmusil/Desktop/sophia/sophia-main
python scripts/execute_comprehensive_cleanup.py
```

When prompted, type `y` to confirm.

### Step 2: Verify Cleanup Results
The script will:
1. Remove vendored dependencies
2. Fix malformed directories
3. Update `.gitignore`
4. Clean git cache
5. Generate a cleanup report

### Step 3: Reinstall Dependencies
```bash
# Frontend dependencies
cd frontend
npm install
cd ..

# Backend dependencies
poetry install
```

### Step 4: Verify Everything Works
```bash
# Test backend
python backend/main.py

# Test frontend
cd frontend
npm run dev
```

### Step 5: Commit Changes
```bash
git add .
git commit -m "chore: comprehensive codebase cleanup

- Remove vendored dependencies (226+ MB reduction)
- Fix malformed directory names
- Update .gitignore with comprehensive patterns
- Clean git cache for proper ignoring

This cleanup reduces repository size and improves maintainability
without affecting any source code or functionality."
```

### Step 6: Create Pull Request
Use the provided `GITHUB_PR_TEMPLATE.md` to create a comprehensive PR.

## Expected Results

### Repository Size
- **Before**: ~250+ MB
- **After**: ~25-30 MB
- **Reduction**: ~220+ MB (88%+)

### Structure Improvements
- ✅ No vendored dependencies in git
- ✅ Clean directory structure
- ✅ Proper `.gitignore` configuration
- ✅ All source code preserved

## Next Steps (Post-Cleanup)

### 1. Clean Git History (Optional)
```bash
# Use BFG Repo-Cleaner to remove large files from history
java -jar bfg.jar --delete-folders node_modules
java -jar bfg.jar --delete-folders venv
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

### 2. Standardize Dependencies
- Choose between Poetry or pip (recommend Poetry)
- Update all dependency files
- Remove duplicate dependency specifications

### 3. Clean Obsolete Scripts
Review and remove scripts starting with:
- `fix_`
- `test_docstring`
- `push_`
- `fix_syntax`
- `fix_precommit`

### 4. Add Pre-commit Hooks
```yaml
# .pre-commit-config.yaml addition
- repo: local
  hooks:
    - id: no-vendored-deps
      name: Check for vendored dependencies
      entry: scripts/check_no_vendored_deps.sh
      language: script
      files: ''
```

## Safety Considerations

### What's Preserved
- ✅ All source code in `backend/`
- ✅ All source code in `frontend/src/`
- ✅ All configuration files
- ✅ All documentation
- ✅ `sophia_admin_api` source code

### What's Removed
- ❌ `node_modules` directories
- ❌ Python virtual environments
- ❌ NPM cache files
- ❌ Malformed directory names

## Rollback Plan
If issues arise:
```bash
# Revert the cleanup commit
git revert HEAD

# Reinstall everything
cd frontend && npm install
cd .. && poetry install
```

## Validation Checklist
- [ ] Cleanup script completed successfully
- [ ] Cleanup report generated
- [ ] Dependencies reinstalled
- [ ] Backend starts without errors
- [ ] Frontend builds without errors
- [ ] All tests pass
- [ ] No source code was deleted

## Summary
This cleanup operation will transform the Sophia AI repository from a bloated 250+ MB repository to a lean 25-30 MB codebase, improving clone times, CI/CD performance, and overall maintainability while preserving all functionality.
