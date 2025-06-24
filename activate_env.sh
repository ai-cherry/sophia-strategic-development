#!/bin/bash
# Generic Virtual Environment Activation Script
# Works for any repository with .venv directory

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/.venv"
PROJECT_NAME="$(basename "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔧 Activating environment for $PROJECT_NAME${NC}"

# Activate virtual environment
if [[ -f "$VENV_PATH/bin/activate" ]]; then
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}✅ Virtual environment activated for $PROJECT_NAME${NC}"
    echo -e "${GREEN}Python: $(python --version) at $(which python)${NC}"
else
    echo -e "${RED}❌ Virtual environment not found at $VENV_PATH${NC}"
    exit 1
fi

# Set PYTHONPATH to current directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Load .env file if it exists
if [[ -f "$SCRIPT_DIR/.env" ]]; then
    echo -e "${YELLOW}📄 Loading .env file...${NC}"
    set -a  # automatically export all variables
    source "$SCRIPT_DIR/.env"
    set +a
    echo -e "${GREEN}✅ Environment variables loaded${NC}"
fi

echo -e "${GREEN}🚀 Environment ready for $PROJECT_NAME!${NC}"

# Keep environment active
exec "$SHELL"
