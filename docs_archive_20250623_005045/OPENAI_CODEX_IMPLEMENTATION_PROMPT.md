# OpenAI Codex Implementation Prompt for Sophia AI Codebase Cleanup

## Executive Summary
This prompt provides a comprehensive implementation guide for cleaning up the Sophia AI codebase based on the detailed review. The repository requires significant cleanup to improve maintainability, reduce size, and clarify structure while respecting the project's permanent secret management scheme.

## Current State Analysis

### Repository Statistics
- **Total Size**: ~250MB+ (inflated by vendored dependencies)
- **Primary Language**: Python 3.11 with FastAPI
- **Frontend**: React/Vite
- **Infrastructure**: Pulumi ESC for secrets, Docker Compose for services
- **Key Issue**: Vendored dependencies and virtual environments in version control

### Critical Issues Identified

1. **Vendored Dependencies** (HIGH PRIORITY)
   - `frontend/node_modules/`: ~202MB committed to Git
   - `sophia_admin_api/venv/`: ~24MB Python virtual environment
   - Large `.npm` cache files in Git history
   - **Impact**: Massive repository size, merge conflicts, poor performance

2. **Dependency Management Confusion**
   - Both `pyproject.toml` (Poetry) and `requirements.txt` (pip) present
   - Version mismatches: openai 1.3.7 vs 1.28.0
   - No clear dependency strategy
   - **Impact**: Inconsistent environments, deployment issues

3. **Dead Code and Scripts**
   - 100+ scripts in `scripts/` directory
   - Many named `fix_*` or `test_*` suggesting temporary fixes
   - Duplicate functionality across scripts
   - **Impact**: Confusion about which scripts are active

4. **Misnamed/Erroneous Files**
   - VSCode tab display issues (not actual files)
   - Potential copy/paste errors in file organization
   - **Impact**: Developer confusion

## Implementation Plan

### Phase 1: Immediate Cleanup (Day 1)

#### 1.1 Remove Vendored Dependencies
```bash
# Create comprehensive .gitignore entries
echo "# Dependencies" >> .gitignore
echo "node_modules/" >> .gitignore
echo "**/node_modules/" >> .gitignore
echo "venv/" >> .gitignore
echo "**/venv/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".npm/" >> .gitignore

# Remove from tracking
git rm -r --cached frontend/node_modules
git rm -r --cached sophia_admin_api/venv
git rm -r --cached "**/__pycache__"
git rm -r --cached "**/*.pyc"

# Commit changes
git commit -m "chore: remove vendored dependencies from version control"
```

#### 1.2 Standardize Dependency Management
```python
# Create unified requirements management script
# scripts/standardize_dependencies.py

import toml
import subprocess
import os

def standardize_dependencies():
    """Consolidate to requirements.txt only"""
    
    # Read pyproject.toml if exists
    if os.path.exists('pyproject.toml'):
        with open('pyproject.toml', 'r') as f:
            pyproject = toml.load(f)
        
        # Extract dependencies
        deps = pyproject.get('tool', {}).get('poetry', {}).get('dependencies', {})
        
        # Write to requirements.txt
        with open('requirements.txt', 'w') as f:
            for dep, version in deps.items():
                if dep != 'python':
                    if isinstance(version, str):
                        f.write(f"{dep}=={version}\n")
                    else:
                        f.write(f"{dep}\n")
        
        # Remove pyproject.toml and poetry.lock
        os.remove('pyproject.toml')
        if os.path.exists('poetry.lock'):
            os.remove('poetry.lock')
    
    # Generate requirements-dev.txt
    dev_deps = [
        'pytest>=7.0.0',
        'pytest-asyncio>=0.21.0',
        'black>=23.0.0',
        'ruff>=0.1.0',
        'mypy>=1.0.0'
    ]
    
    with open('requirements-dev.txt', 'w') as f:
        for dep in dev_deps:
            f.write(f"{dep}\n")

if __name__ == "__main__":
    standardize_dependencies()
```

### Phase 2: Script Consolidation (Day 2)

