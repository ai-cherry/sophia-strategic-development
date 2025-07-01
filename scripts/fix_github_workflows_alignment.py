#!/usr/bin/env python3
"""
Fix GitHub Actions Workflows Alignment
=====================================

Fixes critical misalignments in GitHub Actions workflows to ensure they align
with current Sophia AI platform state and production-first policy.
"""

import re
from pathlib import Path


def fix_environment_defaults(workflow_path: str) -> bool:
    """Fix environment defaults from staging to prod."""
    try:
        with open(workflow_path) as f:
            content = f.read()

        # Fix environment default values
        content = re.sub(
            r"default:\s*['\"]staging['\"]",
            "default: 'prod'",
            content
        )

        # Fix ENVIRONMENT variable assignments
        content = re.sub(
            r'ENVIRONMENT="staging"',
            'ENVIRONMENT="prod"',
            content
        )

        # Fix conditional environment checks
        content = re.sub(
            r'ENVIRONMENT.*staging',
            lambda m: m.group(0).replace('staging', 'prod'),
            content
        )

        with open(workflow_path, 'w') as f:
            f.write(content)

        print(f"✅ Fixed environment defaults in {workflow_path}")
        return True

    except Exception as e:
        print(f"❌ Error fixing {workflow_path}: {e}")
        return False

def fix_yaml_syntax_errors(workflow_path: str) -> bool:
    """Fix common YAML syntax errors in workflows."""
    try:
        with open(workflow_path) as f:
            content = f.read()

        # Fix trailing colons in lists
        content = re.sub(r":\s*$", "", content, flags=re.MULTILINE)

        # Fix indentation issues
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            # Fix common indentation issues
            if line.strip().startswith('echo ') and line.endswith(':'):
                line = line.rstrip(':')
            elif line.strip().startswith('uv ') and line.endswith(':'):
                line = line.rstrip(':')
            elif line.strip().startswith('python ') and line.endswith(':'):
                line = line.rstrip(':')

            fixed_lines.append(line)

        content = '\n'.join(fixed_lines)

        with open(workflow_path, 'w') as f:
            f.write(content)

        print(f"✅ Fixed YAML syntax in {workflow_path}")
        return True

    except Exception as e:
        print(f"❌ Error fixing YAML syntax in {workflow_path}: {e}")
        return False

def remove_database_url_dependencies(workflow_path: str) -> bool:
    """Remove DATABASE_URL dependencies and replace with Snowflake ESC."""
    try:
        with open(workflow_path) as f:
            content = f.read()

        # Remove DATABASE_URL environment variables
        content = re.sub(
            r'^\s*DATABASE_URL:.*$',
            '',
            content,
            flags=re.MULTILINE
        )

        # Remove DATABASE_URL validation checks
        content = re.sub(
            r'.*DATABASE_URL.*not set.*$',
            '',
            content,
            flags=re.MULTILINE
        )

        # Add Snowflake ESC integration if missing
        if 'PULUMI_ORG: scoobyjava-org' not in content:
            content = content.replace(
                'env:',
                'env:\n  PULUMI_ORG: scoobyjava-org'
            )

        with open(workflow_path, 'w') as f:
            f.write(content)

        print(f"✅ Removed DATABASE_URL dependencies in {workflow_path}")
        return True

    except Exception as e:
        print(f"❌ Error removing DATABASE_URL from {workflow_path}: {e}")
        return False

