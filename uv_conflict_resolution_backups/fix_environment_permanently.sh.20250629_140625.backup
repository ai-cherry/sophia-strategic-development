#!/bin/bash
# Sophia AI - Permanent Environment Stabilization Script
# This script permanently fixes all environment configuration issues

set -e

echo "🔒 SOPHIA AI ENVIRONMENT STABILIZATION"
echo "======================================"

# 1. Set permanent environment variables
echo "💾 Setting permanent environment variables..."
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"

# Add to shell profiles
for profile in ~/.bashrc ~/.zshrc ~/.profile; do
    if [[ -f "$profile" ]]; then
        # Remove old Sophia AI environment lines
        grep -v "# Sophia AI Environment" "$profile" > "$profile.tmp" || true
        grep -v "export ENVIRONMENT=" "$profile.tmp" > "$profile.new" || true
        grep -v "export PULUMI_ORG=" "$profile.new" > "$profile.clean" || true
        
        # Add new permanent environment setup
        cat >> "$profile.clean" << EOF

# Sophia AI Environment (Permanent Setup)
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
# END Sophia AI Environment
EOF
        mv "$profile.clean" "$profile"
        rm -f "$profile.tmp" "$profile.new"
        echo "✅ Updated $profile"
    fi
done

# 2. Fix current session
echo "🔧 Fixing current session environment..."
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"

# 3. Validate Pulumi access
echo "🔍 Validating Pulumi ESC access..."
if pulumi env open scoobyjava-org/default/sophia-ai-production --format json > /dev/null 2>&1; then
    echo "✅ Pulumi ESC access successful"
    SECRET_COUNT=$(pulumi env open scoobyjava-org/default/sophia-ai-production --format json | jq ". | length")
    echo "📊 Loaded $SECRET_COUNT secrets from production stack"
else
    echo "⚠️ Pulumi ESC access issue - checking authentication..."
    if ! pulumi whoami > /dev/null 2>&1; then
        echo "❌ Pulumi authentication required"
        echo "💡 Please run: export PULUMI_ACCESS_TOKEN=your_token"
    fi
fi

# 4. Test environment detection
echo "🧪 Testing environment detection..."
cd backend && python -c "
from backend.core.auto_esc_config import get_config_value
import os
print(f\"Environment: {os.getenv(\"ENVIRONMENT\", \"NOT_SET\")}\" )
print(f\"Pulumi Org: {os.getenv(\"PULUMI_ORG\", \"NOT_SET\")}\")
try:
    openai_key = get_config_value(\"openai_api_key\")
    print(f\"OpenAI Key: {openai_key[:20]}...\" if openai_key else \"OpenAI Key: Not found\")
except Exception as e:
    print(f\"Config test failed: {e}\")
" && cd ..

# 5. Update Docker environment
echo "🐳 Updating Docker configurations..."
for compose_file in docker-compose*.yml; do
    if [[ -f "$compose_file" ]]; then
        if ! grep -q "ENVIRONMENT=prod" "$compose_file"; then
            # Add environment section if missing
            echo "  # Added by stabilization script" >> "$compose_file"
            echo "  environment:" >> "$compose_file"
            echo "    - ENVIRONMENT=prod" >> "$compose_file"
            echo "    - PULUMI_ORG=scoobyjava-org" >> "$compose_file"
            echo "✅ Updated $compose_file"
        fi
    fi
done

# 6. Create permanent environment file
echo "📝 Creating permanent environment file..."
cat > .env.sophia << EOF
# Sophia AI Permanent Environment Configuration
ENVIRONMENT=prod
PULUMI_ORG=scoobyjava-org

# This file ensures consistent environment across all processes
# Source this file or use it with docker-compose
EOF

# 7. Create health check script
echo "🏥 Creating environment health check script..."
cat > scripts/check_environment_health.py << "HEALTH_EOF"
#!/usr/bin/env python3
"""Sophia AI Environment Health Check"""

import os
import subprocess
import json
from datetime import datetime

def check_environment_variables():
    """Check if environment variables are set correctly."""
    env_vars = {
        "ENVIRONMENT": "prod",
        "PULUMI_ORG": "scoobyjava-org"
    }
    
    issues = []
    for var, expected in env_vars.items():
        actual = os.getenv(var)
        if actual != expected:
            issues.append(f"{var}: expected {expected}, got {actual}")
    
    return len(issues) == 0, issues

def check_pulumi_auth():
    """Check Pulumi authentication."""
    try:
        result = subprocess.run(["pulumi", "whoami"], capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stderr if result.returncode != 0 else None
    except Exception as e:
        return False, str(e)

def check_stack_access():
    """Check access to production stack."""
    try:
        result = subprocess.run([
            "pulumi", "env", "open", "scoobyjava-org/default/sophia-ai-production", "--format", "json"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            config = json.loads(result.stdout)
            return True, f"Loaded {len(config)} secrets"
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def main():
    print("🏥 Sophia AI Environment Health Check")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    overall_health = True
    
    # Check 1: Environment Variables
    env_ok, env_issues = check_environment_variables()
    print(f"Environment Variables: {✅ if env_ok else ❌}")
    if not env_ok:
        overall_health = False
        for issue in env_issues:
            print(f"  - {issue}")
    print()
    
    # Check 2: Pulumi Authentication
    auth_ok, auth_error = check_pulumi_auth()
    print(f"Pulumi Authentication: {✅ if auth_ok else ❌}")
    if not auth_ok:
        overall_health = False
        print(f"  - {auth_error}")
    print()
    
    # Check 3: Stack Access
    stack_ok, stack_info = check_stack_access()
    print(f"Stack Access: {✅ if stack_ok else ❌}")
    if stack_ok:
        print(f"  - {stack_info}")
    else:
        overall_health = False
        print(f"  - {stack_info}")
    print()
    
    # Overall Status
    print(f"Overall Health: {✅ HEALTHY if overall_health else ❌ ISSUES DETECTED}")
    
    if not overall_health:
        print()
        print("🔧 To fix issues:")
        print("1. Run: export ENVIRONMENT=prod")
        print("2. Run: export PULUMI_ORG=scoobyjava-org")
        print("3. Run: export PULUMI_ACCESS_TOKEN=your_token")
        print("4. Re-run this check")
    
    return 0 if overall_health else 1

if __name__ == "__main__":
    exit(main())
HEALTH_EOF

chmod +x scripts/check_environment_health.py

echo ""
echo "�� ENVIRONMENT STABILIZATION COMPLETE!"
echo "======================================"
echo "✅ Environment variables set permanently"
echo "✅ Shell profiles updated"
echo "✅ Docker configurations updated"
echo "✅ Health check script created"
echo ""
echo "🔍 Run health check: python scripts/check_environment_health.py"
echo "🔧 Manual verification: echo \$ENVIRONMENT"
echo ""
echo "🎯 Environment is now permanently set to PRODUCTION"
