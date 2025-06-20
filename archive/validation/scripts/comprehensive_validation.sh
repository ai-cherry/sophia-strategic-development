#!/bin/bash
# comprehensive_validation.sh
# Comprehensive Codebase Validation After Migration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Initialize validation results
VALIDATION_RESULTS=()
ERROR_COUNT=0
WARNING_COUNT=0

# Add result to tracking
add_result() {
    local status=$1
    local message=$2
    VALIDATION_RESULTS+=("$status: $message")

    case $status in
        "ERROR")
            ((ERROR_COUNT++))
            log_error "$message"
            ;;
        "WARNING")
            ((WARNING_COUNT++))
            log_warning "$message"
            ;;
        "SUCCESS")
            log_success "$message"
            ;;
        "INFO")
            log_info "$message"
            ;;
    esac
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "🚀 Starting Comprehensive Codebase Validation..."
echo "=================================================="

# Phase 1: Dependency Analysis
echo -e "\n📦 Phase 1: Dependency Analysis"
echo "--------------------------------"

log_info "Checking Python dependencies..."
if command_exists python; then
    if python -m pip check >/dev/null 2>&1; then
        add_result "SUCCESS" "Python dependencies are consistent"
    else
        add_result "ERROR" "Python dependency conflicts detected"
        python -m pip check
    fi
else
    add_result "ERROR" "Python not found"
fi

log_info "Checking Node.js dependencies..."
if command_exists npm; then
    if [ -f "frontend/package.json" ]; then
        cd frontend
        if npm audit --audit-level moderate >/dev/null 2>&1; then
            add_result "SUCCESS" "Frontend dependencies secure"
        else
            add_result "WARNING" "Frontend dependency vulnerabilities found"
            npm audit --audit-level moderate
        fi
        cd ..
    fi

    if [ -f "frontend/knowledge-admin/package.json" ]; then
        cd frontend/knowledge-admin
        if npm audit --audit-level moderate >/dev/null 2>&1; then
            add_result "SUCCESS" "Knowledge admin dependencies secure"
        else
            add_result "WARNING" "Knowledge admin dependency vulnerabilities found"
            npm audit --audit-level moderate
        fi
        cd ../..
    fi
else
    add_result "WARNING" "npm not found - skipping Node.js dependency checks"
fi

log_info "Validating Python file compilation..."
NEW_PYTHON_FILES=(
    "scripts/migrate_to_pulumi_idp.py"
    "scripts/enhanced_migration_with_improvements.py"
    "scripts/implement_next_level_enhancements.py"
    "infrastructure/components/dashboard_platform.py"
    "infrastructure/pulumi_idp_main.py"
    "lambda/dashboard-generator/dashboard_generator.py"
)

for file in "${NEW_PYTHON_FILES[@]}"; do
    if [ -f "$file" ]; then
        if python -m py_compile "$file" 2>/dev/null; then
            add_result "SUCCESS" "$file compiles successfully"
        else
            add_result "ERROR" "$file has compilation errors"
            python -m py_compile "$file"
        fi
    else
        add_result "WARNING" "$file not found"
    fi
done

# Phase 2: Code Quality
echo -e "\n🧹 Phase 2: Code Quality"
echo "------------------------"

log_info "Running black formatter check..."
if command_exists black; then
    if black --check . >/dev/null 2>&1; then
        add_result "SUCCESS" "Code formatting is consistent"
    else
        add_result "WARNING" "Code formatting issues found"
        black --check --diff .
    fi
else
    add_result "WARNING" "black not installed - skipping format check"
fi

log_info "Running isort import check..."
if command_exists isort; then
    if isort --check-only . >/dev/null 2>&1; then
        add_result "SUCCESS" "Import sorting is consistent"
    else
        add_result "WARNING" "Import sorting issues found"
        isort --check-only --diff .
    fi
else
    add_result "WARNING" "isort not installed - skipping import check"
fi

log_info "Running ruff linting..."
if command_exists ruff; then
    if ruff check . >/dev/null 2>&1; then
        add_result "SUCCESS" "No linting issues found"
    else
        add_result "WARNING" "Linting issues found"
        ruff check . | head -20  # Show first 20 issues
    fi
else
    add_result "WARNING" "ruff not installed - skipping lint check"
fi

log_info "Running mypy type checking..."
if command_exists mypy; then
    if mypy . >/dev/null 2>&1; then
        add_result "SUCCESS" "No type checking issues found"
    else
        add_result "WARNING" "Type checking issues found"
        mypy . | head -10  # Show first 10 issues
    fi
else
    add_result "WARNING" "mypy not installed - skipping type check"
