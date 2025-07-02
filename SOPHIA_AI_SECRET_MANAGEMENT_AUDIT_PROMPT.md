# SOPHIA AI SECRET MANAGEMENT COMPREHENSIVE AUDIT & REMEDIATION PROMPT

## CRITICAL CONTEXT
You are tasked with conducting a complete audit of the Sophia AI platform's secret management system. The platform uses a pipeline: GitHub Organization Secrets (ai-cherry) → Pulumi ESC → Backend Application. Multiple issues have been identified that need systematic resolution.

## PHASE 1: INVENTORY & DISCOVERY

### 1.1 GitHub Organization Secrets Audit
```bash
# List all organization secrets
gh secret list --org ai-cherry --json name,visibility,updated_at > github_org_secrets_audit.json

# Critical secrets that MUST exist:
CRITICAL_SECRETS=(
    "PULUMI_ACCESS_TOKEN" "OPENAI_API_KEY" "ANTHROPIC_API_KEY" "GONG_ACCESS_KEY"
    "PINECONE_API_KEY" "HUBSPOT_ACCESS_TOKEN" "SLACK_BOT_TOKEN" "SNOWFLAKE_PASSWORD"
    "LAMBDA_API_KEY" "PORTKEY_API_KEY" "OPENROUTER_API_KEY" "LINEAR_API_KEY"
)

# Verify each critical secret exists
for secret in "${CRITICAL_SECRETS[@]}"; do
    echo "Checking $secret..."
    gh secret list --org ai-cherry | grep -q "$secret" && echo "✅ Found" || echo "❌ Missing"
done
```

### 1.2 Codebase Secret Usage Analysis
Create a comprehensive map of all secret references:

```python
# Script: scripts/audit_secret_usage.py
import os
import re
from pathlib import Path
import json

def audit_secret_usage():
    patterns = {
        'get_config_value': r'get_config_value\(["\']([^"\']+)["\']\)',
        'os_getenv': r'os\.getenv\(["\']([^"\']+)["\']\)',
        'os_environ': r'os\.environ\[["\']([^"\']+)["\']\]',
        'env_var_ref': r'\$\{?([A-Z_]+(?:_KEY|_TOKEN|_SECRET|_PASSWORD))\}?'
    }
    
    results = {
        'by_pattern': {},
        'by_file': {},
        'unique_secrets': set()
    }
    
    # Scan all Python files
    for py_file in Path('.').rglob('*.py'):
        if '.git' in str(py_file) or 'node_modules' in str(py_file):
            continue
            
        with open(py_file, 'r') as f:
            content = f.read()
            
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                results['by_file'][str(py_file)] = matches
                results['unique_secrets'].update(matches)
                
    return results
```

### 1.3 Pulumi ESC Structure Verification
```bash
# Get current ESC structure
pulumi env get scoobyjava-org/default/sophia-ai-production --show-secrets > esc_structure.json

# Verify the structure matches expectations
python -c "
import json
with open('esc_structure.json') as f:
    data = json.load(f)
    
# Check for both flat and nested structures
print('Flat keys:', [k for k in data.keys() if not isinstance(data[k], dict)])
print('Nested structure:', json.dumps(data.get('values', {}), indent=2))
"
```

## PHASE 2: NAMING CONVENTION VALIDATION

### 2.1 Create Mapping Validation Script
```python
# Script: scripts/validate_secret_mappings.py
import json
from pathlib import Path

# Load GitHub → Pulumi mappings from sync script
sync_script_path = Path('scripts/ci/sync_from_gh_to_pulumi.py')
with open(sync_script_path) as f:
    content = f.read()
    # Extract mappings (lines 44-155 in the file)
    
# Load backend expectations from auto_esc_config.py
config_path = Path('backend/core/auto_esc_config.py')
with open(config_path) as f:
    content = f.read()
    # Extract esc_key_mappings (lines 86-130)

# Critical mismatches to check:
KNOWN_ISSUES = {
    "ASANA_API_TOKEN": {
        "github_name": "ASANA_API_TOKEN",
        "sync_maps_to": "asana_access_token",
        "backend_expects": "asana_api_token",  # Mismatch!
    },
    "GH_API_TOKEN": {
        "github_name": "GH_API_TOKEN", 
        "sync_maps_to": "github_token",
        "backend_expects": "github_token",  # OK
    },
    "NOTION_API_KEY": {
        "github_name": "NOTION_API_KEY",
        "sync_maps_to": "notion_api_token", 
        "backend_expects": "notion_api_key",  # Mismatch!
    }
}

# Validate all mappings
def validate_mappings():
    issues = []
    # Implementation to check all mappings
    return issues
```

## PHASE 3: PLACEHOLDER DETECTION

