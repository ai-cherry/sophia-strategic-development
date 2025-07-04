#!/bin/bash
# Convenience script for running dependency security audits locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Sophia AI Dependency Security Audit${NC}"
echo "======================================"
echo ""

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ UV is not installed. Please install it first:${NC}"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Parse command line arguments
SEVERITY_THRESHOLD="high"
OUTPUT_FORMAT="human"
SAVE_REPORT=false
CHECK_LICENSES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --severity)
            SEVERITY_THRESHOLD="$2"
            shift 2
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --save)
            SAVE_REPORT=true
            shift
            ;;
        --check-licenses)
            CHECK_LICENSES=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --severity <level>    Set severity threshold (critical, high, medium, low) [default: high]"
            echo "  --format <format>     Output format (human, json, markdown) [default: human]"
            echo "  --save                Save reports to security/reports directory"
            echo "  --check-licenses      Also run license compliance checks"
            echo "  --help                Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Create reports directory if saving
if [ "$SAVE_REPORT" = true ]; then
    mkdir -p security/reports
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
fi

# Install dependencies if not already installed
echo -e "${BLUE}📦 Ensuring dependencies are installed...${NC}"
uv sync --group dev

# Run pip-audit
echo ""
echo -e "${BLUE}🔒 Running pip-audit vulnerability scan...${NC}"

if [ "$OUTPUT_FORMAT" = "json" ]; then
    if [ "$SAVE_REPORT" = true ]; then
        uv run pip-audit --format=json --output=security/reports/pip-audit-${TIMESTAMP}.json
        echo -e "${GREEN}✅ Report saved to security/reports/pip-audit-${TIMESTAMP}.json${NC}"
    else
        uv run pip-audit --format=json
    fi
elif [ "$OUTPUT_FORMAT" = "markdown" ]; then
    if [ "$SAVE_REPORT" = true ]; then
        uv run pip-audit --format=markdown --output=security/reports/pip-audit-${TIMESTAMP}.md
        echo -e "${GREEN}✅ Report saved to security/reports/pip-audit-${TIMESTAMP}.md${NC}"
    else
        uv run pip-audit --format=markdown
    fi
else
    # Human-readable format
    echo ""
    AUDIT_OUTPUT=$(uv run pip-audit --format=json 2>&1)

    if [ $? -eq 0 ]; then
        # Parse JSON output for human-readable display
        VULN_COUNT=$(echo "$AUDIT_OUTPUT" | python -c "import json, sys; data = json.load(sys.stdin); print(len(data.get('vulnerabilities', [])))" 2>/dev/null || echo "0")

        if [ "$VULN_COUNT" = "0" ]; then
            echo -e "${GREEN}✅ No vulnerabilities found!${NC}"
        else
            echo -e "${YELLOW}⚠️  Found $VULN_COUNT vulnerabilities:${NC}"
            echo ""

            # Parse and display vulnerabilities
            echo "$AUDIT_OUTPUT" | python -c "
import json
import sys

data = json.load(sys.stdin)
vulns = data.get('vulnerabilities', [])

# Group by severity
by_severity = {'critical': [], 'high': [], 'medium': [], 'low': [], 'unknown': []}
for vuln in vulns:
    severity = vuln.get('severity', 'unknown').lower()
    if severity not in by_severity:
        severity = 'unknown'
    by_severity[severity].append(vuln)

# Display by severity
for severity in ['critical', 'high', 'medium', 'low', 'unknown']:
    if by_severity[severity]:
        print(f'\n{severity.upper()} ({len(by_severity[severity])}):')
        for vuln in by_severity[severity]:
            print(f\"  • {vuln.get('name', 'unknown')} {vuln.get('version', '')} - {vuln.get('id', 'unknown')}\")
            if vuln.get('fix_versions'):
                print(f\"    Fix: upgrade to {', '.join(vuln.get('fix_versions', []))}\")
"

            if [ "$SAVE_REPORT" = true ]; then
                echo "$AUDIT_OUTPUT" > security/reports/pip-audit-${TIMESTAMP}.json
                echo -e "${GREEN}✅ Full report saved to security/reports/pip-audit-${TIMESTAMP}.json${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ pip-audit scan failed${NC}"
        exit 1
    fi
fi

# Run safety check
echo ""
echo -e "${BLUE}🛡️  Running safety vulnerability scan...${NC}"

if [ "$OUTPUT_FORMAT" = "json" ]; then
    if [ "$SAVE_REPORT" = true ]; then
        uv run safety check --json --output=security/reports/safety-${TIMESTAMP}.json
        echo -e "${GREEN}✅ Report saved to security/reports/safety-${TIMESTAMP}.json${NC}"
    else
        uv run safety check --json
    fi
else
    # Human-readable format
    echo ""
    SAFETY_OUTPUT=$(uv run safety check 2>&1)
    SAFETY_EXIT_CODE=$?

    if [ $SAFETY_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ No vulnerabilities found by safety!${NC}"
    else
        echo "$SAFETY_OUTPUT" | grep -E "^[│├└]" || echo "$SAFETY_OUTPUT"

        if [ "$SAVE_REPORT" = true ]; then
            echo "$SAFETY_OUTPUT" > security/reports/safety-${TIMESTAMP}.txt
            echo -e "${GREEN}✅ Report saved to security/reports/safety-${TIMESTAMP}.txt${NC}"
        fi
    fi
fi

# Run license check if requested
if [ "$CHECK_LICENSES" = true ]; then
    echo ""
    echo -e "${BLUE}📋 Running license compliance check...${NC}"
    echo ""

    LICENSE_OUTPUT=$(uv run safety license 2>&1)
    LICENSE_EXIT_CODE=$?

    if [ $LICENSE_EXIT_CODE -eq 0 ]; then
        echo "$LICENSE_OUTPUT" | grep -E "^[│├└]" || echo "$LICENSE_OUTPUT"

        if [ "$SAVE_REPORT" = true ]; then
            echo "$LICENSE_OUTPUT" > security/reports/licenses-${TIMESTAMP}.txt
            echo -e "${GREEN}✅ License report saved to security/reports/licenses-${TIMESTAMP}.txt${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  License check encountered issues${NC}"
    fi
fi

# Summary
echo ""
echo -e "${BLUE}📊 Audit Summary${NC}"
echo "================"

# Check for high/critical vulnerabilities
HIGH_CRITICAL_COUNT=0
if [ -f security/reports/pip-audit-${TIMESTAMP}.json ]; then
    HIGH_CRITICAL_COUNT=$(python -c "
import json
with open('security/reports/pip-audit-${TIMESTAMP}.json') as f:
    data = json.load(f)
    vulns = data.get('vulnerabilities', [])
    high_critical = [v for v in vulns if v.get('severity', '').lower() in ['high', 'critical']]
    print(len(high_critical))
" 2>/dev/null || echo "0")
fi

if [ "$HIGH_CRITICAL_COUNT" -gt 0 ]; then
    echo -e "${RED}❌ Found $HIGH_CRITICAL_COUNT HIGH/CRITICAL vulnerabilities that should be fixed immediately!${NC}"
    exit 1
else
    echo -e "${GREEN}✅ No HIGH/CRITICAL vulnerabilities found${NC}"
fi

echo ""
echo "Run with --help to see all available options."