fi

# Phase 3: Configuration Validation
echo -e "\n⚙️ Phase 3: Configuration Validation"
echo "------------------------------------"

log_info "Checking Pulumi configuration..."
if command_exists pulumi; then
    if pulumi config get environment >/dev/null 2>&1; then
        add_result "SUCCESS" "Pulumi environment configured"
    else
        add_result "WARNING" "Pulumi environment not configured"
    fi

    if pulumi stack --show-urns >/dev/null 2>&1; then
        add_result "SUCCESS" "Pulumi stack is valid"
    else
        add_result "WARNING" "Pulumi stack issues detected"
    fi
else
    add_result "WARNING" "Pulumi not installed - skipping Pulumi checks"
fi

log_info "Checking Docker configuration..."
if command_exists docker-compose; then
    if docker-compose config >/dev/null 2>&1; then
        add_result "SUCCESS" "Docker Compose configuration is valid"
    else
        add_result "ERROR" "Docker Compose configuration errors"
        docker-compose config
    fi
else
    add_result "WARNING" "docker-compose not found - skipping Docker checks"
fi

log_info "Checking environment variables..."
ENV_VAR_FILES=(
    "env.template"
    "config/portkey.json"
    "config/pulumi-mcp.json"
    "mcp-config/mcp_servers.json"
)

for file in "${ENV_VAR_FILES[@]}"; do
    if [ -f "$file" ]; then
        add_result "SUCCESS" "$file exists"
    else
        add_result "WARNING" "$file not found"
    fi
done

# Check for hardcoded values
log_info "Checking for hardcoded values..."
HARDCODED_CHECK=$(grep -r "localhost\|127.0.0.1\|https://api" scripts/ infrastructure/ lambda/ --include="*.py" 2>/dev/null || true)
if [ -n "$HARDCODED_CHECK" ]; then
    add_result "WARNING" "Potential hardcoded values found"
    echo "$HARDCODED_CHECK" | head -5
else
    add_result "SUCCESS" "No obvious hardcoded values found"
fi

# Phase 4: Integration Testing
echo -e "\n🧪 Phase 4: Integration Testing"
echo "-------------------------------"

log_info "Testing migration script imports..."
if python -c "import scripts.migrate_to_pulumi_idp" 2>/dev/null; then
    add_result "SUCCESS" "Migration script imports successfully"
else
    add_result "ERROR" "Migration script import failed"
    python -c "import scripts.migrate_to_pulumi_idp"
fi

if python -c "import scripts.enhanced_migration_with_improvements" 2>/dev/null; then
    add_result "SUCCESS" "Enhanced migration script imports successfully"
else
    add_result "ERROR" "Enhanced migration script import failed"
    python -c "import scripts.enhanced_migration_with_improvements"
fi

if python -c "import scripts.implement_next_level_enhancements" 2>/dev/null; then
    add_result "SUCCESS" "Next-level enhancements script imports successfully"
else
    add_result "ERROR" "Next-level enhancements script import failed"
    python -c "import scripts.implement_next_level_enhancements"
fi

log_info "Testing infrastructure components..."
if [ -f "infrastructure/components/dashboard_platform.py" ]; then
    if python -c "import sys; sys.path.append('infrastructure'); import components.dashboard_platform" 2>/dev/null; then
        add_result "SUCCESS" "Dashboard platform component imports successfully"
    else
        add_result "ERROR" "Dashboard platform component import failed"
    fi
fi

log_info "Testing Lambda function..."
if [ -f "lambda/dashboard-generator/dashboard_generator.py" ]; then
    cd lambda/dashboard-generator
    if python -c "import dashboard_generator" 2>/dev/null; then
        add_result "SUCCESS" "Lambda function imports successfully"
    else
        add_result "ERROR" "Lambda function import failed"
        python -c "import dashboard_generator"
    fi
    cd ../..
fi

log_info "Testing MCP configuration..."
if [ -f "mcp-config/mcp_servers.json" ]; then
    if python -c "
import json
with open('mcp-config/mcp_servers.json', 'r') as f:
    config = json.load(f)
    print(f'MCP servers configured: {len(config)}')
" 2>/dev/null; then
        add_result "SUCCESS" "MCP configuration is valid JSON"
    else
        add_result "ERROR" "MCP configuration is invalid"
    fi
fi

# Phase 5: Security Audit
echo -e "\n🔒 Phase 5: Security Audit"
echo "--------------------------"