### 3.1 Comprehensive Placeholder Search
```bash
# Search for common placeholder patterns
grep -r -E "(PLACEHOLDER|FAKE|YOUR_|EXAMPLE|TEST_|DEMO_|placeholder|your_.*_here)" \
    --include="*.py" --include="*.yml" --include="*.yaml" --include="*.json" \
    --include="*.env*" --include="*.ts" --include="*.js" \
    --exclude-dir=".git" --exclude-dir="node_modules" \
    . > placeholder_audit.txt

# Search for hardcoded secrets (common patterns)
grep -r -E "sk-[a-zA-Z0-9_-]{20,}|ghp_[a-zA-Z0-9_-]{20,}|pk_[a-zA-Z0-9_-]{20,}" \
    --exclude-dir=".git" --exclude-dir="node_modules" \
    . > potential_hardcoded_secrets.txt

# Check specific files known to have issues
FILES_TO_CHECK=(
    "infrastructure/vercel/index.ts"  # Has PLACEHOLDER values
    "vercel-env-bulk-import.env"      # Has pk_placeholder
    "data/test_ephemeral_credentials.json"  # Has test token
)
```

### 3.2 Environment File Audit
```python
# Script: scripts/audit_env_files.py
import re
from pathlib import Path

def audit_env_files():
    env_patterns = [
        r'.*\.env.*',
        r'.*config.*\.json',
        r'.*secrets.*'
    ]
    
    issues = []
    
    for pattern in env_patterns:
        for file in Path('.').rglob(pattern):
            if '.git' in str(file):
                continue
                
            with open(file) as f:
                content = f.read()
                
            # Check for placeholder values
            if re.search(r'(placeholder|your_|example|test_|demo_)', content, re.I):
                issues.append({
                    'file': str(file),
                    'type': 'placeholder',
                    'content': content
                })
                
    return issues
```

## PHASE 4: GITHUB ACTIONS AUDIT

### 4.1 Workflow Secret References
```python
# Script: scripts/audit_github_workflows.py
import yaml
from pathlib import Path

def audit_workflows():
    workflow_path = Path('.github/workflows')
    secret_references = {}
    
    for workflow_file in workflow_path.glob('*.yml'):
        with open(workflow_file) as f:
            workflow = yaml.safe_load(f)
            
        # Extract all secret references
        secrets = extract_secrets_from_workflow(workflow)
        secret_references[workflow_file.name] = secrets
        
    return secret_references

def extract_secrets_from_workflow(obj, secrets=None):
    if secrets is None:
        secrets = set()
        
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and 'secrets.' in value:
                secret_name = value.split('secrets.')[1].split('}')[0]
                secrets.add(secret_name)
            else:
                extract_secrets_from_workflow(value, secrets)
    elif isinstance(obj, list):
        for item in obj:
            extract_secrets_from_workflow(item, secrets)
            
    return secrets
```

### 4.2 Critical Workflow Analysis
Focus on these workflows:
- `.github/workflows/sync_secrets.yml` - Lines 44-195 contain secret mappings
- `.github/workflows/pulumi-esc-sync.yml` - Uses GITHUB_TOKEN, PULUMI_ACCESS_TOKEN
- `.github/workflows/deploy-sophia-platform.yml` - References multiple secrets
- `.github/workflows/vercel-deployment.yml` - Uses Vercel secrets

## PHASE 5: SECRET ACCESS PATTERN STANDARDIZATION

### 5.1 Identify Non-Standard Access Patterns
```python
# Script: scripts/standardize_secret_access.py
import ast
import os
from pathlib import Path

class SecretAccessAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        
    def visit_Call(self, node):
        # Check for os.getenv() usage
        if (isinstance(node.func, ast.Attribute) and 
            node.func.attr == 'getenv' and
            isinstance(node.func.value, ast.Name) and
            node.func.value.id == 'os'):
            self.issues.append({
                'type': 'os_getenv',
                'line': node.lineno,
                'should_use': 'get_config_value'
            })
            
        # Check for os.environ[] usage
        if (isinstance(node.func, ast.Subscript) and
            isinstance(node.func.value, ast.Attribute) and
            node.func.value.attr == 'environ'):
            self.issues.append({
                'type': 'os_environ',
                'line': node.lineno,
                'should_use': 'get_config_value'
            })
            
        self.generic_visit(node)

def analyze_file(filepath):
    with open(filepath) as f:
        tree = ast.parse(f.read())
    analyzer = SecretAccessAnalyzer()
    analyzer.visit(tree)
    return analyzer.issues
```

## PHASE 6: REMEDIATION IMPLEMENTATION

### 6.1 Fix Naming Convention Mismatches
```python
# Script: scripts/fix_naming_mismatches.py
FIXES_REQUIRED = {
    # In scripts/ci/sync_from_gh_to_pulumi.py
    "ASANA_API_TOKEN": "asana_api_token",  # Change from asana_access_token
    "NOTION_API_KEY": "notion_api_key",     # Change from notion_api_token
    
    # In backend/core/auto_esc_config.py - ensure mappings match
}

def apply_fixes():
    # Update sync script
    sync_script = Path('scripts/ci/sync_from_gh_to_pulumi.py')
    # Apply fixes...
    
    # Update backend config
    config_file = Path('backend/core/auto_esc_config.py')
    # Apply fixes...
```

