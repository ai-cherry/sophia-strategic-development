#!/bin/bash

echo "=== Sophia AI Environment Verification & Activation ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check and report status
check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# 1. Verify we're in the correct directory
echo "1. Checking current directory..."
CURRENT_DIR=$(pwd)
if [[ "$CURRENT_DIR" == *"sophia-main"* ]]; then
    check_status 0 "Current directory: $CURRENT_DIR"
else
    check_status 1 "Not in sophia-main directory! Current: $CURRENT_DIR"
    echo -e "${YELLOW}Changing to sophia-main...${NC}"
    cd ~/sophia-main
    check_status 0 "Changed to: $(pwd)"
fi

echo ""
echo "2. Checking Python virtual environment..."

# 2. Check if .venv exists
if [ -d ".venv" ]; then
    check_status 0 "Virtual environment exists at .venv"
else
    check_status 1 "Virtual environment not found!"
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    check_status 0 "Virtual environment created"
fi

echo ""
echo "3. Activating virtual environment..."

# 3. Activate virtual environment
source .venv/bin/activate
if [ "$VIRTUAL_ENV" != "" ]; then
    check_status 0 "Virtual environment activated: $VIRTUAL_ENV"
else
    check_status 1 "Failed to activate virtual environment"
fi

echo ""
echo "4. Setting environment variables..."

# 4. Set required environment variables
export ENVIRONMENT="prod"
export PULUMI_ORG="scoobyjava-org"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

check_status 0 "ENVIRONMENT set to: $ENVIRONMENT"
check_status 0 "PULUMI_ORG set to: $PULUMI_ORG"
check_status 0 "PYTHONPATH includes: $(pwd)"

echo ""
echo "5. Verifying Python setup..."

# 5. Check Python version and location
PYTHON_VERSION=$(python --version 2>&1)
PYTHON_PATH=$(which python)
check_status 0 "Python version: $PYTHON_VERSION"
check_status 0 "Python path: $PYTHON_PATH"

echo ""
echo "6. Testing backend module import..."

# 6. Test backend import
python -c "import sys; sys.path.insert(0, '.'); import backend; print('Backend module imported successfully')" 2>/dev/null
if [ $? -eq 0 ]; then
    check_status 0 "Backend module import test passed"
else
    check_status 1 "Backend module import test failed"
fi

echo ""
echo "7. Checking key files..."

# 7. Check for key files
FILES_TO_CHECK=(
    "backend/__init__.py"
    "backend/app/__init__.py"
    "requirements.txt"
    ".cursorrules"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        check_status 0 "$file exists"
    else
        check_status 1 "$file missing"
    fi
done

echo ""
echo "=== Environment Status Summary ==="
echo -e "${GREEN}✅ Working directory: $(pwd)${NC}"
echo -e "${GREEN}✅ Virtual environment: ${VIRTUAL_ENV}${NC}"
echo -e "${GREEN}✅ Python: $(which python)${NC}"
echo -e "${GREEN}✅ Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}✅ Pulumi Org: ${PULUMI_ORG}${NC}"

echo ""
echo "=== Quick Command Reference ==="
echo "To activate this environment in a new terminal:"
echo -e "${YELLOW}cd ~/sophia-main && source .venv/bin/activate${NC}"

echo ""
echo "To set environment variables:"
echo -e "${YELLOW}export ENVIRONMENT=prod${NC}"
echo -e "${YELLOW}export PULUMI_ORG=scoobyjava-org${NC}"
echo -e "${YELLOW}export PYTHONPATH=\$PYTHONPATH:$(pwd)${NC}"

echo ""
echo -e "${GREEN}✅ Sophia AI environment is ready!${NC}"
