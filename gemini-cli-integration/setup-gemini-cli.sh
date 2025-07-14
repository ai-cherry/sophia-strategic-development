#!/bin/bash

# Sophia AI - Gemini CLI Integration Setup Script
# Installs and configures Google Gemini CLI with Sophia AI MCP servers

set -e

echo "🚀 Sophia AI - Gemini CLI Integration Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running in Sophia AI project directory
if [ ! -f "package.json" ] && [ ! -f "backend/requirements.txt" ]; then
    print_error "This script must be run from the Sophia AI project root directory"
    exit 1
fi

print_header "1. Checking Prerequisites"

# Check Node.js installation
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_error "Node.js version 18+ is required. Current version: $(node --version)"
    exit 1
fi

print_status "Node.js version: $(node --version) ✓"

# Check npm installation
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi

print_status "npm version: $(npm --version) ✓"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

print_status "Python version: $(python3 --version) ✓"

print_header "2. Installing Gemini CLI"

# Install Gemini CLI globally
print_status "Installing @google/gemini-cli..."
if npm install -g @google/gemini-cli; then
    print_status "Gemini CLI installed successfully ✓"
else
    print_error "Failed to install Gemini CLI"
    exit 1
fi

# Verify installation
if command -v gemini &> /dev/null; then
    print_status "Gemini CLI verification: $(gemini --version) ✓"
else
    print_error "Gemini CLI installation verification failed"
    exit 1
fi

print_header "3. Setting up Sophia AI Integration"

# Create .gemini directory if it doesn't exist
if [ ! -d ".gemini" ]; then
    mkdir -p .gemini
    print_status "Created .gemini directory ✓"
fi

# Copy MCP configuration
if [ -f "gemini-cli-integration/gemini-mcp-config.json" ]; then
    cp gemini-cli-integration/gemini-mcp-config.json .gemini/settings.json
    print_status "Copied MCP configuration to .gemini/settings.json ✓"
else
    print_error "MCP configuration file not found"
    exit 1
fi

# Create Gemini workspace directory
if [ ! -d "/tmp/gemini-workspace" ]; then
    mkdir -p /tmp/gemini-workspace
    print_status "Created Gemini workspace directory ✓"
fi

print_header "4. Creating Project Context Files"

# Create GEMINI.md with project context
cat > GEMINI.md << 'EOF'
# Sophia AI - Gemini CLI Integration

## Project Overview

Sophia AI is an advanced business intelligence platform with AI-powered regulatory compliance monitoring, executive dashboards, and comprehensive data analytics capabilities.

## Architecture

- **Backend**: Python FastAPI with modern_stack Cortex AI integration
- **Frontend**: React with TypeScript and Tailwind CSS
- **MCP Servers**: 4-tier architecture (AI Intelligence, Data Intelligence, Infrastructure, Business Intelligence)
- **Deployment**: Vercel frontend, containerized backend services
- **Monitoring**: Prometheus + Grafana with comprehensive observability

## Key Components

### MCP Server Architecture
1. **sophia-ai-intelligence** (Port 8091) - AI model routing and optimization
2. **sophia-data-intelligence** (Port 8092) - Data warehousing and ETL pipelines
3. **sophia-infrastructure** (Port 8093) - Container and infrastructure management
4. **sophia-business-intelligence** (Port 8094) - CRM and business analytics

### Specialized Agents
- **Regulatory Compliance Agent** - AI-powered regulatory monitoring
- **UI/UX Agent** - Design-to-code automation with Figma integration
- **modern_stack Admin Agent** - Database administration and analytics

## Development Guidelines

### Code Standards
- Python: Black formatting, type hints, comprehensive docstrings
- JavaScript/TypeScript: ESLint + Prettier, strict TypeScript configuration
- React: Functional components with hooks, proper prop typing

### Security Requirements
- All API keys managed via Pulumi ESC
- JWT authentication for MCP servers
- Rate limiting and encryption (AES-256-GCM)
- Comprehensive audit logging

### Testing Standards
- Unit tests with pytest (Python) and Jest (JavaScript)
- Integration tests for MCP server communication
- End-to-end tests for critical user workflows
- Performance testing for dashboard loading times

## Common Tasks

### Development Workflow
```bash
# Start MCP servers
python -m backend.mcp.unified_mcp_servers --server ai-intelligence

# Run frontend development server
cd frontend && npm run dev

# Execute database migrations
python -m backend.database.migrations.run_migrations

# Deploy to production
npm run deploy:production
```

### Debugging and Analysis
- Use `sophia-ai-intelligence` server for AI model debugging
- Use `sophia-data-intelligence` server for data pipeline analysis
- Use `sequential-thinking` server for complex problem reasoning

### Business Intelligence Queries
- Dashboard metrics available via `sophia-business-intelligence` server
- modern_stack queries via `sophia-data-intelligence` server
- Regulatory compliance status via `sophia-regulatory-compliance` server

## File Structure