### 6.2 Remove Placeholders
```python
# Script: scripts/remove_placeholders.py
PLACEHOLDER_REPLACEMENTS = {
    'infrastructure/vercel/index.ts': [
        ('PLACEHOLDER_SET_IN_VERCEL_DASHBOARD', 'get_config_value("vercel_secret")'),
    ],
    'vercel-env-bulk-import.env': [
        ('pk_placeholder_to_be_updated_from_pulumi_esc', '${PORTKEY_API_KEY}'),
    ],
}

def remove_placeholders():
    for file_path, replacements in PLACEHOLDER_REPLACEMENTS.items():
        # Apply replacements...
```

### 6.3 Standardize Secret Access
```python
# Script: scripts/standardize_secret_access_patterns.py
def fix_secret_access(file_path):
    with open(file_path) as f:
        content = f.read()
        
    # Replace os.getenv patterns
    content = re.sub(
        r'os\.getenv\(["\']([^"\']+)["\']\)',
        r'get_config_value("\1".lower())',
        content
    )
    
    # Add import if needed
    if 'get_config_value' in content and 'from backend.core.auto_esc_config' not in content:
        content = 'from backend.core.auto_esc_config import get_config_value\n' + content
        
    return content
```

## PHASE 7: VALIDATION & TESTING

### 7.1 End-to-End Secret Flow Test
```python
# Script: scripts/test_secret_flow.py
import subprocess
import json
from backend.core.auto_esc_config import get_config_value

def test_secret_flow():
    results = {
        'github_to_pulumi': {},
        'pulumi_to_backend': {},
        'service_auth': {}
    }
    
    # Test 1: GitHub → Pulumi sync
    print("Testing GitHub → Pulumi ESC sync...")
    # Trigger sync workflow or run sync script
    
    # Test 2: Pulumi ESC → Backend loading
    print("Testing Pulumi ESC → Backend loading...")
    critical_secrets = [
        'openai_api_key', 'anthropic_api_key', 'gong_access_key',
        'pinecone_api_key', 'hubspot_access_token', 'slack_bot_token',
        'snowflake_password', 'lambda_api_key'
    ]
    
    for secret in critical_secrets:
        value = get_config_value(secret)
        results['pulumi_to_backend'][secret] = {
            'loaded': bool(value),
            'length': len(value) if value else 0,
            'starts_with': value[:10] if value else None
        }
        
    # Test 3: Service authentication
    print("Testing service authentication...")
    # Test actual API calls with loaded secrets
    
    return results
```

### 7.2 Create Validation Dashboard
```python
# Script: scripts/create_secret_validation_dashboard.py
def create_dashboard():
    dashboard = {
        'timestamp': datetime.now().isoformat(),
        'github_secrets': check_github_secrets(),
        'pulumi_esc_status': check_pulumi_esc(),
        'backend_loading': check_backend_loading(),
        'service_health': check_service_health(),
        'issues_found': [],
        'recommendations': []
    }
    
    # Generate HTML report
    generate_html_report(dashboard)
    
    return dashboard
```

## DELIVERABLES CHECKLIST

1. **Secret Inventory Report** (`secret_inventory_report.json`)
   - Complete mapping of all secrets across GitHub, Pulumi ESC, and codebase
   - Categorized by service and criticality

2. **Naming Convention Fix List** (`naming_convention_fixes.md`)
   - Specific file changes required
   - Before/after examples

3. **Placeholder Removal Report** (`placeholder_removal_report.md`)
   - All hardcoded values found
   - Replacement recommendations

4. **Missing Secrets List** (`missing_secrets.txt`)
   - GitHub org secrets that need creation
   - Required values and sources

5. **Updated Configuration Files**
   - Fixed `scripts/ci/sync_from_gh_to_pulumi.py`
   - Updated `backend/core/auto_esc_config.py`
   - Corrected workflow files

6. **Validation Test Suite** (`scripts/validate_secrets/`)
   - Automated tests for complete pipeline
   - Health check scripts

7. **Implementation Guide** (`SECRET_MANAGEMENT_IMPLEMENTATION_GUIDE.md`)
   - Step-by-step remediation instructions
   - Priority matrix for fixes

## EXECUTION INSTRUCTIONS

1. **Start with Phase 1** - Complete inventory of current state
2. **Document all findings** before making changes
3. **Create backups** of files before modification
4. **Test in isolation** - Use a test Pulumi ESC environment if possible
5. **Apply fixes incrementally** - Start with critical secrets
6. **Validate each step** - Don't proceed until current step passes
7. **Create rollback plan** - Document how to revert changes

## SUCCESS METRICS

- ✅ 100% of critical secrets available in GitHub Organization
- ✅ 100% successful sync from GitHub to Pulumi ESC
- ✅ 100% of backend services can load required secrets
- ✅ 0 hardcoded secrets or placeholders in codebase
- ✅ 100% of workflows reference valid organization secrets
- ✅ Consistent naming across entire pipeline
- ✅ All external service authentications working

**Begin execution and report progress at each phase completion.** 