def update_application_entry_points(workflow_path: str) -> bool:
    """Update workflows to use correct FastAPI entry points."""
    try:
        with open(workflow_path) as f:
            content = f.read()

        # Update Python application startup commands
        replacements = [
            (r'python app\.py', 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8000'),
            (r'python main\.py', 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8000'),
            (r'flask run', 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8000'),
            (r'gunicorn.*app', 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8000'),
        ]

        for old_pattern, new_command in replacements:
            content = re.sub(old_pattern, new_command, content)

        with open(workflow_path, 'w') as f:
            f.write(content)

        print(f"✅ Updated application entry points in {workflow_path}")
        return True

    except Exception as e:
        print(f"❌ Error updating entry points in {workflow_path}: {e}")
        return False

def analyze_workflow_health() -> dict[str, list[str]]:
    """Analyze all workflows and categorize their health status."""
    workflows_dir = Path('.github/workflows')

    aligned = []
    needs_updates = []
    deprecated = []

    for workflow_file in workflows_dir.glob('*.yml'):
        workflow_name = workflow_file.name

        try:
            with open(workflow_file) as f:
                content = f.read()

            # Check for misalignment indicators
            has_staging_default = "default: 'staging'" in content
            has_database_url = "DATABASE_URL" in content
            has_old_entry_points = any(pattern in content for pattern in ['python app.py', 'flask run'])

            if has_staging_default or has_database_url or has_old_entry_points:
                needs_updates.append(workflow_name)
            elif workflow_name in ['production_deployment.yml', 'deploy-phase2.yml']:
                deprecated.append(workflow_name)
            else:
                aligned.append(workflow_name)

        except Exception as e:
            print(f"⚠️ Could not analyze {workflow_name}: {e}")
            needs_updates.append(workflow_name)

    return {
        'aligned': aligned,
        'needs_updates': needs_updates,
        'deprecated': deprecated
    }

def create_workflow_hierarchy_documentation():
    """Create documentation for the recommended workflow hierarchy."""
    hierarchy_doc = """# Sophia AI GitHub Actions Workflow Hierarchy

## Primary Workflows

### 1. sophia-main.yml (Production Deployment)
- **Purpose**: Primary production deployment workflow
- **Triggers**: Push to main branch, manual dispatch
- **Environment**: Production only
- **Features**:
  - Pulumi ESC integration
  - Backend + Frontend + Infrastructure deployment
  - Security scanning
  - Automated testing

### 2. deploy-sophia-platform.yml (Multi-Environment)
- **Purpose**: Comprehensive multi-environment deployment
- **Triggers**: Push to main/develop, pull requests
- **Environment**: dev/staging/prod
- **Features**:
  - Preview deployments for PRs
  - Environment-specific configurations
  - Comprehensive testing suite

## Specialized Workflows

### MCP Operations
- `mcp-integration-test.yml` - MCP server testing
- `mcp-security-audit.yml` - Security validation
- `sync-mcp-submodules.yml` - Submodule management

### Infrastructure
- `infrastructure-deploy.yml` - Infrastructure only
- `infrastructure-tests.yml` - Infrastructure validation
- `sync_secrets.yml` - Secret management

### Development
- `cursor-integration.yml` - IDE integration
- `documentation-quality.yml` - Documentation checks
- `test-suite.yml` - Test execution

## Deprecated Workflows
- `production_deployment.yml` - Superseded by sophia-main.yml
- `deploy-phase2.yml` - DATABASE_URL dependency issues

## Usage Guidelines

### For Production Deployments
```bash
# Automatic on push to main
git push origin main

# Manual deployment
gh workflow run "Sophia AI Production Deployment"
```

### For Development
```bash
# Create PR for preview deployment
git push origin feature-branch
# Creates PR which triggers preview deployment
```

### For Infrastructure Changes
```bash
# Manual infrastructure deployment
gh workflow run "Deploy Infrastructure" --ref main
```

## Environment Variables

All workflows use centralized environment configuration:
- `PULUMI_ORG: scoobyjava-org`
- `ENVIRONMENT: prod` (default)
- Secrets managed via Pulumi ESC
- No DATABASE_URL dependencies (use Snowflake via ESC)

## Monitoring

Check workflow status:
```bash
gh run list --limit 10
gh run view <run-id>
```
"""

    with open('GITHUB_WORKFLOWS_HIERARCHY.md', 'w') as f:
        f.write(hierarchy_doc)

    print("✅ Created workflow hierarchy documentation")

def main():
    """Main function to fix all workflow alignment issues."""
    print("🔧 Fixing GitHub Actions Workflow Alignment Issues")
    print("=" * 50)

    # Get list of workflows to fix
    workflows_dir = Path('.github/workflows')

    # Workflows that need environment fixes
    environment_fix_workflows = [
        'deploy-sophia-platform.yml',
        'deploy-sophia-platform-fixed.yml',
        'deploy_infrastructure.yml',
        'master-deployment-workflow.yml'
    ]

    # Workflows that need DATABASE_URL removal
    database_url_workflows = [
        'deploy-phase2.yml',
        'sync_secrets.yml'
    ]

    success_count = 0
    total_fixes = 0

    # Fix environment defaults
    print("\n🎯 Fixing Environment Defaults...")
    for workflow in environment_fix_workflows:
        workflow_path = workflows_dir / workflow
        if workflow_path.exists():
            total_fixes += 1
            if fix_environment_defaults(str(workflow_path)):
                success_count += 1

    # Fix YAML syntax errors
    print("\n🔧 Fixing YAML Syntax Errors...")
    for workflow_file in workflows_dir.glob('*.yml'):
        total_fixes += 1
        if fix_yaml_syntax_errors(str(workflow_file)):
            success_count += 1

    # Remove DATABASE_URL dependencies
    print("\n🗄️ Removing DATABASE_URL Dependencies...")
    for workflow in database_url_workflows:
        workflow_path = workflows_dir / workflow
        if workflow_path.exists():
            total_fixes += 1
            if remove_database_url_dependencies(str(workflow_path)):
                success_count += 1

    # Update application entry points
    print("\n🚀 Updating Application Entry Points...")
    for workflow_file in workflows_dir.glob('*.yml'):
        total_fixes += 1
        if update_application_entry_points(str(workflow_file)):
            success_count += 1

    # Analyze workflow health
    print("\n📊 Analyzing Workflow Health...")
    health_status = analyze_workflow_health()

    print(f"\n✅ Aligned Workflows ({len(health_status['aligned'])}):")
    for workflow in health_status['aligned'][:5]:  # Show first 5
        print(f"  - {workflow}")
    if len(health_status['aligned']) > 5:
        print(f"  ... and {len(health_status['aligned']) - 5} more")

    print(f"\n⚠️ Needs Updates ({len(health_status['needs_updates'])}):")
    for workflow in health_status['needs_updates']:
        print(f"  - {workflow}")

    print(f"\n❌ Deprecated ({len(health_status['deprecated'])}):")
    for workflow in health_status['deprecated']:
        print(f"  - {workflow}")

    # Create documentation
    print("\n📚 Creating Documentation...")
    create_workflow_hierarchy_documentation()

    # Summary
    print("\n" + "=" * 50)
    print("🎯 Workflow Alignment Summary")
    print(f"Total fixes attempted: {total_fixes}")
    print(f"Successful fixes: {success_count}")
    print(f"Success rate: {(success_count/total_fixes)*100:.1f}%")

    alignment_percentage = (len(health_status['aligned']) /
                          (len(health_status['aligned']) + len(health_status['needs_updates']))) * 100
    print(f"Workflow alignment: {alignment_percentage:.1f}%")

    if alignment_percentage >= 90:
        print("✅ Workflows are well-aligned with current state!")
    elif alignment_percentage >= 75:
        print("⚠️ Workflows need minor adjustments")
    else:
        print("❌ Workflows need significant updates")

    print("\n🚀 Next Steps:")
    print("1. Review fixed workflows in .github/workflows/")
    print("2. Test deployment with: gh workflow run 'Sophia AI Production Deployment'")
    print("3. Monitor workflow runs: gh run list")
    print("4. Check GITHUB_WORKFLOWS_HIERARCHY.md for usage guidelines")

if __name__ == "__main__":
    main()