#### 2.1 Audit and Categorize Scripts
```python
# scripts/audit_scripts.py

import os
import ast
import json
from pathlib import Path
from datetime import datetime

def audit_scripts():
    """Analyze all scripts and categorize them"""
    
    scripts_dir = Path('scripts')
    audit_results = {
        'active': [],
        'deprecated': [],
        'fix_scripts': [],
        'test_scripts': [],
        'deployment': [],
        'utilities': []
    }
    
    for script in scripts_dir.glob('**/*.py'):
        # Skip __pycache__
        if '__pycache__' in str(script):
            continue
            
        # Categorize by name pattern
        name = script.name
        
        if name.startswith('fix_'):
            audit_results['fix_scripts'].append(str(script))
        elif name.startswith('test_'):
            audit_results['test_scripts'].append(str(script))
        elif 'deploy' in name or 'push' in name:
            audit_results['deployment'].append(str(script))
        else:
            # Check if recently modified (within 30 days)
            mtime = datetime.fromtimestamp(script.stat().st_mtime)
            if (datetime.now() - mtime).days < 30:
                audit_results['active'].append(str(script))
            else:
                audit_results['deprecated'].append(str(script))
    
    # Save audit results
    with open('scripts_audit.json', 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    return audit_results

def consolidate_scripts(audit_results):
    """Move deprecated scripts to archive"""
    
    archive_dir = Path('scripts/archive')
    archive_dir.mkdir(exist_ok=True)
    
    for script in audit_results['deprecated'] + audit_results['fix_scripts']:
        src = Path(script)
        dst = archive_dir / src.name
        src.rename(dst)
    
    print(f"Archived {len(audit_results['deprecated']) + len(audit_results['fix_scripts'])} scripts")

if __name__ == "__main__":
    results = audit_scripts()
    consolidate_scripts(results)
```

### Phase 3: Documentation and Structure (Day 3)

#### 3.1 Create Script Registry
```python
# scripts/create_script_registry.py

import os
import ast
from pathlib import Path

def extract_docstring(filepath):
    """Extract module docstring from Python file"""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
            return ast.get_docstring(tree) or "No description available"
    except:
        return "Error parsing file"

def create_registry():
    """Create comprehensive script registry"""
    
    registry = """# Sophia AI Script Registry

## Active Scripts

### Deployment Scripts
"""
    
    scripts_dir = Path('scripts')
    categories = {
        'deployment': [],
        'testing': [],
        'utilities': [],
        'integration': []
    }
    
    for script in scripts_dir.glob('*.py'):
        if script.name.startswith('_'):
            continue
            
        docstring = extract_docstring(script)
        entry = f"- **{script.name}**: {docstring.split('.')[0]}"
        
        if 'deploy' in script.name or 'push' in script.name:
            categories['deployment'].append(entry)
        elif 'test' in script.name:
            categories['testing'].append(entry)
        elif 'sync' in script.name or 'integration' in script.name:
            categories['integration'].append(entry)
        else:
            categories['utilities'].append(entry)
    
    for category, entries in categories.items():
        if entries:
            registry += f"\n### {category.title()} Scripts\n"
            registry += "\n".join(entries) + "\n"
    
    with open('scripts/README.md', 'w') as f:
        f.write(registry)

if __name__ == "__main__":
    create_registry()
```

### Phase 4: Git History Cleanup (Day 4)

#### 4.1 Remove Large Files from History
```bash
#!/bin/bash
# scripts/clean_git_history.sh

# Install git-filter-repo if not present
pip install git-filter-repo

# Create backup
cp -r .git .git.backup

# Remove large files from history
git filter-repo --path frontend/node_modules --invert-paths
git filter-repo --path sophia_admin_api/venv --invert-paths
git filter-repo --path "**/.npm" --invert-paths
git filter-repo --path "**/__pycache__" --invert-paths

# Force push will be required after review
echo "Git history cleaned. Review changes before force pushing."
```

### Phase 5: CI/CD Integration (Day 5)

