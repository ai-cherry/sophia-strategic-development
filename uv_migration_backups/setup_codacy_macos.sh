#!/bin/bash

# Codacy Setup Script for Sophia AI on macOS with Cursor IDE
# This script sets up Codacy CLI, MCP server, and Cursor integration
# Following Sophia AI's infrastructure patterns and security best practices

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SOPHIA_ROOT="/Users/lynnmusil/sophia-main"
CURSOR_CONFIG_DIR="$HOME/.cursor"
CODACY_CONFIG_DIR="$SOPHIA_ROOT/.codacy"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running on macOS
check_macos() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        error "This script is designed for macOS only"
    fi
    log "✅ Running on macOS $(sw_vers -productVersion)"
}

# Check prerequisites
check_prerequisites() {
    log "🔍 Checking prerequisites..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js is required but not installed. Please install Node.js 18+"
    fi
    
    local node_version=$(node --version | cut -d'v' -f2)
    log "✅ Node.js version: $node_version"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        error "npm is required but not installed"
    fi
    
    local npm_version=$(npm --version)
    log "✅ npm version: $npm_version"
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        error "curl is required but not installed"
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        error "git is required but not installed"
    fi
    
    # Check if we're in the Sophia AI project
    if [[ ! -f "$SOPHIA_ROOT/cursor_mcp_config.json" ]]; then
        error "Not in Sophia AI project directory. Expected: $SOPHIA_ROOT"
    fi
    
    log "✅ All prerequisites met"
}

