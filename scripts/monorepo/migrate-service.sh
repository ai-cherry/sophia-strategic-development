#!/bin/bash
set -euo pipefail

# Service Migration Script for Sophia AI Monorepo
# This script helps migrate a service to the new monorepo structure

echo "🚀 Sophia AI Service Migration Tool"
echo "==================================="

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}Usage: $0 <source-path> <target-type>${NC}"
    echo ""
    echo "target-type can be:"
    echo "  - app     (for applications)"
    echo "  - lib     (for shared libraries)"
    echo ""
    echo "Examples:"
    echo "  $0 backend/api app"
    echo "  $0 backend/core lib"
    exit 1
fi

SOURCE_PATH=$1
TARGET_TYPE=$2
SERVICE_NAME=$(basename "$SOURCE_PATH")

# Validate source exists
if [ ! -d "$SOURCE_PATH" ]; then
    echo -e "${RED}Error: Source path '$SOURCE_PATH' does not exist${NC}"
    exit 1
fi

# Determine target path
case $TARGET_TYPE in
    app)
        TARGET_BASE="apps"
        ;;
    lib)
        TARGET_BASE="libs"
        ;;
    *)
        echo -e "${RED}Error: Invalid target type '$TARGET_TYPE'${NC}"
        echo "Use 'app' or 'lib'"
        exit 1
        ;;
esac

TARGET_PATH="$TARGET_BASE/$SERVICE_NAME"

echo -e "${BLUE}Migrating: $SOURCE_PATH → $TARGET_PATH${NC}"
echo ""

# Create backup branch
BACKUP_BRANCH="backup/pre-migration-$(date +%Y%m%d-%H%M%S)"
echo "1️⃣ Creating backup branch..."
git checkout -b "$BACKUP_BRANCH" 2>/dev/null || true
git checkout main

# Check if target already exists
if [ -d "$TARGET_PATH" ]; then
    echo -e "${YELLOW}Warning: Target path '$TARGET_PATH' already exists${NC}"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Migration cancelled"
        exit 1
    fi
    rm -rf "$TARGET_PATH"
fi

# Create target directory
echo "2️⃣ Creating target directory..."
mkdir -p "$TARGET_PATH"

# Copy files
echo "3️⃣ Copying files..."
cp -r "$SOURCE_PATH"/* "$TARGET_PATH/" 2>/dev/null || true
cp -r "$SOURCE_PATH"/.[^.]* "$TARGET_PATH/" 2>/dev/null || true

# Create package.json if it doesn't exist (for Python services)
if [ ! -f "$TARGET_PATH/package.json" ] && [ "$TARGET_TYPE" = "app" ]; then
    echo "4️⃣ Creating package.json for Python service..."
    cat > "$TARGET_PATH/package.json" << EOF
{
  "name": "@sophia-ai/$SERVICE_NAME",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "uv run python -m $SERVICE_NAME",
    "build": "echo 'Python build'",
    "test": "uv run pytest tests/",
    "lint": "uv run ruff check .",
    "type-check": "uv run mypy ."
  }
}
EOF
    echo -e "${GREEN}✅ Created package.json${NC}"
fi

# Update imports in Python files
if [ "$TARGET_TYPE" = "lib" ]; then
    echo "5️⃣ Updating Python imports..."
    
    # Find all Python files and update imports
    find "$TARGET_PATH" -name "*.py" -type f | while read -r file; do
        # Update from backend.core to libs.core
        sed -i.bak "s/from backend\.$SERVICE_NAME/from libs.$SERVICE_NAME/g" "$file"
        sed -i.bak "s/import backend\.$SERVICE_NAME/import libs.$SERVICE_NAME/g" "$file"
        rm -f "${file}.bak"
    done
    
    echo -e "${GREEN}✅ Updated imports${NC}"
fi

# Create or update Dockerfile
if [ -f "$SOURCE_PATH/Dockerfile" ]; then
    echo "6️⃣ Updating Dockerfile..."
    cp "$SOURCE_PATH/Dockerfile" "$TARGET_PATH/Dockerfile"
    
    # Update paths in Dockerfile
    sed -i.bak "s|$SOURCE_PATH|$TARGET_PATH|g" "$TARGET_PATH/Dockerfile"
    rm -f "$TARGET_PATH/Dockerfile.bak"
else
    echo "6️⃣ Creating Dockerfile..."
    cat > "$TARGET_PATH/Dockerfile" << 'EOF'
FROM python:3.12-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files from root
COPY pyproject.toml uv.lock ./

# Install production dependencies
RUN uv sync --no-dev --frozen

# Copy application code
COPY . .

# Run the application
CMD ["uv", "run", "python", "-m", "main"]
EOF
fi

# Update CI/CD workflow if exists
WORKFLOW_FILE=".github/workflows/$SERVICE_NAME.yml"
if [ -f "$WORKFLOW_FILE" ]; then
    echo "7️⃣ Updating CI/CD workflow..."
    
    # Create new workflow using template
    cat > "$WORKFLOW_FILE" << EOF
name: $SERVICE_NAME CI/CD

on:
  push:
    branches: [main]
    paths:
      - '$TARGET_PATH/**'
      - 'pyproject.toml'
      - 'uv.lock'
  pull_request:
    paths:
      - '$TARGET_PATH/**'
      - 'pyproject.toml'
      - 'uv.lock'

jobs:
  ci:
    uses: ./.github/workflow-templates/python-ci.yml
    with:
      service-path: $TARGET_PATH
      python-version: '3.12'
      run-tests: true
      run-security: true
EOF
    
    echo -e "${GREEN}✅ Updated workflow${NC}"
fi

# Add to git
echo "8️⃣ Staging changes..."
git add "$TARGET_PATH"

# Create migration record
echo "9️⃣ Updating migration mapping..."
cat >> docs/monorepo/MIGRATION_MAPPING.md << EOF

| \`$SOURCE_PATH\` | \`$TARGET_PATH\` | Migrated $(date +%Y-%m-%d) |
EOF

# Summary
echo ""
echo -e "${GREEN}✨ Migration Complete!${NC}"
echo ""
echo "Summary:"
echo "  - Source: $SOURCE_PATH"
echo "  - Target: $TARGET_PATH"
echo "  - Type: $TARGET_TYPE"
echo "  - Backup: $BACKUP_BRANCH"
echo ""
echo "Next steps:"
echo "1. Review the migrated files in $TARGET_PATH"
echo "2. Update any hardcoded paths in the code"
echo "3. Test the service in its new location"
echo "4. Update documentation"
echo "5. Remove the old directory: rm -rf $SOURCE_PATH"
echo "6. Commit the changes"
echo ""
echo "To test the migrated service:"
if [ "$TARGET_TYPE" = "app" ]; then
    echo "  pnpm turbo run dev --filter=$SERVICE_NAME"
else
    echo "  pnpm turbo run test --filter=$SERVICE_NAME"
fi 