```
sophia-main/
├── backend/                 # Python FastAPI backend
│   ├── agents/             # AI agent implementations
│   ├── api/                # REST API endpoints
│   ├── core/               # Core business logic
│   ├── database/           # Database models and migrations
│   └── mcp/                # MCP server implementations
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── lib/            # Utility libraries
│   │   └── pages/          # Page components
├── ui-ux-agent/           # UI/UX automation system
├── infrastructure/        # Infrastructure as code
└── gemini-cli-integration/ # Gemini CLI configuration
```

## Best Practices

### Performance Optimization
- Use semantic caching for AI model responses
- Implement connection pooling for database operations
- Leverage modern_stack Cortex for heavy analytics workloads
- Monitor performance metrics via Prometheus/Grafana

### Security Best Practices
- Never commit API keys or sensitive credentials
- Use environment variables for configuration
- Implement proper input validation and sanitization
- Regular security audits and dependency updates

### Collaboration Guidelines
- Use descriptive commit messages with emoji prefixes
- Create feature branches for new development
- Comprehensive code reviews before merging
- Document architectural decisions in ADR format

## Troubleshooting

### Common Issues
- MCP server connection failures: Check port availability and environment variables
- Frontend build errors: Verify Node.js version and dependency compatibility
- Database connection issues: Validate modern_stack credentials and network connectivity
- Performance degradation: Monitor Grafana dashboards for bottlenecks

### Support Resources
- Internal documentation: `/docs` directory
- API documentation: Available at `/api/docs` endpoint
- MCP server logs: Available via Prometheus metrics
- Team communication: Slack #sophia-ai-dev channel
EOF

print_status "Created GEMINI.md project context file ✓"

print_header "5. Setting up Environment Configuration"

# Create environment template
cat > .gemini/env.template << 'EOF'
# Sophia AI - Gemini CLI Environment Configuration
# Copy this file to .gemini/env and fill in your credentials

# Pulumi Configuration
PULUMI_ORG=scoobyjava-org
PULUMI_STACK=sophia-ai-production

# API Keys (Get from Pulumi ESC)
FIGMA_PERSONAL_ACCESS_TOKEN=your_figma_token_here
OPENAI_API_KEY=your_openai_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# modern_stack Configuration
modern_stack_ACCOUNT=your_account_here
modern_stack_USER=your_user_here
modern_stack_PASSWORD=your_password_here
modern_stack_WAREHOUSE=your_warehouse_here
modern_stack_DATABASE=your_database_here
modern_stack_SCHEMA=your_schema_here

# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_BASE_PORT=8091

# Gemini CLI Configuration
GEMINI_CLI_WORKSPACE=/tmp/gemini-workspace
GEMINI_CLI_LOG_LEVEL=info
GEMINI_CLI_ENABLE_CHECKPOINTING=true
EOF

print_status "Created environment template ✓"

print_header "6. Installing Additional Dependencies"

# Install MCP-related Python packages if not already installed
if [ -f "backend/requirements.txt" ]; then
    print_status "Installing Python dependencies..."
    pip3 install -r backend/requirements.txt
    print_status "Python dependencies installed ✓"
fi

# Install frontend dependencies if not already installed
if [ -f "frontend/package.json" ]; then
    print_status "Installing frontend dependencies..."
    cd frontend && npm install && cd ..
    print_status "Frontend dependencies installed ✓"
fi

print_header "7. Creating Helper Scripts"

# Create MCP server startup script
cat > gemini-cli-integration/start-mcp-servers.sh << 'EOF'
#!/bin/bash

# Sophia AI - MCP Servers Startup Script
# Starts all MCP servers for Gemini CLI integration

echo "🚀 Starting Sophia AI MCP Servers..."

# Load environment variables
if [ -f ".gemini/env" ]; then
    source .gemini/env
    echo "✓ Environment variables loaded"
else
    echo "⚠️  Warning: .gemini/env file not found. Using defaults."
fi

# Start core MCP servers in background
echo "Starting AI Intelligence server..."
python -m backend.mcp.unified_mcp_servers --server ai-intelligence &
AI_INTELLIGENCE_PID=$!

echo "Starting Data Intelligence server..."
python -m backend.mcp.unified_mcp_servers --server data-intelligence &
DATA_INTELLIGENCE_PID=$!

echo "Starting Infrastructure server..."
python -m backend.mcp.unified_mcp_servers --server infrastructure &
INFRASTRUCTURE_PID=$!

echo "Starting Business Intelligence server..."
python -m backend.mcp.unified_mcp_servers --server business-intelligence &
BUSINESS_INTELLIGENCE_PID=$!

# Wait for servers to start
sleep 5

# Check server health
echo "Checking server health..."
for port in 8091 8092 8093 8094; do
    if nc -z localhost $port; then
        echo "✓ Server on port $port is running"
    else
        echo "✗ Server on port $port is not responding"
    fi
done

echo "🎉 MCP servers startup complete!"
echo "PIDs: AI=$AI_INTELLIGENCE_PID, Data=$DATA_INTELLIGENCE_PID, Infra=$INFRASTRUCTURE_PID, Business=$BUSINESS_INTELLIGENCE_PID"

