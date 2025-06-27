#!/bin/bash

# Sophia AI Environment Verification and Activation Script
# This script ensures the environment is properly set up for Cline and other AI tools

echo "🔍 Sophia AI Environment Verification Starting..."
echo "================================================"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [[ ! -f "sophia_aliases.sh" ]]; then
    echo -e "${RED}❌ Not in Sophia AI directory!${NC}"
    echo "Please run this from ~/sophia-main"
    exit 1
fi

# Check Python virtual environment
if [[ -d ".venv" ]]; then
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    source .venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
else
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment created and activated${NC}"
fi

# Set environment variables
export PYTHONPATH="$(pwd):$PYTHONPATH"
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
export SOPHIA_HOME="$(pwd)"

echo -e "${GREEN}✅ Environment variables set${NC}"

# Verify Python
echo ""
echo "Python Information:"
echo "==================="
echo "Python: $(which python)"
echo "Version: $(python --version)"

# Check shell integration
echo ""
echo "Shell Information:"
echo "=================="
echo "Current Shell: $SHELL"
echo "Terminal Program: ${TERM_PROGRAM:-Not in VSCode}"

# Check VSCode settings
if [[ -f ".vscode/settings.json" ]]; then
    echo -e "${GREEN}✅ VSCode settings found${NC}"
else
    echo -e "${YELLOW}⚠️  VSCode settings not found${NC}"
fi

# Final status
echo ""
echo "================================================"
if [[ "$VIRTUAL_ENV" != "" ]] && [[ "$PYTHONPATH" != "" ]]; then
    echo -e "${GREEN}🚀 Environment is ready for Cline!${NC}"
    echo ""
    echo "Quick Commands:"
    echo "  - Check health: python backend/scripts/check_environment_health.py"
    echo "  - Start backend: python start_backend_services.py"
    echo "  - Start MCP: python start_mcp_servers.py"
else
    echo -e "${RED}❌ Environment setup incomplete${NC}"
    echo "Please check the MASTER_ENVIRONMENT_GUIDE.md for troubleshooting"
fi

# Keep environment active
exec $SHELL