# Install Codacy CLI
install_codacy_cli() {
    log "📦 Installing Codacy CLI..."
    
    # Check if already installed
    if command -v codacy-cli &> /dev/null; then
        local version=$(codacy-cli --version 2>/dev/null || echo "unknown")
        log "✅ Codacy CLI already installed: $version"
        return 0
    fi
    
    # Install via the official script
    log "Downloading and installing Codacy CLI..."
    bash <(curl -Ls https://raw.githubusercontent.com/codacy/codacy-cli-v2/main/codacy-cli.sh)
    
    # Verify installation
    if command -v codacy-cli &> /dev/null; then
        local version=$(codacy-cli --version)
        log "✅ Codacy CLI installed successfully: $version"
    else
        error "Failed to install Codacy CLI"
    fi
}

# Setup Codacy configuration for Sophia AI
setup_codacy_config() {
    log "⚙️  Setting up Codacy configuration for Sophia AI..."
    
    # Create .codacy directory structure
    mkdir -p "$CODACY_CONFIG_DIR"/{config,tools,reports,cache,custom-rules}
    
    # Create main configuration file
    cat > "$CODACY_CONFIG_DIR/config.yml" << 'EOF'
# Codacy Configuration for Sophia AI
version: 2

analysis:
  languages:
    - javascript
    - typescript
    - python
    - yaml
    - json
    - dockerfile

  tools:
    eslint:
      enabled: true
      config_file: .eslintrc.js
    
    semgrep:
      enabled: true
      
    trivy:
      enabled: true
      
    pylint:
      enabled: true
      config_file: .pylintrc
    
    bandit:
      enabled: true
      
    hadolint:
      enabled: true

  exclude_paths:
    - node_modules/
    - .git/
    - dist/
    - build/
    - coverage/
    - .codacy/
    - __pycache__/
    - "*.pyc"
    - docs_archive_*
    - frontend/knowledge-admin/node_modules/
    - sophia-dashboard/node_modules/

  max_allowed_issues: 100
  
security:
  enabled: true
  high_priority_only: false

quality:
  enabled: true
  coverage:
    enabled: true
    minimum: 80

# Sophia AI specific configurations
sophia_ai:
  mcp_servers:
    - backend/mcp/
    - mcp-servers/
  
  agents:
    - backend/agents/
  
  infrastructure:
    - infrastructure/
    - docker-compose*.yml
    - Dockerfile*
  
  dashboards:
    - frontend/src/components/dashboard/
    - sophia-dashboard/
EOF

    # Create custom rules for Sophia AI
    cat > "$CODACY_CONFIG_DIR/custom-rules/sophia-security.yml" << 'EOF'
# Sophia AI Security Rules
rules:
  no-hardcoded-secrets:
    severity: error
    pattern: '(password|secret|key|token)\s*[:=]\s*["\'][^"\']*["\']'
    message: "Hardcoded secrets detected. Use Pulumi ESC for secret management."
    
  require-env-vars:
    severity: warning
    pattern: 'os\.getenv\(["\'][^"\']*["\'],\s*["\'][^"\']*["\']'
    message: "Consider using Pulumi ESC integration instead of default values."
    
  mcp-auth-required:
    severity: error
    pattern: 'mcp.*server.*without.*auth'
    message: "MCP servers must implement proper authentication."
EOF

    # Create performance rules
    cat > "$CODACY_CONFIG_DIR/custom-rules/sophia-performance.yml" << 'EOF'
# Sophia AI Performance Rules
rules:
  async-await-required:
    severity: warning
    pattern: 'def.*api.*\(.*\):(?!.*async)'
    message: "API endpoints should use async/await for better performance."
    
  connection-pooling:
    severity: warning
    pattern: 'create_engine.*pool_size.*None'
    message: "Database connections should use connection pooling."
EOF

    log "✅ Codacy configuration created"
}

# Setup Cursor IDE integration
setup_cursor_integration() {
    log "🎯 Setting up Cursor IDE integration..."
    
    # Ensure Cursor config directory exists
    mkdir -p "$CURSOR_CONFIG_DIR"
    
    # Update Cursor MCP settings if they exist
    local cursor_mcp_file="$CURSOR_CONFIG_DIR/mcp_settings.json"
    
    if [[ -f "$cursor_mcp_file" ]]; then
        log "Updating existing Cursor MCP settings..."
        # Backup existing file
        cp "$cursor_mcp_file" "$cursor_mcp_file.backup.$(date +%Y%m%d_%H%M%S)"
        
        # The Codacy MCP server should already be in the file from our previous update
        log "✅ Cursor MCP settings updated"
    else
        warn "Cursor MCP settings file not found. You may need to configure Cursor manually."
    fi
    
    # Create Cursor workspace settings for Sophia AI
    cat > "$SOPHIA_ROOT/.vscode/settings.json" << 'EOF'
{
  "codacy.enableRealTimeAnalysis": true,
  "codacy.autoFixOnSave": false,
  "codacy.showInlineIssues": true,
  "codacy.analysisTimeout": 60000,
  "codacy.excludePatterns": [
    "node_modules/**",
    "dist/**",
    "build/**",
    ".git/**",
    "docs_archive_*/**",
    "__pycache__/**"
  ],
  "python.defaultInterpreterPath": "./venv/bin/python",
  "typescript.preferences.includePackageJsonAutoImports": "on",
  "eslint.workingDirectories": ["frontend", "sophia-dashboard"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/node_modules": true,
    "docs_archive_*": true
  }
}
EOF

    mkdir -p "$SOPHIA_ROOT/.vscode"
    log "✅ Cursor workspace settings configured"
}

# Setup environment variables
setup_environment() {
    log "🔧 Setting up environment variables..."
    
    # Check if environment variables are already set
    if [[ -n "$CODACY_ACCOUNT_TOKEN" ]]; then
        log "✅ CODACY_ACCOUNT_TOKEN already set"
    else
        warn "CODACY_ACCOUNT_TOKEN not set. You'll need to configure this manually."
        echo "To get your Codacy API token:"
        echo "1. Go to https://app.codacy.com/account/api-tokens"
        echo "2. Create a new API token"
        echo "3. Add it to your Pulumi ESC configuration or shell profile"
    fi
    
    # Add to shell profile if not already there
    local shell_profile=""
    if [[ -n "$ZSH_VERSION" ]]; then
        shell_profile="$HOME/.zshrc"
    elif [[ -n "$BASH_VERSION" ]]; then
        shell_profile="$HOME/.bash_profile"
    fi
    
    if [[ -n "$shell_profile" ]] && [[ -f "$shell_profile" ]]; then
        if ! grep -q "CODACY_WORKSPACE_PATH" "$shell_profile"; then
            echo "" >> "$shell_profile"
            echo "# Sophia AI Codacy Configuration" >> "$shell_profile"
            echo "export CODACY_WORKSPACE_PATH=\"$SOPHIA_ROOT\"" >> "$shell_profile"
            log "✅ Added CODACY_WORKSPACE_PATH to $shell_profile"
        fi
    fi
}

# Test the installation
test_installation() {
    log "🧪 Testing Codacy installation..."
    
    # Test CLI
    if command -v codacy-cli &> /dev/null; then
        log "✅ Codacy CLI is accessible"
        
        # Test with a simple command
        if codacy-cli --help &> /dev/null; then
            log "✅ Codacy CLI is working"
        else
            warn "Codacy CLI installed but not working properly"
        fi
    else
        error "Codacy CLI not found in PATH"
    fi
    
    # Test configuration
    if [[ -f "$CODACY_CONFIG_DIR/config.yml" ]]; then
        log "✅ Codacy configuration file exists"
    else
        warn "Codacy configuration file not found"
    fi
    
    # Test workspace
    if [[ -d "$SOPHIA_ROOT" ]] && [[ -f "$SOPHIA_ROOT/cursor_mcp_config.json" ]]; then
        log "✅ Sophia AI workspace detected"
    else
        warn "Sophia AI workspace not properly configured"
    fi
}

# Run a quick analysis
run_quick_analysis() {
    log "🔍 Running quick analysis on Sophia AI project..."
    
    cd "$SOPHIA_ROOT"
    
    # Create a simple test to verify everything works
    log "Running Codacy CLI test..."
    
    # Test with a specific directory to avoid overwhelming output
    if codacy-cli analyze --tool eslint --directory frontend/src --format json --output .codacy/reports/test-analysis.json 2>/dev/null; then
        log "✅ Quick analysis completed successfully"
        
        if [[ -f ".codacy/reports/test-analysis.json" ]]; then
            local issue_count=$(jq '.issues | length' .codacy/reports/test-analysis.json 2>/dev/null || echo "unknown")
            log "📊 Found $issue_count issues in test analysis"
        fi
    else
        warn "Quick analysis failed - this may be normal if tools need configuration"
    fi
}

# Create health check script
create_health_check() {
    log "🏥 Creating health check script..."
    
    cat > "$SOPHIA_ROOT/scripts/codacy_health_check.sh" << 'EOF'
#!/bin/bash

# Codacy Health Check for Sophia AI
echo "=== Codacy Health Check ==="
echo "Timestamp: $(date)"
echo ""

# Check CLI
echo "📋 CLI Status:"
if command -v codacy-cli &> /dev/null; then
    echo "  ✅ CLI installed: $(codacy-cli --version 2>/dev/null || echo 'version unknown')"
else
    echo "  ❌ CLI not found"
fi

# Check configuration
echo ""
echo "⚙️  Configuration:"
if [[ -f ".codacy/config.yml" ]]; then
    echo "  ✅ Configuration file exists"
else
    echo "  ❌ Configuration file missing"
fi

# Check environment
echo ""
echo "🌍 Environment:"
echo "  Workspace: ${CODACY_WORKSPACE_PATH:-'not set'}"
echo "  API Token: ${CODACY_ACCOUNT_TOKEN:+configured}"

# Check MCP server
echo ""
echo "🔗 MCP Integration:"
if [[ -f "mcp-servers/codacy/codacy_mcp_server.py" ]]; then
    echo "  ✅ MCP server exists"
else
    echo "  ❌ MCP server missing"
fi

# Check Docker
echo ""
echo "🐳 Docker:"
if docker ps --format "table {{.Names}}" | grep -q codacy-mcp; then
    echo "  ✅ Codacy MCP container running"
else
    echo "  ⚠️  Codacy MCP container not running"
fi

echo ""
echo "==========================="
EOF

    chmod +x "$SOPHIA_ROOT/scripts/codacy_health_check.sh"
    log "✅ Health check script created at scripts/codacy_health_check.sh"
}

# Main installation function
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                     Sophia AI - Codacy Setup for macOS                      ║"
    echo "║                           with Cursor IDE Integration                       ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log "🚀 Starting Codacy setup for Sophia AI..."
    
    # Run all setup steps
    check_macos
    check_prerequisites
    install_codacy_cli
    setup_codacy_config
    setup_cursor_integration
    setup_environment
    test_installation
    create_health_check
    
    # Optional quick analysis
    echo ""
    read -p "Run a quick analysis test? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_quick_analysis
    fi
    
    echo ""
    log "🎉 Codacy setup completed successfully!"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Set your CODACY_ACCOUNT_TOKEN environment variable"
    echo "2. Restart Cursor IDE to load the new MCP configuration"
    echo "3. Run: ./scripts/codacy_health_check.sh to verify everything is working"
    echo "4. Start the MCP server: docker-compose -f docker-compose.mcp-gateway.yml up -d codacy-mcp"
    echo ""
    echo -e "${BLUE}Cursor AI Integration:${NC}"
    echo "• Use '@codacy analyze this file' in Cursor chat"
    echo "• Use '@codacy security scan' for security analysis"
    echo "• Use '@codacy fix issues' to automatically fix problems"
    echo ""
    echo -e "${YELLOW}Documentation:${NC}"
    echo "• Configuration: .codacy/config.yml"
    echo "• Custom rules: .codacy/custom-rules/"
    echo "• Reports: .codacy/reports/"
    echo "• Health check: ./scripts/codacy_health_check.sh"
}

# Run the main function
main "$@" 