# Create PID file for cleanup
echo "$AI_INTELLIGENCE_PID $DATA_INTELLIGENCE_PID $INFRASTRUCTURE_PID $BUSINESS_INTELLIGENCE_PID" > .gemini/mcp-servers.pid

echo "To stop servers, run: ./gemini-cli-integration/stop-mcp-servers.sh"
EOF

chmod +x gemini-cli-integration/start-mcp-servers.sh
print_status "Created MCP servers startup script ✓"

# Create MCP server shutdown script
cat > gemini-cli-integration/stop-mcp-servers.sh << 'EOF'
#!/bin/bash

# Sophia AI - MCP Servers Shutdown Script

echo "🛑 Stopping Sophia AI MCP Servers..."

if [ -f ".gemini/mcp-servers.pid" ]; then
    PIDS=$(cat .gemini/mcp-servers.pid)
    for pid in $PIDS; do
        if kill -0 $pid 2>/dev/null; then
            echo "Stopping process $pid..."
            kill $pid
        fi
    done
    rm .gemini/mcp-servers.pid
    echo "✓ All MCP servers stopped"
else
    echo "⚠️  PID file not found. Attempting to kill by port..."
    for port in 8091 8092 8093 8094; do
        PID=$(lsof -ti:$port)
        if [ ! -z "$PID" ]; then
            echo "Killing process $PID on port $port"
            kill $PID
        fi
    done
fi

echo "🎉 MCP servers shutdown complete!"
EOF

chmod +x gemini-cli-integration/stop-mcp-servers.sh
print_status "Created MCP servers shutdown script ✓"

# Create Gemini CLI test script
cat > gemini-cli-integration/test-integration.sh << 'EOF'
#!/bin/bash

# Sophia AI - Gemini CLI Integration Test Script

echo "🧪 Testing Gemini CLI Integration with Sophia AI..."

# Test basic Gemini CLI functionality
echo "Testing Gemini CLI installation..."
if gemini --version; then
    echo "✓ Gemini CLI is working"
else
    echo "✗ Gemini CLI test failed"
    exit 1
fi

# Test MCP server connectivity
echo "Testing MCP server connectivity..."
for port in 8091 8092 8093 8094; do
    if nc -z localhost $port; then
        echo "✓ MCP server on port $port is accessible"
    else
        echo "⚠️  MCP server on port $port is not accessible"
    fi
done

# Test Gemini CLI with MCP configuration
echo "Testing Gemini CLI with MCP configuration..."
if [ -f ".gemini/settings.json" ]; then
    echo "✓ MCP configuration file exists"

    # Validate JSON syntax
    if python3 -m json.tool .gemini/settings.json > /dev/null; then
        echo "✓ MCP configuration JSON is valid"
    else
        echo "✗ MCP configuration JSON is invalid"
        exit 1
    fi
else
    echo "✗ MCP configuration file not found"
    exit 1
fi

echo "🎉 Integration test complete!"
echo ""
echo "Next steps:"
echo "1. Copy .gemini/env.template to .gemini/env and fill in your credentials"
echo "2. Start MCP servers: ./gemini-cli-integration/start-mcp-servers.sh"
echo "3. Run Gemini CLI: gemini"
echo "4. Test MCP integration with: gemini 'Analyze the Sophia AI codebase structure'"
EOF

chmod +x gemini-cli-integration/test-integration.sh
print_status "Created integration test script ✓"

print_header "8. Final Configuration"

# Create .gitignore entries for Gemini CLI
if [ ! -f ".gitignore" ]; then
    touch .gitignore
fi

# Add Gemini CLI specific ignores
cat >> .gitignore << 'EOF'

# Gemini CLI Integration
.gemini/env
.gemini/cache/
.gemini/logs/
.gemini/mcp-servers.pid
/tmp/gemini-workspace/
EOF

print_status "Updated .gitignore for Gemini CLI ✓"

print_header "9. Setup Complete!"

echo ""
echo "🎉 Sophia AI - Gemini CLI Integration Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy environment template: cp .gemini/env.template .gemini/env"
echo "2. Edit .gemini/env with your actual credentials"
echo "3. Start MCP servers: ./gemini-cli-integration/start-mcp-servers.sh"
echo "4. Test integration: ./gemini-cli-integration/test-integration.sh"
echo "5. Launch Gemini CLI: gemini"
echo ""
echo "📚 Documentation:"
echo "- Project context: GEMINI.md"
echo "- MCP configuration: .gemini/settings.json"
echo "- Environment template: .gemini/env.template"
echo ""
echo "🔧 Management Scripts:"
echo "- Start servers: ./gemini-cli-integration/start-mcp-servers.sh"
echo "- Stop servers: ./gemini-cli-integration/stop-mcp-servers.sh"
echo "- Test integration: ./gemini-cli-integration/test-integration.sh"
echo ""
echo "🚀 Ready to enhance your Sophia AI development workflow with Gemini CLI!"
