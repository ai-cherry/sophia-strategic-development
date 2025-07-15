# Environment Files Remediation Plan

**Total Files:** 71 files across 7 categories  
**Estimated Time:** 2-3 days for complete remediation  
**Risk Level:** 🔴 HIGH - Contains potential production secrets

## 📊 Overview by Category

| Category | Files | Risk | Priority | Action |
|----------|-------|------|----------|--------|
| High Priority .env | 2 | 🔴 Critical | P0 | Immediate migration |
| Templates | 4 | 🟡 Medium | P2 | Update placeholders |
| YAML Configs | 11 | 🔴 High | P1 | Migrate secrets |
| Shell Scripts | 10 | 🟡 Medium | P2 | Review & update |
| Python Configs | 38 | 🔴 High | P1 | Refactor to use ESC |
| TypeScript/JS | 6 | 🔴 High | P1 | Refactor to use ESC |
| **Total** | **71** | - | - | - |

## 🚨 Phase 1: Critical Files (Day 1 Morning)

### High Priority Environment Files (2 files)
These contain real secrets and need immediate attention:

1. **`lambda_inference.env`** (339 bytes)
   - Contains: Lambda Labs API credentials
   - Action: Migrate to Pulumi ESC immediately
   - Command: `pulumi config set lambda_labs.api_key --secret`

2. **`Lambda Labs-env-bulk-import.env`** (1,265 bytes, 7 patterns)
   - Contains: Multiple Lambda Labs deployment secrets
   - Action: Already in Pulumi ESC, delete file
   - Verify: `get_config_value("Lambda Labs_token")`

### Remediation Script:
```bash
#!/bin/bash
# Phase 1: Critical .env file migration

# Backup critical files first
mkdir -p .env_backup_20250113
cp lambda_inference.env Lambda Labs-env-bulk-import.env .env_backup_20250113/

# Migrate lambda_inference.env to Pulumi ESC
echo "Migrating Lambda inference credentials..."
python scripts/migrate_env_to_esc.py lambda_inference.env

# Verify migration
python -c "from backend.core.auto_esc_config import get_config_value; print(get_config_value('lambda_inference_url'))"

# If successful, remove files
rm -f lambda_inference.env Lambda Labs-env-bulk-import.env
```

## 📝 Phase 2: Templates Update (Day 1 Afternoon)

### Template Files (4 files)
These should contain placeholders, not real values:

1. **`.env.template`** (451 bytes, 7 patterns)
2. **`.env.example`** (7,522 bytes, 29 patterns) 
3. **`frontend/.env.local.template`** (563 bytes)
4. **`config/estuary/estuary.env.template`** (874 bytes, 9 patterns)

### Template Remediation Script:
```python
#!/usr/bin/env python3
"""Update all template files to use placeholders"""

import re
import os

TEMPLATE_FILES = [
    '.env.template',
    '.env.example', 
    'frontend/.env.local.template',
    'config/estuary/estuary.env.template'
]

PATTERNS = {
    r'sk-[a-zA-Z0-9]{48}': 'sk-YOUR_OPENAI_API_KEY_HERE',
    r'pul-[a-f0-9]{40}': 'pul-YOUR_PULUMI_TOKEN_HERE',
    r'ghp_[a-zA-Z0-9]{36}': 'ghp_YOUR_GITHUB_TOKEN_HERE',
    r'Bearer [a-zA-Z0-9\-_]+': 'Bearer YOUR_AUTH_TOKEN_HERE',
    r'https://api\.[a-z]+\.com/v[0-9]/[a-zA-Z0-9]+': 'https://api.service.com/v1/YOUR_ENDPOINT',
}

for file in TEMPLATE_FILES:
    if os.path.exists(file):
        with open(file, 'r') as f:
            content = f.read()
        
        # Replace patterns
        for pattern, placeholder in PATTERNS.items():
            content = re.sub(pattern, placeholder, content)
        
        # Write back
        with open(file, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {file}")
```

## 🔧 Phase 3: Configuration Files (Day 2)

### YAML Configurations (11 files)
These need secrets moved to Pulumi ESC:

#### Docker Compose Files:
- `deployment/docker-compose-*.yml` (4 files)
- Replace hardcoded env vars with ESC references
- Use `${PULUMI_ESC_VALUE}` syntax

#### Kubernetes/Infrastructure:
- `k8s/argocd/sophia-ai-app.yaml`
- `pulumi/esc/sophia-ai-production.yaml` 
- `infrastructure/gitops/argocd_deployment.yaml`
- Convert to use Kubernetes secrets from ESC

### Python Configuration Files (38 files)
Major refactoring needed:

#### High Impact Files:
1. **MCP Servers** (5 files in `mcp-servers/`)
   - Update to use `get_config_value()`
   - Remove hardcoded API keys