#### 5.1 Add Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-json
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11
        
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.261
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```

#### 5.2 GitHub Actions Validation
```yaml
# .github/workflows/validate-cleanup.yml
name: Validate Cleanup

on:
  pull_request:
    branches: [main]

jobs:
  check-no-vendored-deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check for vendored dependencies
        run: |
          if [ -d "frontend/node_modules" ]; then
            echo "ERROR: frontend/node_modules should not be committed"
            exit 1
          fi
          
          if find . -name "venv" -type d | grep -q .; then
            echo "ERROR: Virtual environments should not be committed"
            exit 1
          fi
          
      - name: Check repository size
        run: |
          SIZE=$(du -sh .git | cut -f1)
          echo "Repository size: $SIZE"
```

## Implementation Checklist

### Pre-Implementation
- [ ] Create full repository backup
- [ ] Document current deployment process
- [ ] Notify team of upcoming changes
- [ ] Create feature branch: `feature/codebase-cleanup`

### Phase 1: Immediate Cleanup
- [ ] Update .gitignore with comprehensive rules
- [ ] Remove vendored dependencies from Git
- [ ] Standardize to requirements.txt
- [ ] Remove pyproject.toml and poetry.lock
- [ ] Test local development setup

### Phase 2: Script Consolidation  
- [ ] Run script audit
- [ ] Archive deprecated scripts
- [ ] Consolidate duplicate functionality
- [ ] Update script imports/references

### Phase 3: Documentation
- [ ] Create scripts/README.md registry
- [ ] Update main README.md
- [ ] Document new development setup
- [ ] Create CONTRIBUTING.md

### Phase 4: Git Cleanup
- [ ] Backup .git directory
- [ ] Run git-filter-repo
- [ ] Verify repository integrity
- [ ] Calculate size reduction

### Phase 5: CI/CD
- [ ] Setup pre-commit hooks
- [ ] Add GitHub Actions validation
- [ ] Update deployment workflows
- [ ] Test CI/CD pipeline

### Post-Implementation
- [ ] Create PR with detailed description
- [ ] Run full test suite
- [ ] Deploy to staging environment
- [ ] Monitor for issues
- [ ] Force push after team approval

## Expected Outcomes

### Repository Improvements
- **Size Reduction**: From ~250MB to ~50MB (80% reduction)
- **Clone Time**: From 2-3 minutes to <30 seconds
- **Build Time**: Consistent across environments
- **Developer Experience**: Clear structure and documentation

### Metrics to Track
1. Repository size before/after
2. Clone time improvements
3. CI/CD pipeline duration
4. Developer onboarding time
5. Dependency resolution time

## Risk Mitigation

### Potential Risks
1. **Breaking Changes**: Thoroughly test all imports and dependencies
2. **Deployment Issues**: Update all deployment scripts and documentation
3. **Git History**: Backup before using git-filter-repo
4. **Team Disruption**: Coordinate with team, provide clear migration guide

### Rollback Plan
1. Keep backup of .git directory
2. Document all changes in detail
3. Create rollback script if needed
4. Test rollback procedure before implementation

## Additional Recommendations

### Long-term Improvements
1. **Monorepo Tools**: Consider Nx or Turborepo for better monorepo management
2. **Dependency Caching**: Implement proper CI/CD caching for dependencies
3. **Code Quality**: Enforce linting and formatting via pre-commit
4. **Documentation**: Maintain up-to-date architecture diagrams
5. **Automated Testing**: Increase test coverage for critical paths

### Best Practices Going Forward
1. Never commit `node_modules/` or `venv/`
2. Use lockfiles (`package-lock.json`, `requirements.txt` with pinned versions)
3. Regular dependency updates via Dependabot
4. Quarterly script audits
5. Maintain clean Git history

## Conclusion

This cleanup will significantly improve the Sophia AI codebase maintainability and developer experience. The phased approach minimizes risk while ensuring thorough cleanup. Following these steps will result in a leaner, more efficient repository that's easier to work with and deploy.

Remember: The permanent secret management solution via Pulumi ESC must remain untouched throughout this cleanup process.
