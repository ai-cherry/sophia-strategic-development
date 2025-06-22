# Comprehensive Sophia AI Cleanup Implementation Guide

## Overview
This guide provides a complete implementation plan to clean up the Sophia AI repository based on the codebase review findings.

## Issues Addressed

### 1. ✅ Virtual Environment Cleanup (COMPLETED)
- Removed `sophia_admin_api/venv`, `sophia_venv`, and `venv` from Git
- Deleted physical directories
- Updated .gitignore
- Fixed malformed filenames

### 2. Dependency Management Consolidation
**Issue**: Both Poetry (pyproject.toml) and pip (requirements.txt) are present with conflicting versions.

**Solution**:
```bash
# Standardize on Poetry
cd /Users/lynnmusil/Desktop/sophia/sophia-main

# Update pyproject.toml with all dependencies
poetry init --no-interaction
poetry add $(cat requirements.txt | grep -v "^#" | grep -v "^$" | cut -d'=' -f1)

# Generate lock file
poetry lock

# Remove old requirements.txt
rm requirements.txt requirements-dev.txt

# Export requirements for Docker/CI if needed
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### 3. Remove Duplicate/Dead Code
**Issue**: Multiple fix scripts and test files cluttering the repository.

**Files to remove**:
```bash
# Remove all the fix_* scripts (keeping only the essential ones)
rm scripts/fix_precommit_*.py
rm scripts/fix_docstring*.py
rm scripts/fix_syntax*.py
rm scripts/fix_streaming*.py
rm scripts/fix_sql*.py
rm scripts/fix_comprehensive*.py
rm scripts/fix_final*.py
rm scripts/fix_all*.py
rm scripts/fix_remaining*.py
rm scripts/fix_critical*.py
rm scripts/final_cleanup.py

# Remove test docstring files
rm scripts/test_docstring*.py

# Remove duplicate architecture files
rm architecture_*.md
rm gong_api_alternative.py
rm deploy_production_mcp.py

# Remove old cleanup guides
rm CODEBASE_CLEANUP_*.md
rm OPENAI_CODEX_*.md
```

### 4. Fix Python Syntax Errors
**Issue**: Many Python files have syntax errors (indentation, async/await, etc.)

**Create a unified syntax fixer**:
```python
#!/usr/bin/env python3
"""Fix all Python syntax errors in the codebase."""

import os
import ast
import autopep8
from pathlib import Path

def fix_python_file(filepath):
    """Fix syntax errors in a Python file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Fix with autopep8
        fixed = autopep8.fix_code(content, options={
            'aggressive': 2,
            'max_line_length': 88,
        })

        # Verify it's valid Python
        ast.parse(fixed)

        with open(filepath, 'w') as f:
            f.write(fixed)

        return True
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

# Fix all Python files
for py_file in Path('.').rglob('*.py'):
    if 'venv' not in str(py_file) and 'node_modules' not in str(py_file):
        fix_python_file(py_file)
```

### 5. Organize Scripts Directory
**Create subdirectories**:
```bash
mkdir -p scripts/{deployment,testing,utilities,data,ci,dev,observability}

# Move scripts to appropriate directories
mv scripts/deploy_*.py scripts/deployment/
mv scripts/test_*.py scripts/testing/
mv scripts/sync_*.py scripts/utilities/
mv scripts/build_*.py scripts/deployment/
mv scripts/run_*.py scripts/utilities/
mv scripts/setup_*.py scripts/utilities/
mv scripts/push_*.py scripts/ci/
mv scripts/ingest_*.py scripts/data/
mv scripts/seed_*.py scripts/data/
```

### 6. Clean Up Root Directory
**Move files to appropriate locations**:
```bash
# Create docs subdirectories
mkdir -p docs/{architecture,deployment,guides,api}

# Move architecture docs
mv *ARCHITECTURE*.md docs/architecture/
mv *STRATEGY*.md docs/architecture/
mv *PLAN*.md docs/architecture/

# Move deployment docs
mv *DEPLOYMENT*.md docs/deployment/
mv *GUIDE*.md docs/guides/

# Move test files
mv test_*.py tests/

# Clean up JSON exports
mkdir -p exports
mv retool_*.json exports/
```

### 7. Fix Duplicate Files
**Remove duplicates**:
```bash
# Remove duplicate main.py entries
# Keep only backend/main.py

# Remove duplicate Pulumi.yaml
# Keep only infrastructure/Pulumi.yaml
rm Pulumi.yaml

# Remove duplicate routes
# backend/app/routes/retool_api_routes.py appears twice
```

### 8. Update Documentation
**Create a clean README structure**:
```markdown
# Sophia AI - Pay Ready Intelligence Platform

## Overview
Sophia AI is an enterprise-grade AI orchestrator for Pay Ready, providing intelligent business automation and insights.

## Quick Start
```bash
# Clone repository
git clone https://github.com/ai-cherry/sophia-ai.git
cd sophia-ai

# Install dependencies
poetry install

# Set up environment
export PULUMI_ORG=scoobyjava-org
pulumi login

# Run locally
poetry run python backend/main.py
```

## Architecture
- Multi-agent AI system with specialized agents
- Pulumi ESC for secret management
- MCP servers for tool integration
- Real-time streaming and caching

## Documentation
- [Setup Guide](docs/guides/SETUP_INSTRUCTIONS.md)
- [Architecture Overview](docs/architecture/SOPHIA_AI_ARCHITECTURE_REVIEW.md)
- [API Reference](docs/api/API_DOCUMENTATION.md)
- [Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md)

## Development
See [LOCAL_DEVELOPMENT_GUIDE.md](LOCAL_DEVELOPMENT_GUIDE.md)
```

### 9. Git Cleanup Commands
```bash
# Stage all changes
git add .

# Commit the cleanup
git commit -m "Major cleanup: Remove venv, consolidate dependencies, fix syntax errors, organize structure"

# Push to repository
git push origin main
```

### 10. Post-Cleanup Verification
```bash
# Verify no venv in Git
git ls-files | grep -E "(venv|node_modules)" | wc -l  # Should be 0

# Check Python syntax
python -m py_compile backend/**/*.py

# Verify Poetry setup
poetry check

# Run tests
poetry run pytest
```

## Implementation Order

1. **Phase 1**: Virtual Environment Cleanup ✅
2. **Phase 2**: Fix Python Syntax Errors (Priority - blocking functionality)
3. **Phase 3**: Consolidate Dependencies
4. **Phase 4**: Remove Dead Code
5. **Phase 5**: Organize Directory Structure
6. **Phase 6**: Update Documentation
7. **Phase 7**: Final Git Cleanup

## Expected Outcomes

- **Repository Size**: Reduced by ~226MB (venv + node_modules)
- **Code Quality**: All Python files syntactically correct
- **Organization**: Clear directory structure
- **Dependencies**: Single source of truth (Poetry)
- **Documentation**: Updated and organized

## Next Steps

After cleanup:
1. Set up CI/CD to prevent future issues
2. Add pre-commit hooks for code quality
3. Implement automated testing
4. Create development guidelines

This cleanup will establish a solid foundation for the Sophia AI platform's continued development.
