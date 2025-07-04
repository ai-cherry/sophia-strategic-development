#!/bin/bash
set -euo pipefail

# Sophia AI Monorepo Bootstrap Script
# This script initializes the monorepo structure and installs necessary tools

echo "🚀 Sophia AI Monorepo Bootstrap"
echo "==============================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "backend" ]; then
    echo -e "${RED}Error: Must run from sophia-main root directory${NC}"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install PNPM
install_pnpm() {
    echo "📦 Installing PNPM..."
    if command_exists npm; then
        npm install -g pnpm@latest
    else
        curl -fsSL https://get.pnpm.io/install.sh | sh -
    fi
}

# Function to check UV installation
check_uv() {
    if ! command_exists uv; then
        echo -e "${YELLOW}UV not found. Please install UV first:${NC}"
        echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
        return 1
    fi
    return 0
}

# Step 1: Check prerequisites
echo "1️⃣ Checking prerequisites..."
if ! check_uv; then
    echo -e "${RED}Please install UV and run this script again${NC}"
    exit 1
fi

if ! command_exists pnpm; then
    install_pnpm
fi

if ! command_exists node; then
    echo -e "${RED}Node.js is required. Please install Node.js 18+ and try again${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites satisfied${NC}"

# Step 2: Create monorepo directory structure
echo ""
echo "2️⃣ Creating monorepo structure..."

# Create apps directory
mkdir -p apps/{api,frontend,mcp-servers,n8n-bridge}

# Create libs directory
mkdir -p libs/{ui,utils,types,core}

# Create config directory
mkdir -p config/{eslint,prettier,typescript,ruff}

echo -e "${GREEN}✅ Directory structure created${NC}"

# Step 3: Initialize root package.json
echo ""
echo "3️⃣ Initializing root workspace..."

if [ ! -f "package.json" ]; then
    cat > package.json << 'EOF'
{
  "name": "@sophia-ai/root",
  "version": "1.0.0",
  "private": true,
  "description": "Sophia AI Monorepo Root",
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "clean": "turbo run clean",
    "security:audit": "./scripts/audit-deps.sh"
  },
  "devDependencies": {
    "turbo": "^1.11.0"
  },
  "engines": {
    "node": ">=18.0.0",
    "pnpm": ">=8.0.0"
  },
  "packageManager": "pnpm@8.14.0"
}
EOF
    echo -e "${GREEN}✅ Created package.json${NC}"
else
    echo -e "${YELLOW}⚠️  package.json already exists, skipping${NC}"
fi

# Step 4: Create pnpm-workspace.yaml
echo ""
echo "4️⃣ Creating PNPM workspace configuration..."

if [ ! -f "pnpm-workspace.yaml" ]; then
    cat > pnpm-workspace.yaml << 'EOF'
packages:
  # Applications
  - 'apps/*'
  # Shared libraries
  - 'libs/*'
  # Configuration packages
  - 'config/*'
EOF
    echo -e "${GREEN}✅ Created pnpm-workspace.yaml${NC}"
else
    echo -e "${YELLOW}⚠️  pnpm-workspace.yaml already exists, skipping${NC}"
fi

# Step 5: Create turbo.json
echo ""
echo "5️⃣ Creating Turborepo configuration..."

if [ ! -f "turbo.json" ]; then
    cat > turbo.json << 'EOF'
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "build/**"],
      "env": ["NODE_ENV"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"],
      "env": ["NODE_ENV"]
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "clean": {
      "cache": false
    }
  }
}
EOF
    echo -e "${GREEN}✅ Created turbo.json${NC}"
else
    echo -e "${YELLOW}⚠️  turbo.json already exists, skipping${NC}"
fi

# Step 6: Install dependencies
echo ""
echo "6️⃣ Installing workspace dependencies..."

# Install pnpm dependencies
pnpm install

# Step 7: Create migration mapping
echo ""
echo "7️⃣ Creating migration mapping..."

cat > docs/monorepo/MIGRATION_MAPPING.md << 'EOF'
# Migration Mapping

## Directory Mapping

| Current Location | New Location | Status |
|-----------------|--------------|--------|
| `backend/api/` | `apps/api/` | Pending |
| `backend/agents/` | `apps/api/src/agents/` | Pending |
| `backend/services/` | `apps/api/src/services/` | Pending |
| `frontend/` | `apps/frontend/` | Pending |
| `mcp-servers/` | `apps/mcp-servers/` | Pending |
| `backend/utils/` | `libs/utils/` | Pending |
| `backend/core/` | `libs/core/` | Pending |

## Import Updates Required

### Python Imports
- `from backend.core.x` → `from libs.core.x`
- `from backend.utils.x` → `from libs.utils.x`

### TypeScript Imports
- `from '../components'` → `from '@sophia-ai/ui'`
- `from '../utils'` → `from '@sophia-ai/utils'`

## Configuration Files

### To Centralize
- ESLint configs → `/config/eslint/`
- Prettier config → `/config/prettier/`
- TypeScript configs → `/config/typescript/`
- Ruff config → `/config/ruff/`
EOF

echo -e "${GREEN}✅ Created migration mapping${NC}"

# Step 8: Create initial .gitignore updates
echo ""
echo "8️⃣ Updating .gitignore..."

# Add monorepo-specific ignores
cat >> .gitignore << 'EOF'

# Monorepo
.turbo/
.pnpm-store/
EOF

# Step 9: Validate setup
echo ""
echo "9️⃣ Validating setup..."

# Create a simple validation script
cat > apps/api/package.json << 'EOF'
{
  "name": "@sophia-ai/api",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "echo": "echo 'API package working'"
  }
}
EOF

# Test turbo
if pnpm turbo run echo --filter=api; then
    echo -e "${GREEN}✅ Turbo validation successful${NC}"
else
    echo -e "${RED}❌ Turbo validation failed${NC}"
fi

# Step 10: Summary
echo ""
echo "✨ Bootstrap Complete!"
echo "===================="
echo ""
echo "Next steps:"
echo "1. Review the migration mapping in docs/monorepo/MIGRATION_MAPPING.md"
echo "2. Start migrating services according to the plan"
echo "3. Run 'pnpm turbo run build' to test the build pipeline"
echo ""
echo "Useful commands:"
echo "  pnpm install              - Install all dependencies"
echo "  pnpm turbo run build      - Build all packages"
echo "  pnpm turbo run dev        - Start dev servers"
echo "  pnpm turbo run test       - Run all tests"
echo "  ./scripts/audit-deps.sh   - Run security audit"
echo ""
echo -e "${GREEN}🎉 Happy coding!${NC}"