2. **Core Services** (10 files in `backend/`, `core/`)
   - `backend/services/unified_memory_service.py`
   - `core/enhanced_memory_architecture.py`
   - Refactor to use centralized config

3. **Infrastructure** (15 files)
   - All use `get_config_value()` pattern
   - Remove embedded credentials

### Automated Python Refactoring:
```python
#!/usr/bin/env python3
"""Refactor Python files to use Pulumi ESC"""

import os
import re
from pathlib import Path

PYTHON_FILES = Path('.').glob('**/*.py')

# Pattern to replace
OLD_PATTERNS = [
    (r'os\.getenv\(["\']([^"\']+)["\']\)', r'get_config_value("\1")'),
    (r'os\.environ\[["\']([^"\']+)["\']\]', r'get_config_value("\1")'),
    (r'API_KEY\s*=\s*["\'][^"\']+["\']', 'API_KEY = get_config_value("api_key")'),
]

IMPORT_LINE = "from backend.core.auto_esc_config import get_config_value\n"

for py_file in PYTHON_FILES:
    if 'auto_esc_config.py' in str(py_file):
        continue
        
    content = py_file.read_text()
    modified = False
    
    for pattern, replacement in OLD_PATTERNS:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    if modified:
        # Add import if needed
        if 'get_config_value' in content and IMPORT_LINE not in content:
            lines = content.split('\n')
            # Add after other imports
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    continue
                else:
                    lines.insert(i, IMPORT_LINE)
                    break
            content = '\n'.join(lines)
        
        py_file.write_text(content)
        print(f"✅ Updated {py_file}")
```

## 🛡️ Phase 4: Verification & Cleanup (Day 2 Afternoon)

### Verification Checklist:
```bash
#!/bin/bash
# Comprehensive verification script

echo "🔍 Verifying secret migration..."

# 1. Check no secrets in Git
echo "Checking for exposed secrets..."
git grep -E 'sk-[a-zA-Z0-9]{48}|pul-[a-f0-9]{40}|ghp_[a-zA-Z0-9]{36}' || echo "✅ No secrets found"

# 2. Verify Pulumi ESC access
echo "Testing Pulumi ESC..."
python -c "
from backend.core.auto_esc_config import get_config_value
configs = ['openai_api_key', 'github_token', 'docker_hub_token']
for c in configs:
    try:
        val = get_config_value(c)
        print(f'✅ {c}: Available')
    except:
        print(f'❌ {c}: Missing')
"

# 3. Test application startup
echo "Testing application with migrated secrets..."
python -m pytest tests/test_secret_migration.py

# 4. Security scan
echo "Running security scan..."
python scripts/utils/enhanced_daily_cleanup.py
```

### Final Cleanup:
```bash
# After verification, remove backed up files
rm -rf .env_backup_20250113/

# Update .gitignore
echo "*.env" >> .gitignore
echo "!*.env.template" >> .gitignore
echo "!*.env.example" >> .gitignore

# Commit changes
git add -A
git commit -m "Complete environment file remediation - migrated to Pulumi ESC"
```

## 📋 Migration Tracking Spreadsheet

| File | Category | Secrets | Status | Notes |
|------|----------|---------|--------|-------|
| lambda_inference.env | Critical | 1 | ⏳ Pending | Migrate to ESC |
| Lambda Labs-env-bulk-import.env | Critical | 7 | ⏳ Pending | Delete (already in ESC) |
| .env.template | Template | 0 | ⏳ Pending | Update placeholders |
| ... | ... | ... | ... | ... |

## 🚀 Quick Start Commands

```bash
# 1. Create migration script
cat > migrate_all_secrets.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting environment file remediation..."

# Phase 1: Critical files
./scripts/migrate_critical_envs.sh

# Phase 2: Templates
python scripts/update_templates.py

# Phase 3: Config files
python scripts/refactor_configs.py

# Phase 4: Verify
./scripts/verify_migration.sh

echo "✅ Migration complete!"
EOF

chmod +x migrate_all_secrets.sh
./migrate_all_secrets.sh
```

## ⚠️ Important Notes

1. **Never commit real secrets** - Even temporarily
2. **Test after each phase** - Ensure nothing breaks
3. **Keep backups** until fully verified
4. **Update documentation** to reflect new patterns
5. **Train team** on Pulumi ESC usage

## 📊 Success Metrics

- [ ] 0 hardcoded secrets in codebase
- [ ] 100% secrets in Pulumi ESC
- [ ] All templates use placeholders
- [ ] Documentation updated
- [ ] CI/CD still functional
- [ ] No production disruptions

## 🆘 Rollback Plan

If issues arise:
```bash
# Restore from backup
cp .env_backup_20250113/* .
git checkout cleanup-backup-20250113
```

---

**Next Steps**: Start with Phase 1 (Critical Files) immediately to eliminate the highest risk items. 