log_info "Running security scan..."
if command_exists bandit; then
    if bandit -r scripts/ infrastructure/ lambda/ -f json -o security_report.json >/dev/null 2>&1; then
        add_result "SUCCESS" "Security scan completed - check security_report.json"
    else
        add_result "WARNING" "Security issues found - check security_report.json"
        bandit -r scripts/ infrastructure/ lambda/ | head -10
    fi
else
    add_result "WARNING" "bandit not installed - skipping security scan"
fi

log_info "Checking for hardcoded secrets..."
SECRET_CHECK=$(grep -r -i "password\|secret\|key\|token" scripts/ infrastructure/ lambda/ --include="*.py" 2>/dev/null | grep -v "# " || true)
if [ -n "$SECRET_CHECK" ]; then
    add_result "WARNING" "Potential hardcoded secrets found"
    echo "$SECRET_CHECK" | head -3
else
    add_result "SUCCESS" "No obvious hardcoded secrets found"
fi

log_info "Checking dependency security..."
if command_exists pip-audit; then
    if pip-audit >/dev/null 2>&1; then
        add_result "SUCCESS" "No vulnerable Python dependencies found"
    else
        add_result "WARNING" "Vulnerable Python dependencies found"
        pip-audit | head -10
    fi
else
    add_result "WARNING" "pip-audit not installed - skipping dependency security check"
fi

# Phase 6: Documentation Check
echo -e "\n📚 Phase 6: Documentation Check"
echo "-------------------------------"

log_info "Checking documentation files..."
DOC_FILES=(
    "ENHANCED_MIGRATION_SUCCESS_REPORT.md"
    "PULUMI_IDP_MIGRATION_PLAN.md"
    "docs/PULUMI_IDP_MIGRATION_GUIDE.md"
    "COMPLETE_TRANSFORMATION_SUMMARY.md"
    "CODEBASE_VALIDATION_PLAN.md"
)

for file in "${DOC_FILES[@]}"; do
    if [ -f "$file" ]; then
        add_result "SUCCESS" "$file exists"
    else
        add_result "WARNING" "$file not found"
    fi
done

log_info "Checking for TODO/FIXME items..."
TODO_CHECK=$(find . -name "*.md" -exec grep -l "TODO\|FIXME\|XXX" {} \; 2>/dev/null || true)
if [ -n "$TODO_CHECK" ]; then
    add_result "INFO" "TODO/FIXME items found in documentation"
    echo "$TODO_CHECK"
else
    add_result "SUCCESS" "No TODO/FIXME items found in documentation"
fi

log_info "Checking for broken references..."
RETOOL_REFS=$(grep -r "retool\|Retool" *.md docs/*.md 2>/dev/null | grep -v "migration\|Retool to Pulumi\|from Retool" || true)
if [ -n "$RETOOL_REFS" ]; then
    add_result "WARNING" "Potential outdated Retool references found"
    echo "$RETOOL_REFS" | head -3
else
    add_result "SUCCESS" "No outdated Retool references found"
fi

# Performance Check
echo -e "\n⚡ Performance Check"
echo "-------------------"

log_info "Checking file sizes..."
LARGE_FILES=$(find . -type f -size +1M -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./venv/*" -not -path "./sophia_venv/*" 2>/dev/null || true)
if [ -n "$LARGE_FILES" ]; then
    add_result "INFO" "Large files found (>1MB)"
    echo "$LARGE_FILES" | head -5
else
    add_result "SUCCESS" "No unusually large files found"
fi

log_info "Analyzing new script sizes..."
for file in "${NEW_PYTHON_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(wc -l < "$file" 2>/dev/null || echo "0")
        if [ "$SIZE" -gt 1000 ]; then
            add_result "INFO" "$file has $SIZE lines (large file)"
        else
            add_result "SUCCESS" "$file has $SIZE lines (reasonable size)"
        fi
    fi
done

# Final Report
echo -e "\n📊 VALIDATION SUMMARY"
echo "====================="

echo -e "\n📈 Results Overview:"
echo "Errors: $ERROR_COUNT"
echo "Warnings: $WARNING_COUNT"
echo "Total Checks: ${#VALIDATION_RESULTS[@]}"

if [ $ERROR_COUNT -eq 0 ] && [ $WARNING_COUNT -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL VALIDATIONS PASSED!${NC}"
    echo "The codebase is ready for production."
    exit 0
elif [ $ERROR_COUNT -eq 0 ]; then
    echo -e "\n${YELLOW}⚠️ VALIDATION COMPLETED WITH WARNINGS${NC}"
    echo "No critical errors found, but some warnings need attention."
    exit 0
else
    echo -e "\n${RED}❌ VALIDATION FAILED${NC}"
    echo "Critical errors found that must be resolved before production."
    exit 1
fi
