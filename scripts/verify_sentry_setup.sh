#!/bin/bash

# Sentry Integration Verification Script
# Verifies that all components are properly configured

set -e

echo "🔍 Sentry Integration Verification for Sophia AI"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a file exists
check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $description: $file"
        return 0
    else
        echo -e "${RED}❌${NC} $description: $file (missing)"
        return 1
    fi
}

# Function to check if a command exists
check_command() {
    local cmd=$1
    local description=$2
    
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✅${NC} $description: $cmd"
        return 0
    else
        echo -e "${RED}❌${NC} $description: $cmd (not found)"
        return 1
    fi
}

echo "📋 Checking Required Files..."
echo "-----------------------------"

# Check core configuration files
check_file "backend/core/sentry_setup.py" "Sentry setup module"
check_file "backend/core/auto_esc_config.py" "Auto ESC config module"
check_file "backend/agents/specialized/sentry_agent.py" "Sentry agent"
check_file "mcp-servers/sentry/sentry_mcp_server.py" "Sentry MCP server"

echo ""
echo "📋 Checking GitHub Workflows..."
echo "-------------------------------"

# Check GitHub workflows
check_file ".github/workflows/sync-sentry-secrets.yml" "Sentry secrets sync workflow"
check_file ".github/workflows/deploy-sentry-mcp.yml" "Sentry MCP deployment workflow"

echo ""
echo "📋 Checking Setup Scripts..."
echo "----------------------------"

# Check setup scripts
check_file "scripts/setup_github_sentry_secrets.sh" "GitHub secrets setup script"
check_file "scripts/create_sentry_project.py" "Sentry project creation script"
check_file "scripts/test/test_sentry_agent.py" "Sentry agent test script"

echo ""
echo "📋 Checking Documentation..."
echo "----------------------------"

# Check documentation
check_file "docs/SENTRY_COMPLETE_SETUP_GUIDE.md" "Complete setup guide"
check_file "sentry_config_setup.md" "Configuration setup guide"

echo ""
echo "🔧 Checking Required Tools..."
echo "-----------------------------"

# Check required tools
check_command "gh" "GitHub CLI"
check_command "python3" "Python 3"
check_command "git" "Git"

echo ""
echo "📊 Configuration Summary"
echo "========================"

echo ""
echo "🔐 Required GitHub Secrets (ai-cherry organization):"
echo "  - SENTRY_AUTH_TOKEN (Personal Access Token)"
echo "  - SENTRY_API_TOKEN (API Token)"
echo "  - SENTRY_CLIENT_SECRET (Client Secret)"
echo "  - SENTRY_ORGANIZATION_SLUG (pay-ready)"
echo "  - SENTRY_PROJECT_SLUG (sophia-ai)"
echo "  - SENTRY_DSN (To be set after project creation)"

echo ""
echo "🏗️ Sentry Project Configuration:"
echo "  - Organization: pay-ready"
echo "  - Project: sophia-ai"
echo "  - Platform: Python"
echo "  - URL: https://sentry.io"

echo ""
echo "⚡ Pulumi ESC Environment:"
echo "  - Organization: scoobyjava-org"
echo "  - Environment: scoobyjava-org/default/sophia-ai-production"

echo ""
echo "🚀 Next Steps:"
echo "=============="
echo ""
echo "1. Set up GitHub secrets:"
echo "   ./scripts/setup_github_sentry_secrets.sh"
echo ""
echo "2. Create Sentry project and get DSN:"
echo "   python3 scripts/create_sentry_project.py"
echo ""
echo "3. Set SENTRY_DSN secret:"
echo "   gh secret set SENTRY_DSN --org ai-cherry --visibility all"
echo ""
echo "4. Sync secrets to Pulumi ESC:"
echo "   gh workflow run sync-sentry-secrets.yml --repo ai-cherry/sophia-main"
echo ""
echo "5. Test the integration:"
echo "   python3 scripts/test/test_sentry_agent.py"
echo ""
echo "6. Verify in Sentry dashboard:"
echo "   https://pay-ready.sentry.io/projects/sophia-ai/"
echo ""

echo -e "${GREEN}✅ Verification complete!${NC}"
echo ""
echo "📖 For detailed instructions, see: docs/SENTRY_COMPLETE_SETUP_GUIDE